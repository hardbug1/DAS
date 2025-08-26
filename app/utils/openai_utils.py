"""
OpenAI 유틸리티 함수들

OpenAI API 관련 유틸리티 함수들을 제공합니다.
"""

import os
import tiktoken
from typing import List, Dict, Any, Tuple, Optional
import structlog
from openai import OpenAI
from app.config.settings import settings

logger = structlog.get_logger()


class OpenAIValidator:
    """OpenAI API 검증 클래스"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, str]:
        """
        API 키 유효성 검증
        
        Args:
            api_key: 검증할 API 키
            
        Returns:
            Tuple[유효성, 메시지]
        """
        if not api_key:
            return False, "API 키가 입력되지 않았습니다."
        
        if not api_key.startswith('sk-'):
            return False, "올바른 OpenAI API 키 형식이 아닙니다. (sk-로 시작해야 함)"
        
        if len(api_key) < 50:
            return False, "API 키가 너무 짧습니다."
        
        if api_key == "your-openai-api-key-here":
            return False, "기본 템플릿 값입니다. 실제 API 키를 입력해주세요."
        
        return True, "API 키 형식이 올바릅니다."
    
    @staticmethod
    def test_api_connection(api_key: str, model: str = "gpt-3.5-turbo") -> Tuple[bool, str]:
        """
        API 연결 테스트
        
        Args:
            api_key: 테스트할 API 키
            model: 테스트할 모델명
            
        Returns:
            Tuple[성공 여부, 메시지]
        """
        try:
            # API 키 형식 검증
            is_valid, message = OpenAIValidator.validate_api_key(api_key)
            if not is_valid:
                return False, message
            
            # 실제 API 호출 테스트
            client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Hello, this is a connection test."}
                ],
                max_tokens=10,
                timeout=10
            )
            
            if response and response.choices:
                logger.info("OpenAI API 연결 테스트 성공", model=model)
                return True, f"API 연결 성공! 모델: {model}"
            else:
                return False, "API 응답이 비어있습니다."
                
        except Exception as e:
            error_msg = str(e)
            logger.error("OpenAI API 연결 테스트 실패", error=error_msg)
            
            # 일반적인 오류 메시지 변환
            if "invalid_api_key" in error_msg.lower():
                return False, "유효하지 않은 API 키입니다."
            elif "quota" in error_msg.lower():
                return False, "API 사용량 한도를 초과했습니다."
            elif "rate_limit" in error_msg.lower():
                return False, "API 호출 속도 제한에 걸렸습니다."
            elif "timeout" in error_msg.lower():
                return False, "API 호출 시간이 초과되었습니다."
            else:
                return False, f"연결 오류: {error_msg}"


class TokenCounter:
    """토큰 계산 유틸리티"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # 지원되지 않는 모델인 경우 기본 인코딩 사용
            self.encoding = tiktoken.get_encoding("cl100k_base")
            logger.warning(f"모델 {model}의 인코딩을 찾을 수 없어 기본 인코딩 사용")
    
    def count_tokens(self, text: str) -> int:
        """텍스트의 토큰 수 계산"""
        try:
            return len(self.encoding.encode(text))
        except Exception as e:
            logger.error("토큰 계산 실패", error=str(e))
            # 대략적인 계산 (영어 기준 4글자 = 1토큰)
            return len(text) // 4
    
    def count_messages_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """메시지 리스트의 총 토큰 수 계산"""
        total_tokens = 0
        
        for message in messages:
            # 메시지 구조에 따른 토큰 계산
            total_tokens += 4  # 메시지 기본 토큰 (role, content 등)
            
            for key, value in message.items():
                if isinstance(value, str):
                    total_tokens += self.count_tokens(value)
                
                if key == "name":  # name 필드가 있는 경우 추가 토큰
                    total_tokens += 1
        
        total_tokens += 2  # 응답을 위한 assistant 메시지 시작 토큰
        
        return total_tokens
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 0) -> Dict[str, float]:
        """토큰 수에 따른 예상 비용 계산 (USD)"""
        # 2024년 기준 OpenAI 가격 (모델별)
        pricing = {
            "gpt-4": {
                "input": 0.03 / 1000,   # $0.03 per 1K tokens
                "output": 0.06 / 1000   # $0.06 per 1K tokens
            },
            "gpt-4-turbo": {
                "input": 0.01 / 1000,   # $0.01 per 1K tokens
                "output": 0.03 / 1000   # $0.03 per 1K tokens
            },
            "gpt-3.5-turbo": {
                "input": 0.001 / 1000,  # $0.001 per 1K tokens
                "output": 0.002 / 1000  # $0.002 per 1K tokens
            }
        }
        
        model_pricing = pricing.get(self.model, pricing["gpt-4"])  # 기본값
        
        input_cost = input_tokens * model_pricing["input"]
        output_cost = output_tokens * model_pricing["output"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": self.model
        }


class ModelInfo:
    """OpenAI 모델 정보"""
    
    MODEL_LIMITS = {
        "gpt-4": {
            "max_tokens": 8192,
            "context_window": 8192,
            "description": "가장 성능이 좋은 모델, 복잡한 작업에 적합"
        },
        "gpt-4-turbo": {
            "max_tokens": 4096,
            "context_window": 128000,
            "description": "빠르고 효율적인 GPT-4, 긴 컨텍스트 처리 가능"
        },
        "gpt-3.5-turbo": {
            "max_tokens": 4096,
            "context_window": 16385,
            "description": "빠르고 경제적인 모델, 일반적인 작업에 적합"
        }
    }
    
    @classmethod
    def get_model_info(cls, model: str) -> Dict[str, Any]:
        """모델 정보 조회"""
        return cls.MODEL_LIMITS.get(model, {
            "max_tokens": 4096,
            "context_window": 8192,
            "description": "알 수 없는 모델"
        })
    
    @classmethod
    def validate_token_limit(cls, model: str, token_count: int) -> Tuple[bool, str]:
        """토큰 수 제한 검증"""
        info = cls.get_model_info(model)
        max_tokens = info["context_window"]
        
        if token_count > max_tokens:
            return False, f"토큰 수({token_count})가 모델 한계({max_tokens})를 초과했습니다."
        
        # 90% 이상 사용 시 경고
        if token_count > max_tokens * 0.9:
            return True, f"토큰 사용량이 높습니다. ({token_count}/{max_tokens})"
        
        return True, f"토큰 사용량 정상 ({token_count}/{max_tokens})"
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """사용 가능한 모델 목록"""
        return list(cls.MODEL_LIMITS.keys())
    
    @classmethod
    def recommend_model(cls, task_type: str) -> str:
        """작업 타입에 따른 모델 추천"""
        recommendations = {
            "sql": "gpt-4",  # 정확성이 중요
            "data_analysis": "gpt-4-turbo",  # 긴 컨텍스트 처리
            "excel": "gpt-3.5-turbo",  # 일반적인 작업
            "general": "gpt-3.5-turbo"  # 경제적
        }
        
        return recommendations.get(task_type, "gpt-3.5-turbo")


class APIUsageTracker:
    """API 사용량 추적"""
    
    def __init__(self):
        self.usage_stats = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "model_usage": {}
        }
    
    def track_usage(self, model: str, input_tokens: int, output_tokens: int):
        """사용량 추적"""
        counter = TokenCounter(model)
        cost_info = counter.estimate_cost(input_tokens, output_tokens)
        
        # 전체 통계 업데이트
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_input_tokens"] += input_tokens
        self.usage_stats["total_output_tokens"] += output_tokens
        self.usage_stats["total_cost"] += cost_info["total_cost"]
        
        # 모델별 통계 업데이트
        if model not in self.usage_stats["model_usage"]:
            self.usage_stats["model_usage"][model] = {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": 0.0
            }
        
        model_stats = self.usage_stats["model_usage"][model]
        model_stats["requests"] += 1
        model_stats["input_tokens"] += input_tokens
        model_stats["output_tokens"] += output_tokens
        model_stats["cost"] += cost_info["total_cost"]
        
        logger.info("API 사용량 기록", 
                   model=model,
                   input_tokens=input_tokens,
                   output_tokens=output_tokens,
                   cost=cost_info["total_cost"])
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """사용량 요약 반환"""
        return self.usage_stats.copy()
    
    def reset_usage(self):
        """사용량 통계 초기화"""
        self.usage_stats = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "model_usage": {}
        }
        logger.info("API 사용량 통계 초기화")


# 전역 인스턴스들
validator = OpenAIValidator()
usage_tracker = APIUsageTracker()

def get_token_counter(model: str = None) -> TokenCounter:
    """토큰 카운터 인스턴스 반환"""
    if model is None:
        model = settings.openai_model
    return TokenCounter(model)
