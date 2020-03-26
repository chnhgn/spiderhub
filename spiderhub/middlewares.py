# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random, requests, json
import threading

from scrapy.downloadermiddlewares.retry import RetryMiddleware, response_status_message
import logging
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from urllib3.exceptions import ProtocolError, ProxyError, ProxySchemeUnknown
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError


class SpiderhubSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SpiderhubDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def __init__(self, agents):
        # super(MyspidertestDownloaderMiddleware, self).__init__()
        self.agents = agents

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(agents=crawler.settings.get('USER_AGENTS'))

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        request.headers['User-Agent'] = random.choice(self.agents)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        spider.logger.info('*****************User-Agent: %s' % request.headers["User-Agent"])
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        

class SpiderRetryMiddleware(RetryMiddleware):
    
    logger = logging.getLogger(__name__)

    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError, ProtocolError, ProxyError, ProxySchemeUnknown)
    proxy_list = []
    lock = threading.Lock()
    
    host = '127.0.0.1'
    port = '5010'
    get_ip_endpoint = '/get'
    del_ip_endpoint = '/delete?proxy=%s'

    def get_proxy_api(self):
        ip_list = []
        response = requests.get("http://http.tiqu.alicdns.com/getip3?num=1&type=1&pro=0&city=0&yys=0&port=1&pack=89036&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=&gm=4")
        ip_list.append(response.content.decode())
        return ip_list

    def get_proxy_ip(self):
        self.lock.acquire()
        if not self.proxy_list:
            print('IP list is empty, getting IP...')
            self.proxy_list.extend(self.get_proxy_api())
            
        proxy_ip = self.proxy_list.pop(0) if self.proxy_list else ''
        self.lock.release()
        return proxy_ip

    def delete_proxy(self, proxy):
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)

    def process_request(self, request, spider):
        proxy_ip = request.meta.get('proxy')
        if not proxy_ip:
            proxy_ip = self.get_proxy_ip()
            request.meta['proxy'] = proxy_ip
            if proxy_ip not in self.proxy_list:
                self.proxy_list.append(proxy_ip)

    def process_response(self, request, response, spider):
        proxy_ip = request.meta.get('proxy')
        
        if not response.body:
            print(response.body)
            self.logger.info('The IP is forbidden, changing another IP...')
            print(proxy_ip)
            self.delete_proxy(proxy_ip)  # Delete the invalid IP
            proxy_ip = self.get_proxy_ip()  # Get a new IP
            request.meta['proxy'] = proxy_ip
            if proxy_ip not in self.proxy_list:
                self.proxy_list.append(proxy_ip)
            return request

        if request.meta.get('dont_retry', False):
            return response
        
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            self.delete_proxy(request.meta.get('proxy', False))  # Delete the IP if it's in the official retry status code
            self.logger.info('Return invalid value, retrying...')
            return self._retry(request, reason, spider) or response
        
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            
            # Any exception needs to change another IP to retry
            self.delete_proxy(request.meta.get('proxy', False))
            proxy_ip = self.get_proxy_ip()
            request.meta['proxy'] = proxy_ip
            self.logger.info('Request exception and changing another IP to retry...')

            return self._retry(request, exception, spider)
