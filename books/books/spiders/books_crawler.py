import scrapy
import os 
import requests
import random
from books.items import BooksItem


class BooksSpider(scrapy.Spider):
    name = "books_crawler"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/catalogue/category/books_1/index.html"]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.countries = self.get_countries()



    def get_countries(self):
        try:
            response = requests.get("https://restcountries.com/v3.1/all")
            if response.status_code == 200:
                data = response.json()
                return [country.get("name", {}).get("common", "Unknown") for country in data]
            else:
                self.logger.warning("Failed to fetch countries")
                return ["Unknown"]
        except Exception as e:
            self.logger.error(f"Country API error: {e}")
            return ["Unknown"]



    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse_cate)



    def parse_cate(self, response):
        cates = response.css("#default > div > div > div > aside > div.side_categories > ul > li > ul > li > a")

        for cate in cates:
            cate_url = response.urljoin(cate.css("::attr(href)").get())

            cate_name = cate.css("::text").get().strip()
            yield scrapy.Request(url=cate_url, callback=self.parse_book_list, meta={"cate_name": cate_name})



    def parse_book_list(self, response):
        full_path = os.path.join("debug_html", f"{response.url}".replace('https://books.toscrape.com/catalogue/category/', ''))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            f.write(response.body)

        products = response.css("#default > div > div > div > div > section > div:nth-child(2) > ol > li")

        for product in products:
            product_url = response.urljoin(product.css("article > div.image_container > a::attr(href)").get())
            title = product.css("article > h3 > a::attr(title)").get().strip()
            price = product.css("article > div.product_price > p.price_color::text").get().strip()
            availability = product.css("article > div.product_price > p.instock.availability::text").getall()[1].strip()
            star = product.css("article > p::attr(class)").get().split()[1]
            cate = response.meta["cate_name"]
            country = random.choice(self.countries)

            item = BooksItem(
                title=title,
                price=price,
                availability=availability,
                star=star,
                cate=cate,
                product_url=product_url,
                country=country
            )
            yield item



        next_page = response.css("#default > div > div > div > div > section > div:nth-child(2) > div > ul > li.next > a::attr(href)").get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            yield scrapy.Request(url=next_page_url, callback=self.parse_book_list, meta={"cate_name": response.meta["cate_name"]})