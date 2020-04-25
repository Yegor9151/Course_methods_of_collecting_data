# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
import re
import os
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class LeroyparserPipeline(object):
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroy_products

    def process_item(self, item, spider):
        '''обрабатываем результаты'''

        item['_id'] = item['_id'][0]  # вытягивает id
        item['link'] = item['link'][0]  # вытягиваем ссылку
        item['price'] = item['price'][0]  # вытягиваем цену
        item['characteristic'] = {
            item['terms'][i]: item['definitions'][i] for i in range(len(item['terms']))
        }  # формируем словарь

        del item['terms'], item['definitions']  # удаляем лючние ключи

        collection = self.mongo_base[spider.name]
        collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)

        return item


class LeroyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                yield scrapy.Request(img)

    def file_path(self, request, response=None, info=None):
        '''сортируем картинки по папакам'''
        pattern = re.compile('\/(\d+)')
        name = re.findall(pattern, request.url)[0]
        path = f'{os.getcwd()}\\images\\{name}\\'
        if os.path.exists(path) == False:
            os.mkdir(path)
        tail = os.path.basename(request.url)
        result = f'{path}{tail}'
        return result

    def item_completed(self, results, item, info):
        if results[0]:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item
