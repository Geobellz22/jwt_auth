from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import EditAccount
from .serializers import EditAccountSerializer, UserRegisteredDetailsSerializer

User = get_user_model()


class EditAccountView(generics.UpdateAPIView):
    serializer_class = EditAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Only get existing EditAccount instance; no creation here
        return EditAccount.objects.filter(user=self.request.user).first()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        user = request.user

        if not instance:
            return Response(
                {"error": "No editable account details found for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Track original values
        original_data = {
            field.name: getattr(instance, field.name)
            for field in instance._meta.fields
            if field.name in request.data
        }

        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')

        # Handle password change
        if new_password:
            if not current_password:
                return Response({"error": "Current password is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(current_password):
                return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validate_password(new_password)
                user.set_password(new_password)
                user.save()
            except ValidationError as e:
                return Response({"password_error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Clean incoming data for serializer
        mutable_data = request.data.copy()
        mutable_data.pop('new_password', None)
        mutable_data.pop('current_password', None)

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Compare for updated fields
        updated_fields = {}
        for field, original_value in original_data.items():
            new_value = getattr(instance, field)
            if new_value != original_value:
                updated_fields[field] = new_value

        if new_password:
            updated_fields["password"] = new_password

        # Send support email if updates occurred
        if updated_fields:
            subject = "User Edited Account Info"
            message = "A user has updated the following fields:\n\n"
            for key, value in updated_fields.items():
                message += f"{key}: {value}\n"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_EMAIL],
                fail_silently=True,
            )

        # Include refresh token if password was updated
        response_data = serializer.data
        if new_password:
            refresh = RefreshToken.for_user(user)
            response_data["refresh"] = str(refresh)
            response_data["access"] = str(refresh.access_token)

        return Response(response_data, status=status.HTTP_200_OK)


class UserRegisteredDetailsView(generics.RetrieveAPIView):
    serializer_class = UserRegisteredDetailsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()

        # Basic completeness check
        if not user.username or not user.email:
            return Response(
                {"error": "User has not completed registration details."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
