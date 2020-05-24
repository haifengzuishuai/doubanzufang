import configparser
import json
import os
import requests
from bs4 import BeautifulSoup
import pymysql

# 获取每个城市的地铁信息 需手动运行
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

got_sid = set()
lines = {}

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


def get_message(ID, cityname, name):
    """
    地铁线路信息获取
    """
    url = 'http://map.amap.com/service/subway?_1555502190153&srhdata=' + \
          ID + '_drw_' + cityname + '.json'
    response = requests.get(url=url, headers=headers)
    html = response.text
    result = json.loads(html)
    # import IPython
    # IPython.embed()
    for i in result['l']:
        for j in i['st']:
            line_name = i['ln']
            # 判断是否含有地铁分线
            if i['la']:
                line_name += f"({i['la']})"

            city_code = ID
            city_name = name
            line_id = i['ls']
            lines[line_id] = {
                'lineId': line_id,
                'lineName': line_name,
                'cityCode': city_code,
                'cityName': city_name,
            }

            station = {
                'cityCode': city_code,
                'cityName': city_name,
                'stationId': j['sid'],
                'stationName': j['n'],
                'stationPosition': j['sl'],
                'stationLines': j['r'],
            }
            try:
                print("11")
                sql = 'insert INTO stations VALUES (%s,%s,%s,%s)'
                cursor.execute(sql, (city_name, line_name, city_code, j['n']))
                connection.commit()
            except Exception as e:
                print(e)
                print('Failed')
                connection.rollback()


def get_city():
    """
    城市信息获取
    """
    url = 'http://map.amap.com/subway/index.html?&1100'
    response = requests.get(url=url, headers=headers)
    html = response.text
    # 编码
    html = html.encode('ISO-8859-1')
    html = html.decode('utf-8')
    soup = BeautifulSoup(html, 'lxml')
    # 城市列表
    res1 = soup.find_all(class_="city-list fl")[0]
    res2 = soup.find_all(class_="more-city-list")[0]

    for i in res1.find_all('a'):
        # 城市ID值
        ID = i['id']
        # 城市拼音名
        cityname = i['cityname']
        # 城市名
        name = i.get_text()
        get_message(ID, cityname, name)
    for i in res2.find_all('a'):
        # 城市ID值
        ID = i['id']
        # 城市拼音名
        cityname = i['cityname']
        # 城市名
        name = i.get_text()
        get_message(ID, cityname, name)


if __name__ == '__main__':
    get_city()
