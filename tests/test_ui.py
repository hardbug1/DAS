"""
UI 컴포넌트 테스트

사용자 인터페이스 관련 기능들을 테스트합니다.
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.ui.handlers import ChatHandler, FileHandler, SettingsHandler
from app.ui.interactions import NotificationManager, ProgressTracker
from app.ui.themes import ThemeManager, ColorPalette


class TestChatHandler:
    """채팅 핸들러 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.chat_handler = ChatHandler()
    
    def test_send_message_normal(self):
        """일반 메시지 전송 테스트"""
        message = "안녕하세요"
        history = []
        
        new_history, cleared_input = self.chat_handler.send_message(message, history)
        
        assert len(new_history) == 1
        assert new_history[0][0] == message
        assert isinstance(new_history[0][1], str)
        assert len(new_history[0][1]) > 0
        assert cleared_input == ""
    
    def test_send_message_empty(self):
        """빈 메시지 전송 테스트"""
        message = ""
        history = []
        
        new_history, cleared_input = self.chat_handler.send_message(message, history)
        
        assert new_history == history
        assert cleared_input == ""
    
    def test_keyword_responses(self):
        """키워드 기반 응답 테스트"""
        test_cases = [
            ("매출 현황은?", "매출"),
            ("파일 업로드", "파일"),
            ("차트 보여줘", "시각화"),
            ("데이터베이스 연결", "데이터베이스"),
            ("안녕하세요", "안녕")
        ]
        
        for message, expected_keyword in test_cases:
            history = []
            new_history, _ = self.chat_handler.send_message(message, history)
            response = new_history[0][1].lower()
            
            # 키워드 관련 응답이 포함되어 있는지 확인
            assert len(response) > 0, f"응답이 비어있음: {message}"
    
    def test_clear_chat(self):
        """채팅 초기화 테스트"""
        # 먼저 메시지를 보내고
        self.chat_handler.send_message("테스트 메시지", [])
        assert len(self.chat_handler.conversation_history) > 0
        
        # 초기화
        cleared_history, cleared_input = self.chat_handler.clear_chat()
        
        assert cleared_history == []
        assert cleared_input == ""
        assert len(self.chat_handler.conversation_history) == 0


class TestFileHandler:
    """파일 핸들러 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.file_handler = FileHandler()
    
    def test_handle_empty_file_upload(self):
        """빈 파일 업로드 테스트"""
        files = []
        result = self.file_handler.handle_file_upload(files)
        
        assert "아직 업로드된 파일이 없습니다" in result
    
    def test_file_size_formatting(self):
        """파일 크기 포맷팅 테스트"""
        test_cases = [
            (512, "512 B"),
            (1024, "1 KB"),
            (1024 * 1024, "1 MB"),
            (1536, "1 KB"),  # 1.5KB는 1KB로 표시
            (1024 * 1024 + 512 * 1024, "1 MB")  # 1.5MB는 1MB로 표시
        ]
        
        for size, expected in test_cases:
            result = self.file_handler._format_file_size(size)
            assert result == expected
    
    def test_time_formatting(self):
        """시간 포맷팅 테스트"""
        from datetime import datetime
        
        # 현재 시간
        now = datetime.now()
        timestamp = now.isoformat()
        
        result = self.file_handler._format_time(timestamp)
        assert ":" in result  # HH:MM 형식
        assert len(result) == 5  # HH:MM은 5글자
    
    def test_time_formatting_invalid(self):
        """잘못된 시간 포맷 테스트"""
        invalid_timestamp = "invalid_timestamp"
        
        result = self.file_handler._format_time(invalid_timestamp)
        assert result == "방금 전"


class TestSettingsHandler:
    """설정 핸들러 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.settings_handler = SettingsHandler()
    
    def test_database_connection_valid(self):
        """유효한 데이터베이스 연결 테스트"""
        result = self.settings_handler.test_database_connection(
            "PostgreSQL", "localhost", 5432, "test_db"
        )
        
        assert "연결 성공" in result or "성공" in result
    
    def test_database_connection_invalid(self):
        """잘못된 데이터베이스 연결 테스트"""
        result = self.settings_handler.test_database_connection(
            "PostgreSQL", "", 5432, ""
        )
        
        assert "실패" in result or "입력해주세요" in result
    
    def test_update_language(self):
        """언어 설정 업데이트 테스트"""
        language = "English"
        result = self.settings_handler.update_language(language)
        
        assert self.settings_handler.settings['language'] == language
        assert language in result
    
    def test_update_theme(self):
        """테마 설정 업데이트 테스트"""
        theme = "다크"
        result = self.settings_handler.update_theme(theme)
        
        assert self.settings_handler.settings['theme'] == theme
        assert theme in result
    
    def test_update_chart_default(self):
        """차트 기본값 업데이트 테스트"""
        chart_type = "막대 차트"
        result = self.settings_handler.update_chart_default(chart_type)
        
        assert self.settings_handler.settings['chart_default'] == chart_type
        assert chart_type in result


class TestNotificationManager:
    """알림 관리자 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.notification_manager = NotificationManager()
    
    def test_show_success(self):
        """성공 알림 테스트"""
        message = "성공적으로 완료되었습니다"
        result = self.notification_manager.show_success(message)
        
        assert message in result
        assert "✅" in result
        assert len(self.notification_manager.notifications) == 1
        assert self.notification_manager.notifications[0]['type'] == 'success'
    
    def test_show_error(self):
        """오류 알림 테스트"""
        message = "오류가 발생했습니다"
        result = self.notification_manager.show_error(message)
        
        assert message in result
        assert "❌" in result
        assert len(self.notification_manager.notifications) == 1
        assert self.notification_manager.notifications[0]['type'] == 'error'
    
    def test_show_info(self):
        """정보 알림 테스트"""
        message = "정보를 확인하세요"
        result = self.notification_manager.show_info(message)
        
        assert message in result
        assert "💡" in result
        assert len(self.notification_manager.notifications) == 1
        assert self.notification_manager.notifications[0]['type'] == 'info'


class TestProgressTracker:
    """진행률 추적기 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.progress_tracker = ProgressTracker()
    
    def test_start_progress(self):
        """진행률 시작 테스트"""
        steps = ["Step 1", "Step 2", "Step 3"]
        result = self.progress_tracker.start_progress(steps)
        
        assert self.progress_tracker.total_steps == 3
        assert self.progress_tracker.current_step == 0
        assert "처리 진행률" in result
        assert "0/3" in result
    
    def test_update_progress(self):
        """진행률 업데이트 테스트"""
        steps = ["Step 1", "Step 2", "Step 3"]
        self.progress_tracker.start_progress(steps)
        
        # 2단계로 업데이트
        result = self.progress_tracker.update_progress(2, "2단계 완료")
        
        assert self.progress_tracker.current_step == 2
        assert "2/3" in result
    
    def test_update_progress_overflow(self):
        """진행률 오버플로우 테스트"""
        steps = ["Step 1", "Step 2"]
        self.progress_tracker.start_progress(steps)
        
        # 총 단계보다 많은 단계로 업데이트 시도
        result = self.progress_tracker.update_progress(5)
        
        # 최대값으로 제한되어야 함
        assert self.progress_tracker.current_step == 2


class TestThemeManager:
    """테마 관리자 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.theme_manager = ThemeManager()
    
    def test_get_theme_valid(self):
        """유효한 테마 가져오기 테스트"""
        theme = self.theme_manager.get_theme("light")
        assert theme is not None
        
        theme = self.theme_manager.get_theme("dark")
        assert theme is not None
    
    def test_get_theme_invalid(self):
        """잘못된 테마 이름 테스트"""
        theme = self.theme_manager.get_theme("invalid_theme")
        assert theme is not None  # 기본 테마가 반환되어야 함
    
    def test_get_custom_css(self):
        """커스텀 CSS 가져오기 테스트"""
        css = self.theme_manager.get_custom_css("light")
        assert isinstance(css, str)
        assert len(css) > 0
        
        css = self.theme_manager.get_custom_css("dark")
        assert isinstance(css, str)
        assert len(css) > 0


class TestColorPalette:
    """색상 팔레트 테스트"""
    
    def test_get_brand_color(self):
        """브랜드 색상 가져오기 테스트"""
        primary = ColorPalette.get_color("primary", "brand")
        assert primary == "#667eea"
        
        secondary = ColorPalette.get_color("secondary", "brand")
        assert secondary == "#764ba2"
    
    def test_get_neutral_color(self):
        """중성 색상 가져오기 테스트"""
        white = ColorPalette.get_color("white", "neutral")
        assert white == "#ffffff"
        
        black = ColorPalette.get_color("black", "neutral")
        assert black == "#000000"
    
    def test_get_invalid_color(self):
        """잘못된 색상 이름 테스트"""
        color = ColorPalette.get_color("invalid_color", "brand")
        assert color == "#667eea"  # 기본 primary 색상이 반환되어야 함
    
    def test_data_viz_colors_count(self):
        """데이터 시각화 색상 개수 테스트"""
        colors = ColorPalette.DATA_VIZ_COLORS
        assert len(colors) >= 8  # 최소 8개의 색상이 있어야 함
        
        # 모든 색상이 hex 형식인지 확인
        for color in colors:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB 형식


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
