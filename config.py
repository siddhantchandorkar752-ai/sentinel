import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_NUMBER: str = os.getenv("TWILIO_FROM_NUMBER", "")
    EMERGENCY_CONTACT_NUMBER: str = os.getenv("EMERGENCY_CONTACT_NUMBER", "")
    EAR_THRESHOLD: float = float(os.getenv("EAR_THRESHOLD", "0.25"))
    MAR_THRESHOLD: float = float(os.getenv("MAR_THRESHOLD", "0.6"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinel.db")
    
    class Config:
        env_file = ".env"

settings = Settings()
