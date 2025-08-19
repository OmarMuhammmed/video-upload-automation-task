from django.utils import timezone
from ..models import UploadStatus
from .platform_services import PlatformServiceFactory

class VideoUploadManager:
    @staticmethod
    def upload_to_platforms(video_post):
        """Upload video to all selected platforms"""
        results = []
        
        for platform in video_post.platforms.all():
            # Get or create upload status
            upload_status, created = UploadStatus.objects.get_or_create(
                video_post=video_post,
                platform=platform,
                defaults={'status': 'pending'}
            )
            
            # Update status to uploading
            upload_status.status = 'uploading'
            upload_status.save()
            
            # Get platform service
            service = PlatformServiceFactory.get_service(platform.platform)
            if not service:
                upload_status.status = 'failed'
                upload_status.error_message = f'No service available for {platform.paltform}'
                upload_status.save()
                continue
            
            # Attempt upload
            try:
                result = service.upload_video(video_post, platform)
                
                if result['success']:
                    upload_status.status = 'success'
                    upload_status.external_id = result.get('external_id', '')
                    upload_status.uploaded_at = timezone.now()
                else:
                    upload_status.status = 'failed'
                    upload_status.error_message = result.get('error', 'Unknown error')
                
                upload_status.save()
                results.append({
                    'platform': platform.platform,
                    'status': upload_status.status,
                    'message': result.get('message', result.get('error', ''))
                })
                
            except Exception as e:
                upload_status.status = 'failed'
                upload_status.error_message = str(e)
                upload_status.save()
                
                results.append({
                    'platform': platform.platform,
                    'status': 'failed',
                    'message': str(e)
                })
        
        return results