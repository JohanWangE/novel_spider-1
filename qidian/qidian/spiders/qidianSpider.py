#coding=utf-8
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from qidian.items import QidianItem
import urllib


class Qidian(CrawlSpider):
    name='qidian'

    def start_requests(self):
        urls = []
        for i in range(1,1001):
            url = 'http://all.qidian.com/Book/BookStore.aspx?PageIndex=%d' % i
            yield self.make_requests_from_url(url)

    def parse_page(self, response):
        item = QidianItem()
        selector = Selector(response)
        content_intro = selector.xpath('//div[@id="contentdiv"]/div')
        book_info_data = content_intro.xpath('div[@class="data"/table/tbody/tr/td')
        click_num = book_info_data[0]
        vip_click_num

    def parse(self, response):
        item = QidianItem()
        selector = Selector(response)
        route_items = selector.xpath('//span[@class="swbt"]')
        
        if len(route_items) <= 0:
            while True:                
                print '-----------------------------------------------------------------'

        for route_item in route_items:
            name = route_item.xpath('a/text()').extract()[0].encode('gbk')
            url = route_item.xpath('a/@href').extract()[0]
            item['name'] = name
            item['url'] = url
            #yield item
            yield Request(url,callback=self.parse)


