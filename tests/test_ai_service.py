"""
AI 서비스 테스트

LangChain 연동 및 AI 채팅 서비스를 테스트합니다.
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.langchain_config import LangChainManager, PromptTemplates, ChatConfiguration
from app.services.ai_chat_service import AIChatService


class TestLangChainManager:
    """LangChain 관리자 테스트"""
    
    @patch('app.core.langchain_config.settings')
    def test_initialization_success(self, mock_settings):
        """정상 초기화 테스트"""
        mock_settings.openai_api_key = "test-api-key"
        mock_settings.openai_model = "gpt-4"
        
        with patch('app.core.langchain_config.ChatOpenAI') as mock_chat_openai:
            mock_llm = Mock()
            mock_chat_openai.return_value = mock_llm
            
            manager = LangChainManager()
            
            assert manager.llm == mock_llm
            assert manager.memory is not None
            mock_chat_openai.assert_called_once()
    
    @patch('app.core.langchain_config.settings')
    def test_initialization_failure(self, mock_settings):
        """초기화 실패 테스트"""
        mock_settings.openai_api_key = "invalid-key"
        mock_settings.openai_model = "gpt-4"
        
        with patch('app.core.langchain_config.ChatOpenAI', side_effect=Exception("API 오류")):
            with pytest.raises(Exception):
                LangChainManager()
    
    def test_get_llm_not_initialized(self):
        """LLM 미초기화 상태 테스트"""
        manager = LangChainManager.__new__(LangChainManager)
        manager.llm = None
        
        with pytest.raises(RuntimeError, match="LLM이 초기화되지 않았습니다"):
            manager.get_llm()
    
    def test_get_memory_not_initialized(self):
        """메모리 미초기화 상태 테스트"""
        manager = LangChainManager.__new__(LangChainManager)
        manager.memory = None
        
        with pytest.raises(RuntimeError, match="메모리가 초기화되지 않았습니다"):
            manager.get_memory()
    
    @patch('app.core.langchain_config.settings')
    def test_memory_operations(self, mock_settings):
        """메모리 연산 테스트"""
        mock_settings.openai_api_key = "test-api-key"
        mock_settings.openai_model = "gpt-4"
        
        with patch('app.core.langchain_config.ChatOpenAI'):
            manager = LangChainManager()
            
            # 메시지 추가
            manager.add_user_message("테스트 메시지")
            manager.add_ai_message("테스트 응답")
            
            # 대화 기록 확인
            history = manager.get_conversation_history()
            assert len(history) == 2
            
            # 메모리 초기화
            manager.clear_memory()
            history_after_clear = manager.get_conversation_history()
            assert len(history_after_clear) == 0


class TestPromptTemplates:
    """프롬프트 템플릿 테스트"""
    
    def test_system_message_creation(self):
        """시스템 메시지 생성 테스트"""
        system_msg = PromptTemplates.get_system_message()
        
        assert system_msg is not None
        assert "AI 데이터 분석 비서" in system_msg.content
        assert "한국어" in system_msg.content
    
    def test_data_analysis_prompt_formatting(self):
        """데이터 분석 프롬프트 포맷팅 테스트"""
        question = "매출 분석을 해주세요"
        context = "테스트 컨텍스트"
        
        formatted = PromptTemplates.format_data_analysis_prompt(question, context)
        
        assert question in formatted
        assert context in formatted
        assert "사용자 질문:" in formatted
    
    def test_sql_prompt_formatting(self):
        """SQL 프롬프트 포맷팅 테스트"""
        question = "SELECT 쿼리를 만들어주세요"
        schema = "users(id, name, email)"
        
        formatted = PromptTemplates.format_sql_prompt(question, schema)
        
        assert question in formatted
        assert schema in formatted
        assert "SQL 쿼리" in formatted
    
    def test_excel_prompt_formatting(self):
        """Excel 프롬프트 포맷팅 테스트"""
        question = "엑셀 파일을 분석해주세요"
        file_info = "sales_data.xlsx"
        
        formatted = PromptTemplates.format_excel_prompt(question, file_info)
        
        assert question in formatted
        assert file_info in formatted
        assert "Excel" in formatted


class TestChatConfiguration:
    """채팅 설정 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = ChatConfiguration.get_config("general")
        
        assert "temperature" in config
        assert "max_tokens" in config
        assert "system_prompt" in config
        assert config["temperature"] == 0.7
    
    def test_specific_config_types(self):
        """특정 타입별 설정 테스트"""
        test_cases = [
            ("data_analysis", 0.3),
            ("sql", 0.1),
            ("excel", 0.5),
            ("general", 0.7)
        ]
        
        for config_type, expected_temp in test_cases:
            config = ChatConfiguration.get_config(config_type)
            assert config["temperature"] == expected_temp
    
    def test_invalid_config_type(self):
        """잘못된 설정 타입 테스트"""
        config = ChatConfiguration.get_config("invalid_type")
        
        # 기본 설정이 반환되어야 함
        assert config == ChatConfiguration.get_config("general")


class TestAIChatService:
    """AI 채팅 서비스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 호출"""
        self.service = AIChatService()
    
    def test_conversation_type_detection(self):
        """대화 타입 감지 테스트"""
        test_cases = [
            ("SQL 쿼리를 만들어주세요", "sql"),
            ("데이터를 분석해주세요", "data_analysis"),
            ("엑셀 파일을 업로드했습니다", "excel"),
            ("안녕하세요", "general"),
            ("SELECT * FROM users", "sql"),
            ("매출 트렌드 분석", "data_analysis"),
            ("CSV 파일 처리", "excel")
        ]
        
        for message, expected_type in test_cases:
            detected_type = self.service._detect_conversation_type(message)
            assert detected_type == expected_type, f"메시지 '{message}'의 예상 타입: {expected_type}, 실제: {detected_type}"
    
    def test_fallback_response_generation(self):
        """대체 응답 생성 테스트"""
        test_messages = [
            "매출 분석을 해주세요",
            "SQL 쿼리를 작성해주세요",
            "파일을 업로드했습니다",
            "안녕하세요"
        ]
        
        for message in test_messages:
            response = self.service._get_fallback_response(message)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # 기본적인 한국어 응답인지 확인
            assert any(char in response for char in ['입니다', '예정', '기능'])
    
    def test_error_response_generation(self):
        """오류 응답 생성 테스트"""
        error_message = "API 키 오류"
        response = self.service._get_error_response(error_message)
        
        assert "죄송합니다" in response
        assert error_message in response
        assert "❌" in response
    
    def test_response_formatting(self):
        """응답 포맷팅 테스트"""
        base_response = "테스트 응답입니다."
        
        # 타입별 포맷팅 테스트
        test_cases = [
            ("sql", "Week 3"),
            ("excel", "Week 4"),
            ("data_analysis", "Week 5"),
            ("general", "")
        ]
        
        for conv_type, expected_text in test_cases:
            formatted = self.service._format_response(base_response, conv_type)
            
            assert base_response in formatted
            if expected_text:
                assert expected_text in formatted
    
    @pytest.mark.asyncio
    async def test_send_message_without_langchain(self):
        """LangChain 없이 메시지 전송 테스트"""
        # AI 서비스가 사용 불가능한 상태로 설정
        self.service.is_available = False
        
        message = "테스트 메시지"
        response, success = await self.service.send_message(message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert success is False  # AI 서비스 불가능 상태이므로 False
    
    def test_conversation_history_management(self):
        """대화 기록 관리 테스트"""
        # 초기 상태
        assert self.service.conversation_count == 0
        
        # 대화 기록 초기화
        self.service.clear_conversation()
        assert self.service.conversation_count == 0
        
        # 기록 조회 (LangChain 없이)
        history = self.service.get_conversation_history()
        assert isinstance(history, list)
    
    def test_ai_connection_test(self):
        """AI 연결 테스트"""
        # AI 서비스 불가능 상태에서 테스트
        self.service.is_available = False
        
        success, message = self.service.test_ai_connection()
        
        assert success is False
        assert "사용 불가능" in message
    
    @patch('app.services.ai_chat_service.settings')
    def test_availability_check_no_api_key(self, mock_settings):
        """API 키 없을 때 가용성 확인 테스트"""
        mock_settings.openai_api_key = "your-openai-api-key-here"
        
        service = AIChatService()
        assert service.is_available is False
    
    @patch('app.services.ai_chat_service.settings')
    def test_availability_check_empty_api_key(self, mock_settings):
        """빈 API 키일 때 가용성 확인 테스트"""
        mock_settings.openai_api_key = ""
        
        service = AIChatService()
        assert service.is_available is False


class TestIntegration:
    """통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_full_chat_flow_without_api(self):
        """API 없이 전체 채팅 플로우 테스트"""
        service = AIChatService()
        
        # 첫 번째 메시지
        message1 = "안녕하세요"
        response1, success1 = await service.send_message(message1)
        
        assert isinstance(response1, str)
        assert len(response1) > 0
        
        # 두 번째 메시지
        message2 = "데이터 분석을 해주세요"
        history = [(message1, response1)]
        response2, success2 = await service.send_message(message2, history)
        
        assert isinstance(response2, str)
        assert len(response2) > 0
        
        # 대화 초기화
        service.clear_conversation()
        assert service.conversation_count == 0
    
    def test_prompt_template_integration(self):
        """프롬프트 템플릿 통합 테스트"""
        service = AIChatService()
        
        # 다양한 타입의 메시지로 컨텍스트 메시지 생성 테스트
        test_cases = [
            ("데이터 분석해주세요", "data_analysis"),
            ("SQL 쿼리 작성", "sql"),
            ("엑셀 파일 분석", "excel"),
            ("일반 질문", "general")
        ]
        
        for message, expected_type in test_cases:
            context_msg = service._get_context_message(expected_type, message)
            
            if expected_type != "general":
                assert context_msg is not None
                assert len(context_msg) > 0
            else:
                assert context_msg is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
