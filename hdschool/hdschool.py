#!/usr/bin/env python
# encoding=utf-8

import requests
from openpyxl import Workbook
import time
import random

#代理IP实时抓取
proxy_list = ['124.88.67.30:80']

headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }


def get_json(url, page, lang_name):
    data = {'first': 'true', 'pn': page, 'kd': lang_name}
    rand = random.randint(0, len(proxy_list) - 1)
    proxies = {"http": 'http://' + str(proxy_list[rand])}
    json = requests.post(url, data, headers=headers, timeout=10).json()
    list_con = json['content']['positionResult']['result']
    info_list = []
    for i in list_con:
        info = []
        info.append(i['companyId'])
        info.append(i['companyFullName'])
        info.append(i['companyShortName'])
        info.append(i['companySize'])
        info.append(i['positionName'])
        info.append(i['workYear'])
        info.append(i['createTime'])
        info.append(i['formatCreateTime'])
        info.append(i['salary'])
        info.append(i['city'])
        info.append(i['education'])
        info.append(i['financeStage'])
        info.append(i['industryField'])
        info.append(i['positionAdvantage'])
        info_list.append(info)
        print(info)
    return info_list


def main():
    lang_name = u'项目经理 技术经理 大数据 架构师'#input('职位名：')
    page = 1
    url = 'http://www.lagou.com/jobs/positionAjax.json?px=default&yx=25k-50k&city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false'
    info_result = []
    while page < 1000:
        info = get_json(url, page, lang_name)
        info_result = info_result + info
        page += 1
        time.sleep(1)
    wb = Workbook()
    ws1 = wb.active
    ws1.title = lang_name
    for row in info_result:
        ws1.append(row)
    wb.save('positions.xlsx')

if __name__ == '__main__':
    main()

