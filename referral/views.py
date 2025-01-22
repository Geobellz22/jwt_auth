from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import get_user_model
from .models import Referral, ReferralReward
from .serializers import ReferralSerializer, ReferralRewardSerializer

User = get_user_model()

# Refactor the create_referral view as a class-based view
class CreateReferralView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can create referrals
    serializer_class = ReferralSerializer

    def post(self, request, *args, **kwargs):
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

        # Ensure the referrer is creating the referral for a valid referred user
        if referrer == referred:
            return Response(
                {'error': 'Referrer cannot refer themselves'}, 
                status=status.HTTP_400_BAD_REQUEST
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

        # Serialize the referral object for the response
        referral_serializer = self.get_serializer(referral)

        return Response(
            {
                'message': 'Referral created successfully',
                'referral': referral_serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

# Refactor the get_referral_rewards view as a class-based view
class GetReferralRewardsView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated to access their rewards
    serializer_class = ReferralRewardSerializer

    def get(self, request, user_id, *args, **kwargs):
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

        # Fetch the referrals made by the user
        referrals = Referral.objects.filter(referrer=user)
        
        # Fetch the rewards associated with those referrals
        rewards = ReferralReward.objects.filter(referral__in=referrals)
        
        # Serialize the rewards for the response
        reward_serializer = self.get_serializer(rewards, many=True)

        return Response(reward_serializer.data, status=status.HTTP_200_OK)
