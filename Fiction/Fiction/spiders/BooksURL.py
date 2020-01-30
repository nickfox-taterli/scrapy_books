# -*- coding: utf-8 -*-
import scrapy
from Fiction.items import BooksUrlItem
from scrapy.http import Request
import lzma
import shutil
import os

class BooksSpider(scrapy.Spider):
    name = 'BooksURL'
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
        if 'allvisit_1.htm' in response.url:
            for book_url in book_urls:
                yield scrapy.Request(book_url, callback=self.parse_read)
        for num in range(1, max_page + 1):
            yield scrapy.Request('https://www.69shu.com/allvisit_' + str(num) + '.htm', callback=self.parse)

    # 获取每一本书的URL
    def parse(self, response):
        book_urls = response.xpath(
            '//*[@id="content"]/div/div[2]/div/ul/li/span[3]/a/@href').extract()
        for book_url in book_urls:
            if '/230.htm' not in response.url:
                yield Request(book_url, callback=self.parse_read)

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
                if '/230/' not in response.url:
                    item = BooksUrlItem()
                    item['url'] = chapter_url
                    yield item

    def closed(self, reason):
        stats = self.crawler.stats.get_stats()

        os.remove('/var/www/html/BooksURL.csv.xz')

        with open('/root/code/Fiction/BooksURL.csv', 'rb') as input:
            with lzma.open(filename='/var/www/html/BooksURL.csv.xz', mode='wb', preset=9 | lzma.PRESET_EXTREME) as output:
                shutil.copyfileobj(input, output)

        os.remove('/root/code/Fiction/BooksURL.csv')

        with open('stats.log', 'a') as f:
            f.write(stats['finish_time'].strftime('%Y-%m-%d %H:%M:%S') + ' 采集章节总数: ' + str(stats['item_scraped_count']) + '\n')