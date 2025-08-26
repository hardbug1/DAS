"""
애플리케이션 통합 테스트

메인 애플리케이션의 기본 기능들을 테스트합니다.
"""

import pytest
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import settings
from app.config.database import test_database_connection
from app.ui.components import create_demo_response


class TestAppConfiguration:
    """애플리케이션 설정 테스트"""
    
    def test_settings_loading(self):
        """설정 로딩 테스트"""
        assert settings.app_name is not None
        assert settings.app_version is not None
        assert settings.gradio_server_port > 0
        assert settings.gradio_server_port < 65536
    
    def test_debug_mode(self):
        """디버그 모드 테스트"""
        # 개발 환경에서는 디버그 모드가 활성화되어야 함
        assert isinstance(settings.debug, bool)
    
    def test_database_url_format(self):
        """데이터베이스 URL 형식 테스트"""
        db_url = settings.database_url
        assert db_url.startswith(('postgresql://', 'sqlite:///', 'mysql://'))


class TestUIComponents:
    """UI 컴포넌트 테스트"""
    
    def test_demo_response_function(self):
        """데모 응답 함수 테스트"""
        message = "테스트 메시지"
        history = []
        
        new_history, cleared_msg = create_demo_response(message, history)
        
        # 응답이 추가되었는지 확인
        assert len(new_history) == 1
        assert new_history[0][0] == message  # 사용자 메시지
        assert isinstance(new_history[0][1], str)  # AI 응답
        assert len(new_history[0][1]) > 0  # 응답이 비어있지 않음
        
        # 입력창이 비워졌는지 확인
        assert cleared_msg == ""
    
    def test_demo_response_empty_message(self):
        """빈 메시지에 대한 응답 테스트"""
        message = ""
        history = []
        
        new_history, cleared_msg = create_demo_response(message, history)
        
        # 빈 메시지는 처리되지 않아야 함
        assert len(new_history) == 0
        assert cleared_msg == ""
    
    def test_demo_response_with_existing_history(self):
        """기존 히스토리가 있는 경우 테스트"""
        message = "새 메시지"
        existing_history = [("이전 메시지", "이전 응답")]
        
        new_history, cleared_msg = create_demo_response(message, existing_history)
        
        # 기존 히스토리 + 새 메시지
        assert len(new_history) == 2
        assert new_history[0] == ("이전 메시지", "이전 응답")
        assert new_history[1][0] == "새 메시지"


class TestDatabaseConnection:
    """데이터베이스 연결 테스트"""
    
    def test_database_connection_function(self):
        """데이터베이스 연결 함수 테스트"""
        try:
            result = test_database_connection()
            assert isinstance(result, bool)
        except Exception as e:
            # 연결 실패해도 예외가 발생하지 않아야 함
            pytest.fail(f"데이터베이스 연결 테스트에서 예외 발생: {e}")


class TestApplicationStructure:
    """애플리케이션 구조 테스트"""
    
    def test_required_directories_exist(self):
        """필수 디렉토리 존재 확인"""
        required_dirs = [
            "app",
            "app/config",
            "app/core", 
            "app/services",
            "app/models",
            "app/utils",
            "app/ui",
            "tests",
            "scripts"
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            assert dir_path.exists(), f"필수 디렉토리가 없습니다: {dir_name}"
            assert dir_path.is_dir(), f"{dir_name}이 디렉토리가 아닙니다"
    
    def test_required_files_exist(self):
        """필수 파일 존재 확인"""
        required_files = [
            "app/__init__.py",
            "app/main.py",
            "app/config/settings.py",
            "app/config/database.py",
            "requirements.txt",
            "README.md",
            "docker-compose.yml",
            "Dockerfile"
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            assert file_path.exists(), f"필수 파일이 없습니다: {file_name}"
            assert file_path.is_file(), f"{file_name}이 파일이 아닙니다"
    
    def test_python_modules_importable(self):
        """Python 모듈 import 테스트"""
        try:
            from app.config import settings
            from app.config import database
            from app.ui import components
            from app.utils import database_utils
        except ImportError as e:
            pytest.fail(f"모듈 import 실패: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
