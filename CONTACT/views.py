from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactUs
from .serializers import ContactUsSerializer

class ContactUsView(CreateAPIView):
    """
    API view to handle 'Contact Us' requests.
    """
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Save the contact form data
        contact = serializer.save()

        # Prepare email details
        subject = contact.subject
        message = contact.message
        from_email = contact.email

        try:
            # Sending acknowledgment email to the user
            send_mail(
                'Contact Us',  
                'Thank you for contacting us. We will get back to you shortly.',  
                settings.EMAIL_HOST_USER,  
                [from_email], 
                fail_silently=False,
            )

            # Forwarding the message to the support team
            send_mail(
                subject,  
                message,  
                from_email,  
                [settings.SUPPORT_EMAIL],  
                fail_silently=False,
            )

        except Exception as e:
            raise Exception("Email sending failed. Please try again later.")

        # Optionally, log or notify the admin
