# CoT vs Tool 패턴 실습 프로젝트

import os
from typing import Dict, List

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

from src_sql.database_manager import DatabaseManager
from src_sql.query_result import QueryResult
from src_sql.sql_gen_cot import CoTSQLGenerator
from src_sql.sql_gen_tool2 import ToolSQLGenerator

# .env 파일 로드
load_dotenv()

# Rich 콘솔 설정
console = Console()


class PromptTester:
    """프롬프트 테스트 및 비교 시스템"""

    def __init__(
        self,
        db_manager: DatabaseManager,
        cot_generator: CoTSQLGenerator,
        tool_generator: ToolSQLGenerator,
    ):
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
                console.print(
                    "❌ 데이터베이스 연결이 끊어졌습니다. 재연결을 시도합니다.",
                    style="red",
                )
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

                results["cot"] = cot_result

            except Exception as e:
                console.print(f"❌ CoT 방식 실행 중 오류: {str(e)}", style="red")
                results["cot"] = QueryResult(
                    success=False, sql_query="", execution_time=0, error_message=str(e)
                )

            # Tool 방식 실행
            console.print("\n🔧 Tool 패턴 방식 실행 중...", style="yellow")
            try:
                tool_result = self.tool.generate_sql(
                    user_question, schema_info, self.db
                )

                if tool_result.success and tool_result.sql_query:
                    db_result = self.db.execute_query(tool_result.sql_query)
                    tool_result.result_data = db_result.result_data
                    if not db_result.success:
                        tool_result.error_message = db_result.error_message
                        tool_result.success = False

                results["tool"] = tool_result

            except Exception as e:
                console.print(f"❌ Tool 방식 실행 중 오류: {str(e)}", style="red")
                results["tool"] = QueryResult(
                    success=False, sql_query="", execution_time=0, error_message=str(e)
                )

        except Exception as e:
            console.print(f"❌ 비교 실행 중 전체 오류: {str(e)}", style="red")

        return results

    def display_results(self, results: Dict[str, QueryResult]):
        """결과 비교 표시"""
        console.print("\n" + "=" * 80, style="bold")
        console.print("📊 결과 비교", style="bold green")
        console.print("=" * 80, style="bold")

        # 비교 테이블
        comparison_table = Table(title="성능 비교")
        comparison_table.add_column("항목", style="cyan")
        comparison_table.add_column("CoT 패턴", style="green")
        comparison_table.add_column("Tool 패턴", style="yellow")

        cot_result = results["cot"]
        tool_result = results["tool"]

        comparison_table.add_row(
            "실행 성공",
            "✅" if cot_result.success else "❌",
            "✅" if tool_result.success else "❌",
        )

        comparison_table.add_row(
            "생성 시간",
            f"{cot_result.execution_time:.2f}초",
            f"{tool_result.execution_time:.2f}초",
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
    console.print(
        """
╔══════════════════════════════════════════════════════════════╗
║                 CoT vs Tool 패턴 실습 프로젝트                   ║
║                  프롬프트 엔지니어링 심화                        ║
╚══════════════════════════════════════════════════════════════╝
    """,
        style="bold blue",
    )

    # 환경 변수 확인
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_url = os.getenv("OPENAI_URL", None)
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not openai_api_key:
        console.print("❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.", style="red")
        console.print(
            "💡 .env 파일에 OPENAI_API_KEY=your-api-key 를 추가하세요.", style="yellow"
        )
        return

    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = int(os.getenv("MYSQL_PORT", 3306))
    mysql_user = os.getenv("MYSQL_USER", "root")
    mysql_password = os.getenv("MYSQL_PASSWORD")

    # 데이터베이스 연결
    db = DatabaseManager(
        host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_password
    )
    if not db.connect():
        console.print("❌ 데이터베이스 연결에 실패했습니다.", style="red")
        console.print("💡 MySQL 서버가 실행 중인지 확인하세요.", style="yellow")
        console.print(
            "💡 Docker: docker run --name prompt-mysql -e MYSQL_ROOT_PASSWORD=password123 -e MYSQL_DATABASE=ecommerce_demo -p 3306:3306 -d mysql:8.0",
            style="cyan",
        )
        return

    # 데이터베이스 초기화 여부 확인
    if Confirm.ask("데이터베이스를 초기화하시겠습니까? (기존 데이터가 삭제됩니다)"):
        if not db.setup_database():
            console.print("❌ 데이터베이스 설정에 실패했습니다.", style="red")
            return

    # SQL 생성기 초기화
    cot_generator = CoTSQLGenerator(
        openai_api_key, base_url=openai_url, openai_model=openai_model
    )
    tool_generator = ToolSQLGenerator(
        openai_api_key, base_url=openai_url, openai_model=openai_model
    )
    tester = PromptTester(db, cot_generator, tool_generator)

    # 예제 질문들
    example_questions = [
        "지난 3개월간 한국 고객들의 평균 주문 금액을 카테고리별로 보여주세요",
        "가장 많이 팔린 상품 TOP 5는 무엇인가요?",
        "월별 매출 추이를 보여주세요",
        "Electronics 카테고리에서 가장 비싼 상품은 무엇인가요?",
        "한국 고객 중 가장 많이 구매한 고객은 누구인가요?",
    ]

    while True:
        console.print("\n" + "=" * 60, style="bold")
        console.print("📝 질문을 선택하거나 직접 입력하세요", style="bold")
        console.print("=" * 60, style="bold")

        # 예제 질문 표시
        console.print("\n📋 예제 질문들:")
        for i, question in enumerate(example_questions, 1):
            console.print(f"  {i}. {question}")

        console.print(f"  {len(example_questions) + 1}. 직접 입력")
        console.print(f"  {len(example_questions) + 2}. 종료")

        choice = Prompt.ask(
            "\n선택하세요",
            choices=[str(i) for i in range(1, len(example_questions) + 3)],
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
