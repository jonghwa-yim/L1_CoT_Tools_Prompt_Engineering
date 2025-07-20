-- ====================================
-- 전자상거래 데이터베이스 구축 스크립트
-- CoT vs Tool 패턴 실습용
-- ====================================

-- 데이터베이스 생성 (MySQL 기준)
CREATE DATABASE IF NOT EXISTS ecommerce_demo;
USE ecommerce_demo;

-- ====================================
-- 1. 테이블 구조 생성
-- ====================================

-- 고객 테이블
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    country VARCHAR(50) NOT NULL,
    signup_date DATE NOT NULL,
    INDEX idx_country (country),
    INDEX idx_signup_date (signup_date)
);

-- 상품 테이블
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    INDEX idx_category (category),
    INDEX idx_price (price)
);

-- 주문 테이블
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled', 'refunded') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status)
);

-- 주문 상세 테이블
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order_id (order_id),
    INDEX idx_product_id (product_id)
);

-- ====================================
-- 2. 샘플 데이터 삽입
-- ====================================

-- 고객 데이터 (다양한 국가, 한국 고객 포함)
INSERT INTO customers (name, email, country, signup_date) VALUES
-- 한국 고객들
('김민수', 'minsu.kim@email.com', 'Korea', '2024-08-15'),
('이지영', 'jiyoung.lee@email.com', 'Korea', '2024-09-20'),
('박철수', 'cheolsu.park@email.com', 'Korea', '2024-10-10'),
('정수진', 'sujin.jung@email.com', 'Korea', '2024-11-05'),
('최영호', 'youngho.choi@email.com', 'Korea', '2025-01-12'),
('한서연', 'seoyeon.han@email.com', 'Korea', '2025-02-18'),
('윤대현', 'daehyun.yoon@email.com', 'Korea', '2025-03-22'),
('송미라', 'mira.song@email.com', 'Korea', '2025-04-15'),

-- 기타 국가 고객들
('John Smith', 'john.smith@email.com', 'USA', '2024-07-10'),
('Emma Wilson', 'emma.wilson@email.com', 'UK', '2024-08-05'),
('Hiroshi Tanaka', 'hiroshi.tanaka@email.com', 'Japan', '2024-09-15'),
('Marie Dubois', 'marie.dubois@email.com', 'France', '2024-10-20'),
('Wang Lei', 'wang.lei@email.com', 'China', '2024-11-25'),
('Anna Mueller', 'anna.mueller@email.com', 'Germany', '2025-01-08'),
('Carlos Rodriguez', 'carlos.rodriguez@email.com', 'Spain', '2025-02-14'),
('Lisa Anderson', 'lisa.anderson@email.com', 'USA', '2025-03-30');

-- 상품 데이터 (다양한 카테고리)
INSERT INTO products (name, category, price, stock_quantity) VALUES
-- Electronics 카테고리
('iPhone 15 Pro', 'Electronics', 1299000.00, 50),
('Samsung Galaxy S24', 'Electronics', 1199000.00, 45),
('MacBook Air M3', 'Electronics', 1590000.00, 30),
('iPad Pro', 'Electronics', 1249000.00, 40),
('AirPods Pro', 'Electronics', 329000.00, 100),
('Dell XPS 13', 'Electronics', 1899000.00, 25),

-- Fashion 카테고리
('Nike Air Max', 'Fashion', 189000.00, 80),
('Adidas Ultraboost', 'Fashion', 220000.00, 75),
('Zara Wool Coat', 'Fashion', 159000.00, 60),
('H&M Cotton T-Shirt', 'Fashion', 29000.00, 200),
('Uniqlo Jeans', 'Fashion', 59000.00, 150),
('Gucci Handbag', 'Fashion', 2890000.00, 15),

-- Home & Garden 카테고리
('IKEA Sofa', 'Home & Garden', 599000.00, 20),
('Dyson Vacuum V15', 'Home & Garden', 899000.00, 35),
('Philips Air Purifier', 'Home & Garden', 449000.00, 40),
('KitchenAid Mixer', 'Home & Garden', 649000.00, 25),
('Instant Pot', 'Home & Garden', 179000.00, 60),

-- Sports 카테고리
('Nike Basketball', 'Sports', 89000.00, 100),
('Wilson Tennis Racket', 'Sports', 279000.00, 45),
('Adidas Soccer Cleats', 'Sports', 199000.00, 70),
('Fitness Tracker', 'Sports', 249000.00, 85),
('Yoga Mat Premium', 'Sports', 79000.00, 120),

-- Books 카테고리
('The Art of Programming', 'Books', 45000.00, 200),
('Machine Learning Guide', 'Books', 52000.00, 150),
('Business Strategy 101', 'Books', 38000.00, 180),
('Korean Cookbook', 'Books', 29000.00, 220),
('Photography Basics', 'Books', 41000.00, 160);

-- 주문 데이터 (최근 6개월, 특히 최근 3개월에 집중)
INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES
-- 2025년 5월 주문들 (최근 3개월 내)
(1, '2025-05-15 14:30:00', 1628000.00, 'completed'),
(3, '2025-05-20 16:45:00', 378000.00, 'completed'),
(5, '2025-05-25 11:20:00', 899000.00, 'completed'),
(2, '2025-05-28 09:15:00', 518000.00, 'completed'),
-- 2025년 6월 주문들
(4, '2025-06-02 13:25:00', 939000.00, 'completed'),
(6, '2025-06-08 15:40:00', 668000.00, 'completed'),
(1, '2025-06-12 10:30:00', 329000.00, 'completed'),
(7, '2025-06-18 14:15:00', 1048000.00, 'completed'),
(8, '2025-06-22 16:20:00', 197000.00, 'completed'),
(3, '2025-06-25 12:45:00', 728000.00, 'completed'),
-- 2025년 7월 주문들 (최근)
(2, '2025-07-01 11:30:00', 789000.00, 'completed'),
(5, '2025-07-03 14:20:00', 438000.00, 'completed'),
(4, '2025-07-05 16:15:00', 328000.00, 'completed'),
(6, '2025-07-06 09:30:00', 89000.00, 'completed'),""",

-- 기타 국가 고객들의 주문 (비교 데이터)
(9, '2025-06-15 12:00:00', 1299000.00, 'completed'),
(10, '2025-06-20 14:30:00', 759000.00, 'completed'),
(11, '2025-07-01 16:45:00', 1249000.00, 'completed'),
(12, '2025-07-02 10:20:00', 528000.00, 'completed'),

-- 이전 기간 주문들 (3개월 이전)
(1, '2025-02-15 14:30:00', 1299000.00, 'completed'),
(2, '2025-03-20 16:45:00', 649000.00, 'completed'),
(3, '2025-04-10 11:20:00', 379000.00, 'completed');

-- 주문 상세 데이터
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
-- 주문 ID 1 (김민수 - 5월)
(1, 1, 1, 1299000.00), -- iPhone 15 Pro
(1, 5, 1, 329000.00),  -- AirPods Pro

-- 주문 ID 2 (박철수 - 5월)
(2, 7, 2, 189000.00),  -- Nike Air Max x2

-- 주문 ID 3 (최영호 - 5월)
(3, 14, 1, 899000.00), -- Dyson Vacuum

-- 주문 ID 4 (이지영 - 5월)
(4, 11, 1, 59000.00),  -- Uniqlo Jeans
(4, 10, 1, 29000.00),  -- H&M T-Shirt
(4, 17, 1, 179000.00), -- Instant Pot
(4, 25, 5, 45000.00),  -- Books

-- 주문 ID 5 (정수진 - 6월)
(5, 12, 1, 2890000.00), -- Gucci Handbag
(5, 10, 1, 29000.00),   -- H&M T-Shirt
(5, 22, 1, 249000.00),  -- Fitness Tracker

-- 주문 ID 6 (한서연 - 6월)
(6, 13, 1, 599000.00),  -- IKEA Sofa
(6, 11, 1, 59000.00),   -- Uniqlo Jeans

-- 주문 ID 7 (김민수 - 6월, 재구매)
(7, 5, 1, 329000.00),   -- AirPods Pro

-- 주문 ID 8 (윤대현 - 6월)
(8, 3, 1, 1590000.00),  -- MacBook Air
(8, 15, 1, 449000.00),  -- Air Purifier
(8, 22, 1, 249000.00),  -- Fitness Tracker

-- 주문 ID 9 (송미라 - 6월)
(9, 7, 1, 189000.00),   -- Nike Air Max

-- 주문 ID 10 (박철수 - 6월, 재구매)
(10, 14, 1, 899000.00), -- Dyson Vacuum
(10, 17, 1, 179000.00), -- Instant Pot
(10, 25, 5, 45000.00),  -- Books

-- 주문 ID 11 (이지영 - 7월)
(11, 6, 1, 1899000.00), -- Dell XPS 13

-- 주문 ID 12 (최영호 - 7월)
(12, 9, 1, 159000.00),  -- Zara Coat
(12, 20, 1, 279000.00), -- Wilson Tennis Racket

-- 주문 ID 13 (정수진 - 7월)
(13, 5, 1, 329000.00),  -- AirPods Pro

-- 주문 ID 14 (한서연 - 7월)
(14, 18, 1, 89000.00),  -- Nike Basketball

-- 기타 국가 고객들 주문 상세
(15, 1, 1, 1299000.00), -- John Smith
(16, 9, 1, 159000.00),  -- Emma Wilson
(16, 13, 1, 599000.00),
(17, 4, 1, 1249000.00), -- Hiroshi Tanaka
(18, 7, 1, 189000.00),  -- Marie Dubois
(18, 11, 1, 59000.00),
(18, 20, 1, 279000.00),

-- 이전 기간 주문 상세
(19, 1, 1, 1299000.00), -- 2월 주문
(20, 16, 1, 649000.00), -- 3월 주문
(21, 7, 2, 189000.00);  -- 4월 주문

-- ====================================
-- 3. 데이터 검증 쿼리들
-- ====================================

-- 전체 데이터 확인
SELECT 'customers' as table_name, COUNT(*) as record_count FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'orders', COUNT(*) FROM orders
UNION ALL
SELECT 'order_items', COUNT(*) FROM order_items;

-- 한국 고객 확인
SELECT name, email, signup_date 
FROM customers 
WHERE country = 'Korea' 
ORDER BY signup_date;

-- 카테고리별 상품 수
SELECT category, COUNT(*) as product_count, 
       MIN(price) as min_price, MAX(price) as max_price
FROM products 
GROUP BY category 
ORDER BY category;

-- 최근 3개월 주문 확인 (CoT 예시 질문용)
SELECT DATE_FORMAT(order_date, '%Y-%m') as order_month,
       COUNT(*) as order_count,
       SUM(total_amount) as total_sales
FROM orders 
WHERE order_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
GROUP BY DATE_FORMAT(order_date, '%Y-%m')
ORDER BY order_month;

-- ====================================
-- 4. CoT 실습용 목표 쿼리 (정답)
-- ====================================

-- 질문: "지난 3개월간 한국 고객들의 평균 주문 금액을 카테고리별로 보여주세요"
SELECT 
    p.category,
    ROUND(AVG(o.total_amount), 2) as avg_order_amount,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT c.customer_id) as customer_count
FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
WHERE 
    c.country = 'Korea'
    AND o.order_date >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
    AND o.status = 'completed'
GROUP BY p.category
ORDER BY avg_order_amount DESC;

-- ====================================
-- 5. 추가 실습 쿼리 예시들
-- ====================================

-- 실습 예시 1: 월별 한국 고객 매출 추이
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') as order_month,
    SUM(o.total_amount) as monthly_sales,
    COUNT(DISTINCT o.order_id) as order_count
FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
WHERE c.country = 'Korea' AND o.status = 'completed'
GROUP BY DATE_FORMAT(o.order_date, '%Y-%m')
ORDER BY order_month;

-- 실습 예시 2: 가장 인기 있는 상품 TOP 5 (한국 고객 기준)
SELECT 
    p.name as product_name,
    p.category,
    SUM(oi.quantity) as total_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue
FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
WHERE c.country = 'Korea' AND o.status = 'completed'
GROUP BY p.product_id, p.name, p.category
ORDER BY total_sold DESC
LIMIT 5;

-- 실습 예시 3: 고객별 구매 패턴 분석
SELECT 
    c.name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    ROUND(AVG(o.total_amount), 2) as avg_order_value,
    COUNT(DISTINCT p.category) as categories_purchased
FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
WHERE c.country = 'Korea' AND o.status = 'completed'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;