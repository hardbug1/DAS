"""
데이터베이스 스키마 정의 및 관리

샘플 데이터와 함께 데이터베이스 스키마를 정의하고 관리합니다.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from typing import Dict, List, Any
import structlog

from app.config.database import Base

logger = structlog.get_logger()


class Company(Base):
    """회사 정보 테이블"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="회사명")
    industry = Column(String(50), comment="업종")
    location = Column(String(100), comment="위치")
    founded_year = Column(Integer, comment="설립년도")
    employees_count = Column(Integer, comment="직원 수")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    products = relationship("Product", back_populates="company")
    sales = relationship("Sale", back_populates="company")


class Customer(Base):
    """고객 정보 테이블"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="고객명")
    email = Column(String(100), unique=True, comment="이메일")
    phone = Column(String(20), comment="전화번호")
    age = Column(Integer, comment="나이")
    gender = Column(String(10), comment="성별")
    city = Column(String(50), comment="도시")
    registration_date = Column(Date, comment="가입일")
    is_active = Column(Boolean, default=True, comment="활성 상태")
    total_spent = Column(Float, default=0.0, comment="총 구매액")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    orders = relationship("Order", back_populates="customer")


class Product(Base):
    """제품 정보 테이블"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="제품명")
    category = Column(String(50), comment="카테고리")
    brand = Column(String(50), comment="브랜드")
    price = Column(Float, nullable=False, comment="가격")
    cost = Column(Float, comment="원가")
    stock_quantity = Column(Integer, default=0, comment="재고량")
    description = Column(Text, comment="제품 설명")
    is_active = Column(Boolean, default=True, comment="판매 중 여부")
    company_id = Column(Integer, ForeignKey("companies.id"), comment="제조사 ID")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    company = relationship("Company", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    """주문 정보 테이블"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, comment="주문번호")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, comment="고객 ID")
    order_date = Column(Date, nullable=False, comment="주문일")
    total_amount = Column(Float, nullable=False, comment="총 주문 금액")
    status = Column(String(20), default="pending", comment="주문 상태")
    payment_method = Column(String(30), comment="결제 방법")
    shipping_address = Column(Text, comment="배송 주소")
    notes = Column(Text, comment="주문 메모")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """주문 항목 테이블"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="주문 ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="제품 ID")
    quantity = Column(Integer, nullable=False, comment="수량")
    unit_price = Column(Float, nullable=False, comment="단가")
    total_price = Column(Float, nullable=False, comment="총 가격")
    discount_rate = Column(Float, default=0.0, comment="할인율")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class Sale(Base):
    """매출 집계 테이블"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_date = Column(Date, nullable=False, comment="매출일")
    company_id = Column(Integer, ForeignKey("companies.id"), comment="회사 ID")
    product_category = Column(String(50), comment="제품 카테고리")
    region = Column(String(50), comment="지역")
    sales_amount = Column(Float, nullable=False, comment="매출액")
    profit = Column(Float, comment="수익")
    units_sold = Column(Integer, comment="판매 수량")
    sales_rep = Column(String(50), comment="영업 담당자")
    channel = Column(String(30), comment="판매 채널")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계 설정
    company = relationship("Company", back_populates="sales")


class DatabaseSchemaInfo:
    """데이터베이스 스키마 정보 관리"""
    
    SCHEMA_DESCRIPTION = """
    이 데이터베이스는 전자상거래 비즈니스 데이터를 저장합니다.
    
    주요 테이블:
    1. companies: 제조사/회사 정보
    2. customers: 고객 정보
    3. products: 제품 정보
    4. orders: 주문 정보
    5. order_items: 주문 상세 항목
    6. sales: 매출 집계 데이터
    
    주요 분석 가능 항목:
    - 매출 분석 (일별, 월별, 카테고리별)
    - 고객 분석 (구매 패턴, 지역별 분포)
    - 제품 분석 (인기 제품, 재고 현황)
    - 주문 분석 (주문 상태, 결제 방법)
    """
    
    @classmethod
    def get_table_info(cls) -> dict:
        """테이블 정보 반환"""
        return {
            "companies": {
                "description": "제조사/회사 정보",
                "columns": {
                    "id": "회사 ID (기본키)",
                    "name": "회사명",
                    "industry": "업종",
                    "location": "위치",
                    "founded_year": "설립년도",
                    "employees_count": "직원 수"
                }
            },
            "customers": {
                "description": "고객 정보",
                "columns": {
                    "id": "고객 ID (기본키)",
                    "name": "고객명",
                    "email": "이메일",
                    "age": "나이",
                    "gender": "성별",
                    "city": "도시",
                    "registration_date": "가입일",
                    "total_spent": "총 구매액"
                }
            },
            "products": {
                "description": "제품 정보",
                "columns": {
                    "id": "제품 ID (기본키)",
                    "name": "제품명",
                    "category": "카테고리",
                    "brand": "브랜드",
                    "price": "가격",
                    "stock_quantity": "재고량",
                    "company_id": "제조사 ID (외래키)"
                }
            },
            "orders": {
                "description": "주문 정보",
                "columns": {
                    "id": "주문 ID (기본키)",
                    "order_number": "주문번호",
                    "customer_id": "고객 ID (외래키)",
                    "order_date": "주문일",
                    "total_amount": "총 주문 금액",
                    "status": "주문 상태"
                }
            },
            "order_items": {
                "description": "주문 상세 항목",
                "columns": {
                    "id": "주문 항목 ID (기본키)",
                    "order_id": "주문 ID (외래키)",
                    "product_id": "제품 ID (외래키)",
                    "quantity": "수량",
                    "unit_price": "단가",
                    "total_price": "총 가격"
                }
            },
            "sales": {
                "description": "매출 집계 데이터",
                "columns": {
                    "id": "매출 ID (기본키)",
                    "sale_date": "매출일",
                    "company_id": "회사 ID (외래키)",
                    "product_category": "제품 카테고리",
                    "region": "지역",
                    "sales_amount": "매출액",
                    "units_sold": "판매 수량"
                }
            }
        }
    
    @classmethod
    def get_sample_queries(cls) -> list:
        """샘플 쿼리 반환"""
        return [
            {
                "question": "지난 달 총 매출은 얼마입니까?",
                "sql": "SELECT SUM(sales_amount) as total_sales FROM sales WHERE sale_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month') AND sale_date < DATE_TRUNC('month', CURRENT_DATE);",
                "description": "지난 달 전체 매출 합계 조회"
            },
            {
                "question": "가장 많이 팔린 제품 TOP 5는?",
                "sql": "SELECT p.name, SUM(oi.quantity) as total_sold FROM products p JOIN order_items oi ON p.id = oi.product_id GROUP BY p.id, p.name ORDER BY total_sold DESC LIMIT 5;",
                "description": "판매량 기준 상위 5개 제품"
            },
            {
                "question": "카테고리별 매출 현황은?",
                "sql": "SELECT product_category, SUM(sales_amount) as category_sales FROM sales GROUP BY product_category ORDER BY category_sales DESC;",
                "description": "제품 카테고리별 매출 집계"
            },
            {
                "question": "서울 고객들의 평균 구매액은?",
                "sql": "SELECT AVG(total_spent) as avg_spent FROM customers WHERE city = '서울';",
                "description": "서울 지역 고객의 평균 구매액"
            },
            {
                "question": "월별 매출 트렌드는?",
                "sql": "SELECT DATE_TRUNC('month', sale_date) as month, SUM(sales_amount) as monthly_sales FROM sales GROUP BY month ORDER BY month;",
                "description": "월별 매출 추이 분석"
            }
        ]
    
    @classmethod
    def get_schema_for_llm(cls) -> str:
        """LLM용 스키마 정보 반환"""
        table_info = cls.get_table_info()
        
        schema_text = "=== 데이터베이스 스키마 정보 ===\n\n"
        schema_text += cls.SCHEMA_DESCRIPTION + "\n\n"
        
        for table_name, info in table_info.items():
            schema_text += f"테이블: {table_name}\n"
            schema_text += f"설명: {info['description']}\n"
            schema_text += "컬럼:\n"
            
            for col_name, col_desc in info['columns'].items():
                schema_text += f"  - {col_name}: {col_desc}\n"
            
            schema_text += "\n"
        
        return schema_text
    
    @classmethod
    def get_relationships_info(cls) -> str:
        """테이블 관계 정보 반환"""
        return """
        === 테이블 관계 정보 ===
        
        1. companies (1) → products (N): company_id
        2. companies (1) → sales (N): company_id
        3. customers (1) → orders (N): customer_id
        4. products (1) → order_items (N): product_id
        5. orders (1) → order_items (N): order_id
        
        주요 조인 패턴:
        - 제품과 제조사: products JOIN companies ON products.company_id = companies.id
        - 주문과 고객: orders JOIN customers ON orders.customer_id = customers.id
        - 주문 상세: orders JOIN order_items ON orders.id = order_items.order_id
        - 제품 판매량: products JOIN order_items ON products.id = order_items.product_id
        """


class DatabaseSchemaInfo:
    """데이터베이스 스키마 정보 제공 클래스"""
    
    def __init__(self):
        self.engine = engine
    
    def get_table_info(self) -> Dict[str, Dict[str, Any]]:
        """테이블 정보 반환"""
        return {
            'companies': {
                'description': '회사 정보 테이블',
                'columns': {
                    'id': '회사 ID (Primary Key)',
                    'name': '회사명',
                    'industry': '업종',
                    'country': '국가',
                    'founded_date': '설립일',
                    'description': '회사 설명'
                }
            },
            'customers': {
                'description': '고객 정보 테이블',
                'columns': {
                    'id': '고객 ID (Primary Key)',
                    'name': '고객명',
                    'email': '이메일',
                    'phone': '전화번호',
                    'age': '나이',
                    'gender': '성별',
                    'city': '거주 도시',
                    'registration_date': '가입일',
                    'is_active': '활성 상태',
                    'total_spent': '총 구매액'
                }
            },
            'products': {
                'description': '제품 정보 테이블',
                'columns': {
                    'id': '제품 ID (Primary Key)',
                    'name': '제품명',
                    'category': '카테고리',
                    'price': '가격',
                    'stock_quantity': '재고량',
                    'company_id': '제조회사 ID (Foreign Key)',
                    'description': '제품 설명'
                }
            },
            'orders': {
                'description': '주문 정보 테이블',
                'columns': {
                    'id': '주문 ID (Primary Key)',
                    'customer_id': '고객 ID (Foreign Key)',
                    'order_date': '주문일',
                    'total_amount': '총 주문금액',
                    'status': '주문 상태',
                    'shipping_address': '배송 주소'
                }
            },
            'order_items': {
                'description': '주문 상세 항목 테이블',
                'columns': {
                    'id': '주문 항목 ID (Primary Key)',
                    'order_id': '주문 ID (Foreign Key)',
                    'product_id': '제품 ID (Foreign Key)',
                    'quantity': '수량',
                    'unit_price': '단가',
                    'total_price': '총 가격'
                }
            },
            'sales': {
                'description': '매출 기록 테이블',
                'columns': {
                    'id': '매출 ID (Primary Key)',
                    'sale_date': '매출 날짜',
                    'total_amount': '매출 금액',
                    'order_count': '주문 건수',
                    'average_order_value': '평균 주문가치'
                }
            }
        }
    
    def get_schema_for_llm(self) -> str:
        """LLM을 위한 스키마 정보 문자열"""
        table_info = self.get_table_info()
        schema_text = "데이터베이스 스키마 정보:\n\n"
        
        for table_name, info in table_info.items():
            schema_text += f"테이블: {table_name}\n"
            schema_text += f"설명: {info['description']}\n"
            schema_text += "컬럼:\n"
            for col_name, col_desc in info['columns'].items():
                schema_text += f"  - {col_name}: {col_desc}\n"
            schema_text += "\n"
        
        return schema_text
    
    def get_relationships_info(self) -> str:
        """테이블 관계 정보"""
        return """
테이블 관계:
- companies (1) ← (N) products (company_id)
- customers (1) ← (N) orders (customer_id)  
- orders (1) ← (N) order_items (order_id)
- products (1) ← (N) order_items (product_id)
- 매출은 일별로 집계된 데이터

주요 JOIN 패턴:
- 매출 분석: sales (일별 집계 데이터)
- 제품 분석: products ⟵ order_items ⟵ orders
- 고객 구매 분석: customers ⟵ orders ⟵ order_items ⟵ products
"""
    
    def get_sample_queries(self) -> List[Dict[str, str]]:
        """샘플 쿼리 목록"""
        return [
            {
                'description': '월별 총 매출',
                'sql': 'SELECT EXTRACT(MONTH FROM sale_date) as month, SUM(total_amount) as total_sales FROM sales GROUP BY EXTRACT(MONTH FROM sale_date) ORDER BY month'
            },
            {
                'description': '카테고리별 제품 수',
                'sql': 'SELECT category, COUNT(*) as product_count FROM products GROUP BY category ORDER BY product_count DESC'
            },
            {
                'description': '고객별 총 구매액',
                'sql': 'SELECT c.name, SUM(o.total_amount) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id, c.name ORDER BY total_spent DESC LIMIT 10'
            },
            {
                'description': '지역별 고객 수',
                'sql': 'SELECT city, COUNT(*) as customer_count FROM customers GROUP BY city ORDER BY customer_count DESC'
            }
        ]
