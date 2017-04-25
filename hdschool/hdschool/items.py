# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HdschoolItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    address_detail = scrapy.Field()
    admissions_name = scrapy.Field()
    admissions_tel = scrapy.Field()
    charging = scrapy.Field()
    children_num = scrapy.Field()
    class_num = scrapy.Field()
    kindergarten_name = scrapy.Field()
    kindergarten_tel = scrapy.Field()
    organizer = scrapy.Field()
    introduction = scrapy.Field()
    property = scrapy.Field()
    school_leavel = scrapy.Field()
    student_plan_num = scrapy.Field()

