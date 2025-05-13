# 📚 Cennext Book Crawler & API

A Python-based project for crawling book data and serving it via a FastAPI REST API. Includes Docker support for easy deployment.

---

## 📦 Features

- Crawl book data using Scrapy
- Export data to `books.csv`
- Serve book data via FastAPI with API key authentication
- Filter books by country
- Swagger UI at `/docs`
- Dockerized for production use

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/lkpilot/Cennext_test.git
cd Cennext_test
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Create .env File

```bash
API_KEY_NAME=your_api_key_header_name
API_KEY=your_secure_api_key
BOOKS_FILE=your_path_to_books_file
```

### 5. Run the Scrapy Crawler

```bash
cd books
scrapy crawl books_crawler
```

### 6. FastAPI app

```bash
docker-compose up --build
```

- Visit the API docs at: http://127.0.0.1:8001/docs

### 7. Run with Docker

```bash
docker-compose up --build
```

- Once built, visit the API docs at: http://127.0.0.1:8001/docs