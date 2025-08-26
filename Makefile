# AI 데이터 분석 비서 - Makefile
# 개발 편의를 위한 명령어 모음

.PHONY: help install run test clean setup-db docker-build docker-run

# 기본 명령어
help:
	@echo "🤖 AI 데이터 분석 비서 - 개발 명령어"
	@echo "=================================="
	@echo "install     - 의존성 패키지 설치"
	@echo "run         - 애플리케이션 실행"
	@echo "test        - 테스트 실행"
	@echo "setup-db    - 데이터베이스 설정"
	@echo "clean       - 임시 파일 정리"
	@echo "docker-build - Docker 이미지 빌드"
	@echo "docker-run  - Docker로 실행"
	@echo "lint        - 코드 품질 검사"
	@echo "format      - 코드 포맷팅"

# 개발 환경 설정
install:
	@echo "📦 의존성 패키지 설치 중..."
	pip install -r requirements.txt

# 애플리케이션 실행
run:
	@echo "🚀 애플리케이션 실행 중..."
	python run.py

# 테스트 실행
test:
	@echo "🧪 테스트 실행 중..."
	python -m pytest tests/ -v --tb=short

# 데이터베이스 설정
setup-db:
	@echo "🗄️ 데이터베이스 설정 중..."
	python scripts/setup_db.py

# 임시 파일 정리
clean:
	@echo "🧹 임시 파일 정리 중..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf logs/*.log
	rm -rf uploads/*

# Docker 이미지 빌드
docker-build:
	@echo "🐳 Docker 이미지 빌드 중..."
	docker build -t ai-data-analyst .

# Docker로 실행
docker-run:
	@echo "🐳 Docker 컨테이너 실행 중..."
	docker-compose up -d

# 코드 품질 검사
lint:
	@echo "🔍 코드 품질 검사 중..."
	flake8 app/ --max-line-length=100 --ignore=E203,W503
	mypy app/ --ignore-missing-imports

# 코드 포맷팅
format:
	@echo "✨ 코드 포맷팅 중..."
	black app/ tests/ --line-length=100
	
# 개발 환경 전체 설정
dev-setup: install setup-db
	@echo "✅ 개발 환경 설정 완료!"
	@echo "   이제 'make run' 명령으로 애플리케이션을 실행하세요."

# 전체 테스트 및 검사
check: test lint
	@echo "✅ 모든 검사 완료!"
