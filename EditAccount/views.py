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
    queryset = EditAccount.objects.all()
    serializer_class = EditAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return EditAccount.objects.get(user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        account_instance = self.get_object()
        
        new_password = request.data.get('new_password')
        if new_password:
            try:
                validate_password(new_password)
                request.user.set_password(new_password)
                request.user.save()
            except ValidationError as e:
                return Response({"password_error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = self.get_serializer(account_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, staus=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        account_instance = self.get_object()
        serializer = self.get_serializer(account_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def update(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password:
            return Response({"error": "Current password Incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password)
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password updated Sucessfully."}, status = status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": "e.messages"}, status = status.HTTP_400_BAD_REQUEST)
            
            