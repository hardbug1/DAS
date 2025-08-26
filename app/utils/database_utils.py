"""
데이터베이스 유틸리티 함수들

데이터베이스 관련 헬퍼 함수들을 제공합니다.
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.database import User, Session as DBSession, QueryHistory, CacheEntry
import structlog

logger = structlog.get_logger()


def create_user_session(
    db: Session, 
    user_id: str, 
    expires_hours: int = 24,
    context: Dict[str, Any] = None
) -> DBSession:
    """사용자 세션 생성"""
    session = DBSession(
        user_id=user_id,
        expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
        context=context or {}
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    logger.info("사용자 세션 생성", session_id=str(session.session_id))
    return session


def get_active_session(db: Session, session_id: str) -> Optional[DBSession]:
    """활성 세션 조회"""
    session = db.query(DBSession).filter(
        DBSession.session_id == session_id,
        DBSession.is_active == True,
        DBSession.expires_at > datetime.utcnow()
    ).first()
    
    return session


def save_query_history(
    db: Session,
    session_id: str,
    user_query: str,
    query_type: str,
    sql_generated: Dict[str, Any] = None,
    result_data: Dict[str, Any] = None,
    chart_config: Dict[str, Any] = None,
    execution_time: float = None,
    is_successful: bool = True
) -> QueryHistory:
    """질의 히스토리 저장"""
    
    query_history = QueryHistory(
        session_id=session_id,
        user_query=user_query,
        query_type=query_type,
        sql_generated=sql_generated,
        result_data=result_data,
        chart_config=chart_config,
        execution_time=execution_time,
        is_successful=is_successful
    )
    
    db.add(query_history)
    db.commit()
    db.refresh(query_history)
    
    logger.info(
        "질의 히스토리 저장",
        query_id=str(query_history.query_id),
        query_type=query_type,
        is_successful=is_successful
    )
    
    return query_history


def get_user_query_history(
    db: Session, 
    user_id: str, 
    limit: int = 50
) -> list[QueryHistory]:
    """사용자 질의 히스토리 조회"""
    
    history = db.query(QueryHistory).join(DBSession).filter(
        DBSession.user_id == user_id
    ).order_by(QueryHistory.executed_at.desc()).limit(limit).all()
    
    return history


def create_cache_key(query: str, context: Dict[str, Any] = None) -> str:
    """캐시 키 생성"""
    # 질의와 컨텍스트를 결합하여 해시 생성
    content = f"{query}:{str(context or {})}"
    return hashlib.sha256(content.encode()).hexdigest()


def get_cached_result(db: Session, cache_key: str) -> Optional[Dict[str, Any]]:
    """캐시된 결과 조회"""
    cache_entry = db.query(CacheEntry).filter(
        CacheEntry.cache_key == cache_key,
        CacheEntry.expires_at > datetime.utcnow()
    ).first()
    
    if cache_entry:
        # 히트 카운트 증가
        cache_entry.hit_count += 1
        db.commit()
        
        logger.info("캐시 히트", cache_key=cache_key, hit_count=cache_entry.hit_count)
        return cache_entry.cached_result
    
    return None


def save_cached_result(
    db: Session,
    cache_key: str,
    query_hash: str,
    result: Dict[str, Any],
    ttl_hours: int = 1
) -> CacheEntry:
    """결과 캐싱"""
    
    cache_entry = CacheEntry(
        cache_key=cache_key,
        query_hash=query_hash,
        cached_result=result,
        expires_at=datetime.utcnow() + timedelta(hours=ttl_hours)
    )
    
    db.add(cache_entry)
    db.commit()
    db.refresh(cache_entry)
    
    logger.info("결과 캐싱 완료", cache_key=cache_key)
    return cache_entry


def cleanup_expired_data(db: Session) -> Dict[str, int]:
    """만료된 데이터 정리"""
    now = datetime.utcnow()
    
    # 만료된 세션 비활성화
    expired_sessions = db.query(DBSession).filter(
        DBSession.expires_at < now,
        DBSession.is_active == True
    ).update({"is_active": False})
    
    # 만료된 캐시 엔트리 삭제
    expired_cache = db.query(CacheEntry).filter(
        CacheEntry.expires_at < now
    ).delete()
    
    db.commit()
    
    result = {
        "expired_sessions": expired_sessions,
        "expired_cache": expired_cache
    }
    
    logger.info("만료된 데이터 정리 완료", **result)
    return result


def get_database_stats(db: Session) -> Dict[str, Any]:
    """데이터베이스 통계 정보"""
    stats = {
        "total_users": db.query(User).count(),
        "active_sessions": db.query(DBSession).filter(
            DBSession.is_active == True,
            DBSession.expires_at > datetime.utcnow()
        ).count(),
        "total_queries": db.query(QueryHistory).count(),
        "successful_queries": db.query(QueryHistory).filter(
            QueryHistory.is_successful == True
        ).count(),
        "cache_entries": db.query(CacheEntry).filter(
            CacheEntry.expires_at > datetime.utcnow()
        ).count()
    }
    
    # 성공률 계산
    if stats["total_queries"] > 0:
        stats["success_rate"] = (stats["successful_queries"] / stats["total_queries"]) * 100
    else:
        stats["success_rate"] = 0
    
    return stats
