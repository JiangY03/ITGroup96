from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from .models import Profile, Transaction, AdminLog, UserActivityLog, User
from django.utils import timezone
from decimal import Decimal
from django.core.paginator import Paginator
from django.db.models import Q
from market.models import Skin
import csv
from django.http import HttpResponse
from datetime import datetime, time
from django.db.models import Sum

logger = logging.getLogger(__name__)

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        logger.info(f"Login attempt: username={username}, user={user}")

        if user is not None:
            login(request, user)
            
            # Record login activity
            UserActivityLog.objects.create(
                user=user,
                action_type="login",
                details=f"User logged in successfully"
            )
            
            # Check if user is admin
            if user.is_staff:
                logger.info("Admin user logged in, redirecting to admin dashboard")
                return redirect('admin_dashboard')
            
            # Redirect logic for non-admin users
            next_url = request.POST.get("next")
            if next_url and next_url.strip():
                logger.info(f"Login successful, redirecting to {next_url}")
                return redirect(next_url)
            else:
                logger.info("Login successful, redirecting to home")
                return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            logger.warning("Login failed: Invalid username or password")

    next_url = request.GET.get("next", "")
    return render(request, "login.html", {"next": next_url})

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after registration
            messages.success(request, "Registration successful. You are now logged in.")
            return redirect("home")
        else:
            # Provide detailed error information
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'password2':
                        messages.error(request, f"Password error: {error}")
                    elif field == 'username':
                        messages.error(request, f"Username error: {error}")
                    elif field == 'email':
                        messages.error(request, f"Email error: {error}")
                    else:
                        messages.error(request, error)
    else:
        form = CustomUserCreationForm()

    return render(request, "register.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("login")


def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')


@login_required
def account_view(request):
    user = request.user
    inventory = user.inventory.all()
    return render(request, 'profile.html', {'inventory': inventory})



@login_required
def profile(request):
    """ User Account Page """
    profile, created = Profile.objects.get_or_create(user=request.user)
    # Get user's inventory information
    inventory = request.user.market_inventory.all().select_related('skin')
    # Get user's transaction history, ordered by date descending
    market_transactions = request.user.transaction_set.all().order_by('-timestamp')
    account_transactions = request.user.account_transactions.all().order_by('-date')
    
    return render(request, 'profile.html', {
        'profile': profile,
        'inventory': inventory,
        'market_transactions': market_transactions,
        'account_transactions': account_transactions
    })


@login_required
def user_profile_view(request):
    # Get or create user Profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Now you can use the profile object
    return render(request, 'profile.html', {'profile': profile})
logger = logging.getLogger(__name__)



logger = logging.getLogger(__name__)

@login_required
def recharge_wallet(request):
    """Handle Wallet Recharge"""
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # Parse request body
        data = json.loads(request.body)
        amount = Decimal(data.get("amount", 0))  # Convert to Decimal type
        card_number = data.get("card_number")

        # Validate recharge amount
        if amount <= 0:
            return JsonResponse({"error": "Invalid recharge amount"}, status=400)

        # Validate card number (assuming 16 digits required)
        if not card_number or not card_number.isdigit() or len(card_number) != 16:
            return JsonResponse({"error": "Invalid card number"}, status=400)

        # Get or create user Profile and update both balances
        with transaction.atomic():  # Use transaction to ensure data consistency
            # Update Profile balance
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.wallet_balance += amount
            profile.save()

            # Update User balance
            user = request.user
            user.balance += amount
            user.save()

            # Create recharge transaction record
            Transaction.objects.create(
                user=request.user,
                description=f"Wallet recharge",
                amount=amount,
                date=timezone.now()
            )

        # Log successful recharge
        logger.info(f"User {request.user.username} recharged {amount} successfully. New balance: {profile.wallet_balance}")

        return JsonResponse({"success": True, "new_balance": profile.wallet_balance})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except ValueError:
        logger.error("Invalid input format")
        return JsonResponse({"error": "Invalid input"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error during recharge: {e}")
        return JsonResponse({"error": "Internal server error"}, status=500)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Get today's date range
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = timezone.make_aware(datetime.combine(today, time.max))

    # Statistics data
    total_users = User.objects.count()
    total_skins = Skin.objects.count()  # Remove is_active filter
    total_transactions = Transaction.objects.filter(
        date__range=(today_start, today_end)
    ).count()
    
    # Calculate today's revenue
    today_revenue = Transaction.objects.filter(
        date__range=(today_start, today_end),
        amount__gt=0  # Only count positive amounts (income)
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'total_users': total_users,
        'total_skins': total_skins,
        'total_transactions': total_transactions,
        'total_revenue': today_revenue
    }
    
    return render(request, 'admin/dashboard.html', context)

@user_passes_test(is_admin)
def user_management(request):
    search_query = request.GET.get('search', '')
    users = User.objects.filter(
        Q(username__icontains=search_query) |
        Q(email__icontains=search_query)
    ).order_by('-date_joined')
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    return render(request, 'admin/user_management.html', {
        'users': users,
        'search_query': search_query
    })

@user_passes_test(is_admin)
def adjust_balance(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        amount = Decimal(request.POST.get('amount', 0))
        reason = request.POST.get('reason', '')
        
        profile = target_user.profile
        profile.wallet_balance += amount
        profile.save()
        
        # Record transaction
        Transaction.objects.create(
            user=target_user,
            description=f"Balance adjusted by admin: {reason}",
            amount=amount,
            date=timezone.now()
        )
        
        # Record admin operation
        AdminLog.objects.create(
            admin_user=request.user,
            action="balance_adjustment",
            target_user=target_user,
            details=f"Adjusted balance by {amount}. Reason: {reason}"
        )
        
        messages.success(request, f"Successfully adjusted balance for {target_user.username}")
        return redirect('user_management')
    
    return render(request, 'admin/adjust_balance.html', {
        'target_user': get_object_or_404(User, id=user_id)
    })

@user_passes_test(is_admin)
def skin_management(request):
    skins = Skin.objects.all().order_by('-id')
    return render(request, 'admin/skin_management.html', {'skins': skins})

@user_passes_test(is_admin)
def add_edit_skin(request, skin_id=None):
    skin = None if skin_id is None else get_object_or_404(Skin, id=skin_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if skin is None:
            skin = Skin.objects.create(
                name=name,
                price=price,
                description=description,
                category=category,
                is_active=is_active
            )
        else:
            skin.name = name
            skin.price = price
            skin.description = description
            skin.category = category
            skin.is_active = is_active
            
        if image:
            skin.image = image
        skin.save()
        
        AdminLog.objects.create(
            admin_user=request.user,
            action="skin_modified",
            details=f"{'Created' if skin_id is None else 'Updated'} skin: {name}"
        )
        
        return redirect('skin_management')
    
    return render(request, 'admin/add_edit_skin.html', {'skin': skin})

@user_passes_test(is_admin)
def delete_skin(request, skin_id):
    skin = get_object_or_404(Skin, id=skin_id)
    skin.delete()
    
    AdminLog.objects.create(
        admin_user=request.user,
        action="skin_deleted",
        details=f"Deleted skin: {skin.name}"
    )
    
    return redirect('skin_management')

@user_passes_test(is_admin)
def export_skins(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="skins.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Price', 'Description', 'Is Active'])
    
    skins = Skin.objects.all()
    for skin in skins:
        writer.writerow([
            skin.name,
            skin.category,
            skin.price,
            skin.description,
            skin.is_active
        ])
    
    return response

@user_passes_test(is_admin)
def import_skins(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        
        for row in reader:
            Skin.objects.create(
                name=row['Name'],
                category=row['Category'],
                price=row['Price'],
                description=row['Description'],
                is_active=row['Is Active'].lower() == 'true'
            )
        
        messages.success(request, "Successfully imported skins")
        return redirect('skin_management')
    
    return render(request, 'admin/import_skins.html')

@user_passes_test(is_admin)
def transaction_history(request):
    transactions = Transaction.objects.all().order_by('-date')
    paginator = Paginator(transactions, 50)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    return render(request, 'admin/transaction_history.html', {
        'transactions': transactions
    })

@user_passes_test(is_admin)
def user_activity_logs(request):
    logs = UserActivityLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    return render(request, 'admin/user_activity_logs.html', {
        'logs': logs
    })

@user_passes_test(is_admin)
def admin_logs(request):
    logs = AdminLog.objects.all().order_by('-timestamp')
    paginator = Paginator(logs, 50)
    page = request.GET.get('page')
    logs = paginator.get_page(page)
    
    return render(request, 'admin/admin_logs.html', {
        'logs': logs
    })

