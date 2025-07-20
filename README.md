# 프로젝트 설정 및 실행 가이드

본 프로젝트는 2개의 sub project로 구성되어 있습니다.

1. **src_sql**: MySQL 데이터베이스를 구축하고 SQL 쿼리를 생성하는 툴 및 CoT (Chain of Thought) 프롬프트 작성 실험.
2. **src_code_llm**: 코드 리뷰를 수행하는 LLM (Large Language Model) 프롬프트 기술 실험.

---

## 1. MySQL 데이터베이스 시작 (src_sql)

### MySQL 서비스 시작

Windows에서 MySQL 서비스를 수동으로 시작하는 방법입니다.

1.  `Win` + `R` 키를 눌러 실행창을 엽니다.
2.  `services.msc`를 입력하고 `Enter` 키를 누릅니다.
3.  서비스 목록에서 **"MySQL"** 또는 **"MySQL80"**과 같은 항목을 찾습니다.
4.  해당 항목을 마우스 오른쪽 버튼으로 클릭하고 **시작(Start)**을 선택합니다.

### 데이터베이스 스키마 확인

`MySQL Command Line Client`를 실행하여 데이터베이스 구조를 확인할 수 있습니다.

#### 데이터베이스 및 테이블 목록 확인

```sql
-- 사용 가능한 모든 데이터베이스를 보여줍니다.
SHOW DATABASES;

-- 'ecommerce_demo' 데이터베이스를 사용합니다.
USE ecommerce_demo;

-- 현재 데이터베이스의 모든 테이블을 보여줍니다.
SHOW TABLES;
```

#### 각 테이블의 컬럼 정보 확인

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

### 코드 설명

이 프로젝트에 포함된 파이썬 스크립트에 대한 설명입니다.

-   **`complete_code1.py`**: 가장 기본적인 기능을 구현한 간단한 도구입니다.
-   **`complete_code2.py`**: 데이터베이스에서 샘플 데이터를 가져오는 기능이 추가된 도구입니다.
-   **`sql_gen_cot.py`**: CoT 방식으로 SQL 쿼리를 생성하는 도구입니다.
-   **`sql_gen_tool1.py`**: Query 생성을 함수화하여 도구로 만들어서 사용하여 SQL 쿼리를 생성하는 도구입니다.
-   **`sql_gen_tool2.py`**: `sql_gen_tool1.py`에서 구현한 Query 생성 툴에 추가로 샘플 Query를 불러오는 도구를 사용하여 SQL 쿼리를 생성하는 도구입니다.

---

## 2. 코드 리뷰 실습 (src_code_llm)

### 프로젝트 개요

`src_code_llm` 폴더는 코드 리뷰를 수행하는 LLM 프롬프트 기술을 실험하기 위한 프로젝트입니다. 이 프로젝트는 Python 코드를 분석하고 개선안을 제시하는 데 초점을 맞추고 있습니다.

### 주요 파일 설명

-   **`knn.py`**: K-최근접 이웃(KNN) 알고리즘을 구현한 Python 코드입니다. 이 코드는 코드 리뷰 실습의 입력으로 사용됩니다.
-   **`sample_test_code_review_llm.py`**: LLM을 사용하여 `knn.py` 코드를 리뷰하고 개선안을 제시하는 스크립트입니다.
-   **`result_simple_q.py`**: 간단한 코드 리뷰 요청에 대한 결과를 저장한 파일입니다.
-   **`result_detailed_q.py`**: 상세한 코드 리뷰 요청에 대한 결과를 저장한 파일입니다.

### 실행 방법

1. `.env` 파일에 OpenAI API 키와 URL을 설정합니다.
    ```plaintext
    OPENAI_API_KEY=your-api-key
    OPENAI_URL=https://api.openai.com/v1
    ```

2. `sample_test_code_review_llm.py`를 실행하여 코드 리뷰를 수행합니다.
    ```bash
    python src_code_llm/sample_test_code_review_llm.py
    ```

3. 결과는 콘솔에 출력되며, 간단한 리뷰와 상세 리뷰 결과를 확인할 수 있습니다.

### 코드 리뷰 요청 예시

- **간단한 요청**:
    ```plaintext
    이 Python 코드를 리뷰하고 개선안을 제시해주세요.
    ```

- **상세한 요청**:
    ```plaintext
    역할: 5년 이상 경력의 ML 및 Python 시니어 개발자
    요청사항: 다음 Python 코드가 어떤 역할을 하는지 분석하고, 오류 또는 비효율적인 코드가 있는지 리뷰하고 완벽히 해결된 개선안을 제시해주세요.
    ```

---

## 3. 요구사항

### Python 패키지 설치

프로젝트 실행에 필요한 Python 패키지는 `requirements.txt` 파일에 정의되어 있습니다. 다음 명령어를 사용하여 패키지를 설치하세요.

```bash
pip install -r requirements.txt
```

### MySQL 설정

MySQL 데이터베이스를 실행하고 `ecommerce_database_setup.sql` 스크립트를 사용하여 데이터베이스를 초기화하세요.

```bash
mysql -u root -p < ecommerce_database_setup.sql
```

---

## 4. 프로젝트 구조

```
.env
.gitignore
ecommerce_database_setup.sql
LICENSE
README.md
requirements.txt
sample_test_LLM.py
src_code_llm/
    knn.py
    result_detailed_q.py
    result_simple_q.py
    sample_test_code_review_llm.py
src_sql/
    complete_code1.py
    complete_code2.py
    database_manager.py
    query_result.py
    sql_gen_cot.py
    sql_gen_tool1.py
    sql_gen_tool2.py
```

이 프로젝트는 데이터베이스와 코드 리뷰라는 두 가지 주요 영역에서 LLM 프롬프트 기술을 실험하는 데 중점을 두고 있습니다.