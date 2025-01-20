from django.urls import path
from .views import RegisterUserView, ConfirmEmailView, CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('confirm-email/', ConfirmEmailView.as_view(), name='confirm_email'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
