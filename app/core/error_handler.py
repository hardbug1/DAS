"""
통합 에러 처리 시스템

애플리케이션 전반의 에러를 체계적으로 처리하고 관리합니다.
"""

import traceback
from typing import Dict, Any, Optional, Tuple
from enum import Enum
import structlog
from datetime import datetime

logger = structlog.get_logger()


class ErrorType(Enum):
    """에러 타입 정의"""
    OPENAI_API_ERROR = "openai_api_error"
    LANGCHAIN_ERROR = "langchain_error"
    DATABASE_ERROR = "database_error"
    FILE_PROCESSING_ERROR = "file_processing_error"
    VALIDATION_ERROR = "validation_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_EXCEEDED_ERROR = "quota_exceeded_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """에러 심각도"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AppError(Exception):
    """애플리케이션 커스텀 에러"""
    
    def __init__(self, 
                 message: str,
                 error_type: ErrorType = ErrorType.UNKNOWN_ERROR,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 user_message: str = None,
                 details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.severity = severity
        self.user_message = user_message or self._generate_user_message()
        self.details = details or {}
        self.timestamp = datetime.now()
        
        # 로깅
        logger.error("AppError 발생",
                    error_type=error_type.value,
                    severity=severity.value,
                    message=message,
                    details=self.details)
    
    def _generate_user_message(self) -> str:
        """에러 타입에 따른 사용자용 메시지 생성"""
        user_messages = {
            ErrorType.OPENAI_API_ERROR: "AI 서비스 연결에 문제가 발생했습니다. API 키와 네트워크 연결을 확인해주세요.",
            ErrorType.LANGCHAIN_ERROR: "AI 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            ErrorType.DATABASE_ERROR: "데이터베이스 연결에 문제가 발생했습니다. 관리자에게 문의하세요.",
            ErrorType.FILE_PROCESSING_ERROR: "파일 처리 중 오류가 발생했습니다. 파일 형식과 크기를 확인해주세요.",
            ErrorType.VALIDATION_ERROR: "입력 데이터에 문제가 있습니다. 입력값을 확인해주세요.",
            ErrorType.NETWORK_ERROR: "네트워크 연결에 문제가 발생했습니다. 인터넷 연결을 확인해주세요.",
            ErrorType.AUTHENTICATION_ERROR: "인증에 실패했습니다. API 키나 인증 정보를 확인해주세요.",
            ErrorType.QUOTA_EXCEEDED_ERROR: "API 사용량 한도를 초과했습니다. 요금제를 확인하거나 시간을 두고 다시 시도해주세요.",
            ErrorType.TIMEOUT_ERROR: "요청 시간이 초과되었습니다. 네트워크 상태를 확인하거나 잠시 후 다시 시도해주세요.",
            ErrorType.UNKNOWN_ERROR: "알 수 없는 오류가 발생했습니다. 관리자에게 문의하세요."
        }
        
        return user_messages.get(self.error_type, "시스템 오류가 발생했습니다.")
    
    def to_dict(self) -> Dict[str, Any]:
        """에러 정보를 딕셔너리로 변환"""
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "message": str(self),
            "user_message": self.user_message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "traceback": traceback.format_exc()
        }


class ErrorHandler:
    """에러 처리 관리자"""
    
    def __init__(self):
        self.error_history = []
        self.error_patterns = {}
        self._setup_error_patterns()
    
    def _setup_error_patterns(self):
        """에러 패턴 정의"""
        self.error_patterns = {
            # OpenAI API 에러 패턴
            "invalid_api_key": (ErrorType.AUTHENTICATION_ERROR, ErrorSeverity.HIGH),
            "quota_exceeded": (ErrorType.QUOTA_EXCEEDED_ERROR, ErrorSeverity.HIGH),
            "rate_limit": (ErrorType.QUOTA_EXCEEDED_ERROR, ErrorSeverity.MEDIUM),
            "timeout": (ErrorType.TIMEOUT_ERROR, ErrorSeverity.MEDIUM),
            "connection": (ErrorType.NETWORK_ERROR, ErrorSeverity.MEDIUM),
            
            # LangChain 에러 패턴
            "langchain": (ErrorType.LANGCHAIN_ERROR, ErrorSeverity.MEDIUM),
            "memory": (ErrorType.LANGCHAIN_ERROR, ErrorSeverity.LOW),
            
            # 데이터베이스 에러 패턴
            "database": (ErrorType.DATABASE_ERROR, ErrorSeverity.HIGH),
            "sqlalchemy": (ErrorType.DATABASE_ERROR, ErrorSeverity.HIGH),
            "connection refused": (ErrorType.DATABASE_ERROR, ErrorSeverity.HIGH),
            
            # 파일 처리 에러 패턴
            "file": (ErrorType.FILE_PROCESSING_ERROR, ErrorSeverity.MEDIUM),
            "upload": (ErrorType.FILE_PROCESSING_ERROR, ErrorSeverity.MEDIUM),
            "pandas": (ErrorType.FILE_PROCESSING_ERROR, ErrorSeverity.MEDIUM),
            
            # 검증 에러 패턴
            "validation": (ErrorType.VALIDATION_ERROR, ErrorSeverity.LOW),
            "invalid": (ErrorType.VALIDATION_ERROR, ErrorSeverity.LOW),
        }
    
    def handle_error(self, error: Exception, context: str = "") -> AppError:
        """에러 처리 및 변환"""
        # 이미 AppError인 경우 그대로 반환
        if isinstance(error, AppError):
            self._record_error(error)
            return error
        
        # 에러 메시지 분석
        error_message = str(error).lower()
        error_type, severity = self._classify_error(error_message)
        
        # AppError로 변환
        app_error = AppError(
            message=str(error),
            error_type=error_type,
            severity=severity,
            details={
                "context": context,
                "original_type": type(error).__name__,
                "traceback": traceback.format_exc()
            }
        )
        
        self._record_error(app_error)
        return app_error
    
    def _classify_error(self, error_message: str) -> Tuple[ErrorType, ErrorSeverity]:
        """에러 메시지 기반 분류"""
        for pattern, (error_type, severity) in self.error_patterns.items():
            if pattern in error_message:
                return error_type, severity
        
        return ErrorType.UNKNOWN_ERROR, ErrorSeverity.MEDIUM
    
    def _record_error(self, error: AppError):
        """에러 기록"""
        self.error_history.append(error)
        
        # 최근 100개만 유지
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 조회"""
        if not self.error_history:
            return {"total_errors": 0}
        
        # 타입별 집계
        type_counts = {}
        severity_counts = {}
        recent_errors = []
        
        for error in self.error_history[-10:]:  # 최근 10개
            error_type = error.error_type.value
            severity = error.severity.value
            
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            recent_errors.append({
                "type": error_type,
                "message": error.user_message,
                "timestamp": error.timestamp.strftime("%H:%M:%S")
            })
        
        return {
            "total_errors": len(self.error_history),
            "type_counts": type_counts,
            "severity_counts": severity_counts,
            "recent_errors": recent_errors
        }
    
    def get_user_friendly_error(self, error: Exception, context: str = "") -> str:
        """사용자 친화적 에러 메시지 생성"""
        app_error = self.handle_error(error, context)
        return app_error.user_message
    
    def clear_error_history(self):
        """에러 기록 초기화"""
        self.error_history.clear()
        logger.info("에러 기록 초기화")


class ErrorRecovery:
    """에러 복구 시스템"""
    
    @staticmethod
    def suggest_recovery_actions(error: AppError) -> list[str]:
        """에러 타입에 따른 복구 방법 제안"""
        recovery_actions = {
            ErrorType.OPENAI_API_ERROR: [
                "OpenAI API 키가 올바르게 설정되었는지 확인하세요",
                "인터넷 연결 상태를 확인하세요",
                "API 사용량 한도를 확인하세요",
                "잠시 후 다시 시도하세요"
            ],
            ErrorType.LANGCHAIN_ERROR: [
                "대화 기록을 초기화해보세요",
                "다른 모델을 시도해보세요",
                "입력 메시지를 짧게 해보세요",
                "잠시 후 다시 시도하세요"
            ],
            ErrorType.DATABASE_ERROR: [
                "데이터베이스 연결 설정을 확인하세요",
                "애플리케이션을 재시작해보세요",
                "관리자에게 문의하세요"
            ],
            ErrorType.FILE_PROCESSING_ERROR: [
                "파일 형식이 지원되는지 확인하세요 (Excel, CSV)",
                "파일 크기가 100MB 이하인지 확인하세요",
                "파일이 손상되지 않았는지 확인하세요",
                "다른 파일로 시도해보세요"
            ],
            ErrorType.VALIDATION_ERROR: [
                "입력값을 다시 확인해주세요",
                "필수 필드가 모두 입력되었는지 확인하세요",
                "올바른 형식으로 입력했는지 확인하세요"
            ],
            ErrorType.NETWORK_ERROR: [
                "인터넷 연결을 확인하세요",
                "방화벽 설정을 확인하세요",
                "잠시 후 다시 시도하세요"
            ],
            ErrorType.AUTHENTICATION_ERROR: [
                "API 키를 다시 확인하세요",
                "API 키가 유효한지 확인하세요",
                "API 키 권한을 확인하세요"
            ],
            ErrorType.QUOTA_EXCEEDED_ERROR: [
                "API 사용량 한도를 확인하세요",
                "요금제를 업그레이드하세요",
                "시간을 두고 다시 시도하세요"
            ],
            ErrorType.TIMEOUT_ERROR: [
                "네트워크 연결을 확인하세요",
                "입력을 짧게 해보세요",
                "잠시 후 다시 시도하세요"
            ]
        }
        
        return recovery_actions.get(error.error_type, [
            "애플리케이션을 재시작해보세요",
            "잠시 후 다시 시도하세요",
            "문제가 지속되면 관리자에게 문의하세요"
        ])
    
    @staticmethod
    def auto_retry_suitable(error: AppError) -> bool:
        """자동 재시도 가능 여부 판단"""
        retry_suitable_types = [
            ErrorType.NETWORK_ERROR,
            ErrorType.TIMEOUT_ERROR,
            ErrorType.LANGCHAIN_ERROR
        ]
        
        return (error.error_type in retry_suitable_types and 
                error.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM])


class UserErrorReporter:
    """사용자용 에러 리포팅 시스템"""
    
    @staticmethod
    def generate_error_report_html(error: AppError) -> str:
        """사용자용 에러 리포트 HTML 생성"""
        severity_colors = {
            ErrorSeverity.LOW: "#28a745",
            ErrorSeverity.MEDIUM: "#ffc107", 
            ErrorSeverity.HIGH: "#fd7e14",
            ErrorSeverity.CRITICAL: "#dc3545"
        }
        
        severity_icons = {
            ErrorSeverity.LOW: "ℹ️",
            ErrorSeverity.MEDIUM: "⚠️",
            ErrorSeverity.HIGH: "❌",
            ErrorSeverity.CRITICAL: "🚨"
        }
        
        color = severity_colors.get(error.severity, "#6c757d")
        icon = severity_icons.get(error.severity, "❗")
        
        recovery_actions = ErrorRecovery.suggest_recovery_actions(error)
        actions_html = ""
        for i, action in enumerate(recovery_actions, 1):
            actions_html += f"<div style='margin: 5px 0;'>{i}. {action}</div>"
        
        return f"""
        <div style="
            background: white;
            border: 2px solid {color};
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
                <div>
                    <h3 style="margin: 0; color: {color};">오류가 발생했습니다</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">
                        {error.user_message}
                    </p>
                </div>
            </div>
            
            <div style="
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            ">
                <strong>💡 해결 방법:</strong>
                {actions_html}
            </div>
            
            <div style="
                font-size: 12px;
                color: #6c757d;
                border-top: 1px solid #e0e0e0;
                padding-top: 10px;
            ">
                <strong>오류 ID:</strong> {error.timestamp.strftime('%Y%m%d_%H%M%S')} |
                <strong>타입:</strong> {error.error_type.value} |
                <strong>시간:</strong> {error.timestamp.strftime('%H:%M:%S')}
            </div>
        </div>
        """
    
    @staticmethod
    def generate_error_summary_html(error_stats: Dict[str, Any]) -> str:
        """에러 요약 HTML 생성"""
        if error_stats.get("total_errors", 0) == 0:
            return """
            <div style="
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            ">
                ✅ <strong>문제없음</strong><br>
                현재 시스템에 오류가 없습니다.
            </div>
            """
        
        recent_errors_html = ""
        for error in error_stats.get("recent_errors", []):
            recent_errors_html += f"""
                <div style="
                    background: #fff;
                    padding: 8px;
                    margin: 5px 0;
                    border-radius: 4px;
                    border-left: 3px solid #dc3545;
                    font-size: 12px;
                ">
                    <strong>{error['timestamp']}</strong> - {error['message']}
                </div>
            """
        
        return f"""
        <div style="
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        ">
            <h4 style="margin: 0 0 10px 0;">⚠️ 에러 요약</h4>
            <div style="margin-bottom: 10px;">
                <strong>총 에러 수:</strong> {error_stats['total_errors']}개
            </div>
            
            {recent_errors_html if recent_errors_html else '<div style="font-style: italic;">최근 에러가 없습니다.</div>'}
            
            <div style="margin-top: 10px; font-size: 12px;">
                문제가 지속되면 애플리케이션을 재시작하거나 관리자에게 문의하세요.
            </div>
        </div>
        """


# 전역 에러 핸들러 인스턴스
error_handler = ErrorHandler()
error_recovery = ErrorRecovery()
user_error_reporter = UserErrorReporter()
