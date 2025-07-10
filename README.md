# 프로젝트 설정 및 실행 가이드

본 프로젝트는 2개의 sub project 가 있다.

1. src_sql : MySQL 데이터베이스를 구축하고 sql query를 만드는 툴 및 CoT prompt 작성 실험.

2. src_code_llm : code review 하는 llm prompt technique 실험.

먼저 MySQL 프로젝트에 대해 설명하겠다.

## 1. MySQL 데이터베이스 시작

Windows에서 MySQL 서비스를 수동으로 시작하는 방법입니다.

1.  `Win` + `R` 키를 눌러 실행창을 엽니다.
2.  `services.msc`를 입력하고 `Enter` 키를 누릅니다.
3.  서비스 목록에서 **"MySQL"** 또는 **"MySQL80"**과 같은 항목을 찾습니다.
4.  해당 항목을 마우스 오른쪽 버튼으로 클릭하고 **시작(Start)**을 선택합니다.

## 2. 데이터베이스 스키마 확인

`MySQL Command Line Client`를 실행하여 데이터베이스 구조를 확인할 수 있습니다.

### 데이터베이스 및 테이블 목록 확인

```sql
-- 사용 가능한 모든 데이터베이스를 보여줍니다.
SHOW DATABASES;

-- 'ecommerce_demo' 데이터베이스를 사용합니다.
USE ecommerce_demo;

-- 현재 데이터베이스의 모든 테이블을 보여줍니다.
SHOW TABLES;
```

### 각 테이블의 컬럼 정보 확인

```sql
-- customers 테이블의 컬럼 정보를 확인합니다.
SHOW COLUMNS FROM customers;

-- order_items 테이블의 컬럼 정보를 확인합니다.
SHOW COLUMNS FROM order_items;

-- orders 테이블의 컬럼 정보를 확인합니다.
SHOW COLUMNS FROM orders;

-- products 테이블의 컬럼 정보를 확인합니다.
SHOW COLUMNS FROM products;
```

## 3. 코드 설명

이 프로젝트에 포함된 파이썬 스크립트에 대한 설명입니다.

-   **`complete_code1.py`**: 가장 기본적인 기능을 구현한 간단한 도구입니다.
-   **`complete_code2.py`**: 데이터베이스에서 샘플 데이터를 가져오는 기능이 추가된 도구입니다.
