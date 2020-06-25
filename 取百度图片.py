# -*- coding:utf-8 -*-
import re

import requests

keyword = input("Input key word: ")
url = 'http://image.baidu.com/search/flip?tn=baiduimage&ie=utf-8&word=' + keyword + '&ct=201326592&v=flip'
result = requests.get(url).text
pic_url = re.findall('"objURL":"(.*?)",', result, re.S)
i = 1
print('找到关键词:' + keyword + '的图片，现在开始下载图片...')
for each in pic_url:
    print('正在下载第' + str(i) + '张图片，图片地址:' + str(each))
    try:
        pic = requests.get(each, timeout=10)
    except requests.exceptions.ConnectionError:
        print('【错误】当前图片无法下载')
        continue
    dir = keyword + '_' + str(i) + '.jpg'
    fp = open(dir, 'wb')
    fp.write(pic.content)
    fp.close()
    i += 1
