# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook

class MinappPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active

    def process_item(self, item, spider):
        line = [item['name'], item['url'], item['id'], item['create_by'], item['create_at'], item['overall_rating'], item['desc'], item['qrcode']]
        self.ws.append(line)  # 将数据以行的形式添加到xlsx中
        self.wb.save(r'd:\minapp.xlsx')  # 保存xlsx文件
        return item
