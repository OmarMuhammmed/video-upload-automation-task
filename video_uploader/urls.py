from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'video-posts', views.VideoPostViewSet, basename='videopost')
router.register(r'platforms', views.PlatformViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]