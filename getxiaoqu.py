# encoding: utf-8

"""
@Author: haifengzuishuai
@Data: 2020/5/16 10:08 下午
"""
import json
import os
import configparser
import re
import time

import pymysql
import requests
from bs4 import BeautifulSoup

config_filename = "mysql/dbMysqlConfig.cnf"
file_path = os.path.join(os.path.dirname(__file__), config_filename)
cf = configparser.ConfigParser()
cf.read(file_path)
result = {}
for option in cf.options("dbMysql"):
    value = cf.get("dbMysql", option)
    result[option] = int(value) if value.isdigit() else value
connection = pymysql.connect(
    host=result['host'],
    port=result['port'],
    user=result['user'],
    password=result['password'],
    db=result['db_name'],
    charset='utf8',
)
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = connection.cursor()
#
# #
cities = {
    'dg': '东莞',
    'dl': '大连',
    'fs': '佛山',
    'gz': '广州',
    'hz': '杭州',
    'hf': '合肥',
    'jn': '济南',
    'nj': '南京',
    'qd': '青岛',
    'sh': '上海',
    'sz': '深圳',
    'su': '苏州',
    'sy': '沈阳',
    'tj': '天津',
    'bj': '北京',
    'cq': '重庆',
    'wh': '武汉',
    'xm': '厦门',
    'cd': '成都',
    'cs': '长沙',
}
'''
# 验证代理是否生效
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20"}
response = requests.get('http://icanhazip.com', proxies=proxies, headers=header)
# 获取状态
print(response.status_code)
print(response.content.decode())
'''
fail = []
for city_ch in cities:
    # 代理服务器
    proxyHost = "http-pro.abuyun.com"
    proxyPort = "9010"

    # 代理隧道验证信息
    proxyUser = "H9DU6H9X86J9EZ3P"
    proxyPass = "D922B7B80E98B889"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20"}
    page = 'http://{0}.{1}.com/xiaoqu/{2}/'.format(str(city_ch), "lianjia", '1')

    # 获取页数
    url = 'https://{}.ke.com/xiaoqu/'.format(str(city_ch))
    response = requests.get(url, timeout=10, headers=header, proxies=proxies, verify=False)
    html = response.content
    soup = BeautifulSoup(html, "lxml")
    page_box = soup.find_all('div', class_='page-box')[0]
    matches = re.search('.*"totalPage":(\d+),.*', str(page_box))
    total_page = int(matches.group(1))

    # 获取城市代码
    sql = 'SELECT cityCode FROM stations WHERE city=%s'
    cursor.execute(sql, cities[city_ch])
    connection.commit()
    result = cursor.fetchone()
    city_code = result[0]

    for i in range(1, total_page + 1):
        page = url + 'pg{}'.format(i)
        response = requests.get(page, timeout=10, headers=header, proxies=proxies, verify=False)
        html = response.content
        soup = BeautifulSoup(html, "lxml")
        find_all = soup.find_all('li', class_="xiaoquListItem")

        for house_elem in find_all:
            name = house_elem.find('div', class_='title')
            name = name.text.replace("\n", "")
            # 插入城市小区名称
            try:
                sql = "INSERT INTO xiaoqu_info(city_code,xiaoqu_name) VALUES (%s,%s)"
                cursor.execute(sql, (city_code, name))
                connection.commit()
                print('插入成功:' + name)
            except Exception as e:
                fail.append(city_code + name)
                print(e)
                print('Failed')
                connection.rollback()
    # wis
print(fail)
