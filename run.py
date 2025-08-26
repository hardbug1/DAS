#!/usr/bin/env python3
"""
AI 데이터 분석 비서 - 실행 스크립트

개발 환경에서 애플리케이션을 쉽게 실행할 수 있는 스크립트입니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경 변수 설정 (개발용)
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("LOG_LEVEL", "INFO")

# SQLite 기본 설정 (PostgreSQL이 없는 경우)
if not os.getenv("DATABASE_URL"):
    db_path = project_root / "data" / "ai_analyst.db"
    db_path.parent.mkdir(exist_ok=True)
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

# Redis 기본 설정
if not os.getenv("REDIS_URL"):
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"

# OpenAI API 키 확인
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다.")
    print("   Week 2에서 AI 기능을 사용하려면 설정이 필요합니다.")
    print("   현재는 데모 모드로 실행됩니다.\n")

if __name__ == "__main__":
    print("🚀 AI 데이터 분석 비서 시작...")
    print("=" * 50)
    
    try:
        from app.main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 애플리케이션을 종료합니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
