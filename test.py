import requests
from bs4 import BeautifulSoup
import pandas
import sqlite3
from datetime import datetime
import json
import re

commentURL = 'http://comment5.news.sina.com.cn/page/info?version=1&format=js&\
channel=gn&newsid=comos-{}&group=&compress=0&ie=utf-8&oe=utf-8&page=1&\
page_size=20'
# newsurl1 = 'http://news.sina.com.cn/o/2018-08-22/doc-ihhzsnec2152965.shtml'

# 抓取评论数方法函数
def getCommentCount(newsurl):
    m = re.search('doc-i(.*).shtml',newsurl)
    newsid = m.group(1)
    comments = requests.get(commentURL.format(newsid))
    jd = json.loads(comments.text.strip('var data='))
    return jd['result']['count']['total']

# 抓取内容文本函数
def getNewsDetial(newsurl):
    result = {}
    res = requests.get(newsurl)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    result['title'] = soup.select('.main-title')[0].text
    result['newssource'] = soup.select('.source')[0].text
    timesource = soup.select('.date')[0].contents[0].strip()
    result['dt'] = datetime.strptime(timesource,'%Y年%m月%d日 %H:%M')
    result['article'] = '\n'.join([p.text.strip() for p in soup.select('#article p')[:-1]])
    result['editor'] = soup.select('.show_author')[0].text.lstrip('责任编辑：')
    result['comments'] = getCommentCount(newsurl)
    return result

# 获取多篇新闻
def parseListLinks(url):
    newsdetails = []
    res = requests.get(url)
    jd = json.loads(res.text.lstrip('  newsloadercallback(').rstrip(');'))
    for ent in jd['result']['data']:
        newsdetails.append(getNewsDetial(ent['url']))
    return newsdetails

url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&\
level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&\
callback=newsloadercallback&_=1534941944412'

news_total = []
for i in range(1, 2):
    newsurl = url.format(i)
    newsary = parseListLinks(newsurl)
    news_total.extend(newsary)

# 使用pandas整理数据
df = pandas.DataFrame(news_total)
print(df.head(5))  # 打印前5篇
df.to_excel('new.xlsx')

with sqlite3.connect('news.sqlite') as db:
    df.to_sql('news', con=db)
    df2 = pandas.read_sql_query("SELECT * FROM news", con=db)
print(df2)