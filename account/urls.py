from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register_user, confirm_email, CustomTokenObtainPairView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('confirm-email/', confirm_email, name='confirm_email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
