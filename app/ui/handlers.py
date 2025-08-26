"""
UI 이벤트 핸들러들

Gradio 컴포넌트의 이벤트 처리를 담당합니다.
"""

import gradio as gr
from typing import List, Tuple, Any, Optional
import random
import time
import structlog
from datetime import datetime
from app.ui.interactions import notification_manager, progress_tracker, animation_effects

logger = structlog.get_logger()


class ChatHandler:
    """채팅 인터페이스 이벤트 핸들러"""
    
    def __init__(self):
        self.conversation_history = []
        self.demo_responses = [
            "안녕하세요! 저는 AI 데이터 분석 비서입니다. 🤖",
            "현재 Week 1 단계로, UI 구현을 완료했습니다!",
            "Week 2에서 실제 LangChain과 OpenAI가 연동될 예정입니다.",
            "곧 Excel 파일을 업로드하고 자연어로 분석할 수 있게 됩니다! 📊",
            "SQL 데이터베이스 질의 기능도 구현될 예정입니다.",
            "조금만 기다려주세요. 멋진 분석 기능들이 준비되고 있습니다! ✨",
            "데이터 시각화 차트도 자동으로 생성될 예정입니다! 📈",
            "궁금한 점이 있으시면 언제든 물어보세요!"
        ]
    
    def send_message(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """메시지 전송 처리"""
        if not message.strip():
            return history, ""
        
        # 로깅
        logger.info("사용자 메시지 수신", message=message, timestamp=datetime.now().isoformat())
        
        # 히스토리에 사용자 메시지 먼저 추가
        history = history or []
        history.append((message, None))
        
        # 타이핑 표시 (실제로는 바로 응답이 나타남)
        # time.sleep(0.5)  # 실제 서비스에서는 주석 해제
        
        # 데모 응답 생성
        response = self._generate_demo_response(message)
        
        # 히스토리 업데이트 (AI 응답 추가)
        history[-1] = (message, response)
        
        # 대화 히스토리 저장
        self.conversation_history.append({
            "user_message": message,
            "ai_response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info("AI 응답 생성", response_length=len(response), history_count=len(history))
        
        return history, ""
    
    def clear_chat(self) -> Tuple[List, str]:
        """채팅 초기화"""
        self.conversation_history.clear()
        logger.info("채팅 히스토리 초기화")
        return [], ""
    
    def _generate_demo_response(self, message: str) -> str:
        """데모 응답 생성"""
        message_lower = message.lower()
        
        # 키워드 기반 맞춤 응답
        if any(keyword in message_lower for keyword in ['매출', '판매', '수익', '돈']):
            return "💰 매출 관련 질문이시네요! Week 2에서 실제 데이터베이스에 연결하면 정확한 매출 분석을 해드릴 수 있습니다. 지금은 데모 모드입니다."
        
        elif any(keyword in message_lower for keyword in ['파일', '엑셀', 'excel', 'csv']):
            return "📊 파일 분석 기능이 궁금하시군요! 곧 Excel과 CSV 파일을 업로드하여 즉시 분석할 수 있게 됩니다. 드래그 앤 드롭으로 간편하게 업로드 가능해질 예정입니다!"
        
        elif any(keyword in message_lower for keyword in ['차트', '그래프', '시각화']):
            return "📈 시각화 기능은 Week 5에서 구현될 예정입니다! Plotly를 사용해서 인터랙티브한 차트를 자동으로 생성할 예정입니다. 막대, 선, 파이, 산점도 등 다양한 차트를 지원할 예정이에요."
        
        elif any(keyword in message_lower for keyword in ['데이터베이스', 'db', 'sql']):
            return "🗄️ 데이터베이스 연동은 Week 3에서 구현됩니다! PostgreSQL, MySQL, SQLite를 지원하며, 자연어로 질문하면 자동으로 SQL을 생성해서 조회할 예정입니다."
        
        elif any(keyword in message_lower for keyword in ['안녕', '안녕하세요', 'hello', 'hi']):
            return "안녕하세요! 👋 AI 데이터 분석 비서입니다. 현재 Week 1 단계로 UI 구현을 완료했습니다. 궁금한 점이 있으시면 언제든 물어보세요!"
        
        elif any(keyword in message_lower for keyword in ['도움말', 'help', '사용법']):
            return """
🔧 **현재 사용 가능한 기능:**
- 💬 채팅 인터페이스 (현재 데모 모드)
- 📁 파일 업로드 준비 (UI만 구현됨)
- ⚙️ 설정 패널 (UI만 구현됨)

🚀 **개발 예정 기능:**
- Week 2: LangChain + OpenAI 연동
- Week 3: SQL 데이터베이스 질의
- Week 4: Excel 파일 분석
- Week 5: 자동 시각화

질문해보세요! 개발 진행 상황에 대해 알려드릴게요. 😊
            """
        
        elif any(keyword in message_lower for keyword in ['언제', 'when', '일정']):
            return "📅 개발 일정을 알려드릴게요!\n\n• Week 1 (현재): UI 구현 ✅\n• Week 2: AI 연동 (예정)\n• Week 3: DB 연동 (예정)\n• Week 4: 파일 분석 (예정)\n• Week 5: 시각화 (예정)\n\n총 8주 계획으로 진행되고 있습니다!"
        
        else:
            # 일반적인 응답 중 랜덤 선택
            return random.choice(self.demo_responses)


class FileHandler:
    """파일 업로드 이벤트 핸들러"""
    
    def __init__(self):
        self.uploaded_files = []
    
    def handle_file_upload(self, files: List[Any]) -> str:
        """파일 업로드 처리"""
        if not files:
            return self._generate_files_display()
        
        # 파일 정보 처리 (현재는 데모)
        for file in files:
            if hasattr(file, 'name'):
                file_info = {
                    'name': file.name,
                    'size': getattr(file, 'size', 0),
                    'upload_time': datetime.now().isoformat()
                }
                self.uploaded_files.append(file_info)
                logger.info("파일 업로드 처리", filename=file.name)
        
        return self._generate_files_display()
    
    def _generate_files_display(self) -> str:
        """업로드된 파일 목록 HTML 생성"""
        if not self.uploaded_files:
            return """
            <div id="uploaded-files" style="margin-top: 15px;">
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">업로드된 파일:</div>
                <div style="font-size: 12px; color: #666; font-style: italic;">
                    아직 업로드된 파일이 없습니다.
                </div>
            </div>
            """
        
        files_html = """
        <div id="uploaded-files" style="margin-top: 15px;">
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">업로드된 파일:</div>
        """
        
        for file in self.uploaded_files:
            files_html += f"""
            <div style="
                background: #e8f5e8; 
                padding: 8px 12px; 
                margin: 5px 0; 
                border-radius: 6px; 
                border-left: 4px solid #28a745;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
            ">
                <div>
                    <div style="font-weight: 600;">📊 {file['name']}</div>
                    <div style="color: #666; font-size: 11px;">
                        {self._format_file_size(file.get('size', 0))} • 
                        {self._format_time(file['upload_time'])}
                    </div>
                </div>
                <button style="
                    background: #dc3545; 
                    color: white; 
                    border: none; 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    font-size: 10px;
                    cursor: pointer;
                " onclick="this.parentElement.remove();">삭제</button>
            </div>
            """
        
        files_html += "</div>"
        return files_html
    
    def _format_file_size(self, size: int) -> str:
        """파일 크기 포맷팅"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size // 1024} KB"
        else:
            return f"{size // (1024 * 1024)} MB"
    
    def _format_time(self, timestamp: str) -> str:
        """시간 포맷팅"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%H:%M")
        except:
            return "방금 전"


class SettingsHandler:
    """설정 패널 이벤트 핸들러"""
    
    def __init__(self):
        self.settings = {
            'language': '한국어',
            'theme': '라이트',
            'chart_default': '자동 선택'
        }
    
    def test_database_connection(self, db_type: str, host: str, port: int, db_name: str) -> str:
        """데이터베이스 연결 테스트 (데모)"""
        logger.info("DB 연결 테스트", db_type=db_type, host=host, port=port, db_name=db_name)
        
        # 진행률 추적 시작
        steps = ["연결 설정 확인", "네트워크 테스트", "인증 확인", "데이터베이스 접근 테스트"]
        progress_html = progress_tracker.start_progress(steps)
        
        # 단계별 진행 시뮬레이션
        for i in range(len(steps)):
            time.sleep(0.3)  # 각 단계별 지연
            progress_tracker.update_progress(i + 1, f"{steps[i]} 완료")
        
        if not host or not db_name:
            return notification_manager.show_error("호스트와 데이터베이스명을 입력해주세요.")
        
        # 성공 알림
        success_msg = f"{db_type} ({host}:{port}/{db_name})에 연결되었습니다. (데모 모드)"
        return notification_manager.show_success(success_msg)
    
    def update_language(self, language: str) -> str:
        """언어 설정 업데이트"""
        self.settings['language'] = language
        logger.info("언어 설정 변경", language=language)
        return f"언어가 {language}로 변경되었습니다."
    
    def update_theme(self, theme: str) -> str:
        """테마 설정 업데이트"""
        self.settings['theme'] = theme
        logger.info("테마 설정 변경", theme=theme)
        return f"테마가 {theme} 모드로 변경되었습니다."
    
    def update_chart_default(self, chart_type: str) -> str:
        """기본 차트 설정 업데이트"""
        self.settings['chart_default'] = chart_type
        logger.info("차트 기본값 변경", chart_type=chart_type)
        return f"기본 차트가 {chart_type}로 설정되었습니다."


# 전역 핸들러 인스턴스
chat_handler = ChatHandler()
file_handler = FileHandler()
settings_handler = SettingsHandler()
