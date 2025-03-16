from rest_framework import serializers
from .models import Skin, Inventory, Transaction

class SkinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skin
        fields = ['id', 'name', 'price', 'description', 'image']

class InventorySerializer(serializers.ModelSerializer):
    skin = SkinSerializer(read_only=True)
    
    class Meta:
        model = Inventory
        fields = ['id', 'user', 'skin', 'acquired_date']
        read_only_fields = ['user', 'acquired_date']

class TransactionSerializer(serializers.ModelSerializer):
    skin = SkinSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'skin', 'amount', 'transaction_type', 'timestamp']
        read_only_fields = ['user', 'timestamp'] 