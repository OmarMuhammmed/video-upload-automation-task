from rest_framework import serializers
from .models import VideoPost, Platform, UploadStatus


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'platform']


class UploadStatusSerializer(serializers.ModelSerializer):
    platform = PlatformSerializer(read_only=True)
    
    class Meta:
        model = UploadStatus
        fields = ['platform', 'status', 'external_id', 'uploaded_at', 'error_message']


class VideoPostSerializer(serializers.ModelSerializer):
    upload_statuses = UploadStatusSerializer(many=True, read_only=True)
    platform_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = VideoPost
        fields = [
            'id', 'title', 'description', 'video_file', 'video_url',
            'created_at', 'updated_at', 'upload_statuses', 'platform_ids'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        platform_ids = validated_data.pop('platform_ids', [])
        video_post = VideoPost.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        
        if platform_ids:
            platforms = Platform.objects.filter(id__in=platform_ids)
            video_post.platforms.set(platforms)
            
            # Trigger upload process
            from .services.upload_manager import VideoUploadManager
            VideoUploadManager.upload_to_platforms(video_post)
        
        return video_post