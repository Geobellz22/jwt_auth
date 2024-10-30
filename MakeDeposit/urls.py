from django.urls import path
from .views import MakeDeposit, ConfirmDeposit

urlpatterns = [
    path('deposit/', MakeDeposit.as_view(), name='make-deposit'),
    path('confirm-deposit/', ConfirmDeposit.as_view(), name='confirm-deposit')
]
