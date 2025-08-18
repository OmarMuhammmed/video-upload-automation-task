from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    api_endpoint = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class VideoPost(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('uploading', 'Uploading'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial Success'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="Alternative to video file")
    platforms = models.ManyToManyField(Platform, through='UploadStatus')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def clean(self):
        super().clean()
        if not self.video_file and not self.video_url:
            raise ValidationError("You must provide either a video file or a video URL.")
    
    def __str__(self):
        return self.title
    
    @property
    def overall_status(self):
        statuses = self.upload_statuses.values_list('status', flat=True)
        if all(status == 'success' for status in statuses):
            return 'success'
        elif any(status == 'failed' for status in statuses):
            return 'partial' if any(status == 'success' for status in statuses) else 'failed'
        elif any(status == 'uploading' for status in statuses):
            return 'uploading'
        return 'pending'

class UploadStatus(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('uploading', 'Uploading'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    video_post = models.ForeignKey(VideoPost, on_delete=models.CASCADE, related_name='upload_statuses')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['video_post', 'platform']
    
    def __str__(self):
        return f"{self.video_post.title} - {self.platform.name} - {self.status}"