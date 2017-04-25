# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MinappItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    url = scrapy.Field()
    id = scrapy.Field()
    create_by = scrapy.Field()
    create_at = scrapy.Field()
    overall_rating = scrapy.Field()
    desc = scrapy.Field()
    qrcode = scrapy.Field()

