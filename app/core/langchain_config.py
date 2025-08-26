"""
LangChain 설정 및 초기화

LangChain 관련 설정과 컴포넌트들을 관리합니다.
"""

import os
from typing import Optional, Dict, Any, List
from langchain.llms.base import LLM
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun
import structlog
from app.config.settings import settings

logger = structlog.get_logger()


class LangChainManager:
    """LangChain 관리 클래스"""
    
    def __init__(self):
        self.llm: Optional[ChatOpenAI] = None
        self.memory: Optional[ConversationBufferWindowMemory] = None
        self._initialize_components()
    
    def _initialize_components(self):
        """LangChain 컴포넌트 초기화"""
        try:
            # OpenAI LLM 초기화
            self.llm = ChatOpenAI(
                openai_api_key=settings.openai_api_key,
                model_name=settings.openai_model,
                temperature=0.7,
                max_tokens=2000,
                request_timeout=60,
                max_retries=3
            )
            
            # 대화 메모리 초기화 (최근 10개 대화 저장)
            self.memory = ConversationBufferWindowMemory(
                k=10,
                memory_key="chat_history",
                return_messages=True
            )
            
            logger.info("LangChain 컴포넌트 초기화 완료")
            
        except Exception as e:
            logger.error("LangChain 초기화 실패", error=str(e))
            raise
    
    def get_llm(self) -> ChatOpenAI:
        """LLM 인스턴스 반환"""
        if self.llm is None:
            raise RuntimeError("LLM이 초기화되지 않았습니다.")
        return self.llm
    
    def get_memory(self) -> ConversationBufferWindowMemory:
        """메모리 인스턴스 반환"""
        if self.memory is None:
            raise RuntimeError("메모리가 초기화되지 않았습니다.")
        return self.memory
    
    def test_connection(self) -> bool:
        """OpenAI API 연결 테스트"""
        try:
            llm = self.get_llm()
            response = llm.invoke([HumanMessage(content="안녕하세요. 연결 테스트입니다.")])
            
            if response and response.content:
                logger.info("OpenAI API 연결 테스트 성공")
                return True
            else:
                logger.warning("OpenAI API 연결 테스트 실패 - 빈 응답")
                return False
                
        except Exception as e:
            logger.error("OpenAI API 연결 테스트 실패", error=str(e))
            return False
    
    def clear_memory(self):
        """대화 메모리 초기화"""
        if self.memory:
            self.memory.clear()
            logger.info("대화 메모리 초기화 완료")
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """대화 기록 조회"""
        if self.memory:
            return self.memory.chat_memory.messages
        return []
    
    def add_user_message(self, message: str):
        """사용자 메시지 추가"""
        if self.memory:
            self.memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, message: str):
        """AI 메시지 추가"""
        if self.memory:
            self.memory.chat_memory.add_ai_message(message)


class PromptTemplates:
    """프롬프트 템플릿 관리"""
    
    # 시스템 프롬프트
    SYSTEM_PROMPT = """
당신은 AI 데이터 분석 비서입니다. 사용자의 질문에 대해 친근하고 정확한 답변을 제공해야 합니다.

주요 역할:
1. 데이터 분석 관련 질문에 전문적으로 답변
2. SQL 쿼리 생성 및 데이터베이스 조회 지원
3. Excel/CSV 파일 분석 및 인사이트 제공
4. 데이터 시각화 추천 및 차트 생성 지원
5. 통계 분석 및 패턴 발견

응답 가이드라인:
- 한국어로 친근하고 이해하기 쉽게 설명
- 구체적이고 실용적인 답변 제공
- 필요시 단계별로 설명
- 데이터나 분석 결과가 없는 경우 명확히 안내
- 항상 정확성을 우선시하고, 불확실한 경우 그렇다고 명시

현재 개발 상태:
- Week 2 단계로 기본 AI 채팅 기능 구현 중
- 실제 데이터베이스 연동은 Week 3에서 구현 예정
- Excel 파일 분석은 Week 4에서 구현 예정
- 차트 생성은 Week 5에서 구현 예정
"""
    
    # 데이터 분석 프롬프트
    DATA_ANALYSIS_PROMPT = """
사용자가 데이터 분석에 대해 질문했습니다.

사용자 질문: {question}
분석 컨텍스트: {context}

다음 사항을 고려하여 답변하세요:
1. 질문의 의도 파악
2. 적절한 분석 방법 제안
3. 예상되는 결과나 인사이트 설명
4. 필요한 데이터나 추가 정보 안내

현재는 데모 단계이므로, 실제 분석 대신 방법론과 접근법을 중심으로 설명해주세요.
"""
    
    # SQL 관련 프롬프트
    SQL_PROMPT = """
사용자가 데이터베이스 쿼리에 대해 질문했습니다.

사용자 질문: {question}
데이터베이스 스키마: {schema}

다음을 포함하여 답변하세요:
1. 적절한 SQL 쿼리 생성
2. 쿼리 설명 및 주의사항
3. 예상 결과 형태 설명
4. 성능 최적화 팁 (필요시)

주의: 현재는 데모 단계이므로 실제 쿼리 실행은 Week 3에서 구현됩니다.
"""
    
    # Excel 분석 프롬프트
    EXCEL_ANALYSIS_PROMPT = """
사용자가 Excel/CSV 파일 분석에 대해 질문했습니다.

사용자 질문: {question}
파일 정보: {file_info}

다음을 포함하여 답변하세요:
1. 분석 가능한 항목들
2. 추천 분석 방법
3. 유용한 차트나 시각화 제안
4. 파일 준비 방법 안내

현재는 데모 단계이므로, 실제 파일 분석은 Week 4에서 구현됩니다.
"""
    
    @classmethod
    def get_system_message(cls) -> SystemMessage:
        """시스템 메시지 반환"""
        return SystemMessage(content=cls.SYSTEM_PROMPT)
    
    @classmethod
    def format_data_analysis_prompt(cls, question: str, context: str = "") -> str:
        """데이터 분석 프롬프트 포맷팅"""
        return cls.DATA_ANALYSIS_PROMPT.format(
            question=question,
            context=context
        )
    
    @classmethod
    def format_sql_prompt(cls, question: str, schema: str = "") -> str:
        """SQL 프롬프트 포맷팅"""
        return cls.SQL_PROMPT.format(
            question=question,
            schema=schema
        )
    
    @classmethod
    def format_excel_prompt(cls, question: str, file_info: str = "") -> str:
        """Excel 분석 프롬프트 포맷팅"""
        return cls.EXCEL_ANALYSIS_PROMPT.format(
            question=question,
            file_info=file_info
        )


class ChatConfiguration:
    """채팅 설정 관리"""
    
    # 응답 설정
    DEFAULT_TEMPERATURE = 0.7
    MAX_TOKENS = 2000
    TIMEOUT_SECONDS = 60
    
    # 메모리 설정
    MEMORY_WINDOW_SIZE = 10
    
    # 응답 타입별 설정
    RESPONSE_CONFIGS = {
        "general": {
            "temperature": 0.7,
            "max_tokens": 1500,
            "system_prompt": PromptTemplates.SYSTEM_PROMPT
        },
        "data_analysis": {
            "temperature": 0.3,
            "max_tokens": 2000,
            "system_prompt": PromptTemplates.SYSTEM_PROMPT
        },
        "sql": {
            "temperature": 0.1,
            "max_tokens": 1000,
            "system_prompt": PromptTemplates.SYSTEM_PROMPT
        },
        "excel": {
            "temperature": 0.5,
            "max_tokens": 1500,
            "system_prompt": PromptTemplates.SYSTEM_PROMPT
        }
    }
    
    @classmethod
    def get_config(cls, response_type: str = "general") -> Dict[str, Any]:
        """응답 타입별 설정 반환"""
        return cls.RESPONSE_CONFIGS.get(response_type, cls.RESPONSE_CONFIGS["general"])


# 전역 LangChain 관리자 인스턴스
try:
    langchain_manager = LangChainManager()
except Exception as e:
    logger.warning("LangChain 초기화 실패 - OpenAI API 키 확인 필요", error=str(e))
    langchain_manager = None
