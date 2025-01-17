from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status, serializers
import random
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from account.models import User 
from account.serializers import UserSerializer, MyTokenObtainPairSerializer
import uuid
@swagger_auto_schema(method='POST', request_body=UserSerializer)
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def register_user(request):
    data = request.data
    user_serializer = UserSerializer(data=data)
    if user_serializer.is_valid(raise_exception=True):
        user = user_serializer.save()
        
        confirmation_code  = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        
        # user.confirmation_code = '9525'
        user.confirmation_code = confirmation_code 
        user.save()
        
        email_subject = 'Email Confirmation'
        email_message = f"""
Good Morning {user.name},

Thank you for Registering with us.

Your Confirmation Code is {confirmation_code }.
"""
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
        return Response({
            'message': 'Confirmation code sent successfully',
            'user': user_serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer   
@api_view(['POST'])
def confirm_email(request):
    confirmation_code = request.data.get('confirmation_code')

    if not confirmation_code:
        return JsonResponse({'message': 'Confirmation code is missing from the request.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(confirmation_code=confirmation_code, is_active=False)
        user.is_active = True
        user.confirmation_code = ""
        user.save()
        return JsonResponse({'message': 'Email confirmation successful.'})
    except User.DoesNotExist:
        return JsonResponse({'message': 'Invalid confirmation code.'}, status=status.HTTP_400_BAD_REQUEST)
