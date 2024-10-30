from django.urls import path
from .views import ReferralLinkView, RegistrationWithReferralView

urlpatterns = [
    path('referral-link/', ReferralLinkView.as_view(), name='referral_detail'),
    path('register-with-referral/', RegistrationWithReferralView.as_view(), name='register_with_referral'),
]
