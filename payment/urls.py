from django.urls import path
from . import views

urlpatterns = [
    path("recharge/", views.recharge, name="recharge"),
]
