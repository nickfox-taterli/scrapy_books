# -*- coding: utf-8 -*-
import scrapy
from Fiction.items import BooksUrlItem
from scrapy.http import Request
import lzma
import shutil
import os

class BooksSpider(scrapy.Spider):
    name = 'BooksURLIndex'
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
            item = BooksUrlItem()
            item['url'] = book_url
            yield item
        for num in range(1, max_page + 1):
            yield scrapy.Request('https://www.69shu.com/allvisit_' + str(num) + '.htm', callback=self.parse)

    # 获取每一本书的URL
    def parse(self, response):
        book_urls = response.xpath(
            '//*[@id="content"]/div/div[2]/div/ul/li/span[3]/a/@href').extract()
        for book_url in book_urls:
            if '/230.htm' not in book_url:
                item = BooksUrlItem()
                item['url'] = book_url
                yield item

    def closed(self, reason):
        stats = self.crawler.stats.get_stats()

        with open('stats.log', 'a') as f:
            f.write(stats['finish_time'].strftime('%Y-%m-%d %H:%M:%S') + ' 采集书本数: ' + str(stats['item_scraped_count']) + '\n')