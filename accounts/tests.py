from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Profile
from market.models import Skin, Transaction
import json

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.test_user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, {
            'username': self.test_user_data['username'],
            'password1': self.test_user_data['password'],
            'password2': self.test_user_data['password'],
            'email': self.test_user_data['email']
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login page
        self.assertTrue(User.objects.filter(username=self.test_user_data['username']).exists())
        self.assertTrue(Profile.objects.filter(user__username=self.test_user_data['username']).exists())

    def test_user_login(self):
        # Create test user
        user = User.objects.create_user(
            username=self.test_user_data['username'],
            password=self.test_user_data['password'],
            email=self.test_user_data['email']
        )
        # Test login
        response = self.client.post(self.login_url, {
            'username': self.test_user_data['username'],
            'password': self.test_user_data['password']
        })
        self.assertEqual(response.status_code, 302)  # Redirect to homepage
        self.assertTrue('_auth_user_id' in self.client.session)

class UserProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile_url = reverse('profile')
        self.recharge_url = reverse('recharge_wallet')

    def test_profile_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')

    def test_recharge_balance(self):
        self.client.login(username='testuser', password='testpass123')
        initial_balance = self.profile.wallet_balance
        recharge_amount = 100
        
        response = self.client.post(
            self.recharge_url,
            data=json.dumps({
                'amount': recharge_amount,
                'card_number': '1234567890123456'  # Added required card number
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.wallet_balance, initial_balance + recharge_amount)

class AdminTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.admin_dashboard_url = reverse('admin_dashboard')
        self.admin_users_url = reverse('user_management')
        self.admin_skins_url = reverse('skin_management')

    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_admin_users_list(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(self.admin_users_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'admin')

class AccountsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_creation(self):
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.wallet_balance, 0.00)
