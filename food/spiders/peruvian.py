# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from math import ceil

from scrapy.http import Request
from scrapy.loader.processors import Compose, Join
from scrapy.spiders import Spider
from scrapy.selector import Selector

from food.loaders import FoodItemLoader


class PeruvianFoodSpider(Spider):
    name = "peruvian_food"

    NUMBER_OF_ITEMS_PER_PAGE = 10

    def start_requests(self):
        yield Request(url=self.get_page_url(1), callback=self.parse)

    def get_page_url(self, page_number):
        return 'http://www.food.com/services/mobile/fdc/search/topic?pn={}&searchTerm=&topicid=343&sortBy='.format(page_number)

    def parse(self, response):
        for r in self.parse_items(response):
            yield r

        number_of_items = response.xpath('//totalResultsCount/text()').extract_first()
        number_of_pages = self.calculate_total_of_pages(number_of_items, self.NUMBER_OF_ITEMS_PER_PAGE)

        for page in range(2, number_of_pages + 1):
            link = self.get_page_url(page)
            yield Request(response.urljoin(link), callback=self.parse_items)

    def parse_items(self, response):
        links = response.xpath('//results')

        for link in links:
            record_type = link.xpath('./record_type/text()').extract_first()
            if record_type == 'Recipe':
                url = link.xpath('./record_url/text()').extract_first()
                description = link.xpath('./main_description/text()').extract_first()
                yield Request(url=url, callback=self.parse_item, meta={'description': description})

    def parse_item(self, response):
        jl = FoodItemLoader(selector=response)

        jl.add_xpath('ingredients', '//li[@data-ingredient]')
        jl.add_xpath('directions', '//div[@data-module="recipeDirections"]/ol')
        jl.add_xpath('title', '//h1/text()')
        jl.add_value('description', response.meta.get('description'))
        jl.add_value('url', response.url)

        yield jl.load_item()

    @staticmethod
    def calculate_total_of_pages(total, number_of_items_per_page):
            return int(ceil(float(total) / float(number_of_items_per_page)))
