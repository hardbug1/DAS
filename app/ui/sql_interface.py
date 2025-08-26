"""
SQL 질의 사용자 인터페이스

자연어를 SQL로 변환하여 데이터베이스를 조회하는 UI 컴포넌트들을 제공합니다.
"""

import gradio as gr
from typing import Dict, List, Any, Tuple, Optional
import asyncio
import json
import structlog
from datetime import datetime

from app.services.sql_query_service import sql_query_service
from app.core.database_schema import DatabaseSchemaInfo
from app.ui.interactions import notification_manager, progress_tracker

logger = structlog.get_logger()


class SQLInterface:
    """SQL 질의 인터페이스"""
    
    def __init__(self):
        self.schema_info = DatabaseSchemaInfo()
        self.query_history = []
    
    def create_sql_interface(self) -> Dict[str, Any]:
        """SQL 질의 인터페이스 생성"""
        components = {}
        
        with gr.Tab("🗄️ SQL 데이터베이스 질의"):
            # 헤더
            gr.HTML("""
            <div style="
                background: linear-gradient(135deg, #2E8B57 0%, #006400 100%);
                color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
                text-align: center;
            ">
                <h2 style="margin: 0 0 10px 0;">🗄️ 자연어 SQL 질의</h2>
                <p style="margin: 0; opacity: 0.9;">
                    자연어로 질문하면 AI가 SQL 쿼리를 생성하여 데이터베이스를 조회합니다
                </p>
            </div>
            """)
            
            with gr.Row():
                # 왼쪽: 질의 영역
                with gr.Column(scale=2):
                    # 자연어 질의 입력
                    components['sql_question'] = gr.Textbox(
                        label="💬 자연어 질문",
                        placeholder="예: 지난 달 총 매출은 얼마입니까?",
                        lines=3,
                        elem_id="sql-question-input"
                    )
                    
                    with gr.Row():
                        components['sql_submit_btn'] = gr.Button(
                            "🔍 질의 실행",
                            variant="primary",
                            scale=2
                        )
                        components['sql_clear_btn'] = gr.Button(
                            "🗑️ 초기화",
                            variant="secondary",
                            scale=1
                        )
                    
                    # 빠른 예시 질문
                    gr.Markdown("### 📝 예시 질문 (클릭하여 입력)")
                    components.update(self._create_example_questions())
                    
                    # 직접 SQL 실행 (고급 사용자용)
                    with gr.Accordion("🔧 직접 SQL 실행 (고급)", open=False):
                        components['direct_sql'] = gr.Code(
                            label="SQL 쿼리",
                            language="sql",
                            placeholder="SELECT * FROM sales LIMIT 10;",
                            lines=5
                        )
                        components['direct_sql_btn'] = gr.Button(
                            "⚡ SQL 실행",
                            variant="secondary"
                        )
                
                # 오른쪽: 스키마 정보
                with gr.Column(scale=1):
                    components.update(self._create_schema_panel())
            
            # 결과 표시 영역
            with gr.Row():
                with gr.Column():
                    # 질의 결과
                    components['sql_result'] = gr.HTML(
                        value=self._create_welcome_message(),
                        elem_id="sql-result-display"
                    )
                    
                    # 실행된 SQL 표시
                    components['executed_sql'] = gr.Code(
                        label="📋 실행된 SQL 쿼리",
                        language="sql",
                        visible=False,
                        lines=5
                    )
                    
                    # 데이터 테이블 (있는 경우)
                    components['result_dataframe'] = gr.DataFrame(
                        label="📊 조회 결과",
                        visible=False,
                        wrap=True,
                        max_rows=20
                    )
            
            # 질의 기록
            with gr.Accordion("📜 질의 기록", open=False):
                components['query_history_display'] = gr.HTML(
                    value="<p style='color: #666;'>아직 실행된 질의가 없습니다.</p>"
                )
        
        return components
    
    def _create_example_questions(self) -> Dict[str, Any]:
        """예시 질문 버튼들 생성"""
        components = {}
        
        example_questions = [
            "지난 달 총 매출은 얼마입니까?",
            "가장 많이 팔린 제품 TOP 5는?",
            "카테고리별 매출 현황을 보여주세요",
            "서울 고객들의 평균 구매액은?",
            "월별 매출 트렌드는 어떻게 되나요?",
            "재고가 가장 많은 제품은?",
            "고객 연령대별 구매 패턴은?",
            "주문 상태별 통계를 보여주세요"
        ]
        
        with gr.Row():
            for i, question in enumerate(example_questions[:4]):
                components[f'example_btn_{i}'] = gr.Button(
                    question,
                    size="sm",
                    variant="secondary"
                )
        
        with gr.Row():
            for i, question in enumerate(example_questions[4:], 4):
                components[f'example_btn_{i}'] = gr.Button(
                    question,
                    size="sm",
                    variant="secondary"
                )
        
        return components
    
    def _create_schema_panel(self) -> Dict[str, Any]:
        """스키마 정보 패널 생성"""
        components = {}
        
        with gr.Accordion("🗄️ 데이터베이스 스키마", open=True):
            # 테이블 목록
            table_info = self.schema_info.get_table_info()
            
            schema_html = """
            <div style="font-size: 14px;">
                <h4 style="margin: 0 0 15px 0; color: #2E8B57;">📊 테이블 구조</h4>
            """
            
            for table_name, info in table_info.items():
                schema_html += f"""
                <div style="
                    background: #f8f9fa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 10px;
                    margin-bottom: 10px;
                ">
                    <div style="font-weight: 600; color: #495057; margin-bottom: 5px;">
                        📋 {table_name}
                    </div>
                    <div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">
                        {info['description']}
                    </div>
                    <div style="font-size: 12px;">
                """
                
                for col_name, col_desc in list(info['columns'].items())[:5]:  # 처음 5개만 표시
                    schema_html += f"<div>• {col_name}: {col_desc}</div>"
                
                if len(info['columns']) > 5:
                    schema_html += f"<div style='color: #6c757d;'>... 총 {len(info['columns'])}개 컬럼</div>"
                
                schema_html += "</div></div>"
            
            schema_html += "</div>"
            
            components['schema_display'] = gr.HTML(schema_html)
            
            # 연결 상태 테스트
            components['db_connection_btn'] = gr.Button(
                "🔌 DB 연결 테스트",
                variant="secondary",
                size="sm"
            )
            
            components['db_status'] = gr.HTML("")
        
        return components
    
    def _create_welcome_message(self) -> str:
        """환영 메시지 생성"""
        return """
        <div style="
            background: #e8f5e8;
            border: 1px solid #c3e6c3;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        ">
            <h3 style="margin: 0 0 15px 0; color: #2E8B57;">🗄️ SQL 질의 준비 완료!</h3>
            <p style="margin: 0 0 10px 0; color: #555;">
                자연어로 질문을 입력하거나 예시 질문을 클릭해보세요.
            </p>
            <div style="
                background: #fff;
                padding: 15px;
                border-radius: 8px;
                margin-top: 15px;
                text-align: left;
                font-size: 14px;
            ">
                <strong>💡 사용 팁:</strong><br>
                • 구체적인 질문일수록 정확한 결과를 얻을 수 있습니다<br>
                • 날짜, 숫자, 카테고리 등을 명시해주세요<br>
                • 예: "2024년 1월 스마트폰 카테고리 매출"
            </div>
        </div>
        """
    
    async def execute_natural_language_query(self, question: str) -> Tuple[str, str, Any, bool, bool]:
        """자연어 질의 실행"""
        if not question.strip():
            return (
                notification_manager.show_error("질문을 입력해주세요."),
                "",
                None,
                False,
                False
            )
        
        try:
            # 진행률 표시
            progress_html = progress_tracker.start_progress([
                "질문 분석 중...",
                "SQL 쿼리 생성 중...",
                "데이터베이스 조회 중...",
                "결과 포맷팅 중..."
            ])
            
            logger.info("자연어 SQL 질의 시작", question=question)
            
            # SQL 서비스 호출
            result = await sql_query_service.execute_natural_language_query(question)
            
            if result["success"]:
                # 성공 결과 포맷팅
                result_html = self._format_success_result(result)
                executed_sql = result.get("sql", "")
                
                # 테이블 데이터 추출
                table_data = None
                if result["data"] and "table_data" in result["data"]:
                    table_data = result["data"]["table_data"]
                    if table_data and "data" in table_data:
                        table_data = table_data["data"]
                
                # 질의 기록 저장
                self._add_to_history(question, result)
                
                return (
                    result_html,
                    executed_sql,
                    table_data,
                    True,  # executed_sql visible
                    bool(table_data)  # dataframe visible
                )
            else:
                # 오류 결과 포맷팅
                error_html = self._format_error_result(result)
                return (
                    error_html,
                    "",
                    None,
                    False,
                    False
                )
        
        except Exception as e:
            logger.error("자연어 SQL 질의 실행 오류", error=str(e))
            error_html = f"""
            <div style="
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            ">
                <h4>❌ 실행 오류</h4>
                <p>질의 실행 중 오류가 발생했습니다: {str(e)}</p>
            </div>
            """
            return (error_html, "", None, False, False)
    
    async def execute_direct_sql(self, sql_query: str) -> Tuple[str, str, Any, bool, bool]:
        """직접 SQL 실행"""
        if not sql_query.strip():
            return (
                notification_manager.show_error("SQL 쿼리를 입력해주세요."),
                "",
                None,
                False,
                False
            )
        
        try:
            logger.info("직접 SQL 실행", sql=sql_query[:100])
            
            result = await sql_query_service.execute_direct_sql(sql_query)
            
            if result["success"]:
                result_html = self._format_direct_sql_result(result)
                
                # 테이블 데이터 추출
                table_data = None
                if result["data"] and "data" in result["data"]:
                    table_data = result["data"]["data"]
                
                # 기록 저장
                self._add_to_history(f"직접 SQL: {sql_query[:50]}...", result)
                
                return (
                    result_html,
                    sql_query,
                    table_data,
                    True,
                    bool(table_data)
                )
            else:
                error_html = self._format_error_result(result)
                return (error_html, sql_query, None, True, False)
        
        except Exception as e:
            logger.error("직접 SQL 실행 오류", error=str(e))
            error_html = f"""
            <div style="background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 8px;">
                <h4>❌ SQL 실행 오류</h4>
                <p>{str(e)}</p>
            </div>
            """
            return (error_html, sql_query, None, True, False)
    
    def _format_success_result(self, result: Dict[str, Any]) -> str:
        """성공 결과 HTML 포맷팅"""
        data = result.get("data", {})
        answer = data.get("answer", "결과를 성공적으로 조회했습니다.")
        execution_time = result.get("execution_time", 0)
        
        html = f"""
        <div style="
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">✅ 질의 실행 완료</h3>
            <div style="
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                color: #333;
                line-height: 1.6;
            ">
                {answer}
            </div>
            <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                ⏱️ 실행 시간: {execution_time:.2f}초
            </div>
        </div>
        """
        
        return html
    
    def _format_direct_sql_result(self, result: Dict[str, Any]) -> str:
        """직접 SQL 결과 포맷팅"""
        data = result.get("data", {})
        execution_time = result.get("execution_time", 0)
        
        if "row_count" in data:
            row_count = data["row_count"]
            summary = data.get("summary", "")
            
            html = f"""
            <div style="
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
            ">
                <h3 style="margin: 0 0 15px 0;">⚡ SQL 실행 완료</h3>
                <div style="
                    background: white;
                    padding: 15px;
                    border-radius: 8px;
                    color: #333;
                ">
                    <p><strong>📊 조회된 행 수:</strong> {row_count}개</p>
                    {f'<p><strong>📈 요약:</strong> {summary}</p>' if summary else ''}
                </div>
                <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                    ⏱️ 실행 시간: {execution_time:.2f}초
                </div>
            </div>
            """
        else:
            message = data.get("message", "쿼리가 실행되었습니다.")
            html = f"""
            <div style="
                background: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
            ">
                <h3 style="margin: 0 0 15px 0;">⚡ SQL 실행 완료</h3>
                <p>{message}</p>
                <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                    ⏱️ 실행 시간: {execution_time:.2f}초
                </div>
            </div>
            """
        
        return html
    
    def _format_error_result(self, result: Dict[str, Any]) -> str:
        """오류 결과 포맷팅"""
        error = result.get("error", "알 수 없는 오류가 발생했습니다.")
        execution_time = result.get("execution_time", 0)
        
        return f"""
        <div style="
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 12px;
            margin: 15px 0;
        ">
            <h3 style="margin: 0 0 15px 0;">❌ 질의 실행 실패</h3>
            <div style="
                background: white;
                padding: 15px;
                border-radius: 8px;
                color: #333;
                line-height: 1.6;
            ">
                {error}
            </div>
            <div style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                ⏱️ 실행 시간: {execution_time:.2f}초
            </div>
        </div>
        """
    
    def _add_to_history(self, question: str, result: Dict[str, Any]):
        """질의 기록에 추가"""
        self.query_history.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "question": question,
            "success": result["success"],
            "execution_time": result.get("execution_time", 0),
            "sql": result.get("sql", "")
        })
        
        # 최근 10개만 유지
        if len(self.query_history) > 10:
            self.query_history = self.query_history[-10:]
    
    def get_query_history_html(self) -> str:
        """질의 기록 HTML 생성"""
        if not self.query_history:
            return "<p style='color: #666;'>아직 실행된 질의가 없습니다.</p>"
        
        html = "<div style='font-size: 14px;'>"
        
        for i, record in enumerate(reversed(self.query_history), 1):
            status_icon = "✅" if record["success"] else "❌"
            status_color = "#28a745" if record["success"] else "#dc3545"
            
            html += f"""
            <div style="
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 10px;
                background: {'#f8f9fa' if record['success'] else '#fff5f5'};
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: {status_color};">
                        {status_icon} 질의 #{len(self.query_history) - i + 1}
                    </span>
                    <span style="font-size: 12px; color: #6c757d;">
                        {record['timestamp']} ({record['execution_time']:.2f}초)
                    </span>
                </div>
                <div style="color: #495057; margin-bottom: 5px;">
                    {record['question'][:100]}{'...' if len(record['question']) > 100 else ''}
                </div>
                {f'<div style="font-size: 12px; color: #6c757d; font-family: monospace;">{record["sql"][:150]}{"..." if len(record["sql"]) > 150 else ""}</div>' if record["sql"] else ''}
            </div>
            """
        
        html += "</div>"
        return html
    
    def clear_interface(self) -> Tuple[str, str, str, None, bool, bool]:
        """인터페이스 초기화"""
        self.query_history.clear()
        return (
            "",  # question input
            self._create_welcome_message(),  # result display
            "",  # executed sql
            None,  # dataframe
            False,  # sql visible
            False   # dataframe visible
        )
    
    def test_database_connection(self) -> str:
        """데이터베이스 연결 테스트"""
        try:
            success, message = sql_query_service.test_database_connection()
            
            if success:
                return f"""
                <div style="
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    color: #155724;
                    padding: 10px;
                    border-radius: 6px;
                    margin: 5px 0;
                    font-size: 12px;
                ">
                    {message}
                </div>
                """
            else:
                return f"""
                <div style="
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    color: #721c24;
                    padding: 10px;
                    border-radius: 6px;
                    margin: 5px 0;
                    font-size: 12px;
                ">
                    {message}
                </div>
                """
        except Exception as e:
            return f"""
            <div style="
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
                padding: 10px;
                border-radius: 6px;
                margin: 5px 0;
                font-size: 12px;
            ">
                ⚠️ 연결 테스트 오류: {str(e)}
            </div>
            """


# 전역 SQL 인터페이스 인스턴스
sql_interface = SQLInterface()
