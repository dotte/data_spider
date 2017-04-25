#http://www.comjia.com/project/s/z3
# -*- coding:utf-8 -*-
__author__ = 'guoyanbin'

import scrapy
import re
from hdschool.items import HdschoolItem
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
import json

class HdschoolSpider(scrapy.Spider):
    name = "hdschool_spider"
    allowed_domains = ["58.118.0.15"]
    start_urls = "http://58.118.0.15/user/querySchoolForChoose/"

    def start_requests(self):
        header = {'Cookie': 'SESSION=xxx',
                  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'Accept': 'text/html, application/xhtml+xml, */*'
                  #'Content-Length': 14
                  }
        for index in range(0, 4):
            print 'starting crawling page %d' % index
            formdata = {"page": str(index), "size": '50'} # "schoolAddress": u"清河街道"
            url = 'http://58.118.0.15/user/querySchoolForChoose'
            yield FormRequest(url, callback=self.parse_next_page, method='post', cookies={'SESSION': 'xxx'}, formdata=formdata) #need to change the SESSION value

    def parse_next_page(self, response):
        print 'staring parsing page'
        hxs = HtmlXPathSelector(response)
        items = hxs.select('//table[@class="table table-hover"]/tbody/tr')
        for item in items:
            tds = item.select('./td')
            id = tds[1].select('a/@onclick').extract()[0][15:-2].strip()
            #hd_item['id'] = tds[1].select('a/@onclick').extract()[0][15:-2].strip()
            #hd_item['name'] = tds[1].select('a/text()').extract()[0].strip()
            #hd_item['address'] = tds[2].select('./text()').extract()[0].strip()
            #hd_item['school_type'] = tds[3].select('./text()').extract()[0].strip()
            detail_url = 'http://58.118.0.15/user/querySchoolInfo?guid='+id
            yield FormRequest(detail_url, callback=self.parse_detail, method='post',
                              cookies={'SESSION': '935c0646-84f9-457f-8179-8f0eb6c504e5'})
        print 'parsing page finished'

    def parse_detail(self, response):
        print 'staring parsing page'
        res = json.loads(response.body)
        hd_item = HdschoolItem()
        hd_item['id'] = res['id']
        hd_item['name'] = res['name']
        hd_item['address'] = res['address']
        hd_item['address_detail'] = res['addressdetail']
        hd_item['admissions_name'] = res['admissionsName']
        hd_item['admissions_tel'] = res['admissionsTel']
        hd_item['charging'] = res['charging']
        hd_item['children_num'] = res['childrennum']
        hd_item['kindergarten_name'] = res['kindergartenName']
        hd_item['kindergarten_tel'] = res['kindergartenTel']
        hd_item['organizer'] = res['organizer']
        hd_item['property'] = res['property']
        hd_item['school_leavel'] = res['schoolleavel']
        hd_item['student_plan_num'] = res['studentplannum']
        hd_item['introduction'] = res['introduction']
        print 'parsing detail finished'
        return hd_item
