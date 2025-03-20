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
                # Try different encodings
                encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
                decoded_file = None
                
                for encoding in encodings:
                    try:
                        csv_file.seek(0)  # Reset file pointer
                        decoded_file = csv_file.read().decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if decoded_file is None:
                    messages.error(request, 'Unable to decode the CSV file. Please ensure it is properly encoded.')
                    return redirect('..')
                
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                
                # Validate CSV headers
                required_fields = {'name', 'price'}
                headers = set(csv_data.fieldnames or [])
                missing_fields = required_fields - headers
                
                if missing_fields:
                    messages.error(request, f'Missing required columns: {", ".join(missing_fields)}')
                    return redirect('..')
                
                success_count = 0
                error_count = 0
                
                for row in csv_data:
                    try:
                        # Set default values for optional fields
                        category = row.get('category', 'rifle')
                        description = row.get('description', '')
                        is_active = row.get('is_active', 'true').lower() == 'true'
                        
                        # Validate required fields
                        if not row.get('name') or not row.get('price'):
                            error_count += 1
                            continue
                        
                        # Validate price format
                        try:
                            price = float(row['price'])
                            if price < 0:
                                error_count += 1
                                continue
                        except ValueError:
                            error_count += 1
                            continue
                        
                        # Create or update skin
                        Skin.objects.update_or_create(
                            name=row['name'],
                            defaults={
                                'category': category,
                                'price': price,
                                'description': description,
                                'is_active': is_active
                            }
                        )
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        continue
                
                if success_count > 0:
                    messages.success(request, f'Successfully imported {success_count} skins.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} rows were skipped due to errors.')
                
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
