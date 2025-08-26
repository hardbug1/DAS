"""
AI 채팅 서비스

실제 AI 기반 채팅 기능을 제공합니다.
"""

import asyncio
from typing import List, Tuple, Optional, Dict, Any
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import structlog
from datetime import datetime

from app.core.langchain_config import langchain_manager, PromptTemplates, ChatConfiguration
from app.config.settings import settings
from app.utils.openai_utils import validator, usage_tracker, get_token_counter

logger = structlog.get_logger()


class AIChatService:
    """AI 채팅 서비스 클래스"""
    
    def __init__(self):
        self.langchain_manager = langchain_manager
        self.is_available = self._check_availability()
        self.conversation_count = 0
    
    def _check_availability(self) -> bool:
        """AI 서비스 사용 가능 여부 확인"""
        if not self.langchain_manager:
            logger.warning("LangChain 관리자가 초기화되지 않음")
            return False
        
        if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
            logger.warning("OpenAI API 키가 설정되지 않음")
            return False
        
        return True
    
    async def send_message(self, user_message: str, conversation_history: List[Tuple[str, str]] = None) -> Tuple[str, bool]:
        """
        사용자 메시지에 대한 AI 응답 생성
        
        Args:
            user_message: 사용자 메시지
            conversation_history: 대화 기록 (선택사항)
        
        Returns:
            Tuple[응답 메시지, 성공 여부]
        """
        if not self.is_available:
            return self._get_fallback_response(user_message), False
        
        try:
            # 대화 타입 감지
            conversation_type = self._detect_conversation_type(user_message)
            logger.info("대화 타입 감지", type=conversation_type, message=user_message)
            
            # 설정 로드
            config = ChatConfiguration.get_config(conversation_type)
            
            # LLM 설정 업데이트
            llm = self.langchain_manager.get_llm()
            llm.temperature = config["temperature"]
            llm.max_tokens = config["max_tokens"]
            
            # 메시지 구성
            messages = self._build_messages(user_message, conversation_type, conversation_history)
            
            # AI 응답 생성
            response = await self._generate_response(llm, messages)
            
            # 메모리에 대화 저장
            self._save_to_memory(user_message, response)
            
            # 응답 후처리
            formatted_response = self._format_response(response, conversation_type)
            
            self.conversation_count += 1
            logger.info("AI 응답 생성 완료", 
                       conversation_count=self.conversation_count,
                       response_length=len(formatted_response))
            
            return formatted_response, True
            
        except Exception as e:
            logger.error("AI 응답 생성 실패", error=str(e))
            return self._get_error_response(str(e)), False
    
    def _detect_conversation_type(self, message: str) -> str:
        """대화 타입 감지"""
        message_lower = message.lower()
        
        # SQL 관련 키워드
        sql_keywords = [
            'sql', 'select', 'query', '쿼리', '조회', 'database', '데이터베이스',
            'table', '테이블', 'join', 'where', 'group by', 'order by'
        ]
        
        # 데이터 분석 키워드
        analysis_keywords = [
            '분석', '통계', '평균', '합계', '최대', '최소', '트렌드', '패턴',
            '상관관계', '예측', '모델링', '인사이트', '대시보드'
        ]
        
        # Excel/파일 관련 키워드
        excel_keywords = [
            'excel', 'csv', '엑셀', '파일', '스프레드시트', '업로드',
            '데이터 파일', '워크북', '시트'
        ]
        
        if any(keyword in message_lower for keyword in sql_keywords):
            return "sql"
        elif any(keyword in message_lower for keyword in excel_keywords):
            return "excel"
        elif any(keyword in message_lower for keyword in analysis_keywords):
            return "data_analysis"
        else:
            return "general"
    
    def _build_messages(self, user_message: str, conversation_type: str, 
                       conversation_history: List[Tuple[str, str]] = None) -> List:
        """메시지 리스트 구성"""
        messages = []
        
        # 시스템 메시지 추가
        messages.append(PromptTemplates.get_system_message())
        
        # 기존 대화 기록 추가 (최근 5개만)
        if conversation_history:
            recent_history = conversation_history[-5:]
            for user_msg, ai_msg in recent_history:
                messages.append(HumanMessage(content=user_msg))
                if ai_msg:
                    messages.append(AIMessage(content=ai_msg))
        
        # 타입별 컨텍스트 메시지 추가
        context_message = self._get_context_message(conversation_type, user_message)
        if context_message:
            messages.append(HumanMessage(content=context_message))
        
        # 현재 사용자 메시지 추가
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def _get_context_message(self, conversation_type: str, user_message: str) -> Optional[str]:
        """타입별 컨텍스트 메시지 생성"""
        if conversation_type == "data_analysis":
            return PromptTemplates.format_data_analysis_prompt(
                question=user_message,
                context="Week 2 개발 단계 - 기본 AI 채팅 구현 중"
            )
        elif conversation_type == "sql":
            return PromptTemplates.format_sql_prompt(
                question=user_message,
                schema="아직 스키마 정보가 없습니다 (Week 3에서 구현 예정)"
            )
        elif conversation_type == "excel":
            return PromptTemplates.format_excel_prompt(
                question=user_message,
                file_info="아직 파일 정보가 없습니다 (Week 4에서 구현 예정)"
            )
        return None
    
    async def _generate_response(self, llm, messages: List) -> str:
        """AI 응답 생성"""
        try:
            # 토큰 수 계산 (요청 전)
            token_counter = get_token_counter(settings.openai_model)
            
            # 메시지를 문자열로 변환하여 토큰 계산
            message_texts = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    message_texts.append(msg.content)
            
            input_tokens = sum(token_counter.count_tokens(text) for text in message_texts)
            
            # 토큰 제한 확인
            from app.utils.openai_utils import ModelInfo
            is_valid, token_message = ModelInfo.validate_token_limit(settings.openai_model, input_tokens)
            
            if not is_valid:
                raise Exception(token_message)
            
            # 비동기 호출
            response = await asyncio.wait_for(
                asyncio.to_thread(llm.invoke, messages),
                timeout=ChatConfiguration.TIMEOUT_SECONDS
            )
            
            if response and hasattr(response, 'content'):
                # 응답 토큰 수 계산 및 사용량 추적
                output_tokens = token_counter.count_tokens(response.content)
                usage_tracker.track_usage(settings.openai_model, input_tokens, output_tokens)
                
                logger.info("AI 응답 생성 완료",
                           input_tokens=input_tokens,
                           output_tokens=output_tokens,
                           model=settings.openai_model)
                
                return response.content
            else:
                raise ValueError("빈 응답 받음")
                
        except asyncio.TimeoutError:
            raise Exception("응답 시간 초과")
        except Exception as e:
            raise Exception(f"AI 응답 생성 오류: {str(e)}")
    
    def _save_to_memory(self, user_message: str, ai_response: str):
        """메모리에 대화 저장"""
        if self.langchain_manager and self.langchain_manager.memory:
            self.langchain_manager.add_user_message(user_message)
            self.langchain_manager.add_ai_message(ai_response)
    
    def _format_response(self, response: str, conversation_type: str) -> str:
        """응답 포맷팅"""
        # 기본 포맷팅
        formatted = response.strip()
        
        # 타입별 후처리
        if conversation_type == "sql":
            # SQL 응답에 주의사항 추가
            if "SELECT" in formatted.upper() or "sql" in formatted.lower():
                formatted += "\n\n💡 **참고**: 실제 SQL 실행은 Week 3에서 구현될 예정입니다."
        
        elif conversation_type == "excel":
            # Excel 응답에 안내 추가
            formatted += "\n\n📁 **참고**: 실제 파일 분석 기능은 Week 4에서 구현될 예정입니다."
        
        elif conversation_type == "data_analysis":
            # 데이터 분석 응답에 차트 안내 추가
            formatted += "\n\n📊 **참고**: 데이터 시각화 기능은 Week 5에서 구현될 예정입니다."
        
        # 개발 상태 정보 추가 (가끔씩)
        if self.conversation_count % 5 == 0:
            formatted += f"\n\n🚀 **개발 현황**: Week 2 - AI 채팅 기능 구현 중 (대화 {self.conversation_count}회)"
        
        return formatted
    
    def _get_fallback_response(self, user_message: str) -> str:
        """AI 서비스 불가능시 대체 응답"""
        responses = [
            "🤖 안녕하세요! 현재 AI 기능이 준비 중입니다.",
            "⚙️ OpenAI API 키 설정이 필요합니다. Week 2에서 AI 연동을 완료할 예정입니다.",
            "🔧 AI 채팅 기능을 구현하고 있습니다. 곧 실제 AI와 대화할 수 있게 됩니다!",
            "📝 현재는 데모 모드입니다. 실제 AI 분석 기능은 단계적으로 구현될 예정입니다."
        ]
        
        # 메시지 내용에 따른 맞춤 응답
        message_lower = user_message.lower()
        
        if any(keyword in message_lower for keyword in ['매출', '분석', '데이터']):
            return "📊 데이터 분석 관련 질문이시네요! Week 3-5에서 실제 분석 기능이 구현될 예정입니다. 현재는 AI 채팅 기본 기능을 구현 중입니다."
        
        elif any(keyword in message_lower for keyword in ['sql', '쿼리', '데이터베이스']):
            return "🗄️ SQL 데이터베이스 기능은 Week 3에서 구현될 예정입니다. LangChain SQLDatabaseChain을 사용하여 자연어를 SQL로 변환하는 기능을 개발할 계획입니다."
        
        elif any(keyword in message_lower for keyword in ['파일', 'excel', 'csv']):
            return "📁 Excel/CSV 파일 분석 기능은 Week 4에서 구현될 예정입니다. Pandas를 활용한 자동 분석 기능을 개발할 계획입니다."
        
        else:
            import random
            return random.choice(responses)
    
    def _get_error_response(self, error: str) -> str:
        """오류 응답 생성"""
        return f"❌ 죄송합니다. AI 응답 생성 중 오류가 발생했습니다.\n\n🔧 **오류 정보**: {error}\n\n💡 **해결 방법**: OpenAI API 키 설정을 확인하거나 잠시 후 다시 시도해주세요."
    
    def clear_conversation(self):
        """대화 기록 초기화"""
        if self.langchain_manager:
            self.langchain_manager.clear_memory()
        self.conversation_count = 0
        logger.info("대화 기록 초기화 완료")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """대화 기록 조회"""
        if not self.langchain_manager:
            return []
        
        history = []
        messages = self.langchain_manager.get_conversation_history()
        
        for i in range(0, len(messages) - 1, 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                ai_msg = messages[i + 1]
                
                history.append({
                    "user_message": user_msg.content,
                    "ai_response": ai_msg.content,
                    "timestamp": datetime.now().isoformat()
                })
        
        return history
    
    def test_ai_connection(self) -> Tuple[bool, str]:
        """AI 연결 테스트"""
        if not self.is_available:
            return False, "AI 서비스가 사용 불가능합니다."
        
        try:
            # OpenAI 유틸리티를 사용한 더 정확한 테스트
            success, message = validator.test_api_connection(
                settings.openai_api_key,
                settings.openai_model
            )
            
            if success:
                logger.info("AI 연결 테스트 성공")
                return True, f"✅ {message}"
            else:
                logger.warning("AI 연결 테스트 실패", reason=message)
                return False, f"❌ {message}"
                
        except Exception as e:
            logger.error("AI 연결 테스트 중 오류", error=str(e))
            return False, f"❌ 연결 테스트 오류: {str(e)}"


# 전역 AI 채팅 서비스 인스턴스
ai_chat_service = AIChatService()
