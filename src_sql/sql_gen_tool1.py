import re
import time
from typing import Dict, Optional

import openai

from src_sql.database_manager import DatabaseManager
from src_sql.query_result import QueryResult


class ToolSQLGenerator:
    """Tool 패턴 방식의 SQL 생성기"""

    def __init__(
        self,
        openai_api_key: str,
        base_url: Optional[str] = None,
        openai_model: str = "",
    ):
        self.client = openai.OpenAI(api_key=openai_api_key, base_url=base_url)
        self.openai_model = openai_model

    def generate_sql(
        self, user_question: str, schema_info: Dict, db_manager: DatabaseManager = None
    ) -> QueryResult:
        """Tool 패턴으로 SQL 쿼리 생성"""
        start_time = time.time()

        try:
            # Tool : 사용자 질문으로 한번에 SQL 생성
            sql_query = self._generate_sql_with_samples(user_question)

            execution_time = time.time() - start_time

            return QueryResult(
                success=True, sql_query=sql_query, execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return QueryResult(
                success=False,
                sql_query="",
                execution_time=execution_time,
                error_message=str(e),
            )

    def _generate_sql_with_samples(self, user_question: str) -> str:
        """Tool 2: 샘플 데이터와 질문을 결합하여 한번에 SQL 생성"""

        prompt = f"""
데이터베이스 전문가로서 사용자 질문을 정확한 SQL 쿼리로 변환하세요.

사용자 질문: "{user_question}"

SQL Query 로만 대답하세요.

참고:
- 한국은 Korea로 표기합니다.
"""

        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # 낮은 temperature --> 일관된 응답 생성
        )

        # 응답 정리
        sql_query = response.choices[0].message.content.strip()

        # 기본적인 정리
        sql_query = re.sub(r"```sql\s*", "", sql_query)
        sql_query = re.sub(r"\s*```", "", sql_query)
        sql_query = re.sub(r"--.*?\n", "", sql_query)
        sql_query = re.sub(r"/\*.*?\*/", "", sql_query, flags=re.DOTALL)
        sql_query = re.sub(r"\s+", " ", sql_query)

        return sql_query.strip()
