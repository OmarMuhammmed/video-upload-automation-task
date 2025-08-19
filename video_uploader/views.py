from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import VideoPost, Platform
from .serializers import VideoPostSerializer, PlatformSerializer
from .services.upload_manager import VideoUploadManager
from rest_framework.permissions import IsAuthenticated


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Platform.objects.filter(is_active=True)
    serializer_class = PlatformSerializer
    permission_classes = [IsAuthenticated]


class VideoPostViewSet(viewsets.ModelViewSet):
    serializer_class = VideoPostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return VideoPost.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def retry_upload(self, request, pk=None):
        """Retry failed uploads for a specific video post"""
        video_post = self.get_object()
        
        # Reset failed uploads to pending
        video_post.upload_statuses.filter(status='failed').update(status='pending')
        
        # Trigger upload process
        results = VideoUploadManager.upload_to_platforms(video_post)
        
        return Response({
            'message': 'Upload retry initiated',
            'results': results
        })
    
    @action(detail=False, methods=['get'])
    def upload_stats(self, request):
        """Get upload statistics"""
        user_posts = self.get_queryset()
        
        stats = {
            'total_posts': user_posts.count(),
            'successful_uploads': user_posts.filter(upload_statuses__status='success').distinct().count(),
            'failed_uploads': user_posts.filter(upload_statuses__status='failed').distinct().count(),
            'pending_uploads': user_posts.filter(upload_statuses__status='pending').distinct().count(),
        }
        
        return Response(stats)