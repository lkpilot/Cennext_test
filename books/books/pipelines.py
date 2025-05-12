import psycopg2
from itemadapter import ItemAdapter
import os
import csv
from dotenv import load_dotenv
load_dotenv("C:/NNL/Cennext/.env")


class BooksPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        star_mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5
        }

        raw_star = adapter.get("star", "").title()  
        adapter["star"] = star_mapping.get(raw_star, 0)  

        return item
    



class DualCSVExportPipeline:
    def open_spider(self, spider):
        self.books_file = open('books.csv', 'w', newline='', encoding='utf-8')
        self.books_with_country_file = open('books_with_country.csv', 'w', newline='', encoding='utf-8')

        self.books_writer = csv.writer(self.books_file)
        self.books_with_country_writer = csv.writer(self.books_with_country_file)

        # Write headers
        self.books_writer.writerow(['title', 'price', 'availability', 'star', 'cate', 'product_url'])
        self.books_with_country_writer.writerow(['title', 'price', 'availability', 'star', 'cate', 'product_url', 'country'])

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        base_data = [
            adapter.get('title'),
            adapter.get('price'),
            adapter.get('availability'),
            adapter.get('star'),
            adapter.get('cate'),
            adapter.get('product_url')
        ]
        
        self.books_writer.writerow(base_data)
        self.books_with_country_writer.writerow(base_data + [adapter.get('country')])
        
        return item

    def close_spider(self, spider):
        self.books_file.close()
        self.books_with_country_file.close()



class BooksPostgresPipeline:
    def open_spider(self, spider):
        self.connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT")
        )
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT,
                price TEXT,
                availability TEXT,
                star INTEGER,
                cate TEXT,
                product_url TEXT UNIQUE,  -- Ensure product_url is unique
                country TEXT
            )
        """)
        self.connection.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        product_url = adapter.get("product_url")

        self.cursor.execute("SELECT 1 FROM books WHERE product_url = %s", (product_url,))
        existing = self.cursor.fetchone()

        if existing:
            spider.logger.info(f"Product URL {product_url} already exists in the database.")
            return None

        self.cursor.execute("""
            INSERT INTO books (title, price, availability, star, cate, product_url, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            adapter.get("title"),
            adapter.get("price"),
            adapter.get("availability"),
            adapter.get("star"),
            adapter.get("cate"),
            adapter.get("product_url"),
            adapter.get("country"),
        ))
        self.connection.commit()

        spider.logger.info(f"Inserted {product_url} into the database.")
        return item



