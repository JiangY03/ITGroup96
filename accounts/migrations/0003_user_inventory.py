# Generated by Django 4.2.20 on 2025-03-09 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_alter_inventory_user_delete_transaction'),
        ('accounts', '0002_transaction_inventoryitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='inventory',
            field=models.ManyToManyField(blank=True, related_name='users', to='market.skin'),
        ),
    ]
