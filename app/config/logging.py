"""
로깅 설정 관리

구조화된 로깅 시스템을 설정합니다.
"""

import structlog
import logging
import sys
from pathlib import Path
from app.config.settings import settings


def setup_logging():
    """로깅 시스템 설정"""
    
    # 로그 레벨 설정
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # 로그 디렉토리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        ]
    )
    
    # structlog 설정
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # 개발 환경에서는 컬러 출력
    if settings.debug:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # 애플리케이션 시작 로그
    logger = structlog.get_logger()
    logger.info(
        "로깅 시스템 초기화 완료",
        app_name=settings.app_name,
        log_level=settings.log_level,
        debug_mode=settings.debug
    )
