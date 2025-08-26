"""
파일 업로드 및 분석 UI 인터페이스

드래그 앤 드롭 파일 업로드, 파일 관리, 데이터 미리보기 등을 제공하는 UI 컴포넌트입니다.
"""

import gradio as gr
import pandas as pd
import structlog
from typing import Dict, List, Any, Tuple, Optional
import asyncio
import json
from datetime import datetime

from app.services.file_upload_service import file_upload_manager, upload_progress_tracker
from app.ui.interactions import notification_manager, progress_tracker
from app.config.settings import settings

logger = structlog.get_logger()


class FileUploadInterface:
    """파일 업로드 인터페이스"""
    
    def __init__(self):
        self.current_session_id = None
        self.uploaded_files = []
        self.current_file_id = None
    
    def create_file_interface(self) -> Dict[str, Any]:
        """파일 업로드 인터페이스 생성"""
        components = {}
        
        with gr.Tab("📁 파일 분석"):
            # 헤더
            gr.HTML("""
            <div style="
                background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
            ">
                <h2 style="margin: 0 0 10px 0;">📁 Excel/CSV 파일 분석</h2>
                <p style="margin: 0; opacity: 0.9;">
                    Excel, CSV 파일을 업로드하여 AI가 자동으로 분석하고 시각화합니다
                </p>
            </div>
            """)
            
            with gr.Row():
                # 왼쪽: 파일 업로드 영역
                with gr.Column(scale=1):
                    # 파일 업로드
                    with gr.Group():
                        gr.Markdown("### 📤 파일 업로드")
                        
                        components['file_upload'] = gr.File(
                            label="파일 선택 또는 드래그 앤 드롭",
                            file_types=['.xlsx', '.xls', '.csv'],
                            file_count="single",
                            elem_id="file-upload"
                        )
                        
                        # 업로드 설정
                        with gr.Accordion("⚙️ 업로드 설정", open=False):
                            components['encoding_select'] = gr.Dropdown(
                                choices=["자동 감지", "UTF-8", "CP949", "Latin-1"],
                                value="자동 감지",
                                label="파일 인코딩"
                            )
                            
                            components['sheet_select'] = gr.Dropdown(
                                choices=[],
                                label="Excel 시트 선택 (Excel 파일만)",
                                visible=False
                            )
                    
                    # 업로드된 파일 목록
                    with gr.Group():
                        gr.Markdown("### 📋 업로드된 파일")
                        components['file_list'] = gr.HTML(
                            value=self._create_empty_file_list(),
                            elem_id="uploaded-file-list"
                        )
                        
                        with gr.Row():
                            components['refresh_files_btn'] = gr.Button(
                                "🔄 새로고침",
                                variant="secondary",
                                size="sm"
                            )
                            components['clear_files_btn'] = gr.Button(
                                "🗑️ 모든 파일 삭제",
                                variant="secondary",
                                size="sm"
                            )
                
                # 오른쪽: 파일 정보 및 미리보기
                with gr.Column(scale=2):
                    # 업로드 상태
                    components['upload_status'] = gr.HTML(
                        value=self._create_welcome_message(),
                        elem_id="upload-status"
                    )
                    
                    # 파일 정보
                    with gr.Accordion("📊 파일 정보", open=False):
                        components['file_info'] = gr.HTML(
                            value="<p style='color: #666;'>파일을 업로드하면 정보가 표시됩니다.</p>"
                        )
                    
                    # 데이터 미리보기
                    with gr.Accordion("👀 데이터 미리보기", open=True):
                        components['data_preview'] = gr.DataFrame(
                            label="데이터 미리보기 (처음 10행)",
                            interactive=False,
                            wrap=True,
                            max_rows=10
                        )
                    
                    # 데이터 품질 분석
                    with gr.Accordion("🔍 데이터 품질 분석", open=False):
                        components['quality_analysis'] = gr.HTML(
                            value="<p style='color: #666;'>데이터 품질 분석 결과가 여기에 표시됩니다.</p>"
                        )
            
            # 진행률 표시
            components['upload_progress'] = gr.HTML(
                visible=False,
                elem_id="upload-progress"
            )
        
        return components
    
    def _create_welcome_message(self) -> str:
        """환영 메시지 생성"""
        max_size = settings.max_excel_file_size_mb
        allowed_formats = ", ".join(settings.allowed_extensions)
        
        return f"""
        <div style="
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h3 style="margin: 0 0 15px 0; color: #2E8B57;">📁 파일 업로드 준비 완료!</h3>
            <p style="margin: 0 0 10px 0; color: #555;">
                Excel 또는 CSV 파일을 드래그 앤 드롭하거나 파일 선택 버튼을 클릭하세요.
            </p>
            <div style="
                background: #fff;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                text-align: left;
                font-size: 14px;
            ">
                <strong>📋 지원 사양:</strong><br>
                • 파일 형식: {allowed_formats}<br>
                • 최대 크기: {max_size}MB<br>
                • 인코딩: UTF-8, CP949, Latin-1 자동 감지<br>
                • Excel 다중 시트 지원
            </div>
        </div>
        """
    
    def _create_empty_file_list(self) -> str:
        """빈 파일 목록 HTML"""
        return """
        <div style="
            border: 2px dashed #ddd;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            color: #999;
            font-size: 14px;
        ">
            📂 업로드된 파일이 없습니다.<br>
            위에서 파일을 업로드해보세요.
        </div>
        """
    
    async def handle_file_upload(self, file_obj) -> Tuple[str, str, Any, str]:
        """파일 업로드 처리"""
        if file_obj is None:
            return (
                notification_manager.show_error("파일을 선택해주세요."),
                "",
                None,
                ""
            )
        
        try:
            # 진행률 시작
            progress_html = progress_tracker.start_progress([
                "파일 검증 중...",
                "보안 검사 중...",
                "데이터 로딩 중...",
                "품질 분석 중...",
                "업로드 완료"
            ])
            
            logger.info("파일 업로드 시작", filename=file_obj.name)
            
            # 세션 ID 확인/생성
            if not self.current_session_id:
                self.current_session_id = file_upload_manager.create_session()
            
            # 파일 업로드 실행
            result = await file_upload_manager.upload_file(
                file_obj.name,  # Gradio에서 제공하는 임시 파일 경로
                file_obj.orig_name,  # 원본 파일명
                self.current_session_id
            )
            
            if result['success']:
                # 성공적으로 업로드됨
                file_record = result['file_record']
                self.current_file_id = file_record['file_id']
                self.uploaded_files = file_upload_manager.get_session_files(self.current_session_id)
                
                # 성공 메시지
                success_html = self._format_upload_success(result)
                
                # 파일 목록 업데이트
                file_list_html = self._format_file_list()
                
                # 데이터 미리보기
                preview_data = result.get('preview_data', [])
                
                # 파일 정보 HTML
                file_info_html = self._format_file_info(file_record, result['data_summary'])
                
                return (
                    success_html,  # upload_status
                    file_list_html,  # file_list
                    preview_data,  # data_preview
                    file_info_html  # file_info
                )
            else:
                # 업로드 실패
                error_html = self._format_upload_error(result)
                return (
                    error_html,
                    self._format_file_list(),
                    None,
                    ""
                )
        
        except Exception as e:
            logger.error("파일 업로드 처리 오류", error=str(e))
            error_html = f"""
            <div style="
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            ">
                <h4>❌ 업로드 오류</h4>
                <p>파일 업로드 중 오류가 발생했습니다: {str(e)}</p>
            </div>
            """
            return (error_html, self._format_file_list(), None, "")
    
    def _format_upload_success(self, result: Dict[str, Any]) -> str:
        """업로드 성공 메시지 포맷팅"""
        file_record = result['file_record']
        data_summary = result['data_summary']
        
        return f"""
        <div style="
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">✅ 파일 업로드 완료!</h3>
            <div style="
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                color: #333;
                line-height: 1.6;
            ">
                <p><strong>📄 파일명:</strong> {file_record['original_filename']}</p>
                <p><strong>📊 데이터 크기:</strong> {data_summary['total_rows']:,}행 × {data_summary['total_columns']}열</p>
                <p><strong>💾 파일 크기:</strong> {file_record['file_info']['size_mb']}MB</p>
                <p><strong>⭐ 품질 점수:</strong> {data_summary['quality_score']}/100</p>
                <p><strong>📈 숫자 컬럼:</strong> {data_summary['numeric_columns']}개</p>
                <p><strong>📝 텍스트 컬럼:</strong> {data_summary['text_columns']}개</p>
            </div>
            <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                ⏰ 업로드 시간: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
        """
    
    def _format_upload_error(self, result: Dict[str, Any]) -> str:
        """업로드 실패 메시지 포맷팅"""
        error = result.get('error', '알 수 없는 오류')
        
        return f"""
        <div style="
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">❌ 파일 업로드 실패</h3>
            <div style="
                background: white;
                padding: 15px;
                border-radius: 8px;
                color: #333;
                line-height: 1.6;
            ">
                {error}
            </div>
            <div style="margin-top: 15px; font-size: 14px;">
                <strong>💡 해결 방법:</strong><br>
                • 파일 형식을 확인하세요 (.xlsx, .xls, .csv)<br>
                • 파일 크기가 {settings.max_excel_file_size_mb}MB 이하인지 확인하세요<br>
                • 파일이 손상되지 않았는지 확인하세요<br>
                • 다른 파일로 다시 시도해보세요
            </div>
        </div>
        """
    
    def _format_file_list(self) -> str:
        """파일 목록 HTML 생성"""
        if not self.uploaded_files:
            return self._create_empty_file_list()
        
        html = """
        <div style="border: 1px solid #e9ecef; border-radius: 8px; overflow: hidden;">
        """
        
        for i, file_record in enumerate(self.uploaded_files):
            bg_color = "#f8f9fa" if i % 2 == 0 else "#ffffff"
            
            html += f"""
            <div style="
                background: {bg_color};
                padding: 12px 15px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <div style="font-weight: 600; color: #495057; margin-bottom: 4px;">
                        📄 {file_record['original_filename']}
                    </div>
                    <div style="font-size: 12px; color: #6c757d;">
                        {file_record['row_count']:,}행 × {file_record['column_count']}열 |
                        {file_record['file_info']['size_mb']}MB |
                        업로드: {file_record['upload_time'][:16]}
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <button onclick="selectFile('{file_record['file_id']}')" 
                            style="padding: 4px 8px; font-size: 12px; 
                                   background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        선택
                    </button>
                    <button onclick="deleteFile('{file_record['file_id']}')"
                            style="padding: 4px 8px; font-size: 12px; 
                                   background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        삭제
                    </button>
                </div>
            </div>
            """
        
        html += "</div>"
        return html
    
    def _format_file_info(self, file_record: Dict[str, Any], data_summary: Dict[str, Any]) -> str:
        """파일 정보 HTML 생성"""
        quality_score = data_summary['quality_score']
        quality_color = "#28a745" if quality_score >= 80 else "#ffc107" if quality_score >= 60 else "#dc3545"
        
        html = f"""
        <div style="font-size: 14px;">
            <div style="margin-bottom: 15px;">
                <h4 style="color: #495057; margin: 0 0 10px 0;">📋 기본 정보</h4>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px;">
                    <p style="margin: 4px 0;"><strong>파일명:</strong> {file_record['original_filename']}</p>
                    <p style="margin: 4px 0;"><strong>크기:</strong> {file_record['file_info']['size_mb']}MB</p>
                    <p style="margin: 4px 0;"><strong>형식:</strong> {file_record['file_info']['extension'].upper()}</p>
                    <p style="margin: 4px 0;"><strong>업로드:</strong> {file_record['upload_time'][:19]}</p>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #495057; margin: 0 0 10px 0;">📊 데이터 구조</h4>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px;">
                    <p style="margin: 4px 0;"><strong>행 수:</strong> {data_summary['total_rows']:,}개</p>
                    <p style="margin: 4px 0;"><strong>열 수:</strong> {data_summary['total_columns']}개</p>
                    <p style="margin: 4px 0;"><strong>숫자 컬럼:</strong> {data_summary['numeric_columns']}개</p>
                    <p style="margin: 4px 0;"><strong>텍스트 컬럼:</strong> {data_summary['text_columns']}개</p>
                    <p style="margin: 4px 0;"><strong>메모리 사용량:</strong> {data_summary['memory_usage_mb']}MB</p>
                </div>
            </div>
            
            <div style="margin-bottom: 15px;">
                <h4 style="color: #495057; margin: 0 0 10px 0;">🔍 데이터 품질</h4>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px;">
                    <p style="margin: 4px 0;">
                        <strong>품질 점수:</strong> 
                        <span style="color: {quality_color}; font-weight: bold;">{quality_score}/100</span>
                    </p>
                    <p style="margin: 4px 0;"><strong>결측값:</strong> {data_summary['missing_values_total']:,}개</p>
                    <p style="margin: 4px 0;"><strong>중복 행:</strong> {data_summary['duplicate_rows']:,}개</p>
                </div>
            </div>
        """
        
        # 컬럼 정보 추가
        if data_summary.get('column_info'):
            html += """
            <div>
                <h4 style="color: #495057; margin: 0 0 10px 0;">📝 컬럼 정보</h4>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 6px; max-height: 200px; overflow-y: auto;">
            """
            
            for col_info in data_summary['column_info'][:10]:  # 처음 10개만
                html += f"""
                <div style="margin-bottom: 8px; padding: 8px; background: white; border-radius: 4px;">
                    <div style="font-weight: 600; color: #495057;">{col_info['name']}</div>
                    <div style="font-size: 12px; color: #6c757d;">
                        타입: {col_info['type']} | 
                        고유값: {col_info['unique_count']:,}개 | 
                        결측값: {col_info['missing_count']}개
                    </div>
                </div>
                """
            
            html += "</div></div>"
        
        html += "</div>"
        return html
    
    def refresh_file_list(self) -> str:
        """파일 목록 새로고침"""
        if self.current_session_id:
            self.uploaded_files = file_upload_manager.get_session_files(self.current_session_id)
        return self._format_file_list()
    
    def clear_all_files(self) -> Tuple[str, str, None, str]:
        """모든 파일 삭제"""
        try:
            if self.current_session_id:
                success = file_upload_manager.clear_session(self.current_session_id)
                if success:
                    self.uploaded_files = []
                    self.current_file_id = None
                    self.current_session_id = None
                    
                    return (
                        notification_manager.show_success("모든 파일이 삭제되었습니다."),
                        self._create_empty_file_list(),
                        None,
                        ""
                    )
                else:
                    return (
                        notification_manager.show_error("파일 삭제 중 오류가 발생했습니다."),
                        self._format_file_list(),
                        None,
                        ""
                    )
            else:
                return (
                    notification_manager.show_info("삭제할 파일이 없습니다."),
                    self._create_empty_file_list(),
                    None,
                    ""
                )
        except Exception as e:
            logger.error("파일 삭제 오류", error=str(e))
            return (
                notification_manager.show_error(f"파일 삭제 중 오류: {str(e)}"),
                self._format_file_list(),
                None,
                ""
            )


# 전역 파일 인터페이스 인스턴스
file_interface = FileUploadInterface()
