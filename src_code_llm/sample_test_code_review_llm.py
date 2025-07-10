import os

from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키와 URL 불러오기
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_URL")

client = OpenAI(api_key=api_key, base_url=base_url)

contents = open("src_code_llm/knn.py", "r").read()

question_simple = """이 Python 코드를 리뷰하고 개선안을 제시해주세요."""

completion = client.chat.completions.create(
    model="ax4",
    messages=[
        {
            "role": "user",
            "content": question_simple,
        },
        {
            "role": "user",
            "content": contents,
        },
    ],
)

print("*** Simple Review: ***")
print(completion.choices[0].message.content)

question_detailed = """**역할**: 5년 이상 경력의 ML 및 Python 시니어 개발자

**요청사항**: 
다음 Python 코드가 어떤 역할을 하는지 분석하고,
오류 또는 비효율적인 코드가 있는지 리뷰하고 완벽히 해결된 개선안을 제시해주세요."""

completion = client.chat.completions.create(
    model="ax4",
    messages=[
        {
            "role": "user",
            "content": question_detailed,
        },
        {
            "role": "user",
            "content": contents,
        },
    ],
)

print("\n*** Detailed Review: ***")
print(completion.choices[0].message.content)
