from django.conf import settings

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors 
import googleapiclient.http 

from abc import ABC, abstractmethod
import os
import pickle


class BasePlatformService(ABC):
    @abstractmethod
    def upload_video(self, video_post, platform):
        pass

class YouTubeService(BasePlatformService):
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/youtube.upload']
        self.api_service_name = 'youtube'
        self.api_version = 'v3'
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.redirect_uri = settings.YOUTUBE_REDIRECT_URI
        self.credentials = {}

    def get_authenticated_service(self, user_id):
        credentials_file = f'youtube_credentials_{user_id}.pickle'
        
        # Try loading existing credentials
        if os.path.exists(credentials_file):
            try:
                with open(credentials_file, 'rb') as token:
                    self.credentials[user_id] = pickle.load(token)
            except Exception as e:
                print(f"Error loading credentials for user {user_id}: {str(e)}")
                os.remove(credentials_file)

        # If no valid credentials, run OAuth flow
        if user_id not in self.credentials or not self.credentials[user_id].valid:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(
                {
                    'installed': {
                        'client_id': self.client_id,
                        'client_secret': self.client_secret,
                        'redirect_uris': [self.redirect_uri],
                        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                        'token_uri': 'https://oauth2.googleapis.com/token'
                    }
                },
                self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            try:
                self.credentials[user_id] = flow.run_local_server(
                    port=8192,
                    open_browser=True,
                    redirect_uri_mismatch_message="Mismatch in redirect URI. Please ensure http://localhost:8192/oauth2callback is added to Google Cloud Console."
                )
                print(f"Successfully obtained credentials for user {user_id}")
            except Exception as e:
                print(f"OAuth flow failed for user {user_id}: {str(e)}")
                raise
            
            # Save credentials
            try:
                with open(credentials_file, 'wb') as token:
                    pickle.dump(self.credentials[user_id], token)
            except Exception as e:
                print(f"Error saving credentials for user {user_id}: {str(e)}")
        
        return googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=self.credentials[user_id])

    def upload_video(self, video_post, platform):
        try:
            user_id = video_post.created_by.id
            youtube = self.get_authenticated_service(user_id)
            
            request_body = {
                'snippet': {
                    'title': video_post.title,
                    'description': video_post.description,
                    'tags': ['video', 'upload'],
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'private'
                }
            }
            
            if not video_post.video_file:
                raise Exception("Video file is required for YouTube upload")
            
            media = googleapiclient.http.MediaFileUpload(
                video_post.video_file.path,
                chunksize=-1,
                resumable=True
            )
            
            videos_insert_request = youtube.videos().insert(
                part='snippet,status',
                body=request_body,
                media_body=media
            )
            
            response = videos_insert_request.execute()
            
            return {
                'success': True,
                'external_id': response.get('id', f'youtube_video_{video_post.id}'),
                'message': 'Successfully uploaded to YouTube'
            }
        
        except googleapiclient.errors.HttpError as e:
            print(f"YouTube API error: {str(e)}")
            return {
                'success': False,
                'error': f"YouTube API error: {str(e)}"
            }
        except Exception as e:
            print(f"General error in upload_video: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }



class VimeoService(BasePlatformService):
    def upload_video(self, video_post, platform):
        try:
            # Simulated Vimeo upload
            headers = {
                'Authorization': f'Bearer {settings.VIMEO_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            # In real implementation I will use Vimeo API
            print(f"Uploading {video_post.title} to Vimeo...")
            
            return {
                'success': True,
                'external_id': f'vimeo_video_{video_post.id}',
                'message': 'Successfully uploaded to Vimeo'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class DailymotionService(BasePlatformService):
    def upload_video(self, video_post, platform):
        try:
            # Simulated Dailymotion upload
            print(f"Uploading {video_post.title} to Dailymotion...")
            
            return {
                'success': True,
                'external_id': f'dailymotion_video_{video_post.id}',
                'message': 'Successfully uploaded to Dailymotion'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Interface for platform services
class PlatformServiceFactory:
    services = {
        'youtube': YouTubeService(),
        'vimeo': VimeoService(),
        'dailymotion': DailymotionService(),
    }
    
    @classmethod
    def get_service(cls, platform_name):
        return cls.services.get(platform_name.lower())