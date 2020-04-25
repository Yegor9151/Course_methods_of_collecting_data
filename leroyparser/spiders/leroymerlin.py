# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, text):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={text}']

    def parse(self, response: HtmlResponse):
        links_on_product = response.xpath("//div[@class='hover-image-buttons']/a/@href").extract()
        for link in links_on_product:
            if 'product' in link:
                yield response.follow(link, callback=self.parse_product)

        next_page = response.xpath("//div[@class='next-paginator-button-wrapper']/a/@href").extract_first()
        yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)

        loader.add_value('_id', str(response))
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//source[@media=' only screen and (min-width: 1024px)']/@srcset")
        loader.add_xpath('terms', "//dt/text()")
        loader.add_xpath('definitions', "//dd/text()")
        loader.add_xpath('price', "//meta[@itemprop='price']/@content")
        loader.add_value('link', str(response))

        yield loader.load_item()
