# simple_main.py - 데이터베이스 없이 바로 실행 가능한 버전
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import time

# === 모델 정의 ===
class SortBy(str, Enum):
    POPULARITY = "popularity"
    PUBLISHED_DATE = "published_date" 
    PRICE = "price"
    RATING = "rating"

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    category: str
    price: float
    rating: float
    published_date: datetime
    isbn: str
    description: str
    cover_image_url: Optional[str] = None

class PaginationInfo(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_prev: bool

class SearchInfo(BaseModel):
    query: Optional[str]
    total_time_ms: int
    filters_applied: List[str]

class BookSearchResponse(BaseModel):
    data: List[BookResponse]
    pagination: PaginationInfo
    search_info: SearchInfo

# === 샘플 데이터 ===
SAMPLE_BOOKS = [
    {
        "id": "1", "title": "파이썬 완벽 가이드", "author": "김개발", "category": "프로그래밍",
        "price": 35000.0, "rating": 4.8, "published_date": datetime(2024, 1, 15),
        "isbn": "9791234567890", "description": "파이썬 프로그래밍의 모든 것", 
        "cover_image_url": None, "popularity_score": 95
    },
    {
        "id": "2", "title": "자바스크립트 마스터", "author": "박코딩", "category": "프로그래밍",
        "price": 28000.0, "rating": 4.5, "published_date": datetime(2024, 2, 20),
        "isbn": "9791234567891", "description": "모던 자바스크립트 완전 정복",
        "cover_image_url": None, "popularity_score": 87
    },
    {
        "id": "3", "title": "데이터 사이언스 입문", "author": "이분석", "category": "데이터",
        "price": 42000.0, "rating": 4.7, "published_date": datetime(2024, 3, 10),
        "isbn": "9791234567892", "description": "데이터 과학의 기초부터 실전까지",
        "cover_image_url": None, "popularity_score": 92
    },
    {
        "id": "4", "title": "머신러닝 실무", "author": "최인공", "category": "AI",
        "price": 48000.0, "rating": 4.9, "published_date": datetime(2024, 1, 25),
        "isbn": "9791234567893", "description": "실무에서 바로 쓰는 머신러닝",
        "cover_image_url": None, "popularity_score": 98
    },
    {
        "id": "5", "title": "웹 개발 트렌드", "author": "한웹맨", "category": "웹개발",
        "price": 32000.0, "rating": 4.3, "published_date": datetime(2024, 3, 5),
        "isbn": "9791234567894", "description": "최신 웹 개발 기술 동향",
        "cover_image_url": None, "popularity_score": 78
    },
    {
        "id": "6", "title": "클라우드 컴퓨팅", "author": "구름이", "category": "인프라",
        "price": 39000.0, "rating": 4.6, "published_date": datetime(2024, 2, 28),
        "isbn": "9791234567895", "description": "AWS, Azure, GCP 완벽 가이드",
        "cover_image_url": None, "popularity_score": 85
    },
    {
        "id": "7", "title": "리액트 네이티브", "author": "모바일킹", "category": "모바일",
        "price": 33000.0, "rating": 4.4, "published_date": datetime(2024, 3, 15),
        "isbn": "9791234567896", "description": "크로스 플랫폼 앱 개발",
        "cover_image_url": None, "popularity_score": 82
    },
    {
        "id": "8", "title": "도커 & 쿠버네티스", "author": "컨테이너맨", "category": "인프라",
        "price": 44000.0, "rating": 4.8, "published_date": datetime(2024, 1, 30),
        "isbn": "9791234567897", "description": "컨테이너 오케스트레이션",
        "cover_image_url": None, "popularity_score": 90
    },
    {
        "id": "9", "title": "블록체인 개발", "author": "체인코더", "category": "블록체인",
        "price": 52000.0, "rating": 4.2, "published_date": datetime(2024, 2, 15),
        "isbn": "9791234567898", "description": "스마트 컨트랙트부터 DApp까지",
        "cover_image_url": None, "popularity_score": 75
    },
    {
        "id": "10", "title": "사이버 보안", "author": "해커맨", "category": "보안",
        "price": 46000.0, "rating": 4.7, "published_date": datetime(2024, 3, 20),
        "isbn": "9791234567899", "description": "화이트해커가 되는 길",
        "cover_image_url": None, "popularity_score": 88
    },
    {
        "id": "11", "title": "알고리즘 문제 해결", "author": "코테왕", "category": "알고리즘",
        "price": 29000.0, "rating": 4.5, "published_date": datetime(2024, 1, 10),
        "isbn": "9791234567800", "description": "코딩테스트 완전 정복",
        "cover_image_url": None, "popularity_score": 93
    },
    {
        "id": "12", "title": "게임 개발 입문", "author": "게임메이커", "category": "게임",
        "price": 38000.0, "rating": 4.3, "published_date": datetime(2024, 2, 10),
        "isbn": "9791234567801", "description": "Unity로 만드는 첫 게임",
        "cover_image_url": None, "popularity_score": 80
    },
    {
        "id": "13", "title": "UI/UX 디자인", "author": "디자이너", "category": "디자인",
        "price": 34000.0, "rating": 4.6, "published_date": datetime(2024, 3, 25),
        "isbn": "9791234567802", "description": "사용자 중심 디자인 가이드",
        "cover_image_url": None, "popularity_score": 86
    },
    {
        "id": "14", "title": "빅데이터 처리", "author": "데이터킹", "category": "데이터",
        "price": 45000.0, "rating": 4.8, "published_date": datetime(2024, 1, 20),
        "isbn": "9791234567803", "description": "Spark와 Hadoop 실무",
        "cover_image_url": None, "popularity_score": 91
    },
    {
        "id": "15", "title": "IoT 개발", "author": "사물맨", "category": "IoT",
        "price": 37000.0, "rating": 4.4, "published_date": datetime(2024, 3, 30),
        "isbn": "9791234567804", "description": "아두이노부터 라즈베리파이까지",
        "cover_image_url": None, "popularity_score": 79
    },
    {
        "id": "16", "title": "파이썬 데이터 분석", "author": "김데이터", "category": "데이터",
        "price": 31000.0, "rating": 4.7, "published_date": datetime(2024, 2, 5),
        "isbn": "9791234567805", "description": "pandas와 numpy 마스터",
        "cover_image_url": None, "popularity_score": 89
    },
    {
        "id": "17", "title": "자바 스프링 부트", "author": "스프링맨", "category": "프로그래밍",
        "price": 41000.0, "rating": 4.5, "published_date": datetime(2024, 1, 5),
        "isbn": "9791234567806", "description": "실무 웹 애플리케이션 개발",
        "cover_image_url": None, "popularity_score": 84
    },
    {
        "id": "18", "title": "Go 언어 입문", "author": "고퍼", "category": "프로그래밍",
        "price": 27000.0, "rating": 4.2, "published_date": datetime(2024, 3, 12),
        "isbn": "9791234567807", "description": "동시성 프로그래밍의 새로운 패러다임",
        "cover_image_url": None, "popularity_score": 76
    },
    {
        "id": "19", "title": "러스트 시스템 프로그래밍", "author": "러스터", "category": "프로그래밍",
        "price": 43000.0, "rating": 4.9, "published_date": datetime(2024, 2, 22),
        "isbn": "9791234567808", "description": "메모리 안전성과 성능의 조화",
        "cover_image_url": None, "popularity_score": 94
    },
    {
        "id": "20", "title": "AI 윤리학", "author": "윤리박사", "category": "AI",
        "price": 25000.0, "rating": 4.1, "published_date": datetime(2024, 3, 8),
        "isbn": "9791234567809", "description": "인공지능 시대의 도덕적 고찰",
        "cover_image_url": None, "popularity_score": 73
    }
]

# === FastAPI 앱 설정 ===
app = FastAPI(
    title="📚 온라인 서점 API",
    version="1.0.0",
    description="간단한 도서 검색 API (메모리 기반)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === 검색 함수 ===
def search_books_in_memory(
    books: List[dict],
    q: Optional[str] = None,
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rating: Optional[float] = None,
    sort_by: SortBy = SortBy.POPULARITY,
    sort_order: SortOrder = SortOrder.DESC,
    page: int = 1,
    page_size: int = 20
) -> tuple[List[dict], int]:
    """메모리에서 도서 검색"""
    
    # 필터링
    filtered_books = []
    for book in books:
        # 검색어 필터 (한글/영어 매칭 개선)
        if q:
            search_text = f"{book['title']} {book['author']} {book['description']}".lower()
            query_lower = q.lower()
            
            # 기본 검색
            if query_lower in search_text:
                pass  # 매칭됨
            # 한글-영어 매칭 (python ↔ 파이썬)
            elif query_lower == "python" and ("파이썬" in search_text or "python" in search_text):
                pass  # 매칭됨
            elif query_lower == "파이썬" and ("python" in search_text or "파이썬" in search_text):
                pass  # 매칭됨
            # 기타 한글-영어 매칭
            elif query_lower == "javascript" and ("자바스크립트" in search_text or "javascript" in search_text):
                pass  # 매칭됨
            elif query_lower == "자바스크립트" and ("javascript" in search_text or "자바스크립트" in search_text):
                pass  # 매칭됨
            else:
                continue  # 매칭 안됨
        
        # 제목 필터
        if title and title.lower() not in book['title'].lower():
            continue
            
        # 저자 필터
        if author and author.lower() not in book['author'].lower():
            continue
            
        # 카테고리 필터
        if category and book['category'] != category:
            continue
            
        # 가격 필터
        if min_price is not None and book['price'] < min_price:
            continue
        if max_price is not None and book['price'] > max_price:
            continue
            
        # 평점 필터
        if min_rating is not None and book['rating'] < min_rating:
            continue
            
        filtered_books.append(book)
    
    # 정렬
    sort_key_map = {
        SortBy.POPULARITY: "popularity_score",
        SortBy.PUBLISHED_DATE: "published_date",
        SortBy.PRICE: "price",
        SortBy.RATING: "rating"
    }
    
    sort_key = sort_key_map[sort_by]
    reverse = (sort_order == SortOrder.DESC)
    filtered_books.sort(key=lambda x: x[sort_key], reverse=reverse)
    
    # 페이징
    total_count = len(filtered_books)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_books = filtered_books[start_idx:end_idx]
    
    return paginated_books, total_count

# === API 엔드포인트 ===
@app.get("/api/v1/books/search", response_model=BookSearchResponse)
async def search_books(
    q: Optional[str] = Query(None, description="통합 검색어"),
    title: Optional[str] = Query(None, description="제목 검색"),
    author: Optional[str] = Query(None, description="저자 검색"),
    category: Optional[str] = Query(None, description="카테고리"),
    min_price: Optional[float] = Query(None, ge=0, description="최소 가격"),
    max_price: Optional[float] = Query(None, ge=0, description="최대 가격"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="최소 평점"),
    sort_by: SortBy = Query(SortBy.POPULARITY, description="정렬 기준"),
    sort_order: SortOrder = Query(SortOrder.DESC, description="정렬 순서"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기")
):
    """📚 도서 검색 API"""
    
    start_time = time.time()
    
    # 파라미터 검증
    if max_price is not None and min_price is not None and max_price < min_price:
        raise HTTPException(status_code=400, detail="최대 가격이 최소 가격보다 작을 수 없습니다")
    
    try:
        # 검색 실행
        books_data, total_count = search_books_in_memory(
            SAMPLE_BOOKS, q, title, author, category, 
            min_price, max_price, min_rating,
            sort_by, sort_order, page, page_size
        )
        
        # 응답 데이터 구성
        books = [BookResponse(**book) for book in books_data]
        
        # 페이징 정보
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1
        
        pagination = PaginationInfo(
            page=page,
            page_size=page_size,
            total_items=total_count,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )
        
        # 적용된 필터 목록
        filters_applied = []
        if min_price is not None or max_price is not None:
            filters_applied.append("price")
        if min_rating is not None:
            filters_applied.append("rating")
        if category:
            filters_applied.append("category")
            
        search_info = SearchInfo(
            query=q or title or author,
            total_time_ms=int((time.time() - start_time) * 1000),
            filters_applied=filters_applied
        )
        
        return BookSearchResponse(
            data=books,
            pagination=pagination,
            search_info=search_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")

@app.get("/api/v1/books/categories")
async def get_categories():
    """📂 카테고리 목록 조회"""
    categories = list(set(book["category"] for book in SAMPLE_BOOKS))
    return {"categories": sorted(categories)}

@app.get("/health")
async def health_check():
    """🏥 헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "total_books": len(SAMPLE_BOOKS),
        "message": "도서 검색 API가 정상 작동 중입니다!"
    }

@app.get("/")
async def root():
    """🏠 API 홈페이지"""
    return {
        "message": "📚 온라인 서점 도서 검색 API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "total_books": len(SAMPLE_BOOKS),
        "docs": "http://localhost:8000/docs",
        "search_endpoint": "/api/v1/books/search",
        "sample_searches": [
            "http://localhost:8000/api/v1/books/search?q=python",
            "http://localhost:8000/api/v1/books/search?category=프로그래밍&min_rating=4.5",
            "http://localhost:8000/api/v1/books/search?sort_by=price&sort_order=asc",
            "http://localhost:8000/api/v1/books/search?min_price=30000&max_price=50000"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 간단한 도서 검색 API 시작 중...")
    print("📚 총 도서 수:", len(SAMPLE_BOOKS))
    print("🌐 API 주소: http://localhost:8000")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔍 검색 테스트: http://localhost:8000/api/v1/books/search?q=python")
    uvicorn.run("book_search_api_server:app", host="0.0.0.0", port=8000, reload=True)