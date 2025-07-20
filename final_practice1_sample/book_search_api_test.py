# book_search_api_test.py - 메모리 기반 API용 테스트 코드
import pytest
from fastapi.testclient import TestClient
from book_search_api_server import app

# 테스트 클라이언트 생성
client = TestClient(app)

class TestBookSearchAPI:
    """도서 검색 API 테스트"""
    
    def test_health_check(self):
        """헬스 체크 테스트"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["total_books"] == 20
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "온라인 서점" in data["message"]
        assert data["total_books"] == 20
    
    def test_get_categories(self):
        """카테고리 목록 조회 테스트"""
        response = client.get("/api/v1/books/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "프로그래밍" in data["categories"]
        assert "AI" in data["categories"]
    
    def test_search_all_books(self):
        """전체 도서 조회 테스트"""
        response = client.get("/api/v1/books/search")
        assert response.status_code == 200
        data = response.json()
        
        # 기본 응답 구조 검증
        assert "data" in data
        assert "pagination" in data
        assert "search_info" in data
        
        # 페이징 정보 검증
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 20
        assert data["pagination"]["total_items"] == 20
        assert len(data["data"]) == 20
    
    def test_search_with_query(self):
        """검색어로 도서 검색 테스트"""
        response = client.get("/api/v1/books/search?q=python")
        assert response.status_code == 200
        data = response.json()
        
        # 검색 결과 검증
        assert len(data["data"]) >= 1  # 파이썬 관련 책이 있어야 함
        assert data["search_info"]["query"] == "python"
        
        # 검색된 책들이 실제로 python을 포함하는지 확인
        found_python_book = False
        for book in data["data"]:
            search_text = f"{book['title']} {book['author']} {book['description']}".lower()
            if "python" in search_text or "파이썬" in search_text:
                found_python_book = True
                break
        
        assert found_python_book, f"파이썬 관련 책을 찾지 못했습니다. 검색 결과: {[book['title'] for book in data['data']]}"
    
    def test_search_by_title(self):
        """제목으로 검색 테스트"""
        response = client.get("/api/v1/books/search?title=파이썬")
        assert response.status_code == 200
        data = response.json()
        
        # 제목에 '파이썬'이 포함된 책만 반환되어야 함
        for book in data["data"]:
            assert "파이썬" in book["title"]
    
    def test_search_by_author(self):
        """저자로 검색 테스트"""
        response = client.get("/api/v1/books/search?author=김개발")
        assert response.status_code == 200
        data = response.json()
        
        # 저자가 '김개발'인 책만 반환되어야 함
        for book in data["data"]:
            assert "김개발" in book["author"]
    
    def test_search_by_category(self):
        """카테고리 필터 테스트"""
        response = client.get("/api/v1/books/search?category=프로그래밍")
        assert response.status_code == 200
        data = response.json()
        
        assert "category" in data["search_info"]["filters_applied"]
        # 모든 결과가 '프로그래밍' 카테고리여야 함
        for book in data["data"]:
            assert book["category"] == "프로그래밍"
    
    def test_search_with_price_filter(self):
        """가격 필터 테스트"""
        response = client.get("/api/v1/books/search?min_price=30000&max_price=50000")
        assert response.status_code == 200
        data = response.json()
        
        assert "price" in data["search_info"]["filters_applied"]
        # 모든 결과가 가격 범위 내에 있어야 함
        for book in data["data"]:
            assert 30000 <= book["price"] <= 50000
    
    def test_search_with_rating_filter(self):
        """평점 필터 테스트"""
        response = client.get("/api/v1/books/search?min_rating=4.5")
        assert response.status_code == 200
        data = response.json()
        
        assert "rating" in data["search_info"]["filters_applied"]
        # 모든 결과가 평점 4.5 이상이어야 함
        for book in data["data"]:
            assert book["rating"] >= 4.5
    
    def test_search_with_sorting_price_asc(self):
        """가격 오름차순 정렬 테스트"""
        response = client.get("/api/v1/books/search?sort_by=price&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        
        # 가격이 오름차순으로 정렬되어 있는지 확인
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices)
    
    def test_search_with_sorting_price_desc(self):
        """가격 내림차순 정렬 테스트"""
        response = client.get("/api/v1/books/search?sort_by=price&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        
        # 가격이 내림차순으로 정렬되어 있는지 확인
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices, reverse=True)
    
    def test_search_with_sorting_rating_desc(self):
        """평점 내림차순 정렬 테스트"""
        response = client.get("/api/v1/books/search?sort_by=rating&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        
        # 평점이 내림차순으로 정렬되어 있는지 확인
        ratings = [book["rating"] for book in data["data"]]
        assert ratings == sorted(ratings, reverse=True)
    
    def test_pagination_first_page(self):
        """첫 번째 페이지 테스트"""
        response = client.get("/api/v1/books/search?page=1&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 5
        assert len(data["data"]) == 5
        assert data["pagination"]["has_prev"] == False
        assert data["pagination"]["has_next"] == True
    
    def test_pagination_second_page(self):
        """두 번째 페이지 테스트"""
        response = client.get("/api/v1/books/search?page=2&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_prev"] == True
        assert len(data["data"]) == 5
    
    def test_pagination_last_page(self):
        """마지막 페이지 테스트"""
        response = client.get("/api/v1/books/search?page=4&page_size=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["pagination"]["page"] == 4
        assert data["pagination"]["has_next"] == False
        assert len(data["data"]) == 5  # 20개 총 도서, 5개씩 4페이지
    
    def test_complex_search(self):
        """복합 검색 테스트"""
        response = client.get(
            "/api/v1/books/search?"
            "category=프로그래밍&"
            "min_price=25000&"
            "max_price=45000&"
            "min_rating=4.0&"
            "sort_by=price&"
            "sort_order=asc"
        )
        assert response.status_code == 200
        data = response.json()
        
        # 필터가 올바르게 적용되었는지 확인
        expected_filters = {"price", "rating", "category"}
        applied_filters = set(data["search_info"]["filters_applied"])
        assert expected_filters.issubset(applied_filters)
        
        # 모든 조건을 만족하는지 확인
        for book in data["data"]:
            assert book["category"] == "프로그래밍"
            assert 25000 <= book["price"] <= 45000
            assert book["rating"] >= 4.0
        
        # 가격이 오름차순인지 확인
        prices = [book["price"] for book in data["data"]]
        assert prices == sorted(prices)
    
    def test_invalid_price_range(self):
        """잘못된 가격 범위 테스트"""
        response = client.get("/api/v1/books/search?min_price=50000&max_price=30000")
        assert response.status_code == 400
        assert "최대 가격이 최소 가격보다 작을 수 없습니다" in response.json()["detail"]
    
    def test_invalid_page_size(self):
        """잘못된 페이지 크기 테스트"""
        response = client.get("/api/v1/books/search?page_size=200")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_rating(self):
        """잘못된 평점 범위 테스트"""
        response = client.get("/api/v1/books/search?min_rating=6.0")
        assert response.status_code == 422  # Validation error
    
    def test_no_results_search(self):
        """검색 결과가 없는 경우 테스트"""
        response = client.get("/api/v1/books/search?q=존재하지않는책")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 0
        assert data["pagination"]["total_items"] == 0
        assert data["pagination"]["total_pages"] == 0
    
    def test_response_time(self):
        """응답 시간 테스트"""
        import time
        start_time = time.time()
        response = client.get("/api/v1/books/search?q=python")
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert response_time_ms < 100  # 100ms 이내 (메모리 기반이므로 매우 빠름)
        
        # API 내부에서 측정한 시간도 확인
        data = response.json()
        assert data["search_info"]["total_time_ms"] < 50

class TestBookResponseModel:
    """BookResponse 모델 테스트"""
    
    def test_book_response_structure(self):
        """도서 응답 구조 테스트"""
        response = client.get("/api/v1/books/search?page_size=1")
        assert response.status_code == 200
        data = response.json()
        
        book = data["data"][0]
        required_fields = [
            "id", "title", "author", "category", "price", 
            "rating", "published_date", "isbn", "description"
        ]
        
        for field in required_fields:
            assert field in book
        
        # 데이터 타입 검증
        assert isinstance(book["id"], str)
        assert isinstance(book["title"], str)
        assert isinstance(book["author"], str)
        assert isinstance(book["category"], str)
        assert isinstance(book["price"], (int, float))
        assert isinstance(book["rating"], (int, float))
        assert isinstance(book["isbn"], str)
        assert isinstance(book["description"], str)

# 성능 테스트
class TestPerformance:
    """성능 테스트"""
    
    def test_concurrent_requests(self):
        """동시 요청 처리 테스트"""
        import concurrent.futures
        import time
        
        def make_request():
            return client.get("/api/v1/books/search?q=python")
        
        start_time = time.time()
        
        # 10개의 동시 요청
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 모든 요청이 성공했는지 확인
        for response in responses:
            assert response.status_code == 200
        
        # 10개 요청이 1초 이내에 완료되어야 함
        assert total_time < 1.0
    
    def test_large_page_size(self):
        """큰 페이지 크기 처리 테스트"""
        response = client.get("/api/v1/books/search?page_size=100")
        assert response.status_code == 200
        data = response.json()
        
        # 전체 도서가 20개이므로 20개만 반환되어야 함
        assert len(data["data"]) == 20
        assert data["pagination"]["total_items"] == 20

if __name__ == "__main__":
    # 테스트 실행 방법 안내
    print("=" * 60)
    print("📚 도서 검색 API 테스트 코드")
    print("=" * 60)
    print()
    print("🛠️  테스트 실행 방법:")
    print()
    print("1️⃣  전체 테스트 실행:")
    print("   pytest book_search_api_test.py -v")
    print()
    print("2️⃣  특정 테스트 클래스만 실행:")
    print("   pytest book_search_api_test.py::TestBookSearchAPI -v")
    print()
    print("3️⃣  특정 테스트 메서드만 실행:")
    print("   pytest book_search_api_test.py::TestBookSearchAPI::test_search_with_query -v")
    print()
    print("4️⃣  성능 테스트만 실행:")
    print("   pytest book_search_api_test.py::TestPerformance -v")
    print()
    print("5️⃣  커버리지와 함께 실행:")
    print("   pytest book_search_api_test.py --cov=book_search_api_server --cov-report=html")
    print()
    print("6️⃣  간단한 실행 (출력 최소화):")
    print("   pytest book_search_api_test.py -q")
    print()
    print("📋 테스트 전 확인사항:")
    print("   - book_search_api_server.py 서버가 실행 중이어야 합니다")
    print("   - pip install pytest pytest-cov 필요")
    print("=" * 60)