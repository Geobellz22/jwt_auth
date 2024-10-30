from django.urls import path
from .views import EditAccountView, ChangePasswordView

urlpatterns = [
    path('edit-account', EditAccountView.as_view(), name='edit-account'),
    path('change-password', ChangePasswordView.as_view(), name='change-password')
]
