# encoding: utf-8

"""
@Author: haifengzuishuai
@Data: 2020/5/23 2:34 下午
"""
import configparser
import os
import re
import lxml
import pymysql
import requests
from bs4 import BeautifulSoup
from lxml import etree

# 数据库连接信息
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


def urls_houchuli(url, cityName):
    html = url.content
    soup = BeautifulSoup(html, "lxml")
    tds = soup.find_all(class_='groups')
    for a in tds:
        find_all = a.find_all(class_='title')
        for q in find_all:
            for u in q.find_all('a'):
                print(u['href'])
                try:
                    sql = 'insert INTO city_urls(cityName,cityUrl) VALUES (%s,%s)'
                    cursor.execute(sql, (cityName, u['href']))
                    connection.commit()
                except Exception as e:
                    print(e)
                    print('Failed')
                    connection.rollback()


for i in cities.values():
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20"}
    get = requests.get('https://www.douban.com/group/search?start=0&cat=1019&sort=time&q={}租房'.format(i),
                       headers=header)
    html = get.content
    soup = BeautifulSoup(html, "lxml")
    page_box = soup.find_all('div', class_='paginator')
    matches = re.search('.*data-total-page="(\d+)"*.', str(page_box))
    if matches:
        total_page = int(matches.group(1))
    else:
        total_page = 1
    if total_page <= 5:
        n = 0
        for j in range(total_page):
            print(n)
            get = requests.get(
                'https://www.douban.com/group/search?start={}&cat=1019&sort=time&q={}租房'.format(n, i),
                headers=header)
            urls_houchuli(get, i)
            n += 20
    if total_page > 5:
        n = 0
        for j in range(5):
            print(n)
            get = requests.get(
                'https://www.douban.com/group/search?start={}&cat=1019&sort=time&q={}租房'.format(n, i),
                headers=header)
            urls_houchuli(get, i)
            n += 20
