# CoT vs Tool 패턴 실습 프로젝트

import os
import re
import json
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import openai
from dotenv import load_dotenv
from tabulate import tabulate
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.prompt import Prompt, Confirm

# .env 파일 로드
load_dotenv()

# Rich 콘솔 설정
console = Console()

@dataclass
class QueryResult:
    """쿼리 실행 결과를 담는 데이터 클래스"""
    success: bool
    sql_query: str
    execution_time: float
    result_data: List[Dict] = None
    error_message: str = None
    reasoning_steps: List[str] = None

class DatabaseManager:
    """데이터베이스 연결 및 관리 클래스"""
    
    def __init__(self, host='localhost', port=3306, database='ecommerce_demo', 
                 user='root', password=''):
        self.connection_config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password,
            'autocommit': True,
            'consume_results': True,
            'connection_timeout': 10,
            'sql_mode': 'TRADITIONAL'
        }
        self.connection = None
    
    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(**self.connection_config)
            if self.connection.is_connected():
                console.print("✅ 데이터베이스 연결 성공!", style="green")
                return True
        except Error as e:
            console.print(f"❌ 데이터베이스 연결 실패: {e}", style="red")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            console.print("🔌 데이터베이스 연결 종료", style="yellow")
    
    def execute_query(self, query: str) -> QueryResult:
        """쿼리 실행 및 결과 반환"""
        start_time = time.time()
        cursor = None
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('SHOW') or query.strip().upper().startswith('DESCRIBE'):
                result_data = cursor.fetchall()
                execution_time = time.time() - start_time
                return QueryResult(
                    success=True,
                    sql_query=query,
                    execution_time=execution_time,
                    result_data=result_data
                )
            else:
                self.connection.commit()
                execution_time = time.time() - start_time
                return QueryResult(
                    success=True,
                    sql_query=query,
                    execution_time=execution_time,
                    result_data=[]
                )
        
        except Error as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query=query,
                execution_time=execution_time,
                error_message=str(e)
            )
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass  # cursor가 이미 닫혔거나 에러가 있어도 무시
    
    def setup_database(self):
        """데이터베이스 및 테이블 생성"""
        setup_queries = [
            # 데이터베이스 생성
            "CREATE DATABASE IF NOT EXISTS ecommerce_demo",
            "USE ecommerce_demo",
            
            # 테이블 삭제 (기존 데이터 정리)
            "DROP TABLE IF EXISTS order_items",
            "DROP TABLE IF EXISTS orders", 
            "DROP TABLE IF EXISTS products",
            "DROP TABLE IF EXISTS customers",
            
            # 고객 테이블
            """CREATE TABLE customers (
                customer_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                country VARCHAR(50) NOT NULL,
                signup_date DATE NOT NULL,
                INDEX idx_country (country),
                INDEX idx_signup_date (signup_date)
            )""",
            
            # 상품 테이블
            """CREATE TABLE products (
                product_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(200) NOT NULL,
                category VARCHAR(50) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock_quantity INT NOT NULL DEFAULT 0,
                INDEX idx_category (category),
                INDEX idx_price (price)
            )""",
            
            # 주문 테이블
            """CREATE TABLE orders (
                order_id INT PRIMARY KEY AUTO_INCREMENT,
                customer_id INT NOT NULL,
                order_date DATETIME NOT NULL,
                total_amount DECIMAL(12,2) NOT NULL,
                status ENUM('pending', 'completed', 'cancelled', 'refunded') NOT NULL DEFAULT 'pending',
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                INDEX idx_customer_id (customer_id),
                INDEX idx_order_date (order_date),
                INDEX idx_status (status)
            )""",
            
            # 주문 상세 테이블
            """CREATE TABLE order_items (
                order_item_id INT PRIMARY KEY AUTO_INCREMENT,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id),
                INDEX idx_order_id (order_id),
                INDEX idx_product_id (product_id)
            )"""
        ]
        
        # 샘플 데이터
        sample_data_queries = [
            # 고객 데이터
            """INSERT INTO customers (name, email, country, signup_date) VALUES
            ('김민수', 'minsu.kim@email.com', 'Korea', '2024-08-15'),
            ('이지영', 'jiyoung.lee@email.com', 'Korea', '2024-09-20'),
            ('박철수', 'cheolsu.park@email.com', 'Korea', '2024-10-10'),
            ('정수진', 'sujin.jung@email.com', 'Korea', '2024-11-05'),
            ('최영호', 'youngho.choi@email.com', 'Korea', '2025-01-12'),
            ('한서연', 'seoyeon.han@email.com', 'Korea', '2025-02-18'),
            ('윤대현', 'daehyun.yoon@email.com', 'Korea', '2025-03-22'),
            ('송미라', 'mira.song@email.com', 'Korea', '2025-04-15'),
            ('John Smith', 'john.smith@email.com', 'USA', '2024-07-10'),
            ('Emma Wilson', 'emma.wilson@email.com', 'UK', '2024-08-05'),
            ('Hiroshi Tanaka', 'hiroshi.tanaka@email.com', 'Japan', '2024-09-15'),
            ('Marie Dubois', 'marie.dubois@email.com', 'France', '2024-10-20')""",
            
            # 상품 데이터
            """INSERT INTO products (name, category, price, stock_quantity) VALUES
            ('iPhone 15 Pro', 'Electronics', 1299000.00, 50),
            ('Samsung Galaxy S24', 'Electronics', 1199000.00, 45),
            ('MacBook Air M3', 'Electronics', 1590000.00, 30),
            ('iPad Pro', 'Electronics', 1249000.00, 40),
            ('AirPods Pro', 'Electronics', 329000.00, 100),
            ('Nike Air Max', 'Fashion', 189000.00, 80),
            ('Adidas Ultraboost', 'Fashion', 220000.00, 75),
            ('Zara Wool Coat', 'Fashion', 159000.00, 60),
            ('H&M Cotton T-Shirt', 'Fashion', 29000.00, 200),
            ('IKEA Sofa', 'Home & Garden', 599000.00, 20),
            ('Dyson Vacuum V15', 'Home & Garden', 899000.00, 35),
            ('Nike Basketball', 'Sports', 89000.00, 100),
            ('Wilson Tennis Racket', 'Sports', 279000.00, 45),
            ('Programming Book', 'Books', 45000.00, 200),
            ('Business Guide', 'Books', 38000.00, 180)""",
            
            # 주문 데이터 (최근 3개월)
            """INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
            (1, '2025-05-15 14:30:00', 1628000.00, 'completed'),
            (3, '2025-05-20 16:45:00', 378000.00, 'completed'),
            (5, '2025-05-25 11:20:00', 899000.00, 'completed'),
            (2, '2025-05-28 09:15:00', 518000.00, 'completed'),
            (4, '2025-06-02 13:25:00', 939000.00, 'completed'),
            (6, '2025-06-08 15:40:00', 668000.00, 'completed'),
            (1, '2025-06-12 10:30:00', 329000.00, 'completed'),
            (7, '2025-06-18 14:15:00', 1048000.00, 'completed'),
            (8, '2025-06-22 16:20:00', 197000.00, 'completed'),
            (3, '2025-06-25 12:45:00', 728000.00, 'completed'),
            (2, '2025-07-01 11:30:00', 789000.00, 'completed'),
            (5, '2025-07-03 14:20:00', 438000.00, 'completed'),
            (4, '2025-07-05 16:15:00', 328000.00, 'completed')""",
            
            # 주문 상세 데이터
            """INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
            (1, 1, 1, 1299000.00), (1, 5, 1, 329000.00),
            (2, 6, 2, 189000.00),
            (3, 11, 1, 899000.00),
            (4, 9, 1, 29000.00), (4, 14, 1, 45000.00),
            (5, 8, 1, 159000.00), (5, 10, 1, 599000.00),
            (6, 7, 1, 220000.00), (6, 9, 1, 29000.00),
            (7, 5, 1, 329000.00),
            (8, 3, 1, 1590000.00), (8, 12, 1, 89000.00),
            (9, 6, 1, 189000.00),
            (10, 11, 1, 899000.00), (10, 15, 1, 38000.00),
            (11, 2, 1, 1199000.00), (11, 13, 1, 279000.00),
            (12, 8, 1, 159000.00), (12, 14, 6, 45000.00),
            (13, 4, 1, 1249000.00), (13, 9, 1, 29000.00)"""
        ]
        
        console.print("🔧 데이터베이스 설정 중...", style="blue")
        
        # 테이블 생성
        for i, query in enumerate(setup_queries):
            console.print(f"  📝 실행 중... ({i+1}/{len(setup_queries)})", end="\r")
            result = self.execute_query(query)
            if not result.success:
                console.print(f"\n❌ 테이블 생성 실패: {result.error_message}", style="red")
                return False
            time.sleep(0.1)  # 약간의 대기 시간
        
        console.print("\n🔧 샘플 데이터 삽입 중...", style="blue")
        
        # 샘플 데이터 삽입
        for i, query in enumerate(sample_data_queries):
            console.print(f"  📊 삽입 중... ({i+1}/{len(sample_data_queries)})", end="\r")
            result = self.execute_query(query)
            if not result.success:
                console.print(f"\n❌ 데이터 삽입 실패: {result.error_message}", style="red")
                return False
            time.sleep(0.1)  # 약간의 대기 시간
        
        console.print("\n✅ 데이터베이스 설정 완료!", style="green")
        return True
    
    def get_schema_info(self) -> Dict[str, Any]:
        """데이터베이스 스키마 정보 반환"""
        schema_info = {}
        
        try:
            # 테이블 목록 조회
            tables_query = "SHOW TABLES"
            result = self.execute_query(tables_query)
            
            if not result.success:
                console.print(f"❌ 테이블 목록 조회 실패: {result.error_message}", style="red")
                return schema_info
            
            # 각 테이블의 컬럼 정보 조회
            for row in result.result_data:
                table_name = list(row.values())[0]
                
                # 각 테이블의 컬럼 정보 조회
                columns_query = f"DESCRIBE {table_name}"
                columns_result = self.execute_query(columns_query)
                
                if columns_result.success:
                    schema_info[table_name] = {
                        'columns': [col['Field'] for col in columns_result.result_data],
                        'details': columns_result.result_data
                    }
                else:
                    console.print(f"⚠️ 테이블 {table_name} 스키마 조회 실패: {columns_result.error_message}", style="yellow")
        
        except Exception as e:
            console.print(f"❌ 스키마 정보 조회 중 오류: {str(e)}", style="red")
        
        return schema_info

class CoTSQLGenerator:
    """Chain of Thought 방식의 SQL 생성기"""
    
    def __init__(self, openai_api_key: str, base_url: Optional[str] = None, openai_model: str = ""):
        self.client = openai.OpenAI(api_key=openai_api_key, base_url=base_url)
        self.openai_model = openai_model
    
    def generate_sql(self, user_question: str, schema_info: Dict) -> QueryResult:
        """CoT 방식으로 SQL 쿼리 생성"""
        start_time = time.time()
        
        # 스키마 정보를 문자열로 변환
        schema_text = self._format_schema_info(schema_info)
        
        prompt = f"""
당신은 데이터베이스 전문가입니다. 사용자의 자연어 질문을 SQL 쿼리로 변환하되, 
Chain of Thought 방식으로 단계별 추론 과정을 보여주세요.

사용자 질문: "{user_question}"

데이터베이스 스키마:
{schema_text}

다음 단계를 따라 SQL 쿼리를 생성해주세요:

1단계: 질문 분석 및 필요 정보 식별
- 시간 범위, 대상, 집계 방법, 그룹화 기준 등을 명확히 하세요

2단계: 필요한 테이블 식별
- 각 정보가 어느 테이블에 있는지 확인하세요

3단계: 테이블 간 조인 관계 설계
- 어떤 컬럼으로 테이블들을 연결할지 정하세요

4단계: 필터 조건 정의
- WHERE 절에 들어갈 조건들을 명시하세요

5단계: 집계 함수와 그룹화 적용
- SELECT, GROUP BY, ORDER BY 절을 설계하세요

6단계: 최종 SQL 쿼리 작성
- 완성된 쿼리를 제시하세요

응답 형식:
1단계: [분석 내용]
2단계: [테이블 식별]
3단계: [조인 설계]
4단계: [필터 조건]
5단계: [집계 설계]
6단계: 
```sql
[최종 SQL 쿼리]
```

중요: 6단계의 SQL 쿼리만 실행 가능한 형태로 작성하고, 다른 설명은 주석으로 처리하지 마세요.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # 추론 단계들 추출
            reasoning_steps = self._extract_reasoning_steps(content)
            
            # SQL 쿼리 추출
            sql_query = self._extract_sql_query(content)
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                sql_query=sql_query,
                execution_time=execution_time,
                reasoning_steps=reasoning_steps
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query="",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _format_schema_info(self, schema_info: Dict) -> str:
        """스키마 정보를 문자열로 포맷팅"""
        schema_text = ""
        for table_name, info in schema_info.items():
            schema_text += f"\n{table_name} 테이블:\n"
            for col in info['details']:
                schema_text += f"  - {col['Field']} ({col['Type']})\n"
        return schema_text
    
    def _extract_reasoning_steps(self, content: str) -> List[str]:
        """응답에서 추론 단계들 추출"""
        steps = []
        for i in range(1, 7):
            pattern = rf"{i}단계:(.+?)(?={i+1}단계:|```sql|$)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                steps.append(f"{i}단계: {match.group(1).strip()}")
        return steps
    
    def _extract_sql_query(self, content: str) -> str:
        """응답에서 SQL 쿼리 추출"""
        sql_pattern = r"```sql\s*(.*?)\s*```"
        match = re.search(sql_pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""

class ToolSQLGenerator:
    """Tool 패턴 방식의 SQL 생성기"""
    
    def __init__(self, openai_api_key: str, base_url: Optional[str] = None, openai_model: str = ""):
        self.client = openai.OpenAI(api_key=openai_api_key, base_url=base_url)
        self.openai_model = openai_model
    
    def generate_sql(self, user_question: str, schema_info: Dict) -> QueryResult:
        """Tool 패턴으로 SQL 쿼리 생성"""
        start_time = time.time()
        
        try:
            # Tool 1: 키워드 추출
            keywords = self._extract_keywords(user_question)
            
            # Tool 2: 관련 스키마 검색
            relevant_schema = self._get_relevant_schema(keywords, schema_info)
            
            # Tool 3: 쿼리 템플릿 생성
            sql_template = self._generate_sql_template(user_question, relevant_schema)
            
            # Tool 4: 쿼리 최적화
            optimized_query = self._optimize_query(sql_template)
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                success=True,
                sql_query=optimized_query,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query="",
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _extract_keywords(self, user_question: str) -> List[str]:
        """Tool 1: 키워드 추출"""
        prompt = f"""
다음 자연어 질문에서 데이터베이스 쿼리에 필요한 핵심 키워드를 추출하세요.

질문: "{user_question}"

키워드 유형별로 분류해서 추출하세요:
- 대상: (고객, 주문, 상품 등)
- 시간: (최근, 3개월, 년도 등)
- 지역: (한국, 미국 등)
- 집계: (평균, 합계, 개수 등)
- 분류: (카테고리, 상태 등)

JSON 형식으로 응답하세요:
{{"keywords": ["키워드1", "키워드2", ...], "categories": ["대상", "시간", ...]}}
"""
        
        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        try:
            result = json.loads(response.choices[0].message.content)
            return result.get("keywords", [])
        except:
            return ["고객", "주문", "평균"]  # 기본값
    
    def _get_relevant_schema(self, keywords: List[str], schema_info: Dict) -> Dict:
        """Tool 2: 관련 스키마 정보 필터링"""
        relevant_tables = {}
        
        # 키워드 기반으로 관련 테이블 선택
        keyword_table_mapping = {
            "고객": "customers",
            "주문": "orders", 
            "상품": "products",
            "카테고리": "products",
            "한국": "customers",
            "평균": "orders"
        }
        
        for keyword in keywords:
            for k, table in keyword_table_mapping.items():
                if k in keyword and table in schema_info:
                    relevant_tables[table] = schema_info[table]
        
        # order_items 테이블은 조인이 필요한 경우 자동 포함
        if "orders" in relevant_tables and "products" in relevant_tables:
            if "order_items" in schema_info:
                relevant_tables["order_items"] = schema_info["order_items"]
        
        return relevant_tables
    
    def _generate_sql_template(self, user_question: str, relevant_schema: Dict) -> str:
        """Tool 3: SQL 템플릿 생성"""
        schema_text = ""
        for table_name, info in relevant_schema.items():
            schema_text += f"{table_name}: {', '.join(info['columns'])}\n"
        
        prompt = f"""
사용자 질문과 관련 스키마 정보를 바탕으로 SQL 쿼리를 생성하세요.

질문: "{user_question}"

관련 스키마:
{schema_text}

규칙:
1. 완전한 실행 가능한 SQL 쿼리만 반환
2. 주석이나 설명 없이 순수 SQL만
3. 적절한 JOIN, WHERE, GROUP BY 사용
4. 컬럼명과 테이블명 정확히 사용

SQL 쿼리:
"""
        
        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    
    def _optimize_query(self, sql_query: str) -> str:
        """Tool 4: 쿼리 최적화"""
        # 간단한 최적화 규칙 적용
        optimized = sql_query
        
        # 불필요한 주석 제거
        optimized = re.sub(r'--.*?\n', '', optimized)
        optimized = re.sub(r'/\*.*?\*/', '', optimized, flags=re.DOTALL)
        
        # 여러 공백을 하나로
        optimized = re.sub(r'\s+', ' ', optimized)
        
        return optimized.strip()

class PromptTester:
    """프롬프트 테스트 및 비교 시스템"""
    
    def __init__(self, db_manager: DatabaseManager, cot_generator: CoTSQLGenerator, 
                 tool_generator: ToolSQLGenerator):
        self.db = db_manager
        self.cot = cot_generator
        self.tool = tool_generator
    
    def run_comparison(self, user_question: str) -> Dict[str, QueryResult]:
        """CoT와 Tool 패턴 비교 실행"""
        console.print(f"\n🔍 질문: {user_question}", style="bold blue")
        
        results = {}
        
        try:
            # 데이터베이스 연결 상태 확인
            if not self.db.connection or not self.db.connection.is_connected():
                console.print("❌ 데이터베이스 연결이 끊어졌습니다. 재연결을 시도합니다.", style="red")
                if not self.db.connect():
                    console.print("❌ 데이터베이스 재연결에 실패했습니다.", style="red")
                    return results
            
            schema_info = self.db.get_schema_info()
            
            if not schema_info:
                console.print("❌ 스키마 정보를 가져올 수 없습니다.", style="red")
                return results
            
            # CoT 방식 실행
            console.print("\n🧠 Chain of Thought 방식 실행 중...", style="yellow")
            try:
                cot_result = self.cot.generate_sql(user_question, schema_info)
                
                if cot_result.success and cot_result.sql_query:
                    db_result = self.db.execute_query(cot_result.sql_query)
                    cot_result.result_data = db_result.result_data
                    if not db_result.success:
                        cot_result.error_message = db_result.error_message
                        cot_result.success = False
                
                results['cot'] = cot_result
            
            except Exception as e:
                console.print(f"❌ CoT 방식 실행 중 오류: {str(e)}", style="red")
                results['cot'] = QueryResult(
                    success=False,
                    sql_query="",
                    execution_time=0,
                    error_message=str(e)
                )
            
            # Tool 방식 실행
            console.print("\n🔧 Tool 패턴 방식 실행 중...", style="yellow")
            try:
                tool_result = self.tool.generate_sql(user_question, schema_info)
                
                if tool_result.success and tool_result.sql_query:
                    db_result = self.db.execute_query(tool_result.sql_query)
                    tool_result.result_data = db_result.result_data
                    if not db_result.success:
                        tool_result.error_message = db_result.error_message
                        tool_result.success = False
                
                results['tool'] = tool_result
            
            except Exception as e:
                console.print(f"❌ Tool 방식 실행 중 오류: {str(e)}", style="red")
                results['tool'] = QueryResult(
                    success=False,
                    sql_query="",
                    execution_time=0,
                    error_message=str(e)
                )
        
        except Exception as e:
            console.print(f"❌ 비교 실행 중 전체 오류: {str(e)}", style="red")
        
        return results
    
    def display_results(self, results: Dict[str, QueryResult]):
        """결과 비교 표시"""
        console.print("\n" + "="*80, style="bold")
        console.print("📊 결과 비교", style="bold green")
        console.print("="*80, style="bold")
        
        # 비교 테이블
        comparison_table = Table(title="성능 비교")
        comparison_table.add_column("항목", style="cyan")
        comparison_table.add_column("CoT 패턴", style="green")
        comparison_table.add_column("Tool 패턴", style="yellow")
        
        cot_result = results['cot']
        tool_result = results['tool']
        
        comparison_table.add_row(
            "실행 성공", 
            "✅" if cot_result.success else "❌",
            "✅" if tool_result.success else "❌"
        )
        
        comparison_table.add_row(
            "생성 시간",
            f"{cot_result.execution_time:.2f}초",
            f"{tool_result.execution_time:.2f}초"
        )
        
        if cot_result.success and tool_result.success:
            cot_rows = len(cot_result.result_data) if cot_result.result_data else 0
            tool_rows = len(tool_result.result_data) if tool_result.result_data else 0
            comparison_table.add_row("결과 행 수", str(cot_rows), str(tool_rows))
        
        console.print(comparison_table)
        
        # CoT 추론 과정 표시
        if cot_result.reasoning_steps:
            console.print("\n🧠 CoT 추론 과정:", style="bold green")
            for step in cot_result.reasoning_steps:
                console.print(f"  {step}")
        
        # SQL 쿼리 표시
        console.print("\n📝 생성된 SQL 쿼리:", style="bold")
        
        if cot_result.sql_query:
            console.print("\n🧠 CoT 방식:")
            syntax = Syntax(cot_result.sql_query, "sql", theme="monokai")
            console.print(syntax)
        
        if tool_result.sql_query:
            console.print("\n🔧 Tool 방식:")
            syntax = Syntax(tool_result.sql_query, "sql", theme="monokai")
            console.print(syntax)
        
        # 실행 결과 표시
        if cot_result.success and cot_result.result_data:
            console.print("\n📊 CoT 실행 결과:", style="bold green")
            self._display_query_results(cot_result.result_data)
        
        if tool_result.success and tool_result.result_data:
            console.print("\n📊 Tool 실행 결과:", style="bold yellow")
            self._display_query_results(tool_result.result_data)
        
        # 오류 메시지 표시
        if not cot_result.success and cot_result.error_message:
            console.print(f"\n❌ CoT 오류: {cot_result.error_message}", style="red")
        
        if not tool_result.success and tool_result.error_message:
            console.print(f"\n❌ Tool 오류: {tool_result.error_message}", style="red")
    
    def _display_query_results(self, result_data: List[Dict]):
        """쿼리 결과를 테이블 형태로 표시"""
        if not result_data:
            console.print("결과가 없습니다.")
            return
        
        # 최대 10행까지만 표시
        display_data = result_data[:10]
        
        if len(result_data) > 10:
            console.print(f"(총 {len(result_data)}행 중 10행만 표시)")
        
        # 테이블 생성
        table = Table()
        
        # 컬럼 추가
        if display_data:
            for column in display_data[0].keys():
                table.add_column(str(column), style="cyan")
            
            # 데이터 추가
            for row in display_data:
                table.add_row(*[str(value) for value in row.values()])
        
        console.print(table)

def main():
    """메인 실행 함수"""
    console.print("""
╔══════════════════════════════════════════════════════════════╗
║                 CoT vs Tool 패턴 실습 프로젝트                   ║
║                  프롬프트 엔지니어링 심화                        ║
╚══════════════════════════════════════════════════════════════╝
    """, style="bold blue")
    
    # 환경 변수 확인
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_url = os.getenv('OPENAI_URL')
    openai_model = os.getenv('OPENAI_MODEL', 'gpt-4')
    if not openai_api_key:
        console.print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.", style="red")
        console.print("💡 .env 파일에 OPENAI_API_KEY=your-api-key 를 추가하세요.", style="yellow")
        return
    
    mysql_host = os.getenv('MYSQL_HOST', 'localhost')
    mysql_port = int(os.getenv('MYSQL_PORT', 3306))
    mysql_user = os.getenv('MYSQL_USER', 'root')
    mysql_password = os.getenv('MYSQL_PASSWORD')
    
    # 데이터베이스 연결
    db = DatabaseManager(host=mysql_host, 
                         port=mysql_port, 
                         user=mysql_user, 
                         password=mysql_password)
    if not db.connect():
        console.print("❌ 데이터베이스 연결에 실패했습니다.", style="red")
        console.print("💡 MySQL 서버가 실행 중인지 확인하세요.", style="yellow")
        console.print("💡 Docker: docker run --name prompt-mysql -e MYSQL_ROOT_PASSWORD=password123 -e MYSQL_DATABASE=ecommerce_demo -p 3306:3306 -d mysql:8.0", style="cyan")
        return
    
    # 데이터베이스 초기화 여부 확인
    if Confirm.ask("데이터베이스를 초기화하시겠습니까? (기존 데이터가 삭제됩니다)"):
        if not db.setup_database():
            console.print("❌ 데이터베이스 설정에 실패했습니다.", style="red")
            return
    
    # SQL 생성기 초기화
    cot_generator = CoTSQLGenerator(openai_api_key, base_url=openai_url, openai_model=openai_model)
    tool_generator = ToolSQLGenerator(openai_api_key, base_url=openai_url, openai_model=openai_model)
    tester = PromptTester(db, cot_generator, tool_generator)
    
    # 예제 질문들
    example_questions = [
        "지난 3개월간 한국 고객들의 평균 주문 금액을 카테고리별로 보여주세요",
        "가장 많이 팔린 상품 TOP 5는 무엇인가요?",
        "월별 매출 추이를 보여주세요",
        "Electronics 카테고리에서 가장 비싼 상품은 무엇인가요?",
        "한국 고객 중 가장 많이 구매한 고객은 누구인가요?"
    ]
    
    while True:
        console.print("\n" + "="*60, style="bold")
        console.print("📝 질문을 선택하거나 직접 입력하세요", style="bold")
        console.print("="*60, style="bold")
        
        # 예제 질문 표시
        console.print("\n📋 예제 질문들:")
        for i, question in enumerate(example_questions, 1):
            console.print(f"  {i}. {question}")
        
        console.print(f"  {len(example_questions) + 1}. 직접 입력")
        console.print(f"  {len(example_questions) + 2}. 종료")
        
        choice = Prompt.ask(
            "\n선택하세요", 
            choices=[str(i) for i in range(1, len(example_questions) + 3)]
        )
        
        if choice == str(len(example_questions) + 2):  # 종료
            break
        elif choice == str(len(example_questions) + 1):  # 직접 입력
            user_question = Prompt.ask("질문을 입력하세요")
        else:  # 예제 질문 선택
            user_question = example_questions[int(choice) - 1]
        
        if user_question.strip():
            # 비교 실행
            results = tester.run_comparison(user_question)
            tester.display_results(results)
            
            # 계속 여부 확인
            if not Confirm.ask("\n다른 질문을 테스트하시겠습니까?"):
                break
    
    # 정리
    db.disconnect()
    console.print("\n👋 프로그램을 종료합니다.", style="green")

if __name__ == "__main__":
    main()