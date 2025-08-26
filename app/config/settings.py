"""
애플리케이션 설정 관리

환경 변수를 통해 설정을 로드하고 관리합니다.
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 애플리케이션 설정
    app_name: str = Field(default="AI 데이터 분석 비서", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # OpenAI API 설정
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # 데이터베이스 설정
    database_url: str = Field(..., env="DATABASE_URL")
    test_database_url: Optional[str] = Field(None, env="TEST_DATABASE_URL")
    
    # Redis 설정
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # 보안 설정
    jwt_secret: str = Field(..., env="JWT_SECRET")
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    # 파일 업로드 설정
    max_file_size: int = Field(default=104857600, env="MAX_FILE_SIZE")  # 100MB
    upload_dir: str = Field(default="./uploads", env="UPLOAD_DIR")
    allowed_extensions: List[str] = Field(
        default=["xlsx", "xls", "csv"], 
        env="ALLOWED_EXTENSIONS"
    )
    
    # 성능 설정
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")  # 1시간
    max_concurrent_queries: int = Field(default=50, env="MAX_CONCURRENT_QUERIES")
    query_timeout: int = Field(default=300, env="QUERY_TIMEOUT")  # 5분
    
    # Gradio 설정
    gradio_server_name: str = Field(default="0.0.0.0", env="GRADIO_SERVER_NAME")
    gradio_server_port: int = Field(default=7860, env="GRADIO_SERVER_PORT")
    gradio_share: bool = Field(default=False, env="GRADIO_SHARE")
    
    # 접근성 및 UI 설정
    enable_accessibility_features: bool = Field(default=True, env="ENABLE_ACCESSIBILITY_FEATURES")
    default_theme: str = Field(default="light", env="DEFAULT_THEME")  # light, dark, blue, green
    enable_animations: bool = Field(default=True, env="ENABLE_ANIMATIONS")
    max_excel_file_size_mb: int = Field(default=100, env="MAX_EXCEL_FILE_SIZE_MB")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 전역 설정 인스턴스
settings = Settings()
