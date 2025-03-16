from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal
from .models import UserProfile

def recharge_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get the user's profile (assumes you have a OneToOneField from User to UserProfile)
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == "POST":
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except Exception:
            messages.error(request, "Please enter a valid amount.")
            return redirect('recharge')
        
        card_number = request.POST.get('card_number')
        
        if amount <= 0 or not card_number:
            messages.error(request, "Please provide a valid card number and amount.")
            return redirect('recharge')
        
        # Update wallet balance
        profile.wallet += amount
        profile.save()
        
        messages.success(request, f"Successfully recharged ¥{amount}.")
        return redirect('account')  # Redirect to account or market page
    return render(request, 'recharge.html', {'profile': profile})
