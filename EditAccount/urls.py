from django.urls import path
from .views import EditAccountView, UserRegisteredDetailsView

urlpatterns = [
    path('edit-account', EditAccountView.as_view(), name='edit-account'),
    path('user-registered-details', UserRegisteredDetailsView.as_view(), name='user-registered-details')
]
