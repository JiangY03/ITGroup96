from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
import io
from .models import Skin, Inventory, Transaction

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
        ]
        return custom_urls + urls
    
    def import_csv(self, request):
        if request.method == 'POST':
            csv_file = request.FILES.get('csv_file')
            if not csv_file:
                messages.error(request, 'Please upload a CSV file.')
                return redirect('..')
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Please upload a valid CSV file.')
                return redirect('..')
            
            try:
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                
                for row in csv_data:
                    # Set default values for optional fields
                    category = row.get('category', 'rifle')
                    description = row.get('description', '')
                    is_active = row.get('is_active', 'true').lower() == 'true'
                    
                    # Validate required fields
                    if not row.get('name') or not row.get('price'):
                        messages.error(request, 'Name and price are required fields.')
                        return redirect('..')
                    
                    # Create or update skin
                    Skin.objects.update_or_create(
                        name=row['name'],
                        defaults={
                            'category': category,
                            'price': float(row['price']),
                            'description': description,
                            'is_active': is_active
                        }
                    )
                
                messages.success(request, 'CSV file imported successfully.')
                return redirect('..')
                
            except Exception as e:
                messages.error(request, f'Error importing CSV file: {str(e)}')
                return redirect('..')
        
        return render(request, 'admin/market/skin/import_csv.html')

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin', 'acquired_date')
    list_filter = ('acquired_date',)
    search_fields = ('user__username', 'skin__name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'amount', 'transaction_type', 'timestamp')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('user__username', 'item__name')
