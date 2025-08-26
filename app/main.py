"""
AI 데이터 분석 비서 - 메인 애플리케이션

Gradio 기반 웹 애플리케이션의 엔트리포인트입니다.
"""

import gradio as gr
import structlog
from app.config.settings import settings
from app.config.logging import setup_logging
from app.config.database import test_database_connection, create_tables
from app.ui.layouts import create_main_layout
from app.ui.handlers import chat_handler, file_handler, settings_handler
from app.ui.ai_status import ai_status_panel, ai_settings_panel
from app.ui.sql_interface import sql_interface
from app.ui.file_interface import file_interface

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
    
    # 새로운 레이아웃 시스템 사용
    app, components = create_main_layout()
    
    # 이벤트 핸들러 연결
    _setup_event_handlers(components)
    
    return app


def _setup_event_handlers(components: dict):
    """이벤트 핸들러 설정"""
    
    # 채팅 관련 이벤트
    if 'send_button' in components and 'message_input' in components and 'chatbot' in components:
        # 전송 버튼 클릭
        components['send_button'].click(
            fn=chat_handler.send_message,
            inputs=[components['message_input'], components['chatbot']],
            outputs=[components['chatbot'], components['message_input']]
        )
        
        # Enter 키로 전송
        components['message_input'].submit(
            fn=chat_handler.send_message,
            inputs=[components['message_input'], components['chatbot']],
            outputs=[components['chatbot'], components['message_input']]
        )
        
        # 대화 초기화
        if 'clear_button' in components:
            components['clear_button'].click(
                fn=chat_handler.clear_chat,
                outputs=[components['chatbot'], components['message_input']]
            )
    
    # 파일 업로드 이벤트
    if 'file_upload' in components and 'uploaded_files_display' in components:
        components['file_upload'].upload(
            fn=file_handler.handle_file_upload,
            inputs=[components['file_upload']],
            outputs=[components['uploaded_files_display']]
        )
    
    # 설정 관련 이벤트
    if 'db_test_button' in components:
        components['db_test_button'].click(
            fn=settings_handler.test_database_connection,
            inputs=[
                components.get('db_type'),
                components.get('db_host'),
                components.get('db_port'),
                components.get('db_name')
            ],
            outputs=[]  # 결과를 알림으로 표시 (추후 구현)
        )
    
    # 설정 변경 이벤트
    if 'language_select' in components:
        components['language_select'].change(
            fn=settings_handler.update_language,
            inputs=[components['language_select']],
            outputs=[]
        )
    
    if 'theme_select' in components:
        components['theme_select'].change(
            fn=settings_handler.update_theme,
            inputs=[components['theme_select']],
            outputs=[]
        )
    
    if 'chart_default' in components:
        components['chart_default'].change(
            fn=settings_handler.update_chart_default,
            inputs=[components['chart_default']],
            outputs=[]
        )
    
    # AI 설정 이벤트
    if 'test_connection_btn' in components and 'test_result' in components:
        components['test_connection_btn'].click(
            fn=ai_settings_panel.test_ai_connection,
            outputs=[components['test_result']]
        )
    
    if 'clear_memory_btn' in components and 'test_result' in components:
        components['clear_memory_btn'].click(
            fn=ai_settings_panel.clear_ai_memory,
            outputs=[components['test_result']]
        )
    
    # SQL 인터페이스 이벤트
    if 'sql_submit_btn' in components:
        components['sql_submit_btn'].click(
            fn=sql_interface.execute_natural_language_query,
            inputs=[components['sql_question']],
            outputs=[
                components['sql_result'],
                components['executed_sql'],
                components['result_dataframe'],
                components['executed_sql'],  # visibility
                components['result_dataframe'],  # visibility
                components['result_chart'],  # chart
                components['result_chart'],  # chart visibility
                components['analysis_insights'],  # insights
                components['analysis_insights']  # insights visibility
            ]
        )
    
    if 'direct_sql_btn' in components:
        components['direct_sql_btn'].click(
            fn=sql_interface.execute_direct_sql,
            inputs=[components['direct_sql']],
            outputs=[
                components['sql_result'],
                components['executed_sql'],
                components['result_dataframe'],
                components['executed_sql'],  # visibility
                components['result_dataframe']  # visibility
            ]
        )
    
    if 'sql_clear_btn' in components:
        components['sql_clear_btn'].click(
            fn=sql_interface.clear_interface,
            outputs=[
                components['sql_question'],
                components['sql_result'],
                components['executed_sql'],
                components['result_dataframe'],
                components['executed_sql'],  # visibility
                components['result_dataframe']  # visibility
            ]
        )
    
    if 'db_connection_btn' in components and 'db_status' in components:
        components['db_connection_btn'].click(
            fn=sql_interface.test_database_connection,
            outputs=[components['db_status']]
        )
    
    # SQL 예시 질문 버튼들
    for i in range(8):  # 8개의 예시 질문
        btn_key = f'example_btn_{i}'
        if btn_key in components:
            def create_example_handler(btn_text):
                def handler():
                    return btn_text
                return handler
            
            components[btn_key].click(
                fn=create_example_handler(components[btn_key].value),
                outputs=[components['sql_question']]
            )
    
    # 파일 업로드 인터페이스 이벤트
    if 'file_upload' in components:
        components['file_upload'].upload(
            fn=file_interface.handle_file_upload,
            inputs=[components['file_upload']],
            outputs=[
                components['upload_status'],
                components['file_list'],
                components['data_preview'],
                components['file_info']
            ]
        )
    
    if 'refresh_files_btn' in components:
        components['refresh_files_btn'].click(
            fn=file_interface.refresh_file_list,
            outputs=[components['file_list']]
        )
    
    if 'clear_files_btn' in components:
        components['clear_files_btn'].click(
            fn=file_interface.clear_all_files,
            outputs=[
                components['upload_status'],
                components['file_list'],
                components['data_preview'],
                components['file_info']
            ]
        )


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
