# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from openpyxl import Workbook

class HdschoolPipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        title = ['ID', u'名称', u'地址', u'详细地址', u'负责人', u'负责人电话', u'费用', u'学生人数', u'联系人', u'联系人电话', u'所属组织', u'类型',
                 u'学校级别', u'计划招生人数', u'介绍']
        self.ws.append(title)

    def process_item(self, item, spider):
        line = [item['id'],item['name'], item['address'], item['address_detail'], item['admissions_name'], item['admissions_tel'], item['charging'], item['children_num'], item['kindergarten_name'], item['kindergarten_tel'], item['organizer'], item['property'], item['school_leavel'], item['student_plan_num'], item['introduction']]
        self.ws.append(line)  # 将数据以行的形式添加到xlsx中
        self.wb.save(r'd:\hdschool.xlsx')  # 保存xlsx文件
        return item

