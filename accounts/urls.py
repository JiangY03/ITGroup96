from django.urls import path,include
from . import views
from .views import recharge_wallet
from .views import account_view

urlpatterns = [
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("", views.home, name="home"),  
    path('account/', views.account_view, name='account'),
   
   
    path('recharge/', views.recharge_wallet, name='recharge_wallet'),  # Ensure path points to correct view
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/users/<int:user_id>/adjust-balance/', views.adjust_balance, name='adjust_balance'),
    path('admin/skins/', views.skin_management, name='skin_management'),
    path('admin/skins/add/', views.add_edit_skin, name='add_skin'),
    path('admin/skins/<int:skin_id>/edit/', views.add_edit_skin, name='edit_skin'),
    path('admin/skins/<int:skin_id>/delete/', views.delete_skin, name='delete_skin'),
    path('admin/skins/export/', views.export_skins, name='export_skins'),
    path('admin/skins/import/', views.import_skins, name='import_skins'),
    path('admin/transactions/', views.transaction_history, name='transaction_history'),
    path('admin/user-logs/', views.user_activity_logs, name='user_activity_logs'),
    path('admin/admin-logs/', views.admin_logs, name='admin_logs'),
]
     

