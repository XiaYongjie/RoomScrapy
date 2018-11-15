# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import js2xml
from lxml import etree
import pymysql 
class DoubanSpider(scrapy.Spider):
    name = 'douban'
    headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'pragma': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            
                }
    def start_requests(self):
        url = 'https://www.douban.com/group/shanghaizufang/discussion?start='
        for i in range(30):
            yield scrapy.Request(url=url+str(i*25),headers =self.headers,callback=self.parse,dont_filter=True)
    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        olt = soup.find('table', attrs={'class':'olt'})
        if olt is not None :
            for item in olt.find_all('td',attrs ={'class':'title'}):            
                if item is not None:
                     url = item.find('a').attrs['href']
                     detail ={'url':url}
                     yield scrapy.Request(url=url,meta=detail,headers =self.headers, callback=self.parse_detail,dont_filter=True)



    def parse_detail(self,response):
        detail = response.meta
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        detail['title'] =soup.title.text
        topic = soup.find('div', attrs={'class':'topic-doc'})
        if topic is not None :
            people = soup.find("span",attrs={'class':'from'})
            if people is not None:
                pepmsg = people.find('a')
                detail['woner'] = pepmsg.attrs['href']+","+pepmsg.text
            detail['release_time'] = topic.find('span',attrs={'class':'color-green'}).text
            richtext = topic.find('div',attrs={'class':'topic-richtext'})
            detail['address_dec']= ''
            detail['pic_list'] =''
            if richtext is not None:
                for text in richtext.find_all('p'):
                    detail['address_dec'] = detail['address_dec']+','+text.text
                for img in richtext.find_all('img'):
                    detail['pic_list'] = detail['pic_list']+','+img.get('src')
            #pattern = re.compile(r'0?(13|14|15|16|17|18|19)[0-9]{9}')  ##拆取手机号
            #index = 0
            #while True:
            #    matchResult=pattern.search(telNumber,index) #从指定位置开始匹配
            #    if not matchResult:
            #        break
            #    print('-'*30)
            #    print('Success:')
            #    for i in range(3):
            #        print('Search content:',matchResult.group(i),'Start from:',matchResult.start(i),'End at:',matchResult.end(i),'Its span is:',matchResult.span(i))
        print(detail)
            #self.insertDB(detail)
    def insertDB(self,detail):
        db= pymysql.connect(host="localhost",user="root",charset='utf8',
        password="password",db="db_rm",port=3306)
        cursor = db.cursor()
        sql = 'insert into room(source,city,title,woner,release_time,address_dec,pic_list) values(%s,%s,%s,%s,%s,%s,%s)'
        try:
            cursor.execute(sql,('豆瓣租房','上海',detail['title'],detail['woner'],detail['release_time'],detail['address_dec'],detail['pic_list']))
            db.commit()
        except:
            print(e)
            print("---------------------插入失败------------------------")
            db.rollback()
        db.close()
