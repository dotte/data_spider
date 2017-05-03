#http://www.comjia.com/project/s/z3
# -*- coding:utf-8 -*-
__author__ = 'guoyanbin'

import scrapy
import re
from zhiyouji.items import ZhiyoujiItem
from scrapy.http import Request
import json

class HdschoolSpider(scrapy.Spider):
    name = "zhiyouji_spider"
    allowed_domains = ["www.jobui.com"]
    start_urls = ["http://www.jobui.com/cmp?area=%E5%8C%97%E4%BA%AC&areaCode=010108&sortField=sortFollow"]

    def start_requests(self):
        header = {'Accept': 'text/html, application/xhtml+xml, */*',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                  'Cookie': 'BDPCIEXP=14; td_cookie=18446744072909819588; PHPSESSID=qhb1f0n5p2b7m6ap60n81k2g04; Hm_lpvt_8b3e2b14eff57d444737b5e71d065e72=1493717083; Hm_lvt_8b3e2b14eff57d444737b5e71d065e72=1493107263,1493108274,1493108489,1493714797; jobui_p=1493107263441_23448927; TN_VisitCookie=182; TN_VisitNum=27; __cfduid=d78b953d57db403d4002610e91726a51f1493107278; isloginStatus=mc0ivOmHaiE%3D; jobui_area=%25E5%258C%2597%25E4%25BA%25AC; jobui_area_tmp=%25E5%258C%2597%25E4%25BA%25AC'
                  }
        for index in range(1, 2):
            print 'starting crawling page %d' % index
            url = 'http://www.jobui.com/cmp?area=%E5%8C%97%E4%BA%AC&areaCode=010108&sortField=sortFollow&n='+str(index)
            yield Request(url, headers=header, callback=self.parse_detail)

    def parse_next_page(self, response):
        print 'staring parsing page'
        detail_url = 'http://58.118.0.15/user/querySchoolInfo?guid='
        yield Request(detail_url, callback=self.parse_detail)
        print 'parsing page finished'

    def parse_detail(self, response):
        print 'staring parsing page'
        items = response.css(".companyList")
        for l_item in items:
            item = ZhiyoujiItem()
            item['name'] = l_item.css(".fs18::text").extract()[0].strip()
            item['url'] = l_item.css(".fs18::attr(href)").extract()[0].strip()
            yield item
        print 'parsing detail finished'

