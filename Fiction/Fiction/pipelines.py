# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import csv
import os
import time
import lzma
import shutil

class FictionPipeline(object):
    def process_item(self, item, spider):
        return item

class FictionPipelineBooks(object):

    def __init__(self):
        #生成时间基准文件名
        self.fn = '/root/scrapy_books/Fiction/Fiction/__store__/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.csv'
        self.db = redis.Redis(db=1)
        # 打开(追加)文件
        self.fw = open(self.fn, 'a', encoding='utf8', newline='')
        # CSV写法
        self.writer = csv.writer(self.fw)

    def process_item(self, item, spider):

        if item['chapter_name'] is None:
            item['chapter_name'] = ''

        self.writer.writerow([item['id_primary'], item['id_subset'],
                              item['title'].replace(',', '，').replace('"', '').replace('\r\n', ''),
                              item['chapter_name'].replace(',', '，').replace('"', '').replace('\r\n', ''),
                              item['chapter_content'].replace(',', '，').replace('"', '').replace('\r\n', '')])

        self.db.hset('books', item['id_primary'] + '-' + item['id_subset'], 0)

        return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.fw.close()
        with open(self.fn, 'rb') as input:
            with lzma.open(filename=self.fn + '.xz', mode='wb', preset=9 | lzma.PRESET_EXTREME) as output:
                shutil.copyfileobj(input, output)

        os.remove(self.fn)
