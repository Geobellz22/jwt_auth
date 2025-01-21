from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Referral, ReferralReward
from .serializers import ReferralSerializer, ReferralRewardSerializer

User = get_user_model()

@api_view(['POST'])
def create_referral(request):
    """
    Create a new referral entry.
    """
    referrer_id = request.data.get('referrer_id')
    referred_id = request.data.get('referred_id')
    
    if not referrer_id or not referred_id:
        return Response(
            {'error': 'Both referrer and referred IDs are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        referrer = User.objects.get(id=referrer_id)
        referred = User.objects.get(id=referred_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'Referrer or referred user does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if Referral.objects.filter(referrer=referrer, referred=referred).exists():
        return Response(
            {'error': 'Referral already exists'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create referral and rewards
    referral = Referral.objects.create(referrer=referrer, referred=referred)
    rewards = [
        ReferralReward(referral=referral, level=level, reward_percentage=percentage)
        for level, percentage in enumerate([4, 6, 8, 10], start=1)
    ]
    ReferralReward.objects.bulk_create(rewards)
    referral_serializer = ReferralSerializer(referral)

    return Response(
        {
            'message': 'Referral created successfully',
            'referral': referral_serializer.data,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
def get_referral_rewards(request, user_id):
    """
    Retrieve referral rewards for a given user.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User does not exist'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    referrals = Referral.objects.filter(referrer=user)
    rewards = ReferralReward.objects.filter(referral__in=referrals)
    reward_serializer = ReferralRewardSerializer(rewards, many=True)

    return Response(reward_serializer.data, status=status.HTTP_200_OK)
