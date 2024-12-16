from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_user, confirm_email, TokenRefreshView

urlpatterns = [
    path('register_user')
]