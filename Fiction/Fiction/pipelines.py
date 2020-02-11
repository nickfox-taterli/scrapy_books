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
import socket
import sqlite3

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient.http import MediaFileUpload

import logging

class FictionPipeline(object):
    def process_item(self, item, spider):
        return item

class FictionPipelineBooks(object):

    def __init__(self):
        # 生成时间基准文件名
        self.fn = '/root/scrapy_books/Fiction/Fiction/__store__/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.csv'
        self.db = redis.Redis(db=1)
        # 打开(追加)文件
        self.fw = open(self.fn, 'a', encoding='utf8', newline='')
        # CSV写法
        self.writer = csv.writer(self.fw)

        socket.setdefaulttimeout(1800)

    def upload_item(self):
        # If modifying these scopes, delete the file token.google.
        SCOPES = ['https://www.googleapis.com/auth/drive']

        creds = None
        # The file token.google stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.google'):
            with open('token.google', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.google', 'wb') as token:
                pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds,cache_discovery = False)

        file_metadata = {'name': os.path.basename(self.fn),
                        'mimeType': 'text/csv','parents': ['1W14BJa9PoqPP1K4C-WhOhu9VShKMsrdF']}
        media = MediaFileUpload(self.fn,
                                mimetype='text/csv')
        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()

        logging.log(logging.INFO, 'Upload to GDrive File ID: %s' , file.get('id'))

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

        self.upload_item()

        with open(self.fn, 'rb') as input_fn:
            with lzma.open(filename=self.fn + '.xz', mode='wb', preset=9 | lzma.PRESET_EXTREME) as output:
                shutil.copyfileobj(input_fn, output)

        os.remove(self.fn)


class SingleBookPipelineBooks(object):

    def __init__(self):
        # 生成时间基准文件名
        self.fn = '/root/scrapy_books/Fiction/Fiction/__store__/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + '.csv'
        # 打开(追加)文件
        self.fw = open(self.fn, 'a', encoding='utf8', newline='')
        # CSV写法
        self.writer = csv.writer(self.fw)
        self.title = ''

    def process_item(self, item, spider):

        if item['chapter_name'] is None:
            item['chapter_name'] = ''

        self.title = item['title']

        self.writer.writerow([item['id_primary'], item['id_subset'],
                              item['title'],
                              item['chapter_name'],
                              item['chapter_content']])

        return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.fw.close()
        con = sqlite3.connect(":memory:")
        cur = con.cursor()
        cur.execute("CREATE TABLE t (ID INT PRIMARY KEY NOT NULL, CHAPTER_NAME TEXT NOT NULL,CHAPTER_CONTENT TEXT NOT NULL);")

        with open(self.fn,'r') as f:
            reader = csv.reader(f)
            for field in reader:
                cur.execute("INSERT INTO t (ID, CHAPTER_NAME, CHAPTER_CONTENT) VALUES (?, ?, ?);", (field[1],field[3],field[4]))
            con.commit()
            cursor = con.execute("SELECT CHAPTER_NAME,CHAPTER_CONTENT FROM t ORDER BY ID ASC")
            fo = open(self.title + '.txt', "w")
            for row in cursor:
                fo.write(row[0] + '\n')
                fo.write(row[1] + '\n')

            con.close()
        
        os.remove(self.fn)
        