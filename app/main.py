"""
AI 데이터 분석 비서 - 메인 애플리케이션

Gradio 기반 웹 애플리케이션의 엔트리포인트입니다.
"""

import gradio as gr
import structlog
from app.config.settings import settings

# 로깅 설정
logger = structlog.get_logger()


def create_app() -> gr.Blocks:
    """Gradio 애플리케이션 생성"""
    
    with gr.Blocks(
        title=settings.app_name,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as app:
        
        # 헤더
        gr.HTML(f"""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: white; margin: 0; font-size: 2em;">🤖 {settings.app_name}</h1>
            <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">자연어로 묻고, AI가 분석하고, 시각화로 답하다</p>
        </div>
        """)
        
        # 메인 인터페이스 (임시 - Week 1에서 구현 예정)
        gr.Markdown("## 🚧 개발 중...")
        gr.Markdown("Week 1에서 채팅 인터페이스가 구현될 예정입니다.")
        
        # 기본 채팅 인터페이스 (플레이스홀더)
        chatbot = gr.Chatbot(
            label="AI 데이터 분석 비서",
            height=400,
            placeholder="곧 여기서 AI와 대화할 수 있습니다!"
        )
        
        msg = gr.Textbox(
            label="질문을 입력하세요",
            placeholder="예: 지난 달 매출 현황을 보여주세요",
            lines=2
        )
        
        send_btn = gr.Button("전송", variant="primary")
        
        # 임시 응답 함수
        def respond(message, history):
            """임시 응답 함수 (Week 2에서 AI 연동 예정)"""
            if message:
                history = history or []
                history.append((message, "안녕하세요! 현재 개발 중입니다. Week 2에서 AI 기능이 추가될 예정입니다. 🚀"))
                return history, ""
            return history, message
        
        send_btn.click(respond, [msg, chatbot], [chatbot, msg])
        msg.submit(respond, [msg, chatbot], [chatbot, msg])
        
        # 상태 정보
        gr.Markdown(f"""
        ### 📊 시스템 정보
        - **버전**: {settings.app_version}
        - **환경**: {'개발' if settings.debug else '프로덕션'}
        - **포트**: {settings.gradio_server_port}
        """)
    
    return app


def main():
    """메인 실행 함수"""
    logger.info(
        "애플리케이션 시작",
        app_name=settings.app_name,
        version=settings.app_version,
        port=settings.gradio_server_port
    )
    
    app = create_app()
    
    app.launch(
        server_name=settings.gradio_server_name,
        server_port=settings.gradio_server_port,
        share=settings.gradio_share,
        debug=settings.debug
    )


if __name__ == "__main__":
    main()
