from dataclasses import dataclass
from typing import Dict, List


@dataclass
class QueryResult:
    """쿼리 실행 결과를 담는 데이터 클래스"""

    success: bool
    sql_query: str
    execution_time: float
    result_data: List[Dict] = None
    error_message: str = None
    reasoning_steps: List[str] = None
