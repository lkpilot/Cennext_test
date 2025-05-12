import scrapy

class BooksItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    star = scrapy.Field()
    cate = scrapy.Field()
    product_url = scrapy.Field()
    country = scrapy.Field()
