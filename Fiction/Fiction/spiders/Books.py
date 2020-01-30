# -*- coding: utf-8 -*-
import scrapy
import socket
from Fiction.items import BooksItem
from scrapy.http import Request
from scrapy.utils.log import configure_logging

class BooksSpider(scrapy.Spider):
    name = 'Books-stop'
    allowed_domains = ['69shu.com']

    # 书目录Index
    def start_requests(self):
        yield scrapy.Request('https://www.69shu.com/allvisit_1.htm', callback=self.start_requests_list)

    # 书目录
    def start_requests_list(self, response):
        max_page = int(response.xpath(
            '/html/body/div[2]/div[3]/div/div[2]/div/div/div/a[14]/text()').extract()[0])
        book_urls = response.xpath(
            '//*[@id="content"]/div/div[2]/div/ul/li/span[3]/a/@href').extract()
         
        for book_url in book_urls:
            yield Request(book_url, callback=self.parse_read)
        for num in range(1, max_page + 1):
            yield scrapy.Request('https://www.69shu.com/allvisit_' + str(num) + '.htm', callback=self.parse)

    # 获取每一本书的URL
    def parse(self, response):
        book_urls = response.xpath(
            '//*[@id="content"]/div/div[2]/div/ul/li/span[3]/a/@href').extract()
        for book_url in book_urls:
            if '/230.htm' not in book_url:
                yield Request(book_url, callback=self.parse_read)

    # 获取马上阅读按钮的URL，进入章节目录
    def parse_read(self, response):
        read_url_slice = response.xpath('//html/body/div[2]/div[4]/div[2]')
        read_url = read_url_slice.xpath('a/@href').extract()[0]
        yield Request(read_url, callback=self.parse_chapter)

    # 获取小说章节的URL
    def parse_chapter(self, response):
        chapter_urls = response.xpath('/html/body/div[2]/div[4]/ul/li/a/@href').extract()
        for chapter_url in chapter_urls:
            if "newmessage" not in chapter_url:
                    yield Request(chapter_url, callback=self.parse_content)

    # 获取小说名字,章节的名字和内容
    def parse_content(self, response):

        try:
            # 小说名字
            title = response.xpath('/html/body/div[2]/div[2]/div[1]/a[3]/text()').extract_first()
            # 小说章节名字
            chapter_name = response.xpath('/html/body/div[2]/table/tbody/tr/td/h1/text()').extract_first()
            # 小说章节内容
            chapter_content = response.xpath('/html/body/div[2]/table/tbody/tr/td/div[1]/text()').extract()
            chapter_content_full = ''

            item = BooksItem()
            item['id_primary'] = response.url.split('/')[4]
            item['id_subset'] = response.url.split('/')[5]
            item['title'] = title
            item['chapter_name'] = chapter_name
            item['chapter_content'] = chapter_content_full.join(chapter_content)
            
            yield item

        except:
            pass