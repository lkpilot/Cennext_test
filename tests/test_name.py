from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
headers = {"X-API-KEY": "1234567890"}

def test_get_books_all():
    response = client.get("/books", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_books_by_country():
    response = client.get("/books?country=Italy", headers=headers)
    assert response.status_code in (200, 404)  # 404 if no books for 'Italy'

def test_post_book():
    book = {
        "title": "Unit Test Book",
        "price": "15$",
        "availability": "In Stock",
        "star": 4,
        "cate": "Testing",
        "product_url": "http://example.com/book",
        "country": "Testland"
    }
    response = client.post("/books", headers=headers, json=book)
    assert response.status_code == 200
    assert response.json()["title"] == "Unit Test Book"

def test_invalid_api_key():
    response = client.get("/books", headers={"X-API-KEY": "wrongkey"})
    assert response.status_code == 403
