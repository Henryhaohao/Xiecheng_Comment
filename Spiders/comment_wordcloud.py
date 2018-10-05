# !/user/bin/env python
# -*- coding:utf-8 -*- 
# time: 2018/10/5--13:29
__author__ = 'Henry'

'''
通过爬取的3010条丽江评论制作成词云
'''

import pymongo, numpy
import jieba.posseg
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from Spiders import config
from PIL import Image

# 配置MONGODB数据库
host = config.MONGODB_HOST
port = config.MONGODB_PORT
client = pymongo.MongoClient(host=host, port=port)
db = client[config.MONGODB_DBNAME]
doc = db[config.MONGODB_DOCNAME]

# 词频统计字典
dic = defaultdict(int)

# 对每条评论进行分词及预处理
def cut_word(sentence):
    # 去掉句子中的特殊字符及标点符号
    sentence = sentence.replace('&quot', '').replace('\n', '')
    biaodian_list = '~！@#￥%……&*（）【】{}：；‘’“”《》，。、？ -_,./<>;:\'"!$^()  ヾ?～≈′'
    for biaodian in biaodian_list:
        sentence = sentence.replace(biaodian, '')

    # 分词（带词性标注）
    words = jieba.posseg.cut(sentence)

    # 常用词
    stop_words = ['的', '我', '你', '他', '她', '它', '我们', '你们', '他们', '她们', '它们',
                  '这', '这儿', '那', '那儿', '在', '在哪', '这里', '哪里', '那里', '了', '吗', '啊',
                  '是', '不是', '着', '谢谢', '也', '就', '去', '到', '可以', '不', '什么', '会',
                  '再', '哦', '有', '很', '都', '和', '还是', '还', '感觉', '上', '但', '来',
                  '一个', '地方', '就是', '里面', '一次', '一些', '这次', '已经', '又', '个', '这个',
                  '那个', '要', '但是', '里', '看', '住', '让', '太', '没', '说', '时候',
                  '小', '大', '还有', '走', '不过', '比较']

    # 只统计名词或词性为x的词语
    for word in words:
        # 去掉句子中的常用词
        if word.word not in stop_words:
            # 判断是否为名词
            if 'n' in word.flag or 'x' in word.flag:
                word = word.word  # 取出该名词
                # print(word)
                dic[word] += 1


def main():
    # 设置自己的分词词语 (参考丽江景点名称:http://you.ctrip.com/sight/lijiang32/3056-sight.html#jingdian)
    jieba.load_userdict('lijiang.txt')
    for i in doc.find():
        cut_word(i['comment'])

    # 对词语进行排序
    sort_dict = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    # print(sort_dict)
    wl_space_split = []
    for i in range(80):
        print(sort_dict[i])
        for _ in range(sort_dict[i][1]):
            wl_space_split.append(sort_dict[i][0])

    # 添加遮罩图片(必须为png格式,背景透明;遮罩图多大,生成的图就多大,但可以用scale参数放大)
    mask = numpy.array(Image.open('heart.png'))
    # 产生词云图并显示
    my_wordcloud = WordCloud(random_state=100,min_font_size=10,max_words=100,mask=mask,font_path='miaowuti.ttf', background_color='white', collocations=False).generate(" ".join(wl_space_split))
    plt.imshow(my_wordcloud)
    plt.axis("off")
    plt.show()
    # 保存词云图
    my_wordcloud.to_file('wordcloud.jpg')


if __name__ == '__main__':
    main()
