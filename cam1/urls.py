from django.urls import path
from .views import upload_frame, mjpeg_feed,camera_page

urlpatterns = [
    path('upload_frame/', upload_frame, name='upload_frame'),
    path('mjpeg_feed/', mjpeg_feed, name='mjpeg_feed'),
    path('camera/', camera_page, name='camera_page')
]
