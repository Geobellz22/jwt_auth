from django.urls import path
from .views import create_referral, get_referral_rewards

urlpatterns = [
    path('referral/', create_referral, name='create-referral'),  # View to create a referral
    path('referral/reward/<int:user_id>/', get_referral_rewards, name='get-referral-rewards'),  # View to get referral rewards by user ID
]
