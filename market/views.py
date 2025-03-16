# market/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Skin, Inventory, Transaction
from django.db import transaction
from accounts.models import Profile, Transaction, UserActivityLog
import logging
from django.utils import timezone
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

@login_required
def market_view(request):
    skins = Skin.objects.all()
    return render(request, 'market.html', {'skins': skins})

@csrf_exempt
def recharge(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            card_number = data.get('card_number')
            amount = float(data.get('amount'))
            
            if card_number and amount > 0:
                with transaction.atomic():
                    user = request.user
                    user.balance += amount
                    user.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        user=user,
                        description=f"Wallet recharge",
                        amount=amount,
                        date=timezone.now()
                    )
                    
                    # Add user activity log
                    UserActivityLog.objects.create(
                        user=user,
                        action_type="recharge",
                        details=f"Recharged wallet with amount ¥{amount}"
                    )
                    
                    return JsonResponse({
                        'success': True,
                        'new_balance': user.balance
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid card number or amount'
                })
        except Exception as e:
            logger.error(f"Error in recharge: {str(e)}", exc_info=True)
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
            
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })

@login_required
@csrf_exempt
def buy_skin(request, item_id):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get skin and user information
                skin = get_object_or_404(Skin, id=item_id)
                user = request.user
                profile = Profile.objects.get(user=user)

                # Check if user already owns this skin
                if Inventory.objects.filter(user=user, skin=skin).exists():
                    return JsonResponse({
                        "success": False,
                        "error": "You already own this skin"
                    })

                # Check if user has enough balance
                if float(user.balance) < float(skin.price):
                    return JsonResponse({
                        "success": False,
                        "error": f"Insufficient balance. You need ¥{skin.price}"
                    })

                # Deduct balance from both User and Profile
                user.balance = float(user.balance) - float(skin.price)
                profile.wallet_balance = float(profile.wallet_balance) - float(skin.price)
                
                # Save both models
                user.save()
                profile.save()

                # Add to inventory with current timestamp
                inventory_item = Inventory.objects.create(
                    user=user,
                    skin=skin,
                    acquired_date=timezone.now()
                )

                # Record transaction with negative amount (purchase)
                Transaction.objects.create(
                    user=user,
                    description=f"Purchased {skin.name}",
                    amount=-float(skin.price),  # Negative amount indicates expenditure
                    date=timezone.now()
                )

                # Add user activity log
                UserActivityLog.objects.create(
                    user=user,
                    action_type="purchase",
                    details=f"Purchased skin: {skin.name} for ¥{skin.price}"
                )

                return JsonResponse({
                    "success": True,
                    "message": "Purchase successful",
                    "new_balance": str(user.balance)
                })

        except Exception as e:
            logger.error(f"Error in buy_skin: {str(e)}", exc_info=True)
            return JsonResponse({
                "success": False,
                "error": str(e)
            })

    return JsonResponse({
        "success": False,
        "error": "Method not allowed"
    })

def market(request):
    # Get all skins from the database with optimized query
    skins = Skin.objects.all().order_by('name')
    
    # Check if user is logged in
    is_authenticated = request.user.is_authenticated
    
    # Get list of skin IDs owned by the user (only for logged-in users)
    if is_authenticated:
        owned_skins = set(Inventory.objects.filter(user=request.user).values_list('skin_id', flat=True))
    else:
        owned_skins = set()
    
    # Add ownership flag for each skin
    for skin in skins:
        skin.is_owned = skin.id in owned_skins
    
    # Add pagination
    paginator = Paginator(skins, 15)  # Show 15 items per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'market.html', {
        'skins': page_obj,
        'page_obj': page_obj,
        'is_paginated': True,
        'paginator': paginator,
        'is_authenticated': is_authenticated,  # Pass authentication status to template
    })

