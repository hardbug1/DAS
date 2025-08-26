"""
데이터베이스 모델 정의

SQLAlchemy ORM 모델들을 정의합니다.
설계 문서의 ERD를 기반으로 구현되었습니다.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, 
    Text, JSON, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.config.database import Base


class User(Base):
    """사용자 테이블"""
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    preferences = Column(JSON, default=dict)
    
    # 관계 설정
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    database_connections = relationship("DatabaseConnection", back_populates="user", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )


class Session(Base):
    """세션 테이블"""
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    context = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    
    # 관계 설정
    user = relationship("User", back_populates="sessions")
    query_history = relationship("QueryHistory", back_populates="session", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_is_active', 'is_active'),
    )


class QueryHistory(Base):
    """질의 히스토리 테이블"""
    __tablename__ = "query_history"
    
    query_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'))
    user_query = Column(Text, nullable=False)
    query_type = Column(String(20), nullable=False)  # 'database', 'file', 'mixed'
    sql_generated = Column(JSON)
    result_data = Column(JSON)
    chart_config = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    execution_time = Column(Float)
    is_successful = Column(Boolean, nullable=False)
    
    # 관계 설정
    session = relationship("Session", back_populates="query_history")
    
    # 인덱스
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_executed_at', 'executed_at'),
        Index('idx_query_type', 'query_type'),
        Index('idx_is_successful', 'is_successful'),
    )


class UploadedFile(Base):
    """업로드된 파일 테이블"""
    __tablename__ = "uploaded_files"
    
    file_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('sessions.session_id', ondelete='CASCADE'))
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'xlsx', 'xls', 'csv'
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    metadata = Column(JSON, default=dict)
    
    # 관계 설정
    session = relationship("Session", back_populates="uploaded_files")
    
    # 인덱스
    __table_args__ = (
        Index('idx_session_id', 'session_id'),
        Index('idx_uploaded_at', 'uploaded_at'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_file_hash', 'file_hash'),
    )


class DatabaseConnection(Base):
    """데이터베이스 연결 정보 테이블"""
    __tablename__ = "database_connections"
    
    connection_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'))
    connection_name = Column(String(100), nullable=False)
    db_type = Column(String(20), nullable=False)  # 'postgresql', 'mysql', 'sqlite'
    host = Column(String(255))
    port = Column(Integer)
    database_name = Column(String(100))
    username = Column(String(100))
    encrypted_password = Column(Text)  # 암호화된 비밀번호
    schema_cache = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # 관계 설정
    user = relationship("User", back_populates="database_connections")
    
    # 인덱스
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_is_active', 'is_active'),
        Index('idx_last_used', 'last_used'),
    )


class CacheEntry(Base):
    """캐시 엔트리 테이블"""
    __tablename__ = "cache_entries"
    
    cache_key = Column(String(255), primary_key=True)
    query_hash = Column(String(64), nullable=False)
    cached_result = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)
    
    # 인덱스
    __table_args__ = (
        Index('idx_query_hash', 'query_hash'),
        Index('idx_expires_at', 'expires_at'),
        Index('idx_created_at', 'created_at'),
    )
