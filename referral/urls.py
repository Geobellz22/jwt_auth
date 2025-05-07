from django.urls import path
from .views import ReferralSummaryView

urlpatterns = [
    path('summary/', ReferralSummaryView.as_view(), name='referral-summary'),
]
