import random
import string
from django.conf import settings

def generate_unique_referral_code(user):
    """
    Generates a unique referral code by combining the username with random letters and numbers.
    """
    from .models import ReferralLink  # avoid circular imports

    while True:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        referral_code = f"{user.username.upper()}_{random_part}"

        if not ReferralLink.objects.filter(referral_code=referral_code).exists():
            return referral_code

def create_referral_link_for_user(user):
    """
    Creates a ReferralLink instance for the given user.
    """
    referral_code = generate_unique_referral_code(user)

    base_url = getattr(
        settings,
        'BACKEND_BASE_URL',
        'http://localhost:8000'  # default fallback to backend localhost
    )

    referral_link = f"{base_url}/referral/{referral_code}"

    from .models import ReferralLink  # avoid circular imports
    ReferralLink.objects.create(
        referred_user=user,
        referral_code=referral_code,
        referral_link=referral_link
    )
