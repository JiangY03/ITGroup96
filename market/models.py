from django.db import models
from accounts.models import User 
from django.conf import settings
 # Custom user model, if not customized, use default User
# from django.contrib.auth.models import User  # No need to import User again
# from market.models import Skin  # No need to import Skin if it's in the current file

class Skin(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='skins/', null=True, blank=True)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='market_inventory')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE)
    acquired_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'skin')
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"{self.user.username}'s {self.skin.name}"


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Skin, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # e.g., "purchase", "sale"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.item.name}"
    
