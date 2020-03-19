# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpiderhubItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ApartmentItem(scrapy.Item):
    community = scrapy.Field()
    area1 = scrapy.Field()
    area2 = scrapy.Field()
    room_maininfo = scrapy.Field()
    room_subinfo = scrapy.Field()
    type_maininfo = scrapy.Field()
    type_subinfo = scrapy.Field()
    area_maininfo = scrapy.Field()
    area_subinfo = scrapy.Field()
    price_total = scrapy.Field()
    price_unit = scrapy.Field()
