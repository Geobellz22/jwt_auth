from django.urls import path
from .views import WithdrawView

urlpatterns = [
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
]
