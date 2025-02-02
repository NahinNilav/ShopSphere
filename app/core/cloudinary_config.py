from cloudinary import config as cloudinary_config
from app.core.config import settings

def initialize_cloudinary():
    cloudinary_config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret
    )