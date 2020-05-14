import requests
from lxml import etree
plot = []
for i in range(1, 31):
    url = "https://hz.lianjia.com/xiaoqu/pg{}/?from=rec".format(i)
    get = requests.get(url)
    html = etree.HTML(get.text)
    # 获取所有a标签的href属性
    for i in range(30):
        linklist = html.xpath("/html/body/div[4]/div[1]/ul/li[{}]/div[1]/div[1]/a/text()".format(i))
        plot.append(linklist)
        print(linklist)
print(plot)