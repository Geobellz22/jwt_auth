from django.conf import settings

def create_referral_link_for_user(user):
    """
    Creates a referral link for the given user based on their username.
    No random code, just username.
    """
    base_url = getattr(
        settings,
        'BACKEND_BASE_URL',
        'http://localhost:8000'  # fallback
    )

    # This format matches the frontend expectation like /register/?ref=username
    referral_link = f"{base_url}/register/?ref={user.username}"
    return referral_link
