from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, Profile
from .models import Skin, Transaction as MarketTransaction
import json

class MarketViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile.wallet_balance = 1000
        self.profile.save()
        
        self.skin = Skin.objects.create(
            name='Test Skin',
            price=100,
            description='Test skin description'
        )
        self.market_url = reverse('market')
        self.buy_url = reverse('buy_skin', args=[self.skin.id])

    def test_market_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.market_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Skin')
        self.assertContains(response, '100')

    def test_buy_skin_success(self):
        self.client.login(username='testuser', password='testpass123')
        initial_balance = self.profile.wallet_balance
        
        response = self.client.post(self.buy_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data.get('success'))
        
        # Check if balance is correctly deducted
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.wallet_balance, initial_balance - self.skin.price)
        
        # Check if transaction record is created
        self.assertTrue(MarketTransaction.objects.filter(
            user=self.user,
            item=self.skin,
            amount=-self.skin.price,
            transaction_type='purchase'
        ).exists())

    def test_buy_skin_insufficient_balance(self):
        self.client.login(username='testuser', password='testpass123')
        self.profile.wallet_balance = 50  # Set balance lower than skin price
        self.profile.save()
        
        response = self.client.post(self.buy_url)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data.get('success'))
        self.assertIn('Insufficient', response_data.get('error', ''))

class TransactionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.skin = Skin.objects.create(
            name='Test Skin',
            price=100
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile.wallet_balance = 1000
        self.profile.save()

    def test_transaction_creation(self):
        transaction = MarketTransaction.objects.create(
            user=self.user,
            item=self.skin,
            amount=-self.skin.price,
            transaction_type='purchase'
        )
        self.assertEqual(transaction.amount, -100)
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(transaction.item, self.skin)

    def test_transaction_history(self):
        self.client.login(username='testuser', password='testpass123')
        # Create some transaction records
        MarketTransaction.objects.create(
            user=self.user,
            item=self.skin,
            amount=-self.skin.price,
            transaction_type='purchase'
        )
        
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Skin')
        self.assertContains(response, '-100')
