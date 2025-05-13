import logging
import pandas as pd
import os
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from cachetools import cached, TTLCache
from starlette.requests import Request
import time
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


API_KEY_NAME = os.getenv("API_KEY_NAME", "")
API_KEY = os.getenv("API_KEY", "")
BOOKS_FILE = os.getenv("BOOKS_FILE", "")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Book(BaseModel):
    title: str
    price: str
    availability: str
    star: int
    cate: str
    product_url: str
    country: str


cache = TTLCache(maxsize=100, ttl=3600)



def api_key_required(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        logger.warning("Invalid API Key attempt")
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    logger.info("API Key validated successfully.")
    return api_key



@cached(cache)
def load_books():
    try:
        if os.path.exists(BOOKS_FILE):
            logger.info(f"Loading books from {BOOKS_FILE}")
            return pd.read_csv(BOOKS_FILE)
        else:
            logger.error(f"{BOOKS_FILE} not found.")
            raise FileNotFoundError(f"{BOOKS_FILE} not found.")
    except Exception as e:
        logger.error(f"Error loading books data: {e}")
        raise HTTPException(status_code=500, detail="Error loading books data.")
    
books_df = load_books()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} | Time: {process_time:.3f}s")

    return response




@app.get("/")
async def read_root():
    return {"Hello": "World"}




@app.get("/books", response_model=List[Book])
async def get_books(country: Optional[str] = None, api_key: str = Depends(api_key_required)):
    try:
        logger.info(f"Fetching books with country filter: {country}")
        if country:
            filtered_books = books_df[books_df['country'].str.lower() == country.lower()]
        else:
            filtered_books = books_df

        if filtered_books.empty:
            logger.warning(f"No books found for country: {country}")
            raise HTTPException(status_code=404, detail="Books not found")

        return filtered_books.to_dict(orient='records')
    except Exception as e:
        logger.error(f"Error fetching books: {e}")  
        raise HTTPException(status_code=500, detail=f"Error fetching books: {e}")  






@app.post("/books", response_model=Book)
async def add_book(book: Book, api_key: str = Depends(api_key_required)):
    try:
        logger.info(f"Adding book: {book.title}")
        global books_df

        new_book = book.dict()
        books_df = pd.concat([books_df, pd.DataFrame([new_book])], ignore_index=True)
        books_df.to_csv(BOOKS_FILE, index=False)

        logger.info(f"Book {book.title} added successfully.")
        return new_book
    except Exception as e:
        logger.error(f"Error adding book: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding book: {e}")





@app.delete("/books/{title}", response_class=JSONResponse)
async def delete_book(title: str, api_key: str = Depends(api_key_required)):
    try:
        logger.info(f"Deleting book with title: {title}")
        global books_df

        original_count = len(books_df)
        books_df = books_df[books_df['title'].str.lower() != title.lower()]
        new_count = len(books_df)

        if original_count == new_count:
            logger.warning(f"Book not found: {title}")
            raise HTTPException(status_code=404, detail="Book not found")

        books_df.to_csv(BOOKS_FILE, index=False)

        logger.info(f"Book {title} deleted successfully.")
        return JSONResponse(status_code=200, content={"message": f"Book '{title}' deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting book: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting book: {e}")

