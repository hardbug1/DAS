#!/usr/bin/env python3
"""
데이터베이스 설정 스크립트

데이터베이스 테이블 생성 및 초기 데이터 설정을 수행합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.database import create_tables, test_database_connection, engine
from app.config.settings import settings
from app.models.database import User, Session, QueryHistory, UploadedFile, DatabaseConnection, CacheEntry
import structlog

logger = structlog.get_logger()


def setup_database():
    """데이터베이스 설정 메인 함수"""
    logger.info("데이터베이스 설정 시작")
    
    try:
        # 1. 데이터베이스 연결 테스트
        logger.info("데이터베이스 연결 테스트 중...")
        if not test_database_connection():
            logger.error("데이터베이스 연결 실패")
            return False
        
        # 2. 테이블 생성
        logger.info("데이터베이스 테이블 생성 중...")
        create_tables()
        
        # 3. 테이블 생성 확인
        with engine.connect() as conn:
            # 테이블 목록 조회
            if settings.database_url.startswith("postgresql"):
                result = conn.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
            else:
                # SQLite
                result = conn.execute("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type='table'
                """)
            
            tables = [row[0] for row in result]
            logger.info("생성된 테이블", tables=tables)
        
        logger.info("데이터베이스 설정 완료")
        return True
        
    except Exception as e:
        logger.error("데이터베이스 설정 실패", error=str(e))
        return False


def create_demo_data():
    """데모 데이터 생성 (개발용)"""
    from app.config.database import SessionLocal
    from datetime import datetime, timedelta
    import uuid
    
    logger.info("데모 데이터 생성 중...")
    
    session = SessionLocal()
    try:
        # 데모 사용자 생성
        demo_user = User(
            username="demo_user",
            email="demo@example.com",
            preferences={"theme": "light", "language": "ko"}
        )
        session.add(demo_user)
        session.commit()
        
        # 데모 세션 생성
        demo_session = Session(
            user_id=demo_user.user_id,
            expires_at=datetime.utcnow() + timedelta(days=1),
            context={"demo": True}
        )
        session.add(demo_session)
        session.commit()
        
        logger.info("데모 데이터 생성 완료", user_id=str(demo_user.user_id))
        
    except Exception as e:
        logger.error("데모 데이터 생성 실패", error=str(e))
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    # 로깅 설정
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    print("🗄️ AI 데이터 분석 비서 - 데이터베이스 설정")
    print("=" * 50)
    
    # 데이터베이스 설정 실행
    success = setup_database()
    
    if success:
        print("✅ 데이터베이스 설정 성공!")
        
        # 데모 데이터 생성 여부 확인
        create_demo = input("\n데모 데이터를 생성하시겠습니까? (y/N): ").lower().strip()
        if create_demo in ['y', 'yes']:
            create_demo_data()
            print("✅ 데모 데이터 생성 완료!")
    else:
        print("❌ 데이터베이스 설정 실패!")
        sys.exit(1)
    
    print("\n🚀 이제 애플리케이션을 실행할 수 있습니다:")
    print("   python app/main.py")
