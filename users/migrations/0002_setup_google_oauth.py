from django.db import migrations
from django.conf import settings

def setup_google_oauth(apps, schema_editor):
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    Site = apps.get_model('sites', 'Site')
    
    # Check if credentials are set
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        print("\nSkipping Google OAuth setup: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not found in settings.")
        return

    # Get or create the default site
    site, _ = Site.objects.get_or_create(
        id=settings.SITE_ID,
        defaults={'domain': 'localhost:8000', 'name': 'localhost'}
    )

    # Create the SocialApp
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': settings.GOOGLE_CLIENT_ID,
            'secret': settings.GOOGLE_CLIENT_SECRET,
        }
    )
    
    if not created:
        app.client_id = settings.GOOGLE_CLIENT_ID
        app.secret = settings.GOOGLE_CLIENT_SECRET
        app.save()

    # Add site to the app
    app.sites.add(site)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('socialaccount', '0001_initial'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(setup_google_oauth),
    ]
