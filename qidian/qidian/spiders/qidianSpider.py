# -*- coding: UTF-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.selector import Selector
from scrapy.http import Request
from qidian.items import QidianItem
from selenium import webdriver
import urllib
import re

#for ajax content fetch
#using selenium...
#or
#using send ajax request manually...
class Qidian(CrawlSpider):
    name='qidian'
    idx = 0
    browser = None
    
    def start_requests(self):
        #self.browser = webdriver.Chrome('d:/software/chromedriver.exe')
        urls = []
        #26047
        for i in range(1,26047):
            url = 'http://a.qidian.com/?page=%d' % i
            yield self.make_requests_from_url(url)

    def parse_page(self, response):
        selector = Selector(response)
        
        item = QidianItem()
        item['url'] = response.url
		
        #book image
        book_img = selector.xpath('//a[@id="bookImg"]/img')
        item['image'] = 'http:' + book_img[0].xpath('@src').extract()[0].strip()
        
        #book info
        book_info = selector.xpath('//div[@class="book-info "]')        
        
        item['name'] = book_info.xpath('h1/em//text()').extract()[0]        
        item['author'] = book_info.xpath('h1/span/a/text()').extract()[0]         
        
        item['intro'] = selector.xpath('//div[@class="book-intro"]/p/text()').extract()[0]
        item['intro'] = item['intro'].replace('\n','')
        item['intro'] = item['intro'].replace('\r','')
        item['intro'] = item['intro'].replace('\t',' ')
        item['intro'] = item['intro'].strip()
        
        tmp = book_info.xpath('p')
        book_tags = tmp[0]
        book_statistics = tmp[2].xpath('em/text()')
        book_statistics_desc = tmp[2].xpath('cite//text()')
        assert len(book_statistics_desc) == 7
        
        #book status
        tag_spans_texts = book_tags.xpath('span/text()')
        item['sign_status'] = u'未签'
        for book_tags_span in tag_spans_texts:
            status = book_tags_span.extract()      
            if status == u'连载' or status == u'完本':
                item['progress'] = status
            elif status == u'签约':
                item['sign_status'] = status
            elif status == u'VIP' or status == u'免费':
                item['pay_status'] = status
        
        #book category
        book_tags_hrefs = book_tags.xpath('a/text()')
        item['major_category'] = book_tags_hrefs[0].extract()
        item['minor_category'] = book_tags_hrefs[1].extract()
        
        #book statistics
        text_count_desc = book_statistics_desc[0].extract()
        click_count_desc = book_statistics_desc[1].extract()
        weekly_click_count_desc = book_statistics_desc[3].extract()
        recommend_count_desc = book_statistics_desc[4].extract()
        weekly_recommend_count_desc = book_statistics_desc[6].extract()
        
        total_text_count =  float(book_statistics[0].extract())
        if text_count_desc[0] == u'万':
            total_text_count = total_text_count*10000.0
        total_text_count = int(total_text_count)
        
        total_click_count = float(book_statistics[1].extract())
        if click_count_desc[0] == u'万':
            total_click_count = total_click_count*10000.0
        total_click_count = int(total_click_count)
        
        #会员周点击3.25万
        beg_pos = weekly_click_count_desc.find(u'会员周点击')+len(u'会员周点击')
        end_pos = weekly_click_count_desc.find(u'万',beg_pos)
        adjust_end_pos = end_pos
        if adjust_end_pos < 0:
            adjust_end_pos = len(weekly_click_count_desc)
        vip_weekly_click_count = float(weekly_click_count_desc[beg_pos:adjust_end_pos])        
        if end_pos > 0:
            vip_weekly_click_count = vip_weekly_click_count*10000.0
        vip_weekly_click_count = int(vip_weekly_click_count)
        
        toal_recommend_count = float(book_statistics[2].extract())
        if recommend_count_desc[0] == u'万':
            toal_recommend_count = toal_recommend_count*10000.0
        toal_recommend_count = int(toal_recommend_count)
        
        #周13.52万
        beg_pos = weekly_recommend_count_desc.find(u'周')+len(u'周')
        end_pos = weekly_recommend_count_desc.find(u'万',beg_pos)
        adjust_end_pos = end_pos
        if adjust_end_pos < 0:
            adjust_end_pos = len(weekly_recommend_count_desc)
        weekly_recommend_count = float(weekly_recommend_count_desc[beg_pos:adjust_end_pos])
        if end_pos > 0:
            weekly_recommend_count = weekly_recommend_count*10000.0
        weekly_recommend_count = int(weekly_recommend_count)
        
        item['total_text_count'] = total_text_count
        item['total_click_count'] = total_click_count
        item['vip_weekly_click_count'] = vip_weekly_click_count        
        item['toal_recommend_count'] = toal_recommend_count
        item['weekly_recommend_count'] = weekly_recommend_count
        
        try:
            item['monthly_pass_count'] = selector.xpath('//i[@id="monthCount"]/text()').extract()[0]
        except:
            item['monthly_pass_count'] = 0
            
        item['weekly_reward_count'] = selector.xpath('//i[@id="rewardNum"]/text()').extract()[0] 
        
        #from ajax
        '''
        self.browser.get(response.url)        
        page = self.browser.page_source
        selector = Selector(text=page)
        
        score_lhs = selector.xpath('//cite[@id="score1"]/text()').extract()[0]
        score_rhs = selector.xpath('//i[@id="score2"]/text()').extract()[0]
        item['score'] = score_lhs + '.' + score_rhs
        item['evaluate_users'] = selector.xpath('//p[@id="j_userCount"]/span/text()').extract()[0]            
        '''
        
        yield item
        
        
    def parse(self, response):
        selector = Selector(response)
        route_items = selector.xpath('//div[@class="book-mid-info"]')

        for route_item in route_items:            
            url = 'http:' + route_item.xpath('h4/a/@href').extract()[0]           
            yield Request(url,callback=self.parse_page)


