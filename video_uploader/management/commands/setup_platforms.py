from django.core.management.base import BaseCommand
from video_uploader.models import Platform

class Command(BaseCommand):
    help = 'Setup initial platform data'
    
    def handle(self, *args, **options):
        platforms = [
            {'name': 'YouTube', 'api_endpoint': 'https://www.googleapis.com/youtube/v3/'},
            {'name': 'Vimeo', 'api_endpoint': 'https://api.vimeo.com/'},
            {'name': 'Dailymotion', 'api_endpoint': 'https://www.dailymotion.com/api/'},
            {'name': 'Twitch', 'api_endpoint': 'https://api.twitch.tv/helix/'},
            {'name': 'Weibo', 'api_endpoint': 'https://api.weibo.com/2/'},
        ]
        
        for platform_data in platforms:
            platform, created = Platform.objects.get_or_create(
                name=platform_data['name'],
                defaults=platform_data
            )
            if created:
                self.stdout.write(f"Created platform: {platform.name}")
            else:
                self.stdout.write(f"Platform already exists: {platform.name}")