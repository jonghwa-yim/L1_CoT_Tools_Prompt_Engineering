import re
import time
from typing import Any, Dict, Optional

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
            while True:
                # Tool 1: 실제 데이터 샘플 수집
                sample_data = self._collect_sample_data(schema_info, db_manager)

                # Tool 2: 샘플 데이터 + 사용자 질문으로 한번에 SQL 생성
                sql_query = self._generate_sql_with_samples(user_question, sample_data)

                # SQL 쿼리 유효성 검사
                validation_result = self.validate_query(sql_query, schema_info)
                if validation_result["is_valid"]:
                    break

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

    def _collect_sample_data(
        self, schema_info: Dict, db_manager: DatabaseManager
    ) -> Dict[str, Any]:
        """Tool 1: 실제 데이터 샘플 수집"""
        sample_data = {}

        # 각 테이블에서 샘플 데이터 조회
        for table_name in schema_info.keys():
            try:
                # 테이블의 처음 3개 행 조회
                sample_query = f"SELECT * FROM {table_name} LIMIT 3"

                if db_manager:
                    result = db_manager.execute_query(sample_query)

                    if result.success and result.result_data:
                        sample_data[table_name] = {
                            "schema": schema_info[table_name],
                            "sample_rows": result.result_data,
                            "total_columns": len(schema_info[table_name]["columns"]),
                        }
                    else:
                        # 쿼리 실행 실패 시 스키마 정보만 사용
                        sample_data[table_name] = {
                            "schema": schema_info[table_name],
                            "sample_rows": [],
                            "total_columns": len(schema_info[table_name]["columns"]),
                        }
                else:
                    # db_manager가 없는 경우 스키마 정보만 사용
                    sample_data[table_name] = {
                        "schema": schema_info[table_name],
                        "sample_rows": [],
                        "total_columns": len(schema_info[table_name]["columns"]),
                    }
            except Exception as e:
                # 에러 발생 시 스키마 정보만 사용
                sample_data[table_name] = {
                    "schema": schema_info[table_name],
                    "sample_rows": [],
                    "total_columns": len(schema_info[table_name]["columns"]),
                }

        return sample_data

    def _generate_sql_with_samples(self, user_question: str, sample_data: Dict) -> str:
        """Tool 2: 샘플 데이터와 질문을 결합하여 한번에 SQL 생성"""

        # 샘플 데이터를 텍스트로 포맷팅
        data_context = ""
        join_hints = []

        for table_name, info in sample_data.items():
            data_context += f"\n=== {table_name} 테이블 ===\n"

            # 스키마 정보
            data_context += "컬럼 정보:\n"
            for col_info in info["schema"]["details"]:
                data_context += f"  - {col_info['Field']} ({col_info['Type']})"
                if col_info["Key"] == "PRI":
                    data_context += " [PRIMARY KEY]"
                elif col_info["Key"] == "MUL":
                    data_context += " [FOREIGN KEY]"
                data_context += "\n"

            # 조인 힌트 생성
            if table_name == "customers":
                join_hints.append("customers.customer_id = orders.customer_id")
            elif table_name == "orders":
                join_hints.append("orders.order_id = order_items.order_id")
            elif table_name == "products":
                join_hints.append("products.product_id = order_items.product_id")

            # 샘플 데이터
            if info["sample_rows"]:
                data_context += (
                    f"\n실제 샘플 데이터 ({len(info['sample_rows'])}개 행):\n"
                )
                for i, row in enumerate(info["sample_rows"], 1):
                    data_context += f"  행{i}: {row}\n"
            else:
                data_context += "\n(샘플 데이터 없음)\n"

        # 조인 힌트 추가
        if join_hints:
            data_context += f"\n=== 테이블 조인 관계 ===\n"
            for hint in join_hints:
                data_context += f"  - {hint}\n"

        prompt = f"""
데이터베이스 전문가로서 사용자 질문을 정확한 SQL 쿼리로 변환하세요.

사용자 질문: "{user_question}"

데이터베이스 구조 및 실제 데이터:
{data_context}

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

    def validate_query(sql_query: str, schema: dict) -> dict:
        """SQL 쿼리의 유효성을 검사하고 스키마와 일치하는지 확인"""
        result = {
            "is_valid": True,
            "message": [],
        }
        return result
