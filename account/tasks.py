from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_verification_email_task(email, confirmation_code):
    """Send email verification."""
    subject = "Verify Your Email"
    
    message = f"""Hello,

Welcome to our platform! To complete your registration, please use this verification code:

🔹 {confirmation_code}

This code will expire in 10 minutes.

If you didn't create this account, please ignore this email.

Best regards,
Your Platform Team"""
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

@shared_task
def notify_support_of_new_registration(user_details):
    """Notify support team of a new registration."""
    support_email = "support@yourcompany.com"
    
    subject = "New User Registration Alert"
    message = f"""
A new user has registered.

📌 **User Details:**
- **Username:** {user_details['username']}
- **Email:** {user_details['email']}
- **Wallets:**
    - Bitcoin: {user_details['wallets'].get('Bitcoin', 'N/A')}
    - Tether USDT TRC20: {user_details['wallets'].get('Tether USDT TRC 20', 'N/A')}
    - Tron: {user_details['wallets'].get('Tron', 'N/A')}
    - USDT TRC20: {user_details['wallets'].get('USDT TRC20', 'N/A')}
    - Ethereum: {user_details['wallets'].get('Ethereum', 'N/A')}
    - BNB: {user_details['wallets'].get('BNB', 'N/A')}
    - Dogecoin: {user_details['wallets'].get('Dogecoin', 'N/A')}
    - USDT ERC20: {user_details['wallets'].get('USDT ERC20', 'N/A')}
    - Bitcoin Cash: {user_details['wallets'].get('Bitcoin Cash', 'N/A')}
    - Shiba: {user_details['wallets'].get('Shiba', 'N/A')}

Best regards,  
Your Platform Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[support_email],
        fail_silently=False,
    )
