"""
SQL 쿼리 서비스

자연어를 SQL로 변환하고 데이터베이스를 조회하는 서비스입니다.
"""

import asyncio
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy import text
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import PromptTemplate
import pandas as pd
import structlog
from datetime import datetime

from app.config.database import engine, SessionLocal
from app.core.langchain_config import langchain_manager
from app.core.database_schema import DatabaseSchemaInfo
from app.core.error_handler import error_handler, ErrorType, ErrorSeverity
from app.config.settings import settings

logger = structlog.get_logger()


class SQLQueryService:
    """SQL 쿼리 서비스"""
    
    def __init__(self):
        self.db_engine = engine
        self.langchain_db = None
        self.sql_chain = None
        self.schema_info = DatabaseSchemaInfo()
        self._initialize_sql_chain()
    
    def _initialize_sql_chain(self):
        """SQL 체인 초기화"""
        try:
            # LangChain SQLDatabase 초기화
            self.langchain_db = SQLDatabase.from_uri(
                str(self.db_engine.url),
                include_tables=["companies", "customers", "products", "orders", "order_items", "sales"]
            )
            
            # 커스텀 프롬프트 설정
            sql_prompt = self._create_sql_prompt()
            
            # SQL 체인 생성
            if langchain_manager and langchain_manager.llm:
                self.sql_chain = SQLDatabaseChain.from_llm(
                    llm=langchain_manager.get_llm(),
                    db=self.langchain_db,
                    prompt=sql_prompt,
                    verbose=True,
                    return_intermediate_steps=True,
                    use_query_checker=True
                )
                
                logger.info("SQL 체인 초기화 완료")
            else:
                logger.warning("LangChain 관리자가 초기화되지 않음 - SQL 기능 제한")
                
        except Exception as e:
            error_handler.handle_error(e, "SQL 체인 초기화")
            logger.error("SQL 체인 초기화 실패", error=str(e))
    
    def _create_sql_prompt(self) -> PromptTemplate:
        """SQL 생성용 커스텀 프롬프트 생성"""
        template = """
당신은 PostgreSQL 전문가입니다. 주어진 입력에 대해 정확한 SQL 쿼리를 작성해야 합니다.

데이터베이스 스키마 정보:
{schema_info}

테이블 관계:
{relationships}

중요한 규칙:
1. 항상 정확한 테이블명과 컬럼명을 사용하세요
2. 날짜 관련 쿼리에서는 PostgreSQL 함수를 사용하세요 (DATE_TRUNC, CURRENT_DATE 등)
3. 한국어 문자열이 포함된 경우 적절히 처리하세요
4. 결과가 너무 많을 경우 LIMIT을 사용하세요
5. 집계 함수 사용 시 GROUP BY를 적절히 사용하세요
6. JOIN이 필요한 경우 적절한 테이블 관계를 사용하세요

샘플 쿼리 예시:
{sample_queries}

질문: {input}
SQL 쿼리:
"""
        
        return PromptTemplate(
            input_variables=["input", "schema_info", "relationships", "sample_queries"],
            template=template
        )
    
    async def execute_natural_language_query(self, question: str) -> Dict[str, Any]:
        """
        자연어 질문을 SQL로 변환하여 실행
        
        Args:
            question: 자연어 질문
            
        Returns:
            Dict containing query results, SQL, and metadata
        """
        if not self.sql_chain:
            return {
                "success": False,
                "error": "SQL 서비스가 초기화되지 않았습니다. OpenAI API 키를 확인해주세요.",
                "data": None,
                "sql": None,
                "execution_time": 0
            }
        
        start_time = datetime.now()
        
        try:
            logger.info("자연어 SQL 질의 시작", question=question)
            
            # 프롬프트에 필요한 정보 준비
            schema_info = self.schema_info.get_schema_for_llm()
            relationships = self.schema_info.get_relationships_info()
            sample_queries = self._format_sample_queries()
            
            # SQL 체인 실행
            result = await asyncio.to_thread(
                self.sql_chain.run,
                input=question,
                schema_info=schema_info,
                relationships=relationships,
                sample_queries=sample_queries
            )
            
            # 중간 단계에서 SQL 추출
            if hasattr(self.sql_chain, 'intermediate_steps') and self.sql_chain.intermediate_steps:
                sql_query = self._extract_sql_from_steps(self.sql_chain.intermediate_steps)
            else:
                sql_query = "SQL 추출 실패"
            
            # 결과 검증 및 포맷팅
            formatted_result = self._format_query_result(result, sql_query)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info("자연어 SQL 질의 완료", 
                       execution_time=execution_time,
                       sql=sql_query[:100] + "..." if len(sql_query) > 100 else sql_query)
            
            return {
                "success": True,
                "data": formatted_result,
                "sql": sql_query,
                "execution_time": execution_time,
                "question": question
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            app_error = error_handler.handle_error(e, "자연어 SQL 질의")
            
            logger.error("자연어 SQL 질의 실패", 
                        error=str(e),
                        execution_time=execution_time)
            
            return {
                "success": False,
                "error": app_error.user_message,
                "data": None,
                "sql": None,
                "execution_time": execution_time
            }
    
    async def execute_direct_sql(self, sql_query: str) -> Dict[str, Any]:
        """
        직접 SQL 쿼리 실행
        
        Args:
            sql_query: 실행할 SQL 쿼리
            
        Returns:
            Dict containing query results and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info("직접 SQL 실행", sql=sql_query[:100] + "..." if len(sql_query) > 100 else sql_query)
            
            # SQL 안전성 검증
            if not self._validate_sql_safety(sql_query):
                raise ValueError("안전하지 않은 SQL 쿼리입니다. SELECT 문만 허용됩니다.")
            
            # 쿼리 실행
            with SessionLocal() as db:
                result = db.execute(text(sql_query))
                
                # 결과를 DataFrame으로 변환
                if result.returns_rows:
                    columns = list(result.keys())
                    rows = result.fetchall()
                    
                    df = pd.DataFrame(rows, columns=columns)
                    
                    # 결과 포맷팅
                    formatted_result = {
                        "columns": columns,
                        "data": df.to_dict('records'),
                        "row_count": len(df),
                        "summary": self._generate_result_summary(df)
                    }
                else:
                    formatted_result = {
                        "message": "쿼리가 성공적으로 실행되었습니다.",
                        "affected_rows": result.rowcount
                    }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info("직접 SQL 실행 완료", 
                       execution_time=execution_time,
                       row_count=formatted_result.get("row_count", 0))
            
            return {
                "success": True,
                "data": formatted_result,
                "sql": sql_query,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            app_error = error_handler.handle_error(e, "직접 SQL 실행")
            
            logger.error("직접 SQL 실행 실패", 
                        error=str(e),
                        execution_time=execution_time)
            
            return {
                "success": False,
                "error": app_error.user_message,
                "data": None,
                "sql": sql_query,
                "execution_time": execution_time
            }
    
    def _validate_sql_safety(self, sql_query: str) -> bool:
        """SQL 쿼리 안전성 검증"""
        sql_lower = sql_query.lower().strip()
        
        # SELECT 문만 허용
        if not sql_lower.startswith('select'):
            return False
        
        # 위험한 키워드 확인
        dangerous_keywords = [
            'drop', 'delete', 'insert', 'update', 'alter', 'create',
            'truncate', 'grant', 'revoke', 'exec', 'execute'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in sql_lower:
                return False
        
        return True
    
    def _extract_sql_from_steps(self, steps: List) -> str:
        """중간 단계에서 SQL 쿼리 추출"""
        try:
            for step in steps:
                if isinstance(step, dict) and 'sql_cmd' in step:
                    return step['sql_cmd']
                elif isinstance(step, str) and 'select' in step.lower():
                    return step
            
            return "SQL 추출 실패"
        except Exception:
            return "SQL 추출 오류"
    
    def _format_sample_queries(self) -> str:
        """샘플 쿼리를 문자열로 포맷팅"""
        samples = self.schema_info.get_sample_queries()
        formatted = ""
        
        for i, sample in enumerate(samples[:3], 1):  # 처음 3개만 사용
            formatted += f"{i}. 질문: {sample['question']}\n"
            formatted += f"   SQL: {sample['sql']}\n\n"
        
        return formatted
    
    def _format_query_result(self, result: str, sql: str) -> Dict[str, Any]:
        """쿼리 결과 포맷팅"""
        try:
            # 결과가 테이블 형태인지 확인
            if "rows" in result.lower() or "|" in result:
                return {
                    "type": "table",
                    "content": result,
                    "raw_result": result
                }
            else:
                return {
                    "type": "text",
                    "content": result,
                    "raw_result": result
                }
        except Exception:
            return {
                "type": "error",
                "content": "결과 포맷팅 실패",
                "raw_result": str(result)
            }
    
    def _generate_result_summary(self, df: pd.DataFrame) -> str:
        """결과 요약 생성"""
        try:
            summary = f"총 {len(df)}개의 행이 조회되었습니다."
            
            if len(df) > 0:
                # 숫자 컬럼에 대한 기본 통계
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    summary += f"\n\n📊 숫자 컬럼 요약:"
                    for col in numeric_cols:
                        summary += f"\n- {col}: 평균 {df[col].mean():.2f}, 최대 {df[col].max():.2f}"
            
            return summary
        except Exception:
            return f"총 {len(df)}개의 행이 조회되었습니다."
    
    def get_table_info(self, table_name: str = None) -> Dict[str, Any]:
        """테이블 정보 조회"""
        try:
            if table_name:
                table_info = self.schema_info.get_table_info()
                if table_name in table_info:
                    return {
                        "success": True,
                        "data": {table_name: table_info[table_name]}
                    }
                else:
                    return {
                        "success": False,
                        "error": f"테이블 '{table_name}'을 찾을 수 없습니다."
                    }
            else:
                return {
                    "success": True,
                    "data": self.schema_info.get_table_info()
                }
        except Exception as e:
            app_error = error_handler.handle_error(e, "테이블 정보 조회")
            return {
                "success": False,
                "error": app_error.user_message
            }
    
    def get_sample_queries(self) -> List[Dict[str, str]]:
        """샘플 쿼리 목록 반환"""
        return self.schema_info.get_sample_queries()
    
    def test_database_connection(self) -> Tuple[bool, str]:
        """데이터베이스 연결 테스트"""
        try:
            with SessionLocal() as db:
                result = db.execute(text("SELECT 1 as test"))
                test_value = result.scalar()
                
                if test_value == 1:
                    # 테이블 존재 여부 확인
                    tables_result = db.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('companies', 'customers', 'products', 'orders', 'order_items', 'sales')
                    """))
                    
                    tables = [row[0] for row in tables_result]
                    
                    if len(tables) >= 6:
                        return True, f"✅ 데이터베이스 연결 성공! {len(tables)}개 테이블 확인됨"
                    else:
                        return False, f"⚠️ 데이터베이스 연결됨, 하지만 {len(tables)}개 테이블만 존재 (샘플 데이터 생성 필요)"
                else:
                    return False, "❌ 데이터베이스 응답 오류"
                    
        except Exception as e:
            logger.error("데이터베이스 연결 테스트 실패", error=str(e))
            return False, f"❌ 데이터베이스 연결 실패: {str(e)}"


# 전역 SQL 쿼리 서비스 인스턴스
sql_query_service = SQLQueryService()
