# encoding: utf-8

"""
@Author: haifengzuishuai
@Data: 2020/5/23 4:33 下午
"""

# 数据库连接信息
import configparser
import os

import pymysql

from mySpider.spiders.groupurls import start_urls

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


def cityurls():
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = connection.cursor()
    sql_countAll = "SELECT cityUrl FROM city_urls WHERE cityName=N'杭州'"
    cursor.execute(sql_countAll)
    countAll = cursor.fetchall()
    countAll1 = []
    for s in countAll:
        countAll1.append(s[0])
    print(countAll1)
    yield countAll1
