"""
Gradio UI 컴포넌트들

재사용 가능한 UI 컴포넌트들을 정의합니다.
"""

import gradio as gr
from app.config.settings import settings


def create_header() -> gr.HTML:
    """헤더 컴포넌트 생성"""
    return gr.HTML(f"""
    <div style="
        text-align: center; 
        padding: 20px; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        border-radius: 10px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.2em; 
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        ">🤖 {settings.app_name}</h1>
        <p style="
            color: white; 
            margin: 10px 0 0 0; 
            opacity: 0.9; 
            font-size: 1.1em;
        ">자연어로 묻고, AI가 분석하고, 시각화로 답하다</p>
        <div style="
            margin-top: 15px; 
            font-size: 0.9em; 
            opacity: 0.8;
        ">
            <span style="
                background: rgba(255,255,255,0.2); 
                padding: 4px 12px; 
                border-radius: 15px; 
                margin: 0 5px;
            ">v{settings.app_version}</span>
            <span style="
                background: rgba(255,255,255,0.2); 
                padding: 4px 12px; 
                border-radius: 15px; 
                margin: 0 5px;
            ">{'개발 모드' if settings.debug else '프로덕션'}</span>
        </div>
    </div>
    """)


def create_status_panel() -> gr.HTML:
    """상태 패널 컴포넌트 생성"""
    return gr.HTML(f"""
    <div style="
        background: #f8f9fa; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 4px solid #28a745;
        margin: 10px 0;
    ">
        <h4 style="margin: 0 0 10px 0; color: #495057;">📊 시스템 상태</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
            <div>
                <strong>🚀 서버 상태:</strong> 
                <span style="color: #28a745;">● 정상 동작</span>
            </div>
            <div>
                <strong>🗄️ 데이터베이스:</strong> 
                <span style="color: #28a745;">● 연결됨</span>
            </div>
            <div>
                <strong>🤖 AI 엔진:</strong> 
                <span style="color: #ffc107;">● 준비 중</span>
            </div>
            <div>
                <strong>📈 캐시:</strong> 
                <span style="color: #28a745;">● 활성화</span>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 0.9em; color: #6c757d;">
            <strong>포트:</strong> {settings.gradio_server_port} | 
            <strong>업데이트:</strong> 실시간 | 
            <strong>다음 단계:</strong> Week 1 - UI 구현
        </div>
    </div>
    """)


def create_progress_panel() -> gr.HTML:
    """개발 진행률 패널"""
    return gr.HTML("""
    <div style="
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
        padding: 20px; 
        border-radius: 10px; 
        margin: 15px 0;
        border: 1px solid #e0e0e0;
    ">
        <h4 style="margin: 0 0 15px 0; color: #1976d2;">🎯 개발 진행 상황</h4>
        
        <div style="margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span><strong>Week 0: 개발 환경 구축</strong></span>
                <span style="color: #28a745;"><strong>90% 완료</strong></span>
            </div>
            <div style="background: #e9ecef; border-radius: 10px; height: 8px;">
                <div style="background: linear-gradient(90deg, #28a745, #20c997); width: 90%; height: 100%; border-radius: 10px;"></div>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9em;">
            <div>✅ 프로젝트 구조</div>
            <div>✅ 설정 파일</div>
            <div>✅ 데이터베이스</div>
            <div>🚧 기본 UI</div>
        </div>
        
        <div style="margin-top: 15px; padding: 10px; background: rgba(255,255,255,0.7); border-radius: 5px;">
            <strong>🎯 다음 목표:</strong> Week 1에서 채팅 인터페이스 구현 예정
        </div>
    </div>
    """)


def create_feature_preview() -> gr.HTML:
    """기능 미리보기 패널"""
    return gr.HTML("""
    <div style="
        background: #fff; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0;
        margin: 15px 0;
    ">
        <h4 style="margin: 0 0 15px 0; color: #495057;">🚀 구현 예정 기능</h4>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">
                <h5 style="margin: 0 0 8px 0; color: #007bff;">💬 자연어 질의</h5>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    "지난 달 매출 현황은?" 같은 자연어 질문으로 데이터 분석
                </p>
            </div>
            
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;">
                <h5 style="margin: 0 0 8px 0; color: #28a745;">📊 자동 시각화</h5>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    데이터 특성에 맞는 차트를 자동으로 생성하고 표시
                </p>
            </div>
            
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h5 style="margin: 0 0 8px 0; color: #ffc107;">📁 파일 분석</h5>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    Excel, CSV 파일을 업로드하여 즉시 분석 가능
                </p>
            </div>
            
            <div style="padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #dc3545;">
                <h5 style="margin: 0 0 8px 0; color: #dc3545;">🗄️ DB 연동</h5>
                <p style="margin: 0; font-size: 0.9em; color: #6c757d;">
                    PostgreSQL, MySQL 등 다양한 데이터베이스 연결
                </p>
            </div>
        </div>
    </div>
    """)


def create_demo_chatbot() -> tuple:
    """데모용 채팅봇 컴포넌트"""
    
    chatbot = gr.Chatbot(
        label="🤖 AI 데이터 분석 비서 (데모)",
        height=400,
        placeholder="Week 2에서 실제 AI 기능이 구현됩니다!",
        show_label=True,
        container=True,
        scale=1
    )
    
    msg = gr.Textbox(
        label="질문을 입력하세요",
        placeholder="예: 지난 달 매출 현황을 보여주세요 (현재는 데모 응답만 제공)",
        lines=2,
        max_lines=5,
        show_label=True,
        container=True
    )
    
    return chatbot, msg


def create_demo_response(message: str, history: list) -> tuple:
    """데모 응답 생성 함수"""
    if not message.strip():
        return history, ""
    
    # 데모 응답 생성
    demo_responses = [
        "안녕하세요! 현재 개발 중인 AI 데이터 분석 비서입니다. 🚀",
        "Week 2에서 실제 AI 기능이 추가될 예정입니다.",
        "곧 자연어로 데이터를 분석할 수 있게 됩니다! 📊",
        "Excel 파일 업로드와 SQL 질의 기능도 구현될 예정입니다.",
        "조금만 기다려주세요. 멋진 기능들이 준비되고 있습니다! ✨"
    ]
    
    import random
    response = random.choice(demo_responses)
    
    history = history or []
    history.append((message, response))
    
    return history, ""
