# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FictionItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BooksUrlItem(scrapy.Item):
    url = scrapy.Field()  # 小说URL

class BooksItem(scrapy.Item):
    id_primary = scrapy.Field()  # 主ID
    id_subset = scrapy.Field()  # 从ID
    title = scrapy.Field()  # 小说名字
    chapter_name = scrapy.Field()  # 小说章节名字
    chapter_content = scrapy.Field()  # 小说章节内容
