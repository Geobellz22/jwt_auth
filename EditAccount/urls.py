from django.urls import path
from .views import EditAccountView

urlpatterns = [
    path('edit-account', EditAccountView.as_view(), name='edit-account')
]
