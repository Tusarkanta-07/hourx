from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up Django Site and social authentication application credentials'

    def add_arguments(self, parser):
        parser.add_argument('provider', type=str, choices=['google', 'github', 'discord', 'linkedin'], help='Social provider name')
        parser.add_argument('client_id', type=str, help='OAuth Client ID / Client ID')
        parser.add_argument('secret_key', type=str, help='OAuth Secret Key / Client Secret')

    def handle(self, *args, **kwargs):
        provider = kwargs['provider']
        client_id = kwargs['client_id']
        secret_key = kwargs['secret_key']

        # Map 'linkedin' provider parameter to allauth's internal provider ID
        provider_id = 'linkedin_oauth2' if provider == 'linkedin' else provider
        provider_display_name = provider.capitalize()

        self.stdout.write("Configuring Django Site...")
        site, created = Site.objects.get_or_create(id=1)
        domain = 'testpythontusar.pythonanywhere.com'
        site.domain = domain
        site.name = domain
        site.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Site: {domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Updated Site: {domain}'))

        self.stdout.write(f"Configuring {provider_display_name} Social Application...")
        app, created = SocialApp.objects.get_or_create(provider=provider_id, defaults={
            'name': provider_display_name,
            'client_id': client_id,
            'secret': secret_key,
        })

        if not created:
            app.client_id = client_id
            app.secret = secret_key
            app.save()
            self.stdout.write(self.style.SUCCESS(f'Updated existing {provider_display_name} SocialApp credentials.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created new {provider_display_name} SocialApp.'))

        app.sites.add(site)
        self.stdout.write(self.style.SUCCESS(f'Successfully linked {provider_display_name} SocialApp to Site ({domain}).'))
        self.stdout.write(self.style.SUCCESS(f'\nAll set! Social authentication for {provider_display_name} is configured.'))
