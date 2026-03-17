from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just log them in
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. twitter accounts
        if not sociallogin.email_addresses:
            # Let allauth handle it, it might still create an account without email
            return

        # Find the first email address in the providers response
        email = sociallogin.email_addresses[0].email
        
        try:
            # Check if user already exists
            user = User.objects.get(email__iexact=email)
            
            # If it exists, connect the social account to the user and login
            sociallogin.connect(request, user)
            
        except User.DoesNotExist:
            pass
