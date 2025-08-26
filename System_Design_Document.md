# 🏗️ AI 데이터 분석 비서 - 시스템 설계 문서

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-Design-yellow.svg)
![Architecture](https://img.shields.io/badge/architecture-Gradio%20%2B%20LangChain-green.svg)

---

**📋 기반 문서**: [PRD_LLM_Data_Analysis_Service.md](./PRD_LLM_Data_Analysis_Service.md)  
**🎨 UI 와이어프레임**: [gradio_ui_wireframe.svg](./gradio_ui_wireframe.svg)

</div>

## 📋 문서 개요

### 🎯 목적
이 문서는 **AI 데이터 분석 비서** 시스템의 기술적 설계를 상세히 정의하여, 개발팀이 일관된 아키텍처로 구현할 수 있도록 가이드를 제공합니다.

### 📚 문서 범위
- 시스템 아키텍처 설계
- 컴포넌트 및 모듈 설계  
- API 인터페이스 정의
- 데이터베이스 스키마 설계
- 보안 및 성능 고려사항

---

## 🏗️ 시스템 아키텍처

### 🎯 전체 아키텍처 개요

```mermaid
graph TB
    subgraph "🌐 Client Layer"
        UI[Gradio Web UI]
        Mobile[Mobile Browser]
    end
    
    subgraph "🎨 Presentation Layer"
        GradioApp[Gradio Application]
        ChatInterface[Chat Interface]
        FileUpload[File Upload Handler]
        ChartRenderer[Chart Renderer]
    end
    
    subgraph "🧠 Business Logic Layer"
        QueryProcessor[Query Processor]
        LangChainAgent[LangChain Agent]
        DataAnalyzer[Data Analyzer]
        ChartGenerator[Chart Generator]
    end
    
    subgraph "🔧 Service Layer"
        NLPService[NLP Service]
        SQLService[SQL Service]
        FileService[File Service]
        CacheService[Cache Service]
    end
    
    subgraph "📊 Data Access Layer"
        DatabaseORM[SQLAlchemy ORM]
        FileManager[File Manager]
        APIClient[OpenAI API Client]
    end
    
    subgraph "🗄️ Storage Layer"
        PostgreSQL[(PostgreSQL)]
        SQLite[(SQLite)]
        FileStorage[File Storage]
        Redis[(Redis Cache)]
    end
    
    subgraph "🌍 External Services"
        OpenAI[OpenAI GPT-4 API]
        PlotlyService[Plotly Service]
    end
    
    UI --> GradioApp
    Mobile --> GradioApp
    GradioApp --> QueryProcessor
    GradioApp --> FileUpload
    GradioApp --> ChartRenderer
    
    QueryProcessor --> LangChainAgent
    QueryProcessor --> DataAnalyzer
    LangChainAgent --> NLPService
    DataAnalyzer --> SQLService
    DataAnalyzer --> FileService
    ChartGenerator --> ChartRenderer
    
    NLPService --> APIClient
    SQLService --> DatabaseORM
    FileService --> FileManager
    CacheService --> Redis
    
    DatabaseORM --> PostgreSQL
    DatabaseORM --> SQLite
    FileManager --> FileStorage
    APIClient --> OpenAI
    ChartRenderer --> PlotlyService
```

### 🎯 레이어별 책임

| 레이어 | 주요 책임 | 기술 스택 |
|--------|-----------|-----------|
| **🌐 Client** | 사용자 인터페이스 제공 | HTML5, CSS3, JavaScript |
| **🎨 Presentation** | UI 컴포넌트 관리 | Gradio 4.0+, Plotly |
| **🧠 Business Logic** | 핵심 비즈니스 로직 처리 | Python, LangChain |
| **🔧 Service** | 외부 서비스 연동 | FastAPI, Pandas |
| **📊 Data Access** | 데이터 접근 추상화 | SQLAlchemy, File I/O |
| **🗄️ Storage** | 데이터 저장 및 관리 | PostgreSQL, Redis |

---

## 🧩 컴포넌트 설계

### 1. 🤖 Query Processor (질의 처리기)

```python
class QueryProcessor:
    """자연어 질의를 분석하고 적절한 처리 경로로 라우팅"""
    
    def __init__(self):
        self.langchain_agent = LangChainAgent()
        self.query_classifier = QueryClassifier()
        self.cache_service = CacheService()
    
    async def process_query(self, query: str, context: dict) -> QueryResult:
        """
        질의 처리 메인 플로우
        
        Args:
            query: 사용자 자연어 질의
            context: 세션 컨텍스트 (업로드된 파일, DB 연결 등)
            
        Returns:
            QueryResult: 처리 결과 (텍스트, 데이터, 차트)
        """
        # 1. 캐시 확인
        cached_result = await self.cache_service.get(query)
        if cached_result:
            return cached_result
            
        # 2. 질의 분류 (DB vs File vs Mixed)
        query_type = self.query_classifier.classify(query, context)
        
        # 3. 적절한 처리기로 라우팅
        if query_type == QueryType.DATABASE:
            result = await self._process_db_query(query, context)
        elif query_type == QueryType.FILE:
            result = await self._process_file_query(query, context)
        else:
            result = await self._process_mixed_query(query, context)
            
        # 4. 결과 캐싱
        await self.cache_service.set(query, result)
        
        return result
```

### 2. 🧠 LangChain Agent (AI 에이전트)

```python
class LangChainAgent:
    """LangChain 기반 AI 에이전트"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.sql_chain = SQLDatabaseChain.from_llm(self.llm)
        self.pandas_agent = create_pandas_dataframe_agent(self.llm)
        
    async def generate_sql(self, query: str, schema: dict) -> str:
        """자연어를 SQL로 변환"""
        prompt = self._build_sql_prompt(query, schema)
        sql = await self.sql_chain.arun(prompt)
        return self._validate_sql(sql)
        
    async def analyze_dataframe(self, df: pd.DataFrame, query: str) -> dict:
        """DataFrame 분석 수행"""
        analysis_result = await self.pandas_agent.arun(
            f"Analyze this data and answer: {query}"
        )
        return self._parse_analysis_result(analysis_result)
```

### 3. 📊 Data Analyzer (데이터 분석기)

```python
class DataAnalyzer:
    """데이터 분석 및 인사이트 생성"""
    
    def __init__(self):
        self.sql_service = SQLService()
        self.file_service = FileService()
        self.chart_generator = ChartGenerator()
        
    async def analyze_sql_data(self, sql: str, connection: str) -> AnalysisResult:
        """SQL 쿼리 실행 및 분석"""
        # 1. 안전한 SQL 실행
        df = await self.sql_service.execute_query(sql, connection)
        
        # 2. 기본 통계 생성
        stats = self._generate_statistics(df)
        
        # 3. 적절한 차트 선택 및 생성
        chart = await self.chart_generator.create_chart(df, stats)
        
        # 4. 인사이트 생성
        insights = self._generate_insights(df, stats)
        
        return AnalysisResult(
            data=df,
            statistics=stats,
            chart=chart,
            insights=insights
        )
        
    def _generate_statistics(self, df: pd.DataFrame) -> dict:
        """기술통계 생성"""
        return {
            'shape': df.shape,
            'dtypes': df.dtypes.to_dict(),
            'describe': df.describe().to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'correlations': df.corr().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 1 else None
        }
```

### 4. 📈 Chart Generator (차트 생성기)

```python
class ChartGenerator:
    """데이터 특성에 맞는 차트 자동 생성"""
    
    def __init__(self):
        self.chart_rules = ChartSelectionRules()
        
    async def create_chart(self, df: pd.DataFrame, stats: dict) -> dict:
        """최적 차트 자동 선택 및 생성"""
        # 1. 데이터 특성 분석
        data_profile = self._analyze_data_profile(df, stats)
        
        # 2. 차트 타입 선택
        chart_type = self.chart_rules.select_chart_type(data_profile)
        
        # 3. 차트 생성
        chart_config = self._generate_chart_config(df, chart_type, data_profile)
        
        return {
            'type': chart_type,
            'config': chart_config,
            'plotly_json': self._create_plotly_chart(chart_config)
        }
        
    def _analyze_data_profile(self, df: pd.DataFrame, stats: dict) -> DataProfile:
        """데이터 프로파일 분석"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        return DataProfile(
            row_count=len(df),
            numeric_columns=numeric_cols,
            categorical_columns=categorical_cols,
            datetime_columns=datetime_cols,
            has_time_series=len(datetime_cols) > 0,
            cardinality={col: df[col].nunique() for col in categorical_cols}
        )
```

---

## 🗄️ 데이터베이스 설계

### 📋 ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    USER {
        string user_id PK
        string username
        string email
        datetime created_at
        datetime last_login
        json preferences
    }
    
    SESSION {
        string session_id PK
        string user_id FK
        datetime created_at
        datetime expires_at
        json context
        boolean is_active
    }
    
    QUERY_HISTORY {
        string query_id PK
        string session_id FK
        string user_query
        string query_type
        json sql_generated
        json result_data
        json chart_config
        datetime executed_at
        float execution_time
        boolean is_successful
    }
    
    UPLOADED_FILE {
        string file_id PK
        string session_id FK
        string original_filename
        string stored_filename
        string file_type
        integer file_size
        string file_hash
        datetime uploaded_at
        datetime expires_at
        json metadata
    }
    
    DATABASE_CONNECTION {
        string connection_id PK
        string user_id FK
        string connection_name
        string db_type
        string host
        integer port
        string database_name
        string username
        string encrypted_password
        json schema_cache
        datetime created_at
        datetime last_used
        boolean is_active
    }
    
    CACHE_ENTRY {
        string cache_key PK
        string query_hash
        json cached_result
        datetime created_at
        datetime expires_at
        integer hit_count
    }
    
    USER ||--o{ SESSION : has
    SESSION ||--o{ QUERY_HISTORY : contains
    SESSION ||--o{ UPLOADED_FILE : uploads
    USER ||--o{ DATABASE_CONNECTION : owns
    QUERY_HISTORY }o--|| CACHE_ENTRY : cached_as
```

### 🏗️ 테이블 스키마

#### 1. Users 테이블
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

#### 2. Sessions 테이블
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    context JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_active (is_active)
);
```

#### 3. Query History 테이블
```sql
CREATE TABLE query_history (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(session_id) ON DELETE CASCADE,
    user_query TEXT NOT NULL,
    query_type VARCHAR(20) NOT NULL CHECK (query_type IN ('database', 'file', 'mixed')),
    sql_generated JSONB,
    result_data JSONB,
    chart_config JSONB,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time FLOAT,
    is_successful BOOLEAN NOT NULL,
    
    INDEX idx_session_id (session_id),
    INDEX idx_executed_at (executed_at),
    INDEX idx_query_type (query_type),
    INDEX idx_is_successful (is_successful)
);
```

---

## 🔌 API 설계

### 🎯 RESTful API 엔드포인트

#### 1. 질의 처리 API

```python
# POST /api/v1/query
{
    "query": "지난 3개월 매출 추이를 보여줘",
    "session_id": "uuid",
    "context": {
        "uploaded_files": ["file_id_1"],
        "database_connection": "connection_id_1"
    }
}

# Response
{
    "query_id": "uuid",
    "status": "success",
    "execution_time": 2.34,
    "result": {
        "text_response": "지난 3개월 매출은 꾸준히 증가하는 추세입니다.",
        "data": {
            "columns": ["month", "revenue"],
            "rows": [["2024-01", 1000000], ["2024-02", 1200000], ["2024-03", 1500000]]
        },
        "chart": {
            "type": "line",
            "plotly_json": {...}
        },
        "insights": [
            "매월 평균 20% 성장률을 보이고 있습니다.",
            "3월에 가장 높은 매출을 기록했습니다."
        ]
    }
}
```

#### 2. 파일 업로드 API

```python
# POST /api/v1/files/upload
# Content-Type: multipart/form-data
{
    "file": <binary_data>,
    "session_id": "uuid"
}

# Response
{
    "file_id": "uuid",
    "original_filename": "sales_data.xlsx",
    "file_size": 1024000,
    "columns": ["date", "product", "revenue", "quantity"],
    "row_count": 10000,
    "preview": [
        {"date": "2024-01-01", "product": "A", "revenue": 1000, "quantity": 10},
        {"date": "2024-01-02", "product": "B", "revenue": 1500, "quantity": 15}
    ]
}
```

#### 3. 데이터베이스 연결 API

```python
# POST /api/v1/database/connect
{
    "connection_name": "Production DB",
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "sales_db",
    "username": "analyst",
    "password": "encrypted_password"
}

# Response
{
    "connection_id": "uuid",
    "status": "connected",
    "schema": {
        "tables": [
            {
                "name": "sales",
                "columns": [
                    {"name": "id", "type": "integer", "nullable": false},
                    {"name": "date", "type": "date", "nullable": false},
                    {"name": "amount", "type": "decimal", "nullable": false}
                ]
            }
        ]
    }
}
```

### 🔄 WebSocket API (실시간 처리)

```python
# WebSocket /ws/query/{session_id}

# Client -> Server
{
    "type": "query_start",
    "query": "복잡한 분석 질의...",
    "context": {...}
}

# Server -> Client (Progress Updates)
{
    "type": "progress",
    "stage": "sql_generation",
    "progress": 25,
    "message": "SQL 쿼리를 생성하고 있습니다..."
}

{
    "type": "progress", 
    "stage": "data_processing",
    "progress": 75,
    "message": "데이터를 분석하고 있습니다..."
}

# Server -> Client (Final Result)
{
    "type": "query_complete",
    "result": {...}
}
```

---

## 🛡️ 보안 설계

### 🔐 인증 및 권한 관리

```python
class SecurityManager:
    """보안 관리자"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET')
        self.password_hasher = PasswordHasher()
        
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """사용자 인증"""
        user = self.user_repository.get_by_username(username)
        if user and self.password_hasher.verify(password, user.password_hash):
            return user
        return None
        
    def generate_session_token(self, user: User) -> str:
        """세션 토큰 생성"""
        payload = {
            'user_id': str(user.user_id),
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
```

### 🛡️ SQL Injection 방지

```python
class SQLSecurityValidator:
    """SQL 보안 검증기"""
    
    FORBIDDEN_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
        'TRUNCATE', 'EXEC', 'EXECUTE', 'GRANT', 'REVOKE'
    ]
    
    def validate_sql(self, sql: str) -> bool:
        """SQL 안전성 검증"""
        # 1. 금지된 키워드 확인
        sql_upper = sql.upper()
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                raise SecurityError(f"Forbidden keyword detected: {keyword}")
                
        # 2. SELECT 문만 허용
        if not sql_upper.strip().startswith('SELECT'):
            raise SecurityError("Only SELECT statements are allowed")
            
        # 3. 파라미터화된 쿼리 강제
        if ';' in sql and sql.count(';') > 1:
            raise SecurityError("Multiple statements not allowed")
            
        return True
```

### 🔒 데이터 암호화

```python
class DataEncryption:
    """데이터 암호화 관리"""
    
    def __init__(self):
        self.fernet = Fernet(os.getenv('ENCRYPTION_KEY'))
        
    def encrypt_sensitive_data(self, data: str) -> str:
        """민감한 데이터 암호화 (DB 비밀번호 등)"""
        return self.fernet.encrypt(data.encode()).decode()
        
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """암호화된 데이터 복호화"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
```

---

## ⚡ 성능 최적화

### 🚀 캐싱 전략

```python
class CacheService:
    """다층 캐싱 서비스"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.memory_cache = {}
        
    async def get_query_result(self, query_hash: str) -> Optional[dict]:
        """쿼리 결과 캐시 조회"""
        # 1. 메모리 캐시 확인 (가장 빠름)
        if query_hash in self.memory_cache:
            return self.memory_cache[query_hash]
            
        # 2. Redis 캐시 확인
        cached_data = await self.redis_client.get(f"query:{query_hash}")
        if cached_data:
            result = json.loads(cached_data)
            # 메모리 캐시에도 저장
            self.memory_cache[query_hash] = result
            return result
            
        return None
        
    async def cache_query_result(self, query_hash: str, result: dict, ttl: int = 3600):
        """쿼리 결과 캐싱"""
        # Redis에 저장 (TTL 적용)
        await self.redis_client.setex(
            f"query:{query_hash}", 
            ttl, 
            json.dumps(result)
        )
        
        # 메모리 캐시에도 저장 (크기 제한)
        if len(self.memory_cache) < 100:
            self.memory_cache[query_hash] = result
```

### 📊 데이터 처리 최적화

```python
class DataProcessor:
    """대용량 데이터 처리 최적화"""
    
    def __init__(self):
        self.chunk_size = 10000
        self.max_memory_usage = 500 * 1024 * 1024  # 500MB
        
    async def process_large_dataset(self, df: pd.DataFrame) -> dict:
        """대용량 데이터셋 처리"""
        if len(df) > self.chunk_size:
            return await self._process_in_chunks(df)
        else:
            return await self._process_full_dataset(df)
            
    async def _process_in_chunks(self, df: pd.DataFrame) -> dict:
        """청크 단위 처리"""
        results = []
        
        for chunk_start in range(0, len(df), self.chunk_size):
            chunk_end = min(chunk_start + self.chunk_size, len(df))
            chunk = df.iloc[chunk_start:chunk_end]
            
            # 메모리 사용량 모니터링
            if self._get_memory_usage() > self.max_memory_usage:
                gc.collect()  # 가비지 컬렉션 강제 실행
                
            chunk_result = await self._analyze_chunk(chunk)
            results.append(chunk_result)
            
        return self._merge_chunk_results(results)
```

---

## 📊 모니터링 및 로깅

### 📈 성능 모니터링

```python
class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        
    @contextmanager
    def measure_execution_time(self, operation_name: str):
        """실행 시간 측정"""
        start_time = time.time()
        try:
            yield
        finally:
            execution_time = time.time() - start_time
            self.metrics_collector.record_execution_time(
                operation_name, 
                execution_time
            )
            
    def record_query_metrics(self, query_type: str, success: bool, execution_time: float):
        """쿼리 메트릭 기록"""
        self.metrics_collector.increment_counter(
            f"queries.{query_type}.{'success' if success else 'failure'}"
        )
        self.metrics_collector.record_histogram(
            f"query_execution_time.{query_type}",
            execution_time
        )
```

### 📝 구조화된 로깅

```python
import structlog

class LoggingConfig:
    """로깅 설정"""
    
    @staticmethod
    def setup_logging():
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

# 사용 예시
logger = structlog.get_logger()

async def process_query(query: str, session_id: str):
    logger.info(
        "Query processing started",
        query=query,
        session_id=session_id,
        user_id=current_user.id
    )
    
    try:
        result = await query_processor.process(query)
        logger.info(
            "Query processing completed",
            query=query,
            session_id=session_id,
            execution_time=result.execution_time,
            result_rows=len(result.data)
        )
        return result
    except Exception as e:
        logger.error(
            "Query processing failed",
            query=query,
            session_id=session_id,
            error=str(e),
            exc_info=True
        )
        raise
```

---

## 🚀 배포 아키텍처

### 🐳 Docker 컨테이너 구성

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aianalyst
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./uploads:/app/uploads
      
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=aianalyst
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app

volumes:
  postgres_data:
  redis_data:
```

### ☸️ Kubernetes 배포 (선택사항)

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-analyst-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-analyst
  template:
    metadata:
      labels:
        app: ai-analyst
    spec:
      containers:
      - name: app
        image: ai-analyst:latest
        ports:
        - containerPort: 7860
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## 📋 개발 가이드라인

### 🏗️ 프로젝트 구조

```
ai-data-analyst/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Gradio 앱 엔트리포인트
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # 설정 관리
│   │   └── database.py         # DB 연결 설정
│   ├── core/
│   │   ├── __init__.py
│   │   ├── query_processor.py  # 질의 처리기
│   │   ├── langchain_agent.py  # LangChain 에이전트
│   │   └── data_analyzer.py    # 데이터 분석기
│   ├── services/
│   │   ├── __init__.py
│   │   ├── nlp_service.py      # NLP 서비스
│   │   ├── sql_service.py      # SQL 서비스
│   │   ├── file_service.py     # 파일 서비스
│   │   └── cache_service.py    # 캐시 서비스
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py         # SQLAlchemy 모델
│   │   └── schemas.py          # Pydantic 스키마
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py         # 보안 유틸리티
│   │   ├── validators.py       # 검증 로직
│   │   └── helpers.py          # 헬퍼 함수
│   └── ui/
│       ├── __init__.py
│       ├── components.py       # Gradio 컴포넌트
│       └── layouts.py          # UI 레이아웃
├── tests/
│   ├── __init__.py
│   ├── test_query_processor.py
│   ├── test_data_analyzer.py
│   └── test_services.py
├── docs/
│   ├── api.md
│   ├── deployment.md
│   └── user_guide.md
├── scripts/
│   ├── setup_db.py
│   └── migrate_data.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 🧪 테스트 전략

```python
# tests/test_query_processor.py
import pytest
from app.core.query_processor import QueryProcessor

class TestQueryProcessor:
    
    @pytest.fixture
    def query_processor(self):
        return QueryProcessor()
        
    @pytest.mark.asyncio
    async def test_process_db_query(self, query_processor):
        """DB 질의 처리 테스트"""
        query = "Show me sales data for last month"
        context = {"database_connection": "test_db"}
        
        result = await query_processor.process_query(query, context)
        
        assert result.status == "success"
        assert result.query_type == "database"
        assert result.data is not None
        
    @pytest.mark.asyncio
    async def test_process_file_query(self, query_processor):
        """파일 질의 처리 테스트"""
        query = "Analyze the uploaded sales data"
        context = {"uploaded_files": ["test_file.xlsx"]}
        
        result = await query_processor.process_query(query, context)
        
        assert result.status == "success"
        assert result.query_type == "file"
```

---

## 📚 참고 문서

### 🔗 관련 문서
- [PRD_LLM_Data_Analysis_Service.md](./PRD_LLM_Data_Analysis_Service.md) - 제품 요구사항 문서
- [gradio_ui_wireframe.svg](./gradio_ui_wireframe.svg) - UI 와이어프레임
- [wireframe_guide.md](./wireframe_guide.md) - UI 구현 가이드

### 📖 기술 문서
- [Gradio Documentation](https://gradio.app/docs/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Plotly Documentation](https://plotly.com/python/)

---

<div align="center">

**📅 문서 버전**: v1.0.0  
**📝 최종 수정**: 2024년 1월  
**👥 작성자**: AI 데이터 분석 비서 개발팀

---

*이 설계 문서는 PRD를 기반으로 작성되었으며, 개발 과정에서 지속적으로 업데이트됩니다.*

</div>
