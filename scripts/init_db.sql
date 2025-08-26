-- AI 데이터 분석 비서 - 데이터베이스 초기화 스크립트

-- 데이터베이스 생성 (이미 존재하는 경우 무시)
-- CREATE DATABASE ai_analyst;

-- UUID 확장 활성화 (PostgreSQL)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 테스트 사용자 데이터 삽입 (개발용)
-- 실제 프로덕션에서는 제거해야 함

-- 샘플 사용자 생성
INSERT INTO users (user_id, username, email, preferences) VALUES
(uuid_generate_v4(), 'demo_user', 'demo@example.com', '{"theme": "light", "language": "ko"}')
ON CONFLICT (username) DO NOTHING;

-- 샘플 데이터베이스 연결 정보 (테스트용)
-- 실제 운영에서는 사용자가 직접 입력

-- 인덱스 최적화를 위한 추가 설정
-- ANALYZE 명령으로 통계 정보 업데이트
-- VACUUM ANALYZE;

-- 권한 설정 (필요시)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_user;
