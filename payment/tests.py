from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile
from decimal import Decimal

class PaymentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_initial_wallet_balance(self):
        """Test that new users start with zero balance"""
        self.assertEqual(self.profile.wallet_balance, Decimal('0.00'))

    def test_add_funds(self):
        """Test adding funds to wallet"""
        initial_balance = self.profile.wallet_balance
        amount_to_add = Decimal('100.00')
        
        # Simulate adding funds
        self.profile.wallet_balance += amount_to_add
        self.profile.save()
        
        # Refresh from database
        self.profile.refresh_from_db()
        
        # Check new balance
        self.assertEqual(
            self.profile.wallet_balance,
            initial_balance + amount_to_add
        )

    def test_insufficient_funds(self):
        """Test transaction with insufficient funds"""
        initial_balance = self.profile.wallet_balance
        amount_to_spend = Decimal('1000.00')  # More than balance
        
        # Attempt to spend
        can_spend = self.profile.wallet_balance >= amount_to_spend
        
        self.assertFalse(can_spend)
        self.assertEqual(self.profile.wallet_balance, initial_balance)  # Balance should not change

    def test_successful_transaction(self):
        """Test successful transaction"""
        # Add initial funds
        self.profile.wallet_balance = Decimal('1000.00')
        self.profile.save()
        
        amount_to_spend = Decimal('500.00')
        initial_balance = self.profile.wallet_balance
        
        # Simulate transaction
        if self.profile.wallet_balance >= amount_to_spend:
            self.profile.wallet_balance -= amount_to_spend
            self.profile.save()
        
        # Refresh from database
        self.profile.refresh_from_db()
        
        # Check new balance
        self.assertEqual(
            self.profile.wallet_balance,
            initial_balance - amount_to_spend
        )
