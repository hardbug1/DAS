"""
Gradio UI 레이아웃 정의

와이어프레임을 기반으로 한 UI 레이아웃 구성
"""

import gradio as gr
from typing import Tuple, Dict, Any
from app.config.settings import settings
from app.ui.components import create_header


def create_main_layout() -> Tuple[gr.Blocks, Dict[str, Any]]:
    """
    메인 레이아웃 생성
    
    와이어프레임 기반의 실제 UI 구현:
    - 헤더 (브랜딩)
    - 채팅 영역 (중앙 상단)
    - 입력 영역 (중앙 하단) 
    - 파일 업로드 (좌측 하단)
    - 설정 패널 (우측 하단)
    """
    
    # 커스텀 CSS (와이어프레임 기반)
    custom_css = """
    /* 전체 컨테이너 */
    .gradio-container {
        max-width: 1200px !important;
        margin: 0 auto;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* 헤더 스타일링 */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 채팅 영역 */
    .chat-container {
        border: 2px solid #e3f2fd;
        border-radius: 12px;
        background: #fafafa;
        margin-bottom: 15px;
    }
    
    .gr-chatbot {
        border: none !important;
        background: white !important;
        border-radius: 8px !important;
    }
    
    /* 입력 영역 */
    .input-container {
        background: white;
        padding: 15px;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .gr-textbox {
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
    
    .gr-textbox:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* 버튼 스타일링 */
    .gr-button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
    }
    
    .gr-button-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    .gr-button-secondary {
        background: #f8f9fa !important;
        border: 2px solid #e0e0e0 !important;
        color: #495057 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    .gr-button-secondary:hover {
        background: #e9ecef !important;
        border-color: #ced4da !important;
    }
    
    /* 사이드바 패널 */
    .sidebar-panel {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 0;
        margin-bottom: 15px;
    }
    
    .panel-header {
        background: #f8f9fa;
        padding: 15px;
        border-bottom: 1px solid #e0e0e0;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        color: #495057;
    }
    
    .panel-content {
        padding: 15px;
    }
    
    /* 파일 업로드 영역 */
    .upload-area {
        border: 2px dashed #FF9800;
        border-radius: 12px;
        background: #fff8e1;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #F57C00;
        background: #fff3e0;
    }
    
    .upload-area.dragover {
        border-color: #E65100;
        background: #ffecb3;
        transform: scale(1.02);
    }
    
    /* 설정 패널 */
    .settings-panel {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
    }
    
    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .setting-item:last-child {
        border-bottom: none;
    }
    
    /* 상태 표시 */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background: #28a745;
        box-shadow: 0 0 8px rgba(40, 167, 69, 0.4);
    }
    
    .status-disconnected {
        background: #dc3545;
        box-shadow: 0 0 8px rgba(220, 53, 69, 0.4);
    }
    
    .status-warning {
        background: #ffc107;
        box-shadow: 0 0 8px rgba(255, 193, 7, 0.4);
    }
    
    /* 반응형 디자인 */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 10px;
        }
        
        .gr-row {
            flex-direction: column !important;
        }
        
        .sidebar-panel {
            margin-top: 20px;
        }
    }
    """
    
    components = {}
    
    with gr.Blocks(
        title=settings.app_name,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple", 
            neutral_hue="gray",
            font=gr.themes.GoogleFont("Inter")
        ),
        css=custom_css
    ) as app:
        
        # 헤더
        components['header'] = create_header()
        
        # 메인 컨텐츠 영역
        with gr.Row(elem_classes="main-content"):
            # 왼쪽: 채팅 영역 (2/3)
            with gr.Column(scale=2, elem_classes="chat-column"):
                components.update(_create_chat_section())
                components.update(_create_input_section())
            
            # 오른쪽: 사이드바 (1/3) 
            with gr.Column(scale=1, elem_classes="sidebar-column"):
                components.update(_create_file_upload_section())
                components.update(_create_settings_section())
        
        # 푸터
        components['footer'] = _create_footer()
    
    return app, components


def _create_chat_section() -> Dict[str, Any]:
    """채팅 섹션 생성"""
    components = {}
    
    with gr.Group(elem_classes="chat-container"):
        gr.HTML("""
        <div class="panel-header">
            💬 AI 데이터 분석 대화
        </div>
        """)
        
        components['chatbot'] = gr.Chatbot(
            label="",
            height=450,
            placeholder="AI와 대화를 시작해보세요! 곧 실제 분석 기능이 추가됩니다.",
            show_label=False,
            container=False,
            elem_classes="main-chatbot",
            bubble_full_width=False,
            show_copy_button=True
        )
    
    return components


def _create_input_section() -> Dict[str, Any]:
    """입력 섹션 생성"""
    components = {}
    
    with gr.Group(elem_classes="input-container"):
        with gr.Row():
            components['message_input'] = gr.Textbox(
                label="",
                placeholder="자연어로 질문해보세요. 예: '지난 달 매출 현황을 보여주세요'",
                lines=2,
                max_lines=5,
                show_label=False,
                container=False,
                scale=4,
                elem_classes="message-input"
            )
            
            with gr.Column(scale=1, min_width=120):
                components['send_button'] = gr.Button(
                    "💬 전송",
                    variant="primary",
                    scale=1,
                    elem_classes="send-button"
                )
                components['clear_button'] = gr.Button(
                    "🗑️ 초기화", 
                    variant="secondary",
                    scale=1,
                    elem_classes="clear-button"
                )
        
        # 빠른 예시 질문들
        gr.HTML("""
        <div style="margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 8px;">
            <strong>💡 예시 질문:</strong>
            <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 8px;">
                <span style="background: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; border: 1px solid #e0e0e0; cursor: pointer;" onclick="document.querySelector('.message-input textarea').value='지난 달 매출 현황은?'">
                    지난 달 매출 현황은?
                </span>
                <span style="background: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; border: 1px solid #e0e0e0; cursor: pointer;" onclick="document.querySelector('.message-input textarea').value='제품별 판매량을 분석해줘'">
                    제품별 판매량을 분석해줘
                </span>
                <span style="background: white; padding: 4px 12px; border-radius: 15px; font-size: 12px; border: 1px solid #e0e0e0; cursor: pointer;" onclick="document.querySelector('.message-input textarea').value='고객 연령대별 구매 패턴은?'">
                    고객 연령대별 구매 패턴은?
                </span>
            </div>
        </div>
        """)
    
    return components


def _create_file_upload_section() -> Dict[str, Any]:
    """파일 업로드 섹션 생성"""
    components = {}
    
    with gr.Group(elem_classes="sidebar-panel"):
        gr.HTML("""
        <div class="panel-header">
            📁 파일 업로드
        </div>
        """)
        
        with gr.Group(elem_classes="panel-content"):
            components['file_upload'] = gr.File(
                label="",
                file_types=[".xlsx", ".xls", ".csv"],
                file_count="multiple",
                show_label=False,
                container=False,
                elem_classes="file-upload"
            )
            
            gr.HTML("""
            <div class="upload-area">
                <div style="font-size: 2em; margin-bottom: 10px;">📂</div>
                <div style="font-weight: 600; margin-bottom: 5px;">
                    파일을 드래그하거나 클릭하여 업로드
                </div>
                <div style="font-size: 12px; color: #666;">
                    Excel (.xlsx, .xls), CSV 파일 지원<br>
                    최대 100MB
                </div>
            </div>
            """)
            
            # 업로드된 파일 목록 표시 영역
            components['uploaded_files_display'] = gr.HTML("""
            <div id="uploaded-files" style="margin-top: 15px;">
                <div style="font-size: 14px; font-weight: 600; margin-bottom: 10px;">업로드된 파일:</div>
                <div style="font-size: 12px; color: #666; font-style: italic;">
                    아직 업로드된 파일이 없습니다.
                </div>
            </div>
            """)
    
    return components


def _create_settings_section() -> Dict[str, Any]:
    """설정 섹션 생성"""
    components = {}
    
    with gr.Group(elem_classes="sidebar-panel"):
        gr.HTML("""
        <div class="panel-header">
            ⚙️ 설정
        </div>
        """)
        
        with gr.Group(elem_classes="panel-content"):
            # 데이터베이스 연결 설정
            with gr.Accordion("🗄️ 데이터베이스 연결", open=False):
                components['db_type'] = gr.Dropdown(
                    choices=["PostgreSQL", "MySQL", "SQLite"],
                    value="PostgreSQL",
                    label="데이터베이스 타입",
                    interactive=True
                )
                
                components['db_host'] = gr.Textbox(
                    label="호스트",
                    placeholder="localhost",
                    value="localhost"
                )
                
                components['db_port'] = gr.Number(
                    label="포트",
                    value=5432,
                    precision=0
                )
                
                components['db_name'] = gr.Textbox(
                    label="데이터베이스명",
                    placeholder="database_name"
                )
                
                components['db_test_button'] = gr.Button(
                    "🔌 연결 테스트",
                    variant="secondary",
                    size="sm"
                )
            
            # 애플리케이션 설정
            with gr.Accordion("🎨 애플리케이션 설정", open=True):
                components['language_select'] = gr.Dropdown(
                    choices=["한국어", "English"],
                    value="한국어",
                    label="언어 설정"
                )
                
                components['theme_select'] = gr.Dropdown(
                    choices=["라이트", "다크", "자동"],
                    value="라이트", 
                    label="테마 설정"
                )
                
                components['chart_default'] = gr.Dropdown(
                    choices=["자동 선택", "막대 차트", "선 차트", "파이 차트"],
                    value="자동 선택",
                    label="기본 차트 타입"
                )
            
            # 시스템 상태
            components['system_status'] = gr.HTML("""
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <div style="font-weight: 600; margin-bottom: 10px;">🔌 시스템 상태</div>
                <div style="font-size: 13px; line-height: 1.6;">
                    <div>
                        <span class="status-indicator status-connected"></span>
                        <strong>웹 서버:</strong> 정상 동작
                    </div>
                    <div>
                        <span class="status-indicator status-connected"></span>
                        <strong>데이터베이스:</strong> 연결됨
                    </div>
                    <div>
                        <span class="status-indicator status-warning"></span>
                        <strong>AI 엔진:</strong> 준비 중 (Week 2)
                    </div>
                    <div>
                        <span class="status-indicator status-connected"></span>
                        <strong>캐시:</strong> 활성화
                    </div>
                </div>
            </div>
            """)
    
    return components


def _create_footer() -> gr.HTML:
    """푸터 생성"""
    return gr.HTML(f"""
    <div style="
        text-align: center; 
        padding: 25px; 
        margin-top: 40px; 
        border-top: 2px solid #e0e0e0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        color: #495057;
    ">
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
            <div style="font-size: 1.2em; font-weight: 600;">
                🤖 <strong>{settings.app_name}</strong>
            </div>
            <div style="margin: 0 15px; font-size: 1.2em; color: #ced4da;">|</div>
            <div style="font-size: 0.9em;">
                v{settings.app_version}
            </div>
        </div>
        <div style="font-size: 0.85em; color: #6c757d; margin-bottom: 8px;">
            <strong>Week 1:</strong> UI 기본 구성 완료 | 
            <strong>다음:</strong> Week 2 AI 연동 예정
        </div>
        <div style="font-size: 0.9em; font-style: italic; color: #495057;">
            <em>"데이터의 힘을 모든 사람에게"</em> 🌟
        </div>
    </div>
    """)
