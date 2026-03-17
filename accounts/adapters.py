from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for django-allauth.
    Explicitly disables the standard email/password registration route
    while allowing Social Accounts (like GitLab) to still register users.
    """
    def is_open_for_signup(self, request):
        # We return False to close standard local registration.
        # Social logins use SocialAccountAdapter.is_open_for_signup,
        # which returns True by default, allowing GitLab users through.
        return False
