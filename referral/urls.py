from django.urls import path
from .views import CreateReferralView, GetReferralRewardsView

urlpatterns = [
    path('referral/', CreateReferralView.as_view(), name='create-referral'),  # View to create a referral
    path('referral/reward/<int:user_id>/', GetReferralRewardsView.as_view(), name='get-referral-rewards'),  # View to get referral rewards by user ID
]
