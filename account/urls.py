from django.urls import path
from .views import RegisterView,  LoginView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    #path('confirm-email/', ConfirmMailView.as_view(), name='confirm_email'),
    #path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
]