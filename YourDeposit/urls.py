from django.urls import path
from . import views

urlpatterns = [
    path('', views.YourDeposit.as_view(), name='your-deposits'),
]
