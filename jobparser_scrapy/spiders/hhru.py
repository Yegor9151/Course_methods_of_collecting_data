# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser_scrapy.items import JobparserScrapyItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, text):
        self.start_urls = [
            f'https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&text={text}&L_save_area=true&area=113&from=cluster_area&showClusters=true']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class,'HH-Pager-Controls-Next')]/@href").extract_first()
        yield response.follow(next_page, callback=self.parse)

        vacancy_links = response.xpath("//a[contains(@class,'HH-LinkModifier')]/@href").extract()
        for link in vacancy_links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        link_id = str(response)
        name = response.xpath("//h1[@data-qa='vacancy-title']/text()").extract_first()
        salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        yield JobparserScrapyItem(name=name,
                                  min_salary=salary,
                                  max_salary=salary,
                                  currency=salary,
                                  link=link_id,
                                  _id=link_id)
