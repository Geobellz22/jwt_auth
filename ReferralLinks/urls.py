from django.urls import path
from .views import ReferralLinkView
urlpatterns = [
    path('referral-link/', ReferralLinkView.as_view(), name='referral_detail')
]