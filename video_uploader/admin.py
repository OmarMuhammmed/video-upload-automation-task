from django.contrib import admin
from django.utils.html import format_html
from .models import VideoPost, Platform, UploadStatus


class PlatformAdmin(admin.ModelAdmin):
    list_display = ['platform', 'is_active', 'api_endpoint']
    list_filter = ['is_active']

admin.site.register(UploadStatus)
class UploadStatusInline(admin.TabularInline):
    model = UploadStatus
    extra = 0
    readonly_fields = ['status', 'external_id', 'uploaded_at', 'error_message']


class VideoPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'status_display', 'platform_list']
    list_filter = ['created_at', 'platforms', 'upload_statuses__status']
    search_fields = ['title', 'description']
    inlines = [UploadStatusInline]
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
        # Trigger upload process only if platforms exist
        if obj.platforms.exists():
            from .services.upload_manager import VideoUploadManager
            VideoUploadManager.upload_to_platforms(obj)
    
    def status_display(self, obj):
        status = obj.overall_status
        colors = {
            'pending': 'orange',
            'uploading': 'blue',
            'success': 'green',
            'failed': 'red',
            'partial': 'yellow'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(status, 'black'),
            status.title()
        )
    status_display.short_description = 'Upload Status'
    
    def platform_list(self, obj):
        return ", ".join([p.platform for p in obj.platforms.all()])
    platform_list.short_description = 'Platforms'


admin.site.register(Platform, PlatformAdmin)
admin.site.register(VideoPost, VideoPostAdmin)
