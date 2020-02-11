# -*- coding: utf-8 -*-
import scrapy
import redis
from Fiction.items import BooksItem
from scrapy.http import Request

class BooksSpider(scrapy.Spider):
    name = 'BookSingleUpdate'
    allowed_domains = ['69shu.com']
    
    db = redis.Redis(db=1)

    custom_settings = {
        'ITEM_PIPELINES':{
            'Fiction.pipelines.SingleBookUpdatePipelineBooks':100,
        }
    }

    # 特定采集某一本书
    def start_requests(self):
        yield scrapy.Request('https://www.69shu.com/txt/1464.htm', callback=self.parse_read)

    # 获取马上阅读按钮的URL，进入章节目录
    def parse_read(self, response):
        read_url_slice = response.xpath('//html/body/div[2]/div[4]/div[2]')
        read_url = read_url_slice.xpath('a/@href').extract()[0]
        yield Request(read_url, callback=self.parse_chapter)

    # 获取小说章节的URL
    def parse_chapter(self, response):
        chapter_urls = response.xpath(
            '/html/body/div[2]/div[4]/ul/li/a/@href').extract()
        for chapter_url in chapter_urls:
            if "newmessage" not in chapter_url:
                uuid = chapter_url.split(
                    '/')[4] + '-' + chapter_url.split('/')[5]
                if self.db.hexists('books_single', uuid) == False:
                    yield Request(chapter_url, callback=self.parse_content)

    # 获取小说名字,章节的名字和内容
    def parse_content(self, response):

        try:
            # 小说名字
            title = response.xpath(
                '/html/body/div[2]/div[2]/div[1]/a[3]/text()').extract_first()
            # 小说章节名字
            chapter_name = response.xpath(
                '/html/body/div[2]/table/tbody/tr/td/h1/text()').extract_first()
            # 小说章节内容
            chapter_content = response.xpath(
                '/html/body/div[2]/table/tbody/tr/td/div[1]/text()').extract()
            chapter_content_full = ''

            item = BooksItem()
            item['id_primary'] = response.url.split('/')[4]
            item['id_subset'] = response.url.split('/')[5]
            item['title'] = title
            item['chapter_name'] = chapter_name
            item['chapter_content'] = chapter_content_full.join(
                chapter_content)

            yield item
        except:
            # 这里最好分开处理,通常是某些内容出现错误,部分可以人工后处理(未实现)
            pass
