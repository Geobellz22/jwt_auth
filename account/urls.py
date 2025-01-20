from django.urls import path
from .views import register_user, confirm_email, CustomTokenObtainPairView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('confirm-email/', confirm_email, name='confirm_email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Ensure CustomTokenObtainPairView is correctly defined
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
