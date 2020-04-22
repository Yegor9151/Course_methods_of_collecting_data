# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import re


class JobparserScrapyPipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy_spider

    def process_item(self, item, spider):
        '''обработка и сохранение items в БД'''

        # создаём паттерны
        pattern1 = re.compile('\xa0')
        pattern2 = re.compile('<\d+ (.+)>')
        pattern3 = re.compile('<\d+ .+\/(\d+)')

        # ррименяем паттерны
        item['min_salary'] = [re.sub(pattern1, '', i) for i in item['min_salary']]
        item['max_salary'] = [re.sub(pattern1, '', i) for i in item['max_salary']]
        item['link'] = re.findall(pattern2, item['link'])[0]
        item['_id'] = re.findall(pattern3, item['_id'])[0]

        # обрабатываем ЗП
        path = ['от ', ' до ']
        # нижняя и верхняя
        if path[0] and path[1] in item['currency']:
            min_index = item['min_salary'].index(path[0])+1
            item['min_salary'] = int(item['min_salary'][min_index])
            max_index = item['max_salary'].index(path[1])+1
            item['max_salary'] = int(item['max_salary'][max_index])
            cur_index = max_index+2
            item['currency'] = item['currency'][cur_index]

        # нижняя
        elif path[0] in item['currency']:
            min_index = item['min_salary'].index(path[0]) + 1
            item['min_salary'] = int(item['min_salary'][min_index])
            item['max_salary'] = None
            cur_index = min_index + 2
            item['currency'] = item['currency'][cur_index]

        # верхняя
        elif path[1][1:4] in item['currency']:
            item['min_salary'] = None
            max_index = item['max_salary'].index(path[1][1:4])+1
            item['max_salary'] = int(item['max_salary'][max_index])
            cur_index = max_index+2
            item['currency'] = item['currency'][cur_index]

        # отсутствует
        else:
            item['min_salary'] = None
            item['max_salary'] = None
            item['currency'] = None

        collection = self.mongo_base[spider.name]
        collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)

        return item
