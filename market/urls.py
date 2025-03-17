from django.urls import path
from . import views

urlpatterns = [
    path('market/', views.market, name='market'),
    path('buy_skin/<int:item_id>/', views.buy_skin, name='buy_skin'),
]

