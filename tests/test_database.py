"""
데이터베이스 관련 테스트

데이터베이스 연결, 모델, 유틸리티 함수들을 테스트합니다.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.database import Base, test_database_connection
from app.models.database import User, Session as DBSession, QueryHistory
from app.utils.database_utils import (
    create_user_session, save_query_history, 
    create_cache_key, get_database_stats
)


@pytest.fixture
def test_db():
    """테스트용 인메모리 데이터베이스"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(test_db):
    """테스트용 사용자"""
    user = User(
        username="test_user",
        email="test@example.com",
        preferences={"theme": "light"}
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    return user


class TestDatabaseModels:
    """데이터베이스 모델 테스트"""
    
    def test_user_creation(self, test_db):
        """사용자 생성 테스트"""
        user = User(
            username="testuser",
            email="test@example.com",
            preferences={"language": "ko"}
        )
        
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        assert user.user_id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.preferences["language"] == "ko"
        assert user.created_at is not None
    
    def test_session_creation(self, test_db, test_user):
        """세션 생성 테스트"""
        session = DBSession(
            user_id=test_user.user_id,
            expires_at=datetime.utcnow() + timedelta(hours=24),
            context={"test": True}
        )
        
        test_db.add(session)
        test_db.commit()
        test_db.refresh(session)
        
        assert session.session_id is not None
        assert session.user_id == test_user.user_id
        assert session.is_active == True
        assert session.context["test"] == True
    
    def test_query_history_creation(self, test_db, test_user):
        """질의 히스토리 생성 테스트"""
        # 먼저 세션 생성
        session = create_user_session(test_db, test_user.user_id)
        
        # 질의 히스토리 생성
        history = save_query_history(
            test_db,
            session_id=str(session.session_id),
            user_query="테스트 질의",
            query_type="database",
            execution_time=1.5,
            is_successful=True
        )
        
        assert history.query_id is not None
        assert history.user_query == "테스트 질의"
        assert history.query_type == "database"
        assert history.execution_time == 1.5
        assert history.is_successful == True


class TestDatabaseUtils:
    """데이터베이스 유틸리티 테스트"""
    
    def test_create_cache_key(self):
        """캐시 키 생성 테스트"""
        query = "SELECT * FROM users"
        context = {"db": "test"}
        
        key1 = create_cache_key(query, context)
        key2 = create_cache_key(query, context)
        key3 = create_cache_key(query, {"db": "prod"})
        
        # 같은 입력에 대해 같은 키 생성
        assert key1 == key2
        # 다른 컨텍스트에 대해 다른 키 생성
        assert key1 != key3
        # 키는 64자리 16진수 문자열
        assert len(key1) == 64
        assert all(c in '0123456789abcdef' for c in key1)
    
    def test_database_stats(self, test_db, test_user):
        """데이터베이스 통계 테스트"""
        # 세션과 질의 히스토리 생성
        session = create_user_session(test_db, test_user.user_id)
        save_query_history(
            test_db,
            session_id=str(session.session_id),
            user_query="테스트 질의 1",
            query_type="database",
            is_successful=True
        )
        save_query_history(
            test_db,
            session_id=str(session.session_id),
            user_query="테스트 질의 2",
            query_type="file",
            is_successful=False
        )
        
        stats = get_database_stats(test_db)
        
        assert stats["total_users"] == 1
        assert stats["active_sessions"] == 1
        assert stats["total_queries"] == 2
        assert stats["successful_queries"] == 1
        assert stats["success_rate"] == 50.0


class TestDatabaseConnection:
    """데이터베이스 연결 테스트"""
    
    def test_database_connection(self):
        """데이터베이스 연결 테스트"""
        # 실제 데이터베이스 연결 테스트는 환경에 따라 달라질 수 있음
        # 여기서는 함수 호출만 테스트
        try:
            result = test_database_connection()
            # 연결 성공 또는 실패 모두 boolean 반환
            assert isinstance(result, bool)
        except Exception as e:
            # 연결 실패시에도 예외가 발생하지 않아야 함
            pytest.fail(f"데이터베이스 연결 테스트에서 예외 발생: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
