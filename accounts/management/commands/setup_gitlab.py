from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Sets up the Django Site and GitLab SocialApp automatically'

    def add_arguments(self, parser):
        parser.add_argument('client_id', type=str, help='Your GitLab Application Client ID')
        parser.add_argument('secret_key', type=str, help='Your GitLab Application Secret Key')

    def handle(self, *args, **kwargs):
        client_id = kwargs['client_id']
        secret_key = kwargs['secret_key']

        self.stdout.write("Configuring Django Site...")
        site, created = Site.objects.get_or_create(id=1)
        # testpythontusar.pythonanywhere.com is the prod URL, in dev it might be 127.0.0.1:8000
        # Check if we are running on PythonAnywhere by checking for an env variable or directory
        # but the prompt says they want this for the production site specifically.
        domain = 'testpythontusar.pythonanywhere.com' 
        # Optionally support localhost overrides? 
        # Let's just set it to the requested pythonanywhere domain.
        site.domain = domain
        site.name = domain
        site.save()
        
        if created:
             self.stdout.write(self.style.SUCCESS(f'Created Site: {domain}'))
        else:
             self.stdout.write(self.style.SUCCESS(f'Updated Site: {domain}'))

        self.stdout.write("Configuring GitLab Social Application...")
        app, created = SocialApp.objects.get_or_create(provider='gitlab', defaults={
            'name': 'GitLab',
            'client_id': client_id,
            'secret': secret_key,
        })
        
        if not created:
            app.client_id = client_id
            app.secret = secret_key
            app.save()
            self.stdout.write(self.style.SUCCESS('Updated existing GitLab SocialApp credentials.'))
        else:
            self.stdout.write(self.style.SUCCESS('Created new GitLab SocialApp.'))

        # This is the CRITICAL step that fixes the DoesNotExist error.
        app.sites.add(site)
        self.stdout.write(self.style.SUCCESS(f'Successfully linked GitLab SocialApp to Site ({domain}).'))
        
        self.stdout.write(self.style.SUCCESS('\nAll set! The "Log in with GitLab" button should now work perfectly in production.'))
