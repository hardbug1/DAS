"""
고급 UI 인터랙션 기능

사용자 경험을 향상시키는 인터랙티브 요소들을 구현합니다.
"""

import gradio as gr
import json
from typing import Dict, List, Any, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger()


class NotificationManager:
    """알림 관리 시스템"""
    
    def __init__(self):
        self.notifications = []
    
    def show_success(self, message: str) -> str:
        """성공 알림 표시"""
        notification = {
            'type': 'success',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return self._generate_notification_html(notification)
    
    def show_error(self, message: str) -> str:
        """오류 알림 표시"""
        notification = {
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return self._generate_notification_html(notification)
    
    def show_info(self, message: str) -> str:
        """정보 알림 표시"""
        notification = {
            'type': 'info',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.notifications.append(notification)
        return self._generate_notification_html(notification)
    
    def _generate_notification_html(self, notification: Dict) -> str:
        """알림 HTML 생성"""
        type_styles = {
            'success': {'bg': '#d4edda', 'border': '#c3e6cb', 'color': '#155724', 'icon': '✅'},
            'error': {'bg': '#f8d7da', 'border': '#f5c6cb', 'color': '#721c24', 'icon': '❌'},
            'info': {'bg': '#d1ecf1', 'border': '#bee5eb', 'color': '#0c5460', 'icon': '💡'}
        }
        
        style = type_styles.get(notification['type'], type_styles['info'])
        
        return f"""
        <div style="
            background: {style['bg']};
            border: 1px solid {style['border']};
            color: {style['color']};
            padding: 12px 16px;
            border-radius: 8px;
            margin: 10px 0;
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease-out;
        ">
            <span style="margin-right: 10px; font-size: 16px;">{style['icon']}</span>
            <span style="flex: 1;">{notification['message']}</span>
            <button onclick="this.parentElement.style.display='none'" style="
                background: none;
                border: none;
                color: {style['color']};
                cursor: pointer;
                font-size: 16px;
                padding: 0;
                margin-left: 10px;
            ">×</button>
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        </style>
        """


class ProgressTracker:
    """진행률 추적 시스템"""
    
    def __init__(self):
        self.current_step = 0
        self.total_steps = 0
        self.step_descriptions = []
    
    def start_progress(self, steps: List[str]) -> str:
        """진행률 추적 시작"""
        self.current_step = 0
        self.total_steps = len(steps)
        self.step_descriptions = steps
        
        return self._generate_progress_html()
    
    def update_progress(self, step: int, message: str = "") -> str:
        """진행률 업데이트"""
        self.current_step = min(step, self.total_steps)
        
        if message:
            logger.info("진행률 업데이트", step=step, total=self.total_steps, message=message)
        
        return self._generate_progress_html()
    
    def _generate_progress_html(self) -> str:
        """진행률 HTML 생성"""
        if self.total_steps == 0:
            return ""
        
        progress_percent = (self.current_step / self.total_steps) * 100
        
        html = f"""
        <div style="
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h4 style="margin: 0; color: #495057;">🔄 처리 진행률</h4>
                <span style="font-weight: 600; color: #667eea;">{self.current_step}/{self.total_steps}</span>
            </div>
            
            <div style="
                background: #e9ecef;
                border-radius: 10px;
                height: 12px;
                overflow: hidden;
                margin-bottom: 15px;
            ">
                <div style="
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    height: 100%;
                    width: {progress_percent}%;
                    transition: width 0.3s ease;
                    border-radius: 10px;
                "></div>
            </div>
            
            <div style="display: grid; gap: 8px;">
        """
        
        for i, step_desc in enumerate(self.step_descriptions):
            status_icon = "✅" if i < self.current_step else "⏳" if i == self.current_step else "⚪"
            text_color = "#28a745" if i < self.current_step else "#667eea" if i == self.current_step else "#6c757d"
            
            html += f"""
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 8px;
                    background: {'#f8f9fa' if i == self.current_step else 'transparent'};
                    border-radius: 6px;
                    color: {text_color};
                ">
                    <span style="margin-right: 10px;">{status_icon}</span>
                    <span style="font-size: 14px;">
                        <strong>Step {i+1}:</strong> {step_desc}
                    </span>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html


class QuickActions:
    """빠른 액션 버튼들"""
    
    @staticmethod
    def create_example_buttons() -> gr.HTML:
        """예시 질문 버튼들 생성"""
        examples = [
            "지난 달 매출 현황은?",
            "제품별 판매량을 분석해줘",
            "고객 연령대별 구매 패턴은?",
            "월별 매출 트렌드를 차트로 보여줘",
            "가장 많이 팔린 제품 TOP 10은?",
            "지역별 매출 분포를 분석해줘"
        ]
        
        buttons_html = """
        <div style="
            background: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <div style="font-weight: 600; margin-bottom: 12px; color: #495057;">
                💡 빠른 예시 질문
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 8px;">
        """
        
        for example in examples:
            buttons_html += f"""
                <button onclick="
                    document.querySelector('.message-input textarea').value = '{example}';
                    document.querySelector('.message-input textarea').focus();
                " style="
                    background: white;
                    border: 1px solid #e0e0e0;
                    padding: 10px 15px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 13px;
                    transition: all 0.2s ease;
                    text-align: left;
                " onmouseover="
                    this.style.background='#e3f2fd';
                    this.style.borderColor='#2196F3';
                    this.style.transform='translateY(-1px)';
                " onmouseout="
                    this.style.background='white';
                    this.style.borderColor='#e0e0e0';
                    this.style.transform='translateY(0)';
                ">
                    {example}
                </button>
            """
        
        buttons_html += """
            </div>
        </div>
        """
        
        return gr.HTML(buttons_html)
    
    @staticmethod
    def create_file_templates() -> gr.HTML:
        """파일 템플릿 다운로드 버튼들"""
        templates = [
            {"name": "매출 데이터 템플릿", "desc": "월별/제품별 매출 분석용", "file": "sales_template.xlsx"},
            {"name": "고객 데이터 템플릿", "desc": "고객 정보 및 구매 이력", "file": "customer_template.xlsx"},
            {"name": "재고 데이터 템플릿", "desc": "상품 재고 현황 분석용", "file": "inventory_template.xlsx"}
        ]
        
        html = """
        <div style="
            background: #fff3e0;
            border: 1px solid #ffcc02;
            border-radius: 12px;
            padding: 15px;
            margin: 15px 0;
        ">
            <div style="font-weight: 600; margin-bottom: 12px; color: #e65100;">
                📋 Excel 템플릿 다운로드
            </div>
            <div style="font-size: 12px; color: #bf360c; margin-bottom: 15px;">
                아래 템플릿을 다운로드하여 데이터를 입력한 후 업로드하세요.
            </div>
        """
        
        for template in templates:
            html += f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px;
                    background: white;
                    border-radius: 8px;
                    margin: 8px 0;
                ">
                    <div>
                        <div style="font-weight: 600; font-size: 13px;">{template['name']}</div>
                        <div style="font-size: 11px; color: #666;">{template['desc']}</div>
                    </div>
                    <button onclick="alert('Week 4에서 실제 다운로드 기능이 구현됩니다!')" style="
                        background: #ff9800;
                        color: white;
                        border: none;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 11px;
                        cursor: pointer;
                    ">다운로드</button>
                </div>
            """
        
        html += "</div>"
        return gr.HTML(html)


class AnimationEffects:
    """애니메이션 효과들"""
    
    @staticmethod
    def typing_indicator() -> str:
        """타이핑 표시 애니메이션"""
        return """
        <div style="
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 20px;
            margin: 10px 0;
            max-width: 100px;
        ">
            <span style="margin-right: 8px;">🤖</span>
            <div style="display: flex; gap: 3px;">
                <div style="
                    width: 6px;
                    height: 6px;
                    background: #667eea;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out both;
                "></div>
                <div style="
                    width: 6px;
                    height: 6px;
                    background: #667eea;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out both;
                    animation-delay: 0.2s;
                "></div>
                <div style="
                    width: 6px;
                    height: 6px;
                    background: #667eea;
                    border-radius: 50%;
                    animation: typing 1.4s infinite ease-in-out both;
                    animation-delay: 0.4s;
                "></div>
            </div>
        </div>
        <style>
        @keyframes typing {
            0%, 80%, 100% { 
                transform: scale(0);
                opacity: 0.5;
            }
            40% { 
                transform: scale(1);
                opacity: 1;
            }
        }
        </style>
        """
    
    @staticmethod
    def pulse_effect(element_id: str) -> str:
        """펄스 효과 CSS"""
        return f"""
        <style>
        #{element_id} {{
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        </style>
        """


class KeyboardShortcuts:
    """키보드 단축키 시스템"""
    
    @staticmethod
    def create_shortcuts_guide() -> gr.HTML:
        """단축키 가이드 생성"""
        shortcuts = [
            {"key": "Ctrl + Enter", "action": "메시지 전송"},
            {"key": "Ctrl + L", "action": "대화 초기화"},
            {"key": "Ctrl + U", "action": "파일 업로드"},
            {"key": "Ctrl + /", "action": "단축키 도움말"},
            {"key": "Esc", "action": "포커스 해제"}
        ]
        
        html = """
        <div style="
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            z-index: 1000;
            min-width: 250px;
            display: none;
        " id="shortcuts-guide">
            <div style="font-weight: 600; margin-bottom: 12px; color: #495057;">
                ⌨️ 키보드 단축키
            </div>
        """
        
        for shortcut in shortcuts:
            html += f"""
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 6px 0;
                    border-bottom: 1px solid #f0f0f0;
                ">
                    <span style="
                        background: #f8f9fa;
                        padding: 2px 8px;
                        border-radius: 4px;
                        font-family: monospace;
                        font-size: 12px;
                        font-weight: 600;
                    ">{shortcut['key']}</span>
                    <span style="font-size: 13px; color: #666;">{shortcut['action']}</span>
                </div>
            """
        
        html += """
        </div>
        
        <script>
        document.addEventListener('keydown', function(e) {
            // Ctrl + / : 단축키 가이드 토글
            if (e.ctrlKey && e.key === '/') {
                e.preventDefault();
                const guide = document.getElementById('shortcuts-guide');
                guide.style.display = guide.style.display === 'none' ? 'block' : 'none';
            }
            
            // Ctrl + L : 대화 초기화
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                const clearBtn = document.querySelector('.clear-button button');
                if (clearBtn) clearBtn.click();
            }
            
            // Esc : 단축키 가이드 숨기기
            if (e.key === 'Escape') {
                document.getElementById('shortcuts-guide').style.display = 'none';
            }
        });
        </script>
        """
        
        return gr.HTML(html)


# 전역 인스턴스들
notification_manager = NotificationManager()
progress_tracker = ProgressTracker()
quick_actions = QuickActions()
animation_effects = AnimationEffects()
keyboard_shortcuts = KeyboardShortcuts()
