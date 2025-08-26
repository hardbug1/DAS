"""
AI 상태 관리 UI 컴포넌트

AI 서비스 상태를 모니터링하고 표시하는 UI 컴포넌트들을 제공합니다.
"""

import gradio as gr
from typing import Dict, Any, Tuple
import structlog
from datetime import datetime

from app.services.ai_chat_service import ai_chat_service
from app.config.settings import settings

logger = structlog.get_logger()


class AIStatusPanel:
    """AI 상태 패널 관리"""
    
    def __init__(self):
        self.last_check_time = None
        self.status_cache = {}
    
    def create_status_display(self) -> gr.HTML:
        """AI 상태 표시 패널 생성"""
        return gr.HTML(self._generate_status_html(), elem_id="ai-status-panel")
    
    def _generate_status_html(self) -> str:
        """AI 상태 HTML 생성"""
        # AI 서비스 상태 확인
        ai_available = ai_chat_service.is_available
        api_key_configured = bool(settings.openai_api_key and 
                                settings.openai_api_key != "your-openai-api-key-here")
        
        # 연결 테스트 (캐시된 결과 사용)
        connection_status = self._get_cached_connection_status()
        
        # 상태 아이콘 및 색상 결정
        if ai_available and api_key_configured and connection_status:
            status_icon = "🟢"
            status_text = "정상 동작"
            status_color = "#28a745"
            detail_text = "OpenAI GPT-4와 연결되어 실제 AI 응답을 제공합니다."
        elif api_key_configured:
            status_icon = "🟡"
            status_text = "연결 확인 중"
            status_color = "#ffc107"
            detail_text = "API 키는 설정되었으나 연결 상태를 확인 중입니다."
        else:
            status_icon = "🔴"
            status_text = "데모 모드"
            status_color = "#dc3545"
            detail_text = "OpenAI API 키가 설정되지 않아 데모 응답을 제공합니다."
        
        # 설정 정보
        model_info = settings.openai_model if api_key_configured else "설정 안됨"
        conversation_count = getattr(ai_chat_service, 'conversation_count', 0)
        
        return f"""
        <div style="
            background: white;
            border: 2px solid {status_color};
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 24px; margin-right: 10px;">{status_icon}</span>
                <div>
                    <h3 style="margin: 0; color: {status_color};">AI 서비스 상태: {status_text}</h3>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">{detail_text}</p>
                </div>
            </div>
            
            <div style="
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 15px;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
            ">
                <div>
                    <strong>🤖 AI 모델:</strong><br>
                    <span style="color: #495057;">{model_info}</span>
                </div>
                <div>
                    <strong>💬 대화 횟수:</strong><br>
                    <span style="color: #495057;">{conversation_count}회</span>
                </div>
                <div>
                    <strong>🔑 API 키:</strong><br>
                    <span style="color: #495057;">{'설정됨' if api_key_configured else '미설정'}</span>
                </div>
                <div>
                    <strong>⏰ 마지막 확인:</strong><br>
                    <span style="color: #495057;">{datetime.now().strftime('%H:%M:%S')}</span>
                </div>
            </div>
            
            <div style="margin-top: 15px; text-align: center;">
                <button onclick="refreshAIStatus()" style="
                    background: {status_color};
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">상태 새로고침</button>
            </div>
        </div>
        
        <script>
        function refreshAIStatus() {{
            // 상태 새로고침 기능 (실제 구현은 Gradio 이벤트로 처리)
            const panel = document.getElementById('ai-status-panel');
            if (panel) {{
                panel.style.opacity = '0.6';
                setTimeout(() => {{
                    panel.style.opacity = '1';
                    // 실제로는 Gradio 이벤트를 트리거해야 함
                }}, 1000);
            }}
        }}
        </script>
        """
    
    def _get_cached_connection_status(self) -> bool:
        """캐시된 연결 상태 조회"""
        now = datetime.now()
        
        # 5분마다 연결 상태 갱신
        if (self.last_check_time is None or 
            (now - self.last_check_time).seconds > 300):
            
            try:
                success, _ = ai_chat_service.test_ai_connection()
                self.status_cache['connection'] = success
                self.last_check_time = now
                logger.info("AI 연결 상태 갱신", status=success)
            except Exception as e:
                logger.warning("AI 연결 상태 확인 실패", error=str(e))
                self.status_cache['connection'] = False
        
        return self.status_cache.get('connection', False)
    
    def refresh_status(self) -> str:
        """상태 새로고침"""
        # 캐시 초기화
        self.last_check_time = None
        self.status_cache.clear()
        
        # 새로운 상태 HTML 생성
        return self._generate_status_html()


class AISettingsPanel:
    """AI 설정 패널"""
    
    @staticmethod
    def create_settings_panel() -> Dict[str, Any]:
        """AI 설정 패널 생성"""
        components = {}
        
        with gr.Accordion("🤖 AI 설정", open=True):
            # API 키 설정
            components['api_key_input'] = gr.Textbox(
                label="OpenAI API 키",
                type="password",
                placeholder="sk-...",
                value="설정됨" if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here" else "",
                info="실제 AI 기능을 사용하려면 OpenAI API 키가 필요합니다."
            )
            
            # 모델 선택
            components['model_select'] = gr.Dropdown(
                label="AI 모델",
                choices=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                value=settings.openai_model,
                info="사용할 OpenAI 모델을 선택하세요."
            )
            
            # 응답 설정
            with gr.Row():
                components['temperature_slider'] = gr.Slider(
                    label="창의성 (Temperature)",
                    minimum=0.0,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    info="0: 일관적, 1: 창의적"
                )
                
                components['max_tokens_slider'] = gr.Slider(
                    label="최대 토큰 수",
                    minimum=100,
                    maximum=4000,
                    value=2000,
                    step=100,
                    info="응답의 최대 길이"
                )
            
            # 대화 설정
            components['memory_size_slider'] = gr.Slider(
                label="대화 기억 크기",
                minimum=1,
                maximum=20,
                value=10,
                step=1,
                info="기억할 이전 대화의 개수"
            )
            
            # 테스트 버튼
            with gr.Row():
                components['test_connection_btn'] = gr.Button(
                    "🔌 연결 테스트",
                    variant="secondary"
                )
                
                components['clear_memory_btn'] = gr.Button(
                    "🗑️ 대화 기록 초기화",
                    variant="secondary"
                )
            
            # 결과 표시
            components['test_result'] = gr.HTML("")
        
        return components
    
    @staticmethod
    def test_ai_connection() -> str:
        """AI 연결 테스트"""
        try:
            success, message = ai_chat_service.test_ai_connection()
            
            if success:
                return f"""
                <div style="
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 10px 0;
                ">
                    ✅ <strong>연결 성공!</strong><br>
                    {message}
                </div>
                """
            else:
                return f"""
                <div style="
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                    padding: 12px;
                    border-radius: 6px;
                    margin: 10px 0;
                ">
                    ❌ <strong>연결 실패</strong><br>
                    {message}
                </div>
                """
        except Exception as e:
            return f"""
            <div style="
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 12px;
                border-radius: 6px;
                margin: 10px 0;
            ">
                ⚠️ <strong>테스트 오류</strong><br>
                {str(e)}
            </div>
            """
    
    @staticmethod
    def clear_ai_memory() -> str:
        """AI 대화 기록 초기화"""
        try:
            ai_chat_service.clear_conversation()
            return """
            <div style="
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 12px;
                border-radius: 6px;
                margin: 10px 0;
            ">
                🗑️ <strong>초기화 완료</strong><br>
                AI 대화 기록이 모두 삭제되었습니다.
            </div>
            """
        except Exception as e:
            return f"""
            <div style="
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 12px;
                border-radius: 6px;
                margin: 10px 0;
            ">
                ❌ <strong>초기화 실패</strong><br>
                {str(e)}
            </div>
            """


class ConversationAnalytics:
    """대화 분석 패널"""
    
    @staticmethod
    def create_analytics_panel() -> gr.HTML:
        """대화 분석 패널 생성"""
        return gr.HTML(
            ConversationAnalytics._generate_analytics_html(),
            elem_id="conversation-analytics"
        )
    
    @staticmethod
    def _generate_analytics_html() -> str:
        """대화 분석 HTML 생성"""
        # 대화 기록 분석
        conversation_count = getattr(ai_chat_service, 'conversation_count', 0)
        
        # 간단한 통계 (실제로는 데이터베이스에서 조회)
        stats = {
            "총 대화": conversation_count,
            "AI 응답": conversation_count,
            "데모 응답": 0,  # 실제로는 계산 필요
            "평균 응답 시간": "2.3초"  # 실제로는 측정 필요
        }
        
        return f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">📈 대화 분석</h3>
            
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            ">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['총 대화']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">총 대화</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['AI 응답']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">AI 응답</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['데모 응답']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">데모 응답</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold;">{stats['평균 응답 시간']}</div>
                    <div style="font-size: 12px; opacity: 0.8;">평균 응답 시간</div>
                </div>
            </div>
            
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 10px;
                border-radius: 6px;
                font-size: 12px;
            ">
                💡 <strong>팁:</strong> Week 3에서 데이터베이스 연동 후 더 상세한 분석 정보를 제공할 예정입니다.
            </div>
        </div>
        """
    
    @staticmethod
    def refresh_analytics() -> str:
        """분석 데이터 새로고침"""
        return ConversationAnalytics._generate_analytics_html()


# 전역 인스턴스들
ai_status_panel = AIStatusPanel()
ai_settings_panel = AISettingsPanel()
conversation_analytics = ConversationAnalytics()
