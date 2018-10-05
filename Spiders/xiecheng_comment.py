# !/user/bin/env python
# -*- coding:utf-8 -*- 
# time: 2018/10/4--22:00
__author__ = 'Henry'

'''
项目内容:多线程Threading爬取携程的丽江古城景点评论并生成词云
目标网址:http://you.ctrip.com/sight/lijiang32/3056.html
'''

import requests, re, time, pymongo, threading
from html.parser import HTMLParser
from Xiecheng_Comment.Spiders import config

# 配置MONGODB数据库
host = config.MONGODB_HOST
port = config.MONGODB_PORT
client = pymongo.MongoClient(host=host, port=port)
db = client[config.MONGODB_DBNAME]
doc = db[config.MONGODB_DOCNAME]


def get_comment(page):
    '''根据页码获取评论'''
    print('*' * 30 + '正在爬取第' + page + '页' + '*' * 30)
    url = 'http://you.ctrip.com/destinationsite/TTDSecond/SharedView/AsynCommentView'
    data = {
        'poiID': '75924',
        'districtId': '32',
        'districtEName': 'Lijiang',
        'pagenow': page,
        'order': '3.0',
        'star': '0.0',
        'tourist': '0.0',
        'resourceId': '3056',
        'resourcetype': '2',
    }
    headers = {
        # 'Referer':'http://you.ctrip.com/sight/tianzhushan161/126298.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    html = requests.post(url, data=data, headers=headers)
    comments = re.findall(r'heightbox">(.*?)</span', html.text)
    for i in comments:
        i = HTMLParser().unescape(i)  # 将&#x20;&#x20;等unicode转成中文
        print(i)
        print('*' * 60)
        item = {'comment': i}
        doc.insert_one(item)


def main():
    '''主运行函数'''
    # 创建线程池
    threadpool = []
    for page in range(1, 302):
        # 将线程加入线程池
        threadpool.append(threading.Thread(target=get_comment, args=(str(page),)))
    # 开始线程
    for th in threadpool:
        th.start()
    # 等待所有线程运行完毕
    for th in threadpool:
        th.join()


if __name__ == '__main__':
    start = time.time()
    main()
    total = time.time() - start
    print('total time use:' + str(int(total)) + 's')
