from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Referral, ReferralReward
from .serializers import ReferralSerializer, ReferralRewardSerializer
from django.contrib.auth import get_user_model

User = get_user_model()  # Use the custom user model if it exists

# Create a referral
@api_view(['POST'])
def create_referral(request):
    referrer_id = request.data.get('referrer_id')
    referred_id = request.data.get('referred_id')
    
    if not referrer_id or not referred_id:
        return Response({'error': 'Both referrer and referred IDs are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        referrer = User.objects.get(id=referrer_id)
        referred = User.objects.get(id=referred_id)
    except User.DoesNotExist:
        return Response({'error': 'Referrer or referred user does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if Referral.objects.filter(referrer=referrer, referred=referred).exists():
        return Response({'error': 'Referral already exists'}, status=status.HTTP_400_BAD_REQUEST)

    referral = Referral.objects.create(referrer=referrer, referred=referred)
    referral_serializer = ReferralSerializer(referral)
    
    # Create referral rewards based on levels
    rewards = [
        ReferralReward(referral=referral, level=1, reward_percentage=4),
        ReferralReward(referral=referral, level=2, reward_percentage=6),
        ReferralReward(referral=referral, level=3, reward_percentage=8),
        ReferralReward(referral=referral, level=4, reward_percentage=10),
    ]
    ReferralReward.objects.bulk_create(rewards)  # Efficiently create multiple reward objects
    
    return Response({
        'message': 'Referral created successfully',
        'referral': referral_serializer.data,
    }, status=status.HTTP_201_CREATED)

# Get referral rewards for a specific user
@api_view(['GET'])
def get_referral_rewards(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get all referrals made by this user
    referrals = Referral.objects.filter(referrer=user)
    rewards = ReferralReward.objects.filter(referral__in=referrals)
    reward_serializer = ReferralRewardSerializer(rewards, many=True)
    
    return Response(reward_serializer.data, status=status.HTTP_200_OK)
