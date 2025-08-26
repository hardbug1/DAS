"""
데이터베이스 연결 및 설정 관리

SQLAlchemy를 사용한 데이터베이스 연결 설정을 관리합니다.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import structlog
from app.config.settings import settings

logger = structlog.get_logger()

# SQLAlchemy 기본 설정
Base = declarative_base()
metadata = MetaData()

# 데이터베이스 엔진 설정
def create_database_engine(database_url: str = None):
    """데이터베이스 엔진 생성"""
    url = database_url or settings.database_url
    
    # SQLite인 경우 특별 설정
    if url.startswith("sqlite"):
        engine = create_engine(
            url,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,
                "timeout": 20
            },
            echo=settings.debug
        )
    else:
        # PostgreSQL 등 다른 데이터베이스
        engine = create_engine(
            url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.debug
        )
    
    logger.info("데이터베이스 엔진 생성 완료", database_url=url.split('@')[0] + '@***')
    return engine

# 전역 엔진 및 세션 팩토리
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """데이터베이스 세션 생성"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error("데이터베이스 세션 오류", error=str(e))
        session.rollback()
        raise
    finally:
        session.close()

def create_tables():
    """데이터베이스 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error("테이블 생성 실패", error=str(e))
        raise

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            logger.info("데이터베이스 연결 테스트 성공")
            return True
    except Exception as e:
        logger.error("데이터베이스 연결 실패", error=str(e))
        return False
