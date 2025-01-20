from django.urls import path
from .views import register_user, confirm_email, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView  # Correct import for TokenRefreshView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('confirm-email/', confirm_email, name='confirm_email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Custom TokenObtainPairView
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # TokenRefreshView import corrected
]
