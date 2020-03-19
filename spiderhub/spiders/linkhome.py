# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from spiderhub.items import ApartmentItem


class LinkhomeSpider(RedisCrawlSpider):
    name = 'linkhome'
    
    redis_key = 'linkhome:start_urls'
    
    allowed_domains = ['bj.lianjia.com']
    
    rules = (
        Rule(LinkExtractor(restrict_xpaths="//div[contains(@class,'title')]/a[contains(@href,'https://bj.lianjia.com/ershoufang/')]"), callback="parse_detail", follow=False),
    )

    def parse_detail(self, response):
        item = ApartmentItem()
        item['community'] = response.xpath("//div[contains(@class,'communityName')]/a[contains(@class,'info')]/text()").extract_first()
        item['area1'] = response.xpath("//div[contains(@class,'areaName')]/span[contains(@class,'info')]/a/text()").extract()[0]
        item['area2'] = response.xpath("//div[contains(@class,'areaName')]/span[contains(@class,'info')]/a/text()").extract()[1]
        item['room_maininfo'] = response.xpath("//div[contains(@class,'room')]/div[contains(@class,'mainInfo')]/text()").extract_first()
        item['room_subinfo'] = response.xpath("//div[contains(@class,'room')]/div[contains(@class,'subInfo')]/text()").extract_first()
        item['type_maininfo'] = response.xpath("//div[contains(@class,'type')]/div[contains(@class,'mainInfo')]/text()").extract_first()
        item['type_subinfo'] = response.xpath("//div[contains(@class,'type')]/div[contains(@class,'subInfo')]/text()").extract_first()
        item['area_maininfo'] = response.xpath("//div[contains(@class,'area')]/div[contains(@class,'mainInfo')]/text()").extract_first()
        item['area_subinfo'] = response.xpath("//div[contains(@class,'area')]/div[contains(@class,'subInfo')]/text()").extract_first()
        item['price_total'] = response.xpath("//div[@class='price ']/span[@class='total']/text()").extract_first()
        item['price_unit'] = response.xpath("//span[@class='unitPriceValue']/text()").extract_first().replace('"', '')
        
        yield item

