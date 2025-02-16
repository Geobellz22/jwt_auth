from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import EditAccount
from .serializers import EditAccountSerializer
from rest_framework.exceptions import ValidationError

class EditAccountView(generics.RetrieveUpdateAPIView):
    serializer_class = EditAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Get or create EditAccount for the current user
        account, created = EditAccount.objects.get_or_create(user=self.request.user)
        return account
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Always use partial updates
        instance = self.get_object()
        
        # Handle password separately from the serializer
        new_password = request.data.get('new_password')
        if new_password:
            try:
                validate_password(new_password)
                request.user.set_password(new_password)
                request.user.save()
                # Remove password from data that goes to serializer
                mutable_data = request.data.copy()
                mutable_data.pop('new_password')
                serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
            except ValidationError as e:
                return Response({"password_error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            
            # Generate new tokens if password was changed
            if new_password:
                refresh = RefreshToken.for_user(request.user)
                response_data = serializer.data
                response_data['refresh'] = str(refresh)
                response_data['access'] = str(refresh.access_token)
                return Response(response_data, status=status.HTTP_200_OK)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not current_password or not new_password:
            return Response(
                {"error": "Both current_password and new_password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password)
            user.set_password(new_password)
            user.save()
            
            # Generate new tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                "message": "Password updated successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)