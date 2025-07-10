import time
from typing import Any, Dict

import mysql.connector
from mysql.connector import Error
from rich.console import Console

from src_sql.query_result import QueryResult

# Rich 콘솔 설정
console = Console()


class DatabaseManager:
    """데이터베이스 연결 및 관리 클래스"""

    def __init__(
        self,
        host="localhost",
        port=3306,
        database="ecommerce_demo",
        user="root",
        password="",
    ):
        self.connection_config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "autocommit": True,
            "consume_results": True,
            "connection_timeout": 10,
            "sql_mode": "TRADITIONAL",
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

            if (
                query.strip().upper().startswith("SELECT")
                or query.strip().upper().startswith("SHOW")
                or query.strip().upper().startswith("DESCRIBE")
            ):
                result_data = cursor.fetchall()
                execution_time = time.time() - start_time
                return QueryResult(
                    success=True,
                    sql_query=query,
                    execution_time=execution_time,
                    result_data=result_data,
                )
            else:
                self.connection.commit()
                execution_time = time.time() - start_time
                return QueryResult(
                    success=True,
                    sql_query=query,
                    execution_time=execution_time,
                    result_data=[],
                )

        except Error as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query=query,
                execution_time=execution_time,
                error_message=str(e),
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
            )""",
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
            (13, 4, 1, 1249000.00), (13, 9, 1, 29000.00)""",
        ]

        console.print("🔧 데이터베이스 설정 중...", style="blue")

        # 테이블 생성
        for i, query in enumerate(setup_queries):
            console.print(f"  📝 실행 중... ({i + 1}/{len(setup_queries)})", end="\r")
            result = self.execute_query(query)
            if not result.success:
                console.print(
                    f"\n❌ 테이블 생성 실패: {result.error_message}", style="red"
                )
                return False
            time.sleep(0.1)  # 약간의 대기 시간

        console.print("\n🔧 샘플 데이터 삽입 중...", style="blue")

        # 샘플 데이터 삽입
        for i, query in enumerate(sample_data_queries):
            console.print(
                f"  📊 삽입 중... ({i + 1}/{len(sample_data_queries)})", end="\r"
            )
            result = self.execute_query(query)
            if not result.success:
                console.print(
                    f"\n❌ 데이터 삽입 실패: {result.error_message}", style="red"
                )
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
                console.print(
                    f"❌ 테이블 목록 조회 실패: {result.error_message}", style="red"
                )
                return schema_info

            # 각 테이블의 컬럼 정보 조회
            for row in result.result_data:
                table_name = list(row.values())[0]

                # 각 테이블의 컬럼 정보 조회
                columns_query = f"DESCRIBE {table_name}"
                columns_result = self.execute_query(columns_query)

                if columns_result.success:
                    schema_info[table_name] = {
                        "columns": [col["Field"] for col in columns_result.result_data],
                        "details": columns_result.result_data,
                    }
                else:
                    console.print(
                        f"⚠️ 테이블 {table_name} 스키마 조회 실패: {columns_result.error_message}",
                        style="yellow",
                    )

        except Exception as e:
            console.print(f"❌ 스키마 정보 조회 중 오류: {str(e)}", style="red")

        return schema_info
