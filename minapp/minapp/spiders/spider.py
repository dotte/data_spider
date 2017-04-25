#http://www.comjia.com/project/s/z3
# -*- coding:utf-8 -*-
__author__ = 'guoyanbin'

import scrapy
import json
from minapp.items import MinappItem

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'minapp.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
    'Cookie': 'csrftoken=SlVJ8BxHZ4HEVpFlCDTDW1yjfvBbNlLz; _ga=GA1.2.468945924.1483952464; sessionid=psn0yryybt7tb83oze91r3lpgql9rlwp'
}

class MinappSpider(scrapy.Spider):
    name = "minapp"
    allowed_domains = ["minapp.com"]
    start_urls = ["https://minapp.com/"]

    def parse(self, response):
        for index in range(1, 28):
            print 'starting crawling page %d' % index
            next_page_url = self.start_urls[0] + "api/v3/trochili/miniapp/?tag=&offset=" + str(index*12) #https://minapp.com/api/v3/trochili/miniapp/?tag=&offset=240
            yield scrapy.Request(next_page_url, headers=headers, callback=self.parse_next_page)

    def parse_next_page(self, response):
        print 'staring parsing page'
        items = json.loads(response.body)['objects']

        #items = response.json().objects
        for l_item in items:
            item = MinappItem()
            item['name'] = l_item['name']
            item['url'] = l_item['url']
            item['id'] = l_item['id']
            item['create_by'] = l_item['created_by']
            item['create_at'] = l_item['created_at']
            item['overall_rating'] = l_item['overall_rating']
            item['desc'] = l_item['description']
            item['qrcode'] = l_item['qrcode']['image']
            yield item
        print 'parsing page finished'