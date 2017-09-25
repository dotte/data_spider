# -*- coding: utf-8 -*-
"""
@author:dotte
todo:1、year 截取的不准确 2、单价和总价 没有处理‘暂无报价’ 3、多线程抓取 4、自动login

"""
import urllib2
from bs4 import BeautifulSoup
import time
import threading
import sys
import sqlite3
import random
import json
import re

reload(sys)
sys.setdefaultencoding("utf-8")


headers = {
    'Accept':'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'zh-CN',
    'Connection': 'Keep-Alive',
    'Host': 'tj.lianjia.com',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'

}

proxy = [{u'http': u'119.23.161.182:3128'}
            #{u'http': u'121.232.145.177:9000'}
            #{u'http': u'http://61.135.217.7:80'},
            #{u'http': u'http://60.255.230.185:808'},
            #{u'http': u'http://139.213.1.50:8118'},
            #{u'http': u'http://120.32.138.228:27610'}
         ]

# Some User Agents
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

#北京区域列表和平 南开 河西 河北 河东 红桥 西青 北辰 东丽 津南
regions=[u"和平",u"南开",u"河西",u"河北",u"河东"]
#regions=[u"东城",u"西城",u"朝阳",u"海淀",u"丰台",u"石景山",u"通州",u"昌平",u"大兴",u"亦庄开发区",u"顺义",u"房山",u"门头沟",u"平谷",u"怀柔",u"密云",u"延庆",u"燕郊"]


class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """

    def __init__(self, path, command='', *args, **kwargs):
        self.lock = threading.RLock()  # 锁
        self.path = path  # 数据库连接参数

        if command != '':
            conn = self.get_conn()
            cu = conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = sqlite3.connect(self.path)  # ,check_same_thread=False)
        conn.text_factory = str
        return conn

    def conn_close(self, conn=None):
        conn.close()

    def conn_trans(func):
        def connection(self, *args, **kwargs):
            self.lock.acquire()
            conn = self.get_conn()
            kwargs['conn'] = conn
            rs = func(self, *args, **kwargs)
            self.conn_close(conn)
            self.lock.release()
            return rs

        return connection

    @conn_trans
    def execute(self, command, method_flag=0, conn=None):
        cu = conn.cursor()
        try:
            if not method_flag:
                cu.execute(command)
            else:
                cu.execute(command[0], command[1])
            conn.commit()
        except sqlite3.IntegrityError, e:
            # print e
            return -1
        except Exception, e:
            print e
            return -2
        return 0

    @conn_trans
    def fetchall(self, command="select name from xiaoqu", conn=None):
        cu = conn.cursor()
        lists = []
        try:
            cu.execute(command)
            lists = cu.fetchall()
        except Exception, e:
            print e
            pass
        return lists

def gen_xiaoqu_insert_command(info_dict):
    """
    生成小区数据库插入命令
    """
    info_list=[u'小区名称',u'大区域',u'小区域',u'小区户型',u'建造时间']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t=tuple(t)
    command=(r"insert into xiaoqu values(?,?,?,?,?)",t)
    return command

def gen_chengjiao_insert_command(info_dict):
    """
    生成成交记录数据库插入命令
    """
    info_list=[u'链接',u'小区名称',u'户型',u'面积',u'朝向',u'楼层',u'建造时间',u'签约时间',u'签约单价',u'签约总价',u'房产类型',u'学区',u'地铁']
    t=[]
    for il in info_list:
        if il in info_dict:
            t.append(info_dict[il])
        else:
            t.append('')
    t=tuple(t)
    command=(r"insert into chengjiao values(?,?,?,?,?,?,?,?,?,?,?,?,?)",t)
    return command

def do_xiaoqu_spider(region):
    url = u"http://tj.lianjia.com/xiaoqu/rs" + region + "/"
    print(url)
    try:
        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds)-1)])
        source = urllib2.urlopen(req, timeout=20).read()
        plain_text = unicode(source)
        soap = BeautifulSoup(plain_text,'lxml')
    except Exception, e:
        print e
        return
    content = soap.find('div', {'class': 'page-box house-lst-page-box'}).get('page-data')
    total_page = 0
    if content:
        f = json.loads(content)
        total_page = f['totalPage']
        print total_page
    for i in range(total_page):
        url_page = u"http://tj.lianjia.com/xiaoqu/pg%drs%s/" % (i+1,region)
        xiaoqu_spider(url_page)
        time.sleep(1)

def xiaoqu_spider(url_page):
    try:
        print(url_page)
        req = urllib2.Request(url_page, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=20).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, 'lxml')
    except (urllib2.HTTPError, urllib2.URLError), e:
        print e
        return
    except Exception, e:
        print e
        return

    xiaoqu_list = soup.findAll('div', {'class': 'info'})
    for xq in xiaoqu_list:
        info_dict = {}
        info_dict.update({u'小区名称': xq.find('a').text})
        content = xq.find('div', {'class': 'positionInfo'}).get_text().strip()
        big_area=xq.find('a', {'class': 'district'}).get_text()
        small_area = xq.find('a', {'class': 'bizcircle'}).get_text()
        #info = re.match(r".+>(.+)</a>.+>(.+)</a>.+</span>(.+)<span>.+</span>(.+)", content)
        #if info:
            #info = info.groups()
        info_dict.update({u'大区域': big_area})
        info_dict.update({u'小区域': small_area})
        info_dict.update({u'小区户型': ''})
        info_dict.update({u'建造时间': ''})
        print(info_dict)
        command = gen_xiaoqu_insert_command(info_dict)
        db_xq.execute(command, 1)

def get_all_cheng_jiao_records():
    total_pages = 1
    for i in range(total_pages):
        url_page = u"http://tj.lianjia.com/chengjiao/pg%s/" % (i + 1)
        get_cheng_jiao_records_by_page(url_page)
        time.sleep(1)

def get_all_cheng_jiao_records_by_xiaoqu(xiaoqu):
    url = u"http://tj.lianjia.com/chengjiao/rs"+xiaoqu+"/"
    try:
        print(url)
        proxy_support = urllib2.ProxyHandler(proxy[random.randint(0, len(proxy) - 1)])  # 注册代理
        # opener = urllib2.build_opener(proxy_support,urllib2.HTTPHandler(debuglevel=1))
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
        req = urllib2.Request(url, headers=hds[random.randint(0, len(hds) - 1)])
        source_code = urllib2.urlopen(req, timeout=20).read()
        plain_text = unicode(source_code)  # ,errors='ignore')
        soup = BeautifulSoup(plain_text, "lxml")
    except Exception, e:
        print e
        return
    content = soup.find('div', {'class': 'page-box house-lst-page-box'})
    total_pages = 0
    if content:
        d = content.get('page-data')
        f = json.loads(d)
        total_pages = f['totalPage']

    for i in range(total_pages):
        #url_page = u"http://bj.lianjia.com/chengjiao/pg%drs%s/" % (i + 1, xiaoqu)
        url_page = u"http://tj.lianjia.com/chengjiao/pg%drs%s/" % (i + 1, xiaoqu)
        get_cheng_jiao_records_by_page(url_page)
        time.sleep(1)


def get_cheng_jiao_records_by_page(url_page):
    try:
        print(url_page)
        req = urllib2.Request(url_page, headers=headers)
        source_code = urllib2.urlopen(req, timeout=20).read()
        #plain_text = unicode(source_code, errors='ignore')
        soup = BeautifulSoup(source_code, "lxml")
        cj_list = soup.findAll('div', {'class': 'info'})
        for cj in cj_list:
            info_dict = {}
            href = cj.find('a')
            if not href:
                continue
            info_dict.update({u'链接': href.attrs['href']})
            content = cj.find('a').text.split()
            if content:
                info_dict.update({u'小区名称': content[0]})
                info_dict.update({u'户型': content[1]})
                info_dict.update({u'面积': content[2][:-2]})
            content=unicode(cj.find('div',{'class':'houseInfo'}).renderContents().strip())
            content=content.split('|')
            if content:
                info_dict.update({u'朝向':content[0][31:].strip()})
                info_dict.update({u'精装':content[1].strip()})
                if len(content)>=3:
                    content[2]=content[2].strip();
                    info_dict.update({u'电梯':content[2]})
            content=cj.find('div',{'class':'dealDate'})
            if content:
                info_dict.update({u'签约时间':content.text})
            content = cj.find('div', {'class': 'totalPrice'})
            if content:
                info_dict.update({u'签约总价': content.text[:-1]})
            content = cj.find('div', {'class': 'unitPrice'})
            if content:
                info_dict.update({u'签约单价': content.text[:-3]})
            content = cj.find('div', {'class': 'positionInfo'})
            content = content.text.split(' ')
            if content:
                info_dict.update({u'楼层': content[0]})
                info_dict.update({u'建造时间': content[1][:4]})
            print(info_dict)
            print("write db")
            command = gen_chengjiao_insert_command(info_dict)
            db_cj.execute(command, 1)
    except Exception,e:
        print e
        return
    #print soup

def do_xiaoqu_chengjiao_spider():
    count = 0
    xq_list = db_xq.fetchall()
    for xq in xq_list:
        get_all_cheng_jiao_records_by_xiaoqu(xq[0])
        count += 1
        print 'have spidered %d xiaoqu' % count
    print 'done'



if  __name__ == "__main__":
    #command = "create table if not exists xiaoqu (name TEXT primary key UNIQUE, regionb TEXT, regions TEXT, style TEXT, year TEXT)"
    #db_xq = SQLiteWraper('lianjia-tj-xq.db', command)

    db_xq = SQLiteWraper('lianjia-tj-xq.db', '')



    command = "create table if not exists chengjiao (href TEXT primary key UNIQUE, name TEXT, style TEXT, area TEXT, orientation TEXT, floor TEXT, year TEXT, sign_time TEXT, unit_price TEXT, total_price TEXT,fangchan_class TEXT, school TEXT, subway TEXT)"
    db_cj = SQLiteWraper('lianjia-tj-cj.db', command)
    #for region in regions:
        #do_xiaoqu_spider(region)
    #get_all_cheng_jiao_records_by_xiaoqu(u'怡美家园')
    do_xiaoqu_chengjiao_spider()

    #get_all_cheng_jiao_records()

