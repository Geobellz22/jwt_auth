from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ContactUs
from django.core.mail import send_mail
from .serializers import ContactUsSerializer
from django.conf import settings

@api_view(['POST'])
def contact_us(request):
    serializer = ContactUsSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        subject = serializer.validated_data.get('subject')
        message = serializer.validated_data.get('message')
        from_email = serializer.validated_data.get('email')

        try:
            # Sending acknowledgment email to the user
            send_mail(
                'Contact Us',  
                'Thank you for contacting us. We will get back to you shortly.',  
                settings.EMAIL_HOST_USER,  
                [from_email], 
                fail_silently=False,
            )

            send_mail(
                subject,  
                message,  
                from_email,  
                [settings.SUPPORT_EMAIL],  
                fail_silently=False,
            )

        except Exception as e:
            return Response({'error': 'Something went wrong, please try again'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': 'Message sent successfully'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
