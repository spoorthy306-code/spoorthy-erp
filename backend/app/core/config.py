# SPOORTHY QUANTUM OS — Configuration
# Application settings and configuration

import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/spoorthy_quantum"

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET: str = "jwt-secret-key"
    API_KEY: str = "api-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Quantum Computing
    DWAVE_API_TOKEN: str = ""
    QISKIT_API_TOKEN: str = ""

    # GSTN API
    GSTN_API_URL: str = "https://api.gstn.gov.in"
    GSTN_CLIENT_ID: str = ""
    GSTN_CLIENT_SECRET: str = ""

    # RBI FX Rates
    RBI_FX_API_URL: str = "https://www.rbi.org.in"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Cache
    REDIS_URL: str = "redis://localhost:6379"

    # Email
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""

    # AWS / S3 (optional)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "spoorthy-erp"
    AWS_REGION: str = "ap-south-1"

    # Quantum (optional)
    DWAVE_SOLVER: str = ""
    IBM_QUANTUM_TOKEN: str = ""
    QUANTUM_ENGINE_URL: str = ""

    # GST
    GSTN_API_KEY: str = ""

    # Payments
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""

    # Database pool
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Security extras
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12
    ENCRYPTION_KEY: str = ""

    # SMTP extras
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@spoorthy.com"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Redis
    REDIS_MAX_CONNECTIONS: int = 50

    model_config = {"env_file": ".env", "case_sensitive": True, "extra": "ignore"}

settings = Settings()