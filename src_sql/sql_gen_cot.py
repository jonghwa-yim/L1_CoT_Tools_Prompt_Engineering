import re
import time
from typing import Dict, List, Optional

import openai

from src_sql.query_result import QueryResult


class CoTSQLGenerator:
    """Chain of Thought 방식의 SQL 생성기"""

    def __init__(
        self,
        openai_api_key: str,
        base_url: Optional[str] = None,
        openai_model: str = "",
    ):
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
                temperature=0.1,  # 낮은 temperature --> 일관된 응답 생성
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
                reasoning_steps=reasoning_steps,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query="",
                execution_time=execution_time,
                error_message=str(e),
            )

    def _format_schema_info(self, schema_info: Dict) -> str:
        """스키마 정보를 문자열로 포맷팅"""
        schema_text = ""
        for table_name, info in schema_info.items():
            schema_text += f"\n{table_name} 테이블:\n"
            for col in info["details"]:
                schema_text += f"  - {col['Field']} ({col['Type']})\n"
        return schema_text

    def _extract_reasoning_steps(self, content: str) -> List[str]:
        """응답에서 추론 단계들 추출"""
        steps = []
        for i in range(1, 7):
            pattern = rf"{i}단계:(.+?)(?={i + 1}단계:|```sql|$)"
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
