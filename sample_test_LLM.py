import os

from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키와 URL 불러오기
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_URL", None)
model_name = os.getenv("OPENAI_MODEL", None)

client = OpenAI(api_key=api_key, base_url=base_url)


contents = """데이터베이스: 전자상거래 플랫폼

**역할**: 5년 이상 경력의 데이터베이스 전문가

**목표**: 자연어 질문을 정확한 SQL 쿼리로 변환

**사용자 질문**: "지난 3개월간 한국 고객들의 평균 주문 금액을 카테고리별로 보여주세요"

**데이터베이스 스키마**:
- customers: customer_id, name, email, country, signup_date
- orders: order_id, customer_id, order_date, total_amount, status
- products: product_id, name, category, price, stock_quantity
- order_items: order_item_id, order_id, product_id, quantity, unit_price
"""

contents_CoT = """데이터베이스: 전자상거래 플랫폼

**역할**: 5년 이상 경력의 데이터베이스 전문가

**목표**: 자연어 질문을 정확한 SQL 쿼리로 변환

**사용자 질문**: "지난 3개월간 한국 고객들의 평균 주문 금액을 카테고리별로 보여주세요"

**데이터베이스 스키마**:
- customers: customer_id, name, email, country, signup_date
- orders: order_id, customer_id, order_date, total_amount, status
- products: product_id, name, category, price, stock_quantity
- order_items: order_item_id, order_id, product_id, quantity, unit_price

**단계별 사고 과정**:

1단계: 질문 분석 및 요구사항 추출
- (추출 내용)
- 검증: 모든 주요 키워드가 SQL 요소로 매핑되었는가?

2단계: 필요한 테이블 식별
- (주 테이블 및 연결 테이블)
- 검증: 모든 필요 데이터에 접근 가능한가?

3단계: 조인 관계 설계
- ...
- 검증: 조인 경로가 논리적으로 올바른가?

4단계: 필터 조건 구성
- (필터...)
- 검증: 필터가 요구사항을 정확히 반영하는가?

5단계: 집계 및 그룹화 설계
- (집계 함수 및 그룹화 기준)
- 검증: 비즈니스 관점에서 유의미한 결과인가?"""

completion = client.chat.completions.create(
    model=model_name,
    messages=[
        {
            "role": "user",
            "content": contents,
        },
    ],
)

print(completion.choices[0].message.content)
