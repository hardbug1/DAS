#!/usr/bin/env python3
"""
샘플 데이터 생성 스크립트

데이터베이스에 테스트용 샘플 데이터를 생성합니다.
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
import random
from faker import Faker

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.database import SessionLocal, engine
from app.core.database_schema import (
    Base, Company, Customer, Product, Order, OrderItem, Sale
)
import structlog

# 로깅 설정
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Faker 인스턴스 생성 (한국어)
fake = Faker('ko_KR')
Faker.seed(42)  # 재현 가능한 데이터 생성


class SampleDataCreator:
    """샘플 데이터 생성기"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.companies = []
        self.customers = []
        self.products = []
        self.orders = []
    
    def create_all_sample_data(self):
        """모든 샘플 데이터 생성"""
        try:
            logger.info("샘플 데이터 생성 시작")
            
            # 기존 데이터 확인
            if self._check_existing_data():
                logger.info("이미 샘플 데이터가 존재합니다.")
                choice = input("기존 데이터를 삭제하고 새로 생성하시겠습니까? (y/N): ")
                if choice.lower() != 'y':
                    return
                
                self._clear_existing_data()
            
            # 단계별 데이터 생성
            self._create_companies()
            self._create_customers()
            self._create_products()
            self._create_orders()
            self._create_order_items()
            self._create_sales_data()
            
            self.db.commit()
            logger.info("샘플 데이터 생성 완료")
            
            # 생성된 데이터 요약
            self._print_data_summary()
            
        except Exception as e:
            logger.error("샘플 데이터 생성 실패", error=str(e))
            self.db.rollback()
            raise
        finally:
            self.db.close()
    
    def _check_existing_data(self) -> bool:
        """기존 데이터 존재 여부 확인"""
        company_count = self.db.query(Company).count()
        return company_count > 0
    
    def _clear_existing_data(self):
        """기존 데이터 삭제"""
        logger.info("기존 데이터 삭제 중...")
        
        # 외래키 순서를 고려하여 삭제
        self.db.query(Sale).delete()
        self.db.query(OrderItem).delete()
        self.db.query(Order).delete()
        self.db.query(Product).delete()
        self.db.query(Customer).delete()
        self.db.query(Company).delete()
        
        self.db.commit()
        logger.info("기존 데이터 삭제 완료")
    
    def _create_companies(self):
        """회사 데이터 생성"""
        logger.info("회사 데이터 생성 중...")
        
        company_data = [
            {"name": "삼성전자", "industry": "전자제품", "location": "수원", "founded_year": 1969, "employees_count": 105000},
            {"name": "LG전자", "industry": "전자제품", "location": "서울", "founded_year": 1958, "employees_count": 75000},
            {"name": "네이버", "industry": "IT서비스", "location": "판교", "founded_year": 1999, "employees_count": 3500},
            {"name": "카카오", "industry": "IT서비스", "location": "판교", "founded_year": 1995, "employees_count": 4500},
            {"name": "현대자동차", "industry": "자동차", "location": "울산", "founded_year": 1967, "employees_count": 110000},
            {"name": "아모레퍼시픽", "industry": "화장품", "location": "서울", "founded_year": 1945, "employees_count": 6000},
            {"name": "CJ제일제당", "industry": "식품", "location": "서울", "founded_year": 1953, "employees_count": 4200},
            {"name": "신세계", "industry": "유통", "location": "서울", "founded_year": 1955, "employees_count": 25000},
            {"name": "롯데", "industry": "식품", "location": "서울", "founded_year": 1948, "employees_count": 35000},
            {"name": "SK하이닉스", "industry": "반도체", "location": "이천", "founded_year": 1983, "employees_count": 30000}
        ]
        
        for data in company_data:
            company = Company(**data)
            self.db.add(company)
            self.companies.append(company)
        
        self.db.flush()  # ID 생성을 위해
        logger.info(f"회사 {len(self.companies)}개 생성 완료")
    
    def _create_customers(self):
        """고객 데이터 생성"""
        logger.info("고객 데이터 생성 중...")
        
        cities = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "수원", "창원", "성남"]
        genders = ["남성", "여성"]
        
        used_emails = set()
        for i in range(500):  # 500명의 고객
            registration_date = fake.date_between(start_date='-2y', end_date='today')
            
            # 중복되지 않는 이메일 생성
            email = fake.email()
            while email in used_emails:
                email = fake.email()
            used_emails.add(email)
            
            customer = Customer(
                name=fake.name(),
                email=email,
                phone=fake.phone_number(),
                age=random.randint(20, 70),
                gender=random.choice(genders),
                city=random.choice(cities),
                registration_date=registration_date,
                is_active=random.choice([True, True, True, False]),  # 75% 활성
                total_spent=round(random.uniform(0, 500000), 2)
            )
            
            self.db.add(customer)
            self.customers.append(customer)
        
        self.db.flush()
        logger.info(f"고객 {len(self.customers)}명 생성 완료")
    
    def _create_products(self):
        """제품 데이터 생성"""
        logger.info("제품 데이터 생성 중...")
        
        # 카테고리별 제품 데이터
        product_templates = {
            "스마트폰": [
                {"name": "갤럭시 S24", "brand": "삼성", "price": 1200000, "cost": 800000},
                {"name": "갤럭시 노트", "brand": "삼성", "price": 1400000, "cost": 900000},
                {"name": "아이폰 15", "brand": "애플", "price": 1300000, "cost": 850000},
                {"name": "아이폰 Pro", "brand": "애플", "price": 1600000, "cost": 1000000},
                {"name": "LG 윙", "brand": "LG", "price": 900000, "cost": 600000},
            ],
            "노트북": [
                {"name": "갤럭시북", "brand": "삼성", "price": 1500000, "cost": 1000000},
                {"name": "그램 17", "brand": "LG", "price": 1800000, "cost": 1200000},
                {"name": "맥북 에어", "brand": "애플", "price": 1600000, "cost": 1050000},
                {"name": "맥북 프로", "brand": "애플", "price": 2200000, "cost": 1400000},
            ],
            "가전제품": [
                {"name": "냉장고", "brand": "삼성", "price": 800000, "cost": 500000},
                {"name": "세탁기", "brand": "LG", "price": 600000, "cost": 400000},
                {"name": "에어컨", "brand": "삼성", "price": 1000000, "cost": 650000},
                {"name": "TV", "brand": "LG", "price": 1200000, "cost": 800000},
            ],
            "화장품": [
                {"name": "크림", "brand": "아모레", "price": 50000, "cost": 20000},
                {"name": "립스틱", "brand": "아모레", "price": 30000, "cost": 12000},
                {"name": "파운데이션", "brand": "아모레", "price": 40000, "cost": 16000},
            ],
            "식품": [
                {"name": "라면", "brand": "CJ", "price": 5000, "cost": 2000},
                {"name": "과자", "brand": "롯데", "price": 3000, "cost": 1200},
                {"name": "음료", "brand": "CJ", "price": 2000, "cost": 800},
            ]
        }
        
        for category, items in product_templates.items():
            for item in items:
                # 여러 변형 생성
                for i in range(random.randint(2, 4)):
                    company = random.choice(self.companies)
                    
                    product = Product(
                        name=f"{item['name']} {i+1}",
                        category=category,
                        brand=item['brand'],
                        price=item['price'] + random.randint(-100000, 100000),
                        cost=item['cost'] + random.randint(-50000, 50000),
                        stock_quantity=random.randint(10, 1000),
                        description=fake.text(max_nb_chars=200),
                        is_active=random.choice([True, True, True, False]),
                        company_id=company.id
                    )
                    
                    self.db.add(product)
                    self.products.append(product)
        
        self.db.flush()
        logger.info(f"제품 {len(self.products)}개 생성 완료")
    
    def _create_orders(self):
        """주문 데이터 생성"""
        logger.info("주문 데이터 생성 중...")
        
        statuses = ["completed", "completed", "completed", "pending", "shipped", "cancelled"]
        payment_methods = ["신용카드", "체크카드", "계좌이체", "카카오페이", "네이버페이"]
        
        for i in range(1000):  # 1000개의 주문
            customer = random.choice(self.customers)
            order_date = fake.date_between(start_date='-1y', end_date='today')
            
            order = Order(
                order_number=f"ORD{datetime.now().year}{i+1:06d}",
                customer_id=customer.id,
                order_date=order_date,
                total_amount=0,  # order_items 생성 후 계산
                status=random.choice(statuses),
                payment_method=random.choice(payment_methods),
                shipping_address=fake.address(),
                notes=fake.text(max_nb_chars=100) if random.random() < 0.3 else None
            )
            
            self.db.add(order)
            self.orders.append(order)
        
        self.db.flush()
        logger.info(f"주문 {len(self.orders)}개 생성 완료")
    
    def _create_order_items(self):
        """주문 항목 데이터 생성"""
        logger.info("주문 항목 데이터 생성 중...")
        
        for order in self.orders:
            # 주문당 1-5개의 항목
            num_items = random.randint(1, 5)
            total_amount = 0
            
            selected_products = random.sample(
                [p for p in self.products if p.is_active], 
                min(num_items, len([p for p in self.products if p.is_active]))
            )
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.price
                discount_rate = random.choice([0, 0, 0, 0.05, 0.1, 0.15])  # 할인 적용
                discounted_price = unit_price * (1 - discount_rate)
                total_price = discounted_price * quantity
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                    discount_rate=discount_rate
                )
                
                self.db.add(order_item)
                total_amount += total_price
            
            # 주문 총액 업데이트
            order.total_amount = total_amount
        
        logger.info("주문 항목 생성 완료")
    
    def _create_sales_data(self):
        """매출 집계 데이터 생성"""
        logger.info("매출 데이터 생성 중...")
        
        categories = ["스마트폰", "노트북", "가전제품", "화장품", "식품"]
        regions = ["서울", "경기", "부산", "대구", "광주", "대전", "강원", "제주"]
        channels = ["온라인", "오프라인", "모바일앱", "전화주문"]
        sales_reps = ["김영수", "이민정", "박철수", "정수진", "최동욱", "한지연"]
        
        # 지난 12개월간의 일별 매출 데이터 생성
        start_date = date.today() - timedelta(days=365)
        current_date = start_date
        
        while current_date <= date.today():
            # 하루에 여러 카테고리/지역별 매출 생성
            for _ in range(random.randint(5, 15)):
                company = random.choice(self.companies)
                category = random.choice(categories)
                region = random.choice(regions)
                
                # 계절성 반영 (12월, 1월에 매출 증가)
                seasonal_multiplier = 1.0
                if current_date.month in [11, 12, 1]:
                    seasonal_multiplier = 1.5
                elif current_date.month in [6, 7, 8]:
                    seasonal_multiplier = 1.2
                
                # 주말 매출 감소
                if current_date.weekday() >= 5:  # 토, 일
                    seasonal_multiplier *= 0.8
                
                base_amount = random.uniform(100000, 2000000) * seasonal_multiplier
                profit_margin = random.uniform(0.1, 0.4)
                
                sale = Sale(
                    sale_date=current_date,
                    company_id=company.id,
                    product_category=category,
                    region=region,
                    sales_amount=round(base_amount, 2),
                    profit=round(base_amount * profit_margin, 2),
                    units_sold=random.randint(1, 100),
                    sales_rep=random.choice(sales_reps),
                    channel=random.choice(channels)
                )
                
                self.db.add(sale)
            
            current_date += timedelta(days=1)
        
        logger.info("매출 데이터 생성 완료")
    
    def _print_data_summary(self):
        """생성된 데이터 요약 출력"""
        print("\n" + "="*50)
        print("📊 샘플 데이터 생성 요약")
        print("="*50)
        
        company_count = self.db.query(Company).count()
        customer_count = self.db.query(Customer).count()
        product_count = self.db.query(Product).count()
        order_count = self.db.query(Order).count()
        order_item_count = self.db.query(OrderItem).count()
        sale_count = self.db.query(Sale).count()
        
        print(f"🏢 회사: {company_count:,}개")
        print(f"👥 고객: {customer_count:,}명")
        print(f"📦 제품: {product_count:,}개")
        print(f"🛒 주문: {order_count:,}개")
        print(f"📝 주문항목: {order_item_count:,}개")
        print(f"💰 매출기록: {sale_count:,}개")
        
        # 매출 통계
        total_sales = self.db.query(Sale).with_entities(
            Sale.sales_amount
        ).all()
        
        if total_sales:
            total_amount = sum(s[0] for s in total_sales)
            print(f"\n💵 총 매출액: {total_amount:,.0f}원")
        
        print("="*50)
        print("✅ 샘플 데이터 생성이 완료되었습니다!")
        print("이제 SQL 쿼리 테스트를 시작할 수 있습니다.")
        print("="*50)


def main():
    """메인 실행 함수"""
    print("🗄️ AI 데이터 분석 비서 - 샘플 데이터 생성")
    print("=" * 50)
    
    try:
        # 테이블 생성
        logger.info("데이터베이스 테이블 생성")
        Base.metadata.create_all(bind=engine)
        
        # 샘플 데이터 생성
        creator = SampleDataCreator()
        creator.create_all_sample_data()
        
    except Exception as e:
        logger.error("샘플 데이터 생성 실패", error=str(e))
        print(f"❌ 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
