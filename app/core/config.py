from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Config
    db_username: str
    db_password: str
    db_hostname: str
    db_port: str
    db_name: str

    # JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int = 7  

    LOCAL_URL: str = "http://localhost:8000"
    NGROK_URL: str = "https://your-ngrok-url.ngrok.io"  
    USE_NGROK: bool = False  
    SEARCH_API_URL: str = "https://9e24-103-221-254-42.ngrok-free.app"

    @property
    def BASE_URL(self) -> str:
        return self.NGROK_URL if self.USE_NGROK else self.LOCAL_URL

    # Cloudinary Config
    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    # Supabase Config
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str

    class Config:
        env_file = ".env"


settings = Settings()