"""
Configuration module for Executive Dashboard V4.0

This module handles all environment-based configuration using pydantic-settings.
Supports multiple environments (dev/prod) with easy toggling between placeholder
and real data services.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Environment variables take precedence over defaults.
    Create a .env file in the project root for local development.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_name: str = "Executive Dashboard V4.0"
    app_version: str = "4.0.0"
    debug: bool = False
    
    # Environment (dev/staging/prod)
    environment: Literal["dev", "staging", "prod"] = "dev"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security - JWT
    # NOTE: secret_key must be set via environment variable for production
    secret_key: str = ""  # Must be set in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 10080  # 7 days
    
    # Data Service Selection
    # Set to "real" to switch from placeholder to real external API
    data_service: Literal["placeholder", "real"] = "placeholder"
    
    # Real Data Service Configuration (when data_service="real")
    real_api_base_url: str = "http://localhost:9000"
    # NOTE: real_api_key must be set via environment variable for production
    real_api_key: str = ""  # Must be set in production
    
    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"])
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60


    def model_post_init(self, __context):
        """Validate settings after initialization."""
        import secrets
        
        # Validate secret_key is set for production
        if self.environment == "prod" and not self.secret_key:
            raise ValueError("secret_key must be set in production environment (set SECRET_KEY env var)")
        if not self.secret_key:
            self.secret_key = secrets.token_urlsafe(32)
            print("WARNING: Using generated secret_key. Set SECRET_KEY env var for production!")
        
        # Validate real_api_key is set when using real data service
        if self.data_service == "real" and not self.real_api_key:
            raise ValueError("real_api_key must be set when data_service='real' (set REAL_API_KEY env var)")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.
    
    This function is called once per application lifetime,
    ensuring environment variables are loaded only once.
    """
    return Settings()
