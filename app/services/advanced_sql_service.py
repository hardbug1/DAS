"""
고급 SQL 생성 서비스

복잡한 쿼리 지원, 스키마 인식 강화, 자연어 이해 향상을 위한 고급 SQL 생성 엔진
"""

import re
import structlog
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
try:
    from dateutil import parser as date_parser
except ImportError:
    date_parser = None
from sqlalchemy import text, inspect
from app.config.database import engine, SessionLocal
from app.core.database_schema import Base

logger = structlog.get_logger()


class NaturalLanguageProcessor:
    """자연어 처리 및 SQL 매핑"""
    
    def __init__(self):
        self.time_patterns = self._initialize_time_patterns()
        self.business_terms = self._initialize_business_terms()
        self.aggregation_terms = self._initialize_aggregation_terms()
        
    def _initialize_time_patterns(self) -> Dict[str, str]:
        """시간 표현 패턴 정의"""
        return {
            # 상대적 시간
            r'지난\s*(\d+)\s*년': lambda m: f"sale_date >= DATE('{datetime.now() - timedelta(days=int(m.group(1))*365)}')",
            r'지난\s*(\d+)\s*달|지난\s*(\d+)\s*개월': lambda m: f"sale_date >= DATE('{datetime.now() - timedelta(days=int(m.group(1) or m.group(2))*30)}')",
            r'지난\s*(\d+)\s*주': lambda m: f"sale_date >= DATE('{datetime.now() - timedelta(weeks=int(m.group(1)))}')",
            r'지난\s*(\d+)\s*일': lambda m: f"sale_date >= DATE('{datetime.now() - timedelta(days=int(m.group(1)))}')",
            
            # 특정 기간
            r'올해|금년': f"EXTRACT(YEAR FROM sale_date) = {datetime.now().year}",
            r'작년|지난해': f"EXTRACT(YEAR FROM sale_date) = {datetime.now().year - 1}",
            r'이번\s*달|이번\s*월': f"EXTRACT(YEAR FROM sale_date) = {datetime.now().year} AND EXTRACT(MONTH FROM sale_date) = {datetime.now().month}",
            r'지난\s*달|저번\s*달': f"EXTRACT(YEAR FROM sale_date) = {datetime.now().year} AND EXTRACT(MONTH FROM sale_date) = {datetime.now().month - 1 if datetime.now().month > 1 else 12}",
            
            # 계절
            r'봄': "EXTRACT(MONTH FROM sale_date) IN (3, 4, 5)",
            r'여름': "EXTRACT(MONTH FROM sale_date) IN (6, 7, 8)",
            r'가을': "EXTRACT(MONTH FROM sale_date) IN (9, 10, 11)",
            r'겨울': "EXTRACT(MONTH FROM sale_date) IN (12, 1, 2)",
            
            # 요일
            r'평일': "EXTRACT(DOW FROM sale_date) BETWEEN 1 AND 5",
            r'주말': "EXTRACT(DOW FROM sale_date) IN (0, 6)",
        }
    
    def _initialize_business_terms(self) -> Dict[str, Dict[str, str]]:
        """비즈니스 용어 매핑"""
        return {
            # 매출 관련
            'revenue': {
                'patterns': [r'매출', r'수익', r'매출액', r'수입', r'판매액'],
                'column': 'sales.amount',
                'table': 'sales',
                'aggregation': 'SUM'
            },
            'profit': {
                'patterns': [r'수익', r'이익', r'순이익'],
                'column': 'sales.amount - (order_items.quantity * products.price * 0.7)',  # 가정적 원가율
                'table': 'sales',
                'aggregation': 'SUM'
            },
            
            # 고객 관련
            'customer_count': {
                'patterns': [r'고객\s*수', r'고객\s*숫자', r'회원\s*수'],
                'column': 'customers.id',
                'table': 'customers',
                'aggregation': 'COUNT(DISTINCT'
            },
            'customer_age': {
                'patterns': [r'고객\s*나이', r'연령', r'나이'],
                'column': 'customers.age',
                'table': 'customers',
                'aggregation': 'AVG'
            },
            
            # 제품 관련
            'product_count': {
                'patterns': [r'제품\s*수', r'상품\s*수', r'아이템\s*수'],
                'column': 'products.id',
                'table': 'products',
                'aggregation': 'COUNT'
            },
            'inventory': {
                'patterns': [r'재고', r'재고량', r'보유량'],
                'column': 'products.stock_quantity',
                'table': 'products',
                'aggregation': 'SUM'
            },
            
            # 주문 관련
            'order_count': {
                'patterns': [r'주문\s*수', r'주문\s*건수', r'거래\s*건수'],
                'column': 'orders.id',
                'table': 'orders',
                'aggregation': 'COUNT'
            },
            'order_amount': {
                'patterns': [r'주문\s*금액', r'거래\s*금액', r'주문액'],
                'column': 'orders.total_amount',
                'table': 'orders',
                'aggregation': 'AVG'
            }
        }
    
    def _initialize_aggregation_terms(self) -> Dict[str, str]:
        """집계 함수 매핑"""
        return {
            r'총|전체|합계': 'SUM',
            r'평균|avg': 'AVG',
            r'최대|최고|max': 'MAX',
            r'최소|최저|min': 'MIN',
            r'개수|수량|건수|count': 'COUNT',
            r'상위|top': 'ORDER BY {column} DESC LIMIT',
            r'하위|bottom': 'ORDER BY {column} ASC LIMIT',
        }
    
    def parse_natural_language(self, question: str) -> Dict[str, Any]:
        """자연어 질문을 구조화된 정보로 파싱"""
        parsed = {
            'intent': self._detect_intent(question),
            'entities': self._extract_entities(question),
            'time_conditions': self._extract_time_conditions(question),
            'aggregations': self._extract_aggregations(question),
            'filters': self._extract_filters(question),
            'sorting': self._extract_sorting(question),
            'grouping': self._extract_grouping(question)
        }
        
        logger.info("자연어 파싱 완료", question=question, parsed=parsed)
        return parsed
    
    def _detect_intent(self, question: str) -> str:
        """질문의 의도 감지"""
        question_lower = question.lower()
        
        if any(pattern in question_lower for pattern in ['비교', '차이', '대비']):
            return 'comparison'
        elif any(pattern in question_lower for pattern in ['추세', '트렌드', '변화', '증가', '감소']):
            return 'trend'
        elif any(pattern in question_lower for pattern in ['상위', 'top', '최고', '가장 많이']):
            return 'ranking'
        elif any(pattern in question_lower for pattern in ['분포', '분석', '통계']):
            return 'distribution'
        elif any(pattern in question_lower for pattern in ['총', '합계', '전체']):
            return 'aggregation'
        else:
            return 'general'
    
    def _extract_entities(self, question: str) -> List[Dict[str, str]]:
        """엔티티 추출 (테이블, 컬럼, 값)"""
        entities = []
        
        # 비즈니스 용어 매칭
        for term, info in self.business_terms.items():
            for pattern in info['patterns']:
                if re.search(pattern, question):
                    entities.append({
                        'type': 'business_term',
                        'value': term,
                        'column': info['column'],
                        'table': info['table'],
                        'aggregation': info['aggregation']
                    })
        
        # 지역 매칭
        regions = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '수원', '창원', '성남']
        for region in regions:
            if region in question:
                entities.append({
                    'type': 'location',
                    'value': region,
                    'column': 'customers.city',
                    'condition': f"customers.city = '{region}'"
                })
        
        # 카테고리 매칭
        categories = ['전자제품', '의류', '식품', '생활용품', '화장품']
        for category in categories:
            if category in question:
                entities.append({
                    'type': 'category',
                    'value': category,
                    'column': 'products.category',
                    'condition': f"products.category = '{category}'"
                })
        
        return entities
    
    def _extract_time_conditions(self, question: str) -> List[str]:
        """시간 조건 추출"""
        conditions = []
        
        for pattern, condition in self.time_patterns.items():
            matches = re.finditer(pattern, question)
            for match in matches:
                if callable(condition):
                    conditions.append(condition(match))
                else:
                    conditions.append(condition)
        
        return conditions
    
    def _extract_aggregations(self, question: str) -> List[Dict[str, str]]:
        """집계 함수 추출"""
        aggregations = []
        
        for pattern, func in self.aggregation_terms.items():
            if re.search(pattern, question):
                aggregations.append({
                    'function': func,
                    'pattern': pattern
                })
        
        return aggregations
    
    def _extract_filters(self, question: str) -> List[str]:
        """필터 조건 추출"""
        filters = []
        
        # 숫자 범위 패턴
        amount_patterns = [
            (r'(\d+)만원\s*이상', lambda m: f"total_amount >= {int(m.group(1)) * 10000}"),
            (r'(\d+)만원\s*이하', lambda m: f"total_amount <= {int(m.group(1)) * 10000}"),
            (r'(\d+)\s*세\s*이상', lambda m: f"customers.age >= {m.group(1)}"),
            (r'(\d+)\s*세\s*이하', lambda m: f"customers.age <= {m.group(1)}"),
        ]
        
        for pattern, converter in amount_patterns:
            matches = re.finditer(pattern, question)
            for match in matches:
                filters.append(converter(match))
        
        return filters
    
    def _extract_sorting(self, question: str) -> Optional[Dict[str, str]]:
        """정렬 조건 추출"""
        if re.search(r'높은\s*순|많은\s*순|큰\s*순', question):
            return {'direction': 'DESC'}
        elif re.search(r'낮은\s*순|적은\s*순|작은\s*순', question):
            return {'direction': 'ASC'}
        
        return None
    
    def _extract_grouping(self, question: str) -> List[str]:
        """그룹화 조건 추출"""
        grouping = []
        
        group_patterns = {
            r'지역별|도시별': 'customers.city',
            r'카테고리별|분류별': 'products.category',
            r'월별|달별': 'EXTRACT(MONTH FROM sale_date)',
            r'년도별|연도별': 'EXTRACT(YEAR FROM sale_date)',
            r'요일별': 'EXTRACT(DOW FROM sale_date)',
            r'고객별': 'customers.id',
            r'제품별|상품별': 'products.id',
            r'회사별|업체별': 'companies.name'
        }
        
        for pattern, column in group_patterns.items():
            if re.search(pattern, question):
                grouping.append(column)
        
        return grouping


class QueryOptimizer:
    """SQL 쿼리 최적화"""
    
    def __init__(self):
        self.optimization_rules = self._initialize_optimization_rules()
    
    def _initialize_optimization_rules(self) -> List[Dict[str, Any]]:
        """최적화 규칙 정의"""
        return [
            {
                'name': 'index_hint',
                'pattern': r'WHERE.*customers\.city',
                'suggestion': 'customers.city 컬럼에 인덱스 생성을 고려해보세요.',
                'optimization': 'CREATE INDEX idx_customers_city ON customers(city);'
            },
            {
                'name': 'join_optimization',
                'pattern': r'JOIN.*JOIN.*JOIN',
                'suggestion': '다중 JOIN 쿼리입니다. 필요한 컬럼만 SELECT하는 것을 권장합니다.',
                'optimization': None
            },
            {
                'name': 'limit_suggestion',
                'pattern': r'ORDER BY.*(?!LIMIT)',
                'suggestion': '정렬 쿼리에 LIMIT를 추가하면 성능이 향상됩니다.',
                'optimization': None
            }
        ]
    
    def optimize_query(self, sql_query: str) -> Dict[str, Any]:
        """쿼리 최적화 및 제안사항 반환"""
        suggestions = []
        optimizations = []
        
        for rule in self.optimization_rules:
            if re.search(rule['pattern'], sql_query, re.IGNORECASE):
                suggestions.append(rule['suggestion'])
                if rule['optimization']:
                    optimizations.append(rule['optimization'])
        
        # 기본 성능 분석
        performance_analysis = self._analyze_performance(sql_query)
        
        return {
            'suggestions': suggestions,
            'optimizations': optimizations,
            'performance_analysis': performance_analysis,
            'complexity_score': self._calculate_complexity(sql_query)
        }
    
    def _analyze_performance(self, sql_query: str) -> Dict[str, Any]:
        """쿼리 성능 분석"""
        analysis = {
            'estimated_complexity': 'medium',
            'join_count': len(re.findall(r'\bJOIN\b', sql_query, re.IGNORECASE)),
            'subquery_count': len(re.findall(r'\bSELECT\b.*\bFROM\b.*\bSELECT\b', sql_query, re.IGNORECASE)),
            'aggregation_count': len(re.findall(r'\b(SUM|AVG|COUNT|MAX|MIN)\b', sql_query, re.IGNORECASE))
        }
        
        # 복잡도 계산
        complexity_score = (
            analysis['join_count'] * 2 +
            analysis['subquery_count'] * 3 +
            analysis['aggregation_count'] * 1
        )
        
        if complexity_score <= 3:
            analysis['estimated_complexity'] = 'low'
        elif complexity_score <= 8:
            analysis['estimated_complexity'] = 'medium'
        else:
            analysis['estimated_complexity'] = 'high'
        
        return analysis
    
    def _calculate_complexity(self, sql_query: str) -> int:
        """쿼리 복잡도 점수 계산"""
        score = 0
        
        # 기본 점수
        score += 1
        
        # JOIN 점수
        score += len(re.findall(r'\bJOIN\b', sql_query, re.IGNORECASE)) * 2
        
        # 서브쿼리 점수
        score += len(re.findall(r'\(\s*SELECT\b', sql_query, re.IGNORECASE)) * 3
        
        # 집계 함수 점수
        score += len(re.findall(r'\b(SUM|AVG|COUNT|MAX|MIN)\b', sql_query, re.IGNORECASE))
        
        # GROUP BY 점수
        if re.search(r'\bGROUP BY\b', sql_query, re.IGNORECASE):
            score += 2
        
        # ORDER BY 점수
        if re.search(r'\bORDER BY\b', sql_query, re.IGNORECASE):
            score += 1
        
        return score


class AdvancedSQLService:
    """고급 SQL 생성 서비스"""
    
    def __init__(self):
        self.nlp = NaturalLanguageProcessor()
        self.optimizer = QueryOptimizer()
        self.schema_info = self._load_schema_info()
        
    def _load_schema_info(self) -> Dict[str, Any]:
        """데이터베이스 스키마 정보 로드"""
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            schema_info = {}
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                foreign_keys = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)
                
                schema_info[table_name] = {
                    'columns': {col['name']: col['type'] for col in columns},
                    'foreign_keys': foreign_keys,
                    'indexes': indexes
                }
            
            logger.info("스키마 정보 로드 완료", tables_count=len(tables))
            return schema_info
            
        except Exception as e:
            logger.error("스키마 정보 로드 실패", error=str(e))
            return {}
    
    def generate_advanced_sql(self, question: str) -> Dict[str, Any]:
        """고급 SQL 쿼리 생성"""
        try:
            # 자연어 파싱
            parsed = self.nlp.parse_natural_language(question)
            
            # SQL 구성 요소 생성
            sql_components = self._build_sql_components(parsed)
            
            # SQL 쿼리 조립
            sql_query = self._assemble_sql_query(sql_components)
            
            # 쿼리 최적화 및 분석
            optimization = self.optimizer.optimize_query(sql_query)
            
            # 설명 생성
            explanation = self._generate_explanation(parsed, sql_components, optimization)
            
            return {
                'success': True,
                'sql_query': sql_query,
                'parsed_intent': parsed,
                'optimization': optimization,
                'explanation': explanation,
                'complexity_score': optimization['complexity_score']
            }
            
        except Exception as e:
            logger.error("고급 SQL 생성 실패", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'sql_query': None,
                'explanation': f"SQL 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _build_sql_components(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """SQL 구성 요소 빌드"""
        components = {
            'select': self._build_select_clause(parsed),
            'from': self._build_from_clause(parsed),
            'joins': self._build_joins(parsed),
            'where': self._build_where_clause(parsed),
            'group_by': self._build_group_by(parsed),
            'having': self._build_having_clause(parsed),
            'order_by': self._build_order_by(parsed),
            'limit': self._build_limit_clause(parsed)
        }
        
        return components
    
    def _build_select_clause(self, parsed: Dict[str, Any]) -> str:
        """SELECT 절 구성"""
        select_columns = []
        
        # 엔티티 기반 컬럼 선택
        for entity in parsed['entities']:
            if entity['type'] == 'business_term':
                if 'COUNT' in entity['aggregation']:
                    select_columns.append(f"{entity['aggregation']}({entity['column']}))")
                else:
                    select_columns.append(f"{entity['aggregation']}({entity['column']})")
        
        # 그룹화 컬럼 추가
        for group_col in parsed['grouping']:
            if group_col not in select_columns:
                select_columns.append(group_col)
        
        # 기본값 설정
        if not select_columns:
            select_columns = ['*']
        
        return ', '.join(select_columns)
    
    def _build_from_clause(self, parsed: Dict[str, Any]) -> str:
        """FROM 절 구성"""
        # 주요 테이블 결정
        main_tables = set()
        for entity in parsed['entities']:
            if 'table' in entity:
                main_tables.add(entity['table'])
        
        if not main_tables:
            return 'sales'  # 기본 테이블
        
        return list(main_tables)[0]  # 첫 번째 테이블을 메인으로
    
    def _build_joins(self, parsed: Dict[str, Any]) -> List[str]:
        """JOIN 절 구성"""
        joins = []
        
        # 필요한 테이블들 수집
        required_tables = set()
        for entity in parsed['entities']:
            if 'table' in entity:
                required_tables.add(entity['table'])
        
        # 표준 JOIN 패턴
        join_patterns = [
            ("sales", "orders", "sales.order_id = orders.id"),
            ("orders", "customers", "orders.customer_id = customers.id"),
            ("orders", "order_items", "orders.id = order_items.order_id"),
            ("order_items", "products", "order_items.product_id = products.id"),
            ("products", "companies", "products.company_id = companies.id")
        ]
        
        for table1, table2, condition in join_patterns:
            if table1 in required_tables and table2 in required_tables:
                joins.append(f"JOIN {table2} ON {condition}")
        
        return joins
    
    def _build_where_clause(self, parsed: Dict[str, Any]) -> List[str]:
        """WHERE 절 구성"""
        conditions = []
        
        # 시간 조건
        conditions.extend(parsed['time_conditions'])
        
        # 필터 조건
        conditions.extend(parsed['filters'])
        
        # 엔티티 조건
        for entity in parsed['entities']:
            if 'condition' in entity:
                conditions.append(entity['condition'])
        
        return conditions
    
    def _build_group_by(self, parsed: Dict[str, Any]) -> List[str]:
        """GROUP BY 절 구성"""
        return parsed['grouping']
    
    def _build_having_clause(self, parsed: Dict[str, Any]) -> List[str]:
        """HAVING 절 구성"""
        # 집계 함수에 대한 조건
        having = []
        
        # 예: "평균 주문액이 10만원 이상인"
        for entity in parsed['entities']:
            if entity['type'] == 'business_term' and 'aggregation' in entity:
                # 추후 구현 예정
                pass
        
        return having
    
    def _build_order_by(self, parsed: Dict[str, Any]) -> Optional[str]:
        """ORDER BY 절 구성"""
        sorting = parsed['sorting']
        if not sorting:
            return None
        
        # 정렬 대상 결정
        sort_column = None
        for entity in parsed['entities']:
            if entity['type'] == 'business_term':
                if 'aggregation' in entity:
                    sort_column = f"{entity['aggregation']}({entity['column']})"
                else:
                    sort_column = entity['column']
                break
        
        if not sort_column:
            sort_column = "1"  # 첫 번째 컬럼
        
        return f"{sort_column} {sorting['direction']}"
    
    def _build_limit_clause(self, parsed: Dict[str, Any]) -> Optional[int]:
        """LIMIT 절 구성"""
        # TOP N 패턴 검색
        for agg in parsed['aggregations']:
            if 'LIMIT' in agg['function']:
                # 숫자 추출 (예: "상위 5개")
                return 5  # 기본값
        
        return None
    
    def _assemble_sql_query(self, components: Dict[str, Any]) -> str:
        """SQL 쿼리 조립"""
        query_parts = []
        
        # SELECT
        query_parts.append(f"SELECT {components['select']}")
        
        # FROM
        query_parts.append(f"FROM {components['from']}")
        
        # JOINs
        for join in components['joins']:
            query_parts.append(join)
        
        # WHERE
        if components['where']:
            query_parts.append(f"WHERE {' AND '.join(components['where'])}")
        
        # GROUP BY
        if components['group_by']:
            query_parts.append(f"GROUP BY {', '.join(components['group_by'])}")
        
        # HAVING
        if components['having']:
            query_parts.append(f"HAVING {' AND '.join(components['having'])}")
        
        # ORDER BY
        if components['order_by']:
            query_parts.append(f"ORDER BY {components['order_by']}")
        
        # LIMIT
        if components['limit']:
            query_parts.append(f"LIMIT {components['limit']}")
        
        return '\n'.join(query_parts)
    
    def _generate_explanation(self, parsed: Dict[str, Any], components: Dict[str, Any], optimization: Dict[str, Any]) -> str:
        """쿼리 설명 생성"""
        explanation_parts = []
        
        explanation_parts.append("🔍 **쿼리 분석 결과:**")
        
        # 의도 설명
        intent_descriptions = {
            'comparison': '데이터 비교 분석',
            'trend': '트렌드 분석',
            'ranking': '순위 분석',
            'distribution': '분포 분석',
            'aggregation': '집계 분석',
            'general': '일반 조회'
        }
        explanation_parts.append(f"- **분석 유형**: {intent_descriptions.get(parsed['intent'], '일반 조회')}")
        
        # 대상 테이블
        tables = set()
        for entity in parsed['entities']:
            if 'table' in entity:
                tables.add(entity['table'])
        if tables:
            explanation_parts.append(f"- **대상 테이블**: {', '.join(tables)}")
        
        # 시간 조건
        if parsed['time_conditions']:
            explanation_parts.append(f"- **시간 조건**: {len(parsed['time_conditions'])}개 적용")
        
        # 그룹화
        if parsed['grouping']:
            explanation_parts.append(f"- **그룹화**: {', '.join(parsed['grouping'])}")
        
        # 성능 정보
        complexity = optimization['performance_analysis']['estimated_complexity']
        complexity_desc = {'low': '낮음', 'medium': '보통', 'high': '높음'}
        explanation_parts.append(f"- **쿼리 복잡도**: {complexity_desc.get(complexity, '보통')} (점수: {optimization['complexity_score']})")
        
        # 최적화 제안
        if optimization['suggestions']:
            explanation_parts.append("\n💡 **최적화 제안:**")
            for suggestion in optimization['suggestions']:
                explanation_parts.append(f"- {suggestion}")
        
        return '\n'.join(explanation_parts)


# 전역 고급 SQL 서비스 인스턴스
advanced_sql_service = AdvancedSQLService()
