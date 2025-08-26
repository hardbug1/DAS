"""
AI 데이터 분석 비서 - 메인 애플리케이션

Gradio 기반 웹 애플리케이션의 엔트리포인트입니다.
"""

import gradio as gr
import structlog
from app.config.settings import settings
from app.config.logging import setup_logging
from app.config.database import test_database_connection, create_tables
from app.ui.components import (
    create_header, create_status_panel, create_progress_panel,
    create_feature_preview, create_demo_chatbot, create_demo_response
)

# 로깅 설정
setup_logging()
logger = structlog.get_logger()


def initialize_app():
    """애플리케이션 초기화"""
    logger.info("애플리케이션 초기화 시작")
    
    try:
        # 데이터베이스 연결 테스트
        if test_database_connection():
            logger.info("데이터베이스 연결 성공")
            # 테이블 생성 (없는 경우에만)
            create_tables()
        else:
            logger.warning("데이터베이스 연결 실패 - SQLite 사용")
            
    except Exception as e:
        logger.error("초기화 중 오류 발생", error=str(e))


def create_app() -> gr.Blocks:
    """Gradio 애플리케이션 생성"""
    
    # 커스텀 CSS
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto;
    }
    
    .gr-button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }
    
    .gr-button-primary:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    .gr-textbox {
        border-radius: 8px !important;
    }
    
    .gr-panel {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
    }
    """
    
    with gr.Blocks(
        title=settings.app_name,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="gray"
        ),
        css=custom_css
    ) as app:
        
        # 헤더
        create_header()
        
        # 메인 컨텐츠
        with gr.Row():
            with gr.Column(scale=2):
                # 채팅 인터페이스
                chatbot, msg = create_demo_chatbot()
                
                with gr.Row():
                    send_btn = gr.Button("💬 전송", variant="primary", scale=1)
                    clear_btn = gr.Button("🗑️ 대화 초기화", variant="secondary", scale=1)
                
                # 이벤트 핸들러
                def clear_chat():
                    return [], ""
                
                send_btn.click(create_demo_response, [msg, chatbot], [chatbot, msg])
                msg.submit(create_demo_response, [msg, chatbot], [chatbot, msg])
                clear_btn.click(clear_chat, outputs=[chatbot, msg])
                
            with gr.Column(scale=1):
                # 상태 및 정보 패널
                create_status_panel()
                create_progress_panel()
        
        # 기능 미리보기
        create_feature_preview()
        
        # 개발 정보
        with gr.Accordion("🛠️ 개발자 정보", open=False):
            gr.Markdown(f"""
            ### 📋 개발 환경 정보
            
            **애플리케이션**
            - 이름: {settings.app_name}
            - 버전: {settings.app_version}
            - 환경: {'개발 모드' if settings.debug else '프로덕션 모드'}
            - 포트: {settings.gradio_server_port}
            
            **기술 스택**
            - Frontend: Gradio 4.0+
            - Backend: Python 3.11+
            - Database: PostgreSQL/SQLite
            - AI: LangChain + OpenAI GPT-4
            
            **개발 진행률**
            - Week 0: 개발 환경 구축 (90% 완료)
            - Week 1: UI 구현 (예정)
            - Week 2: AI 연동 (예정)
            
            **문서**
            - [📋 PRD](./PRD_LLM_Data_Analysis_Service.md)
            - [🏗️ 설계 문서](./System_Design_Document.md)
            - [✅ 개발 체크리스트](./Development_Checklist.md)
            """)
        
        # 푸터
        gr.HTML("""
        <div style="
            text-align: center; 
            padding: 20px; 
            margin-top: 30px; 
            border-top: 1px solid #e0e0e0;
            color: #6c757d;
            font-size: 0.9em;
        ">
            <p style="margin: 0;">
                🤖 <strong>AI 데이터 분석 비서</strong> | 
                개발 중 | 
                <em>"데이터의 힘을 모든 사람에게"</em> 🌟
            </p>
        </div>
        """)
    
    return app


def main():
    """메인 실행 함수"""
    logger.info(
        "🚀 AI 데이터 분석 비서 시작",
        app_name=settings.app_name,
        version=settings.app_version,
        port=settings.gradio_server_port,
        debug=settings.debug
    )
    
    # 애플리케이션 초기화
    initialize_app()
    
    # Gradio 앱 생성 및 실행
    app = create_app()
    
    logger.info(
        "Gradio 서버 시작",
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        share=settings.gradio_share
    )
    
    app.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        share=settings.gradio_share,
        debug=settings.debug,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()
