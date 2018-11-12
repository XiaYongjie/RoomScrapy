import scrapy
import requests
from bs4 import BeautifulSoup
import js2xml
from lxml import etree
import json
import pymysql 

db= pymysql.connect(host="localhost",user="root",
     password="password",db="db_rm",port=3306)

class TutorialSpide(scrapy.Spider):
    name='mgzf'
    data = { 'cityId' : '289' ,'currentPage':1,'rentTypes':'3','stationIds':'113,114,115'}
    list =[]
    url = "https://api.mgzf.com/mogoroom-find/v2/find/getRoomListByCriteria"
    def start_requests(self):
        heads = {
            "Accept":"application/json, text/plain, */*",
            "Channel" : 3,
            "Content-Type":"application/x-www-form-urlencoded",
            "Origin":"http://www.mgzf.com",
            "Referer":"http://www.mgzf.com/list/pg2/",
            "User-Agent:" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36"
            }
        yield scrapy.Request(url=self.url,method='post',body=json.dumps(self.data))

    def parse(self,response):
        result = json.loads(response.text)
        if(result['code']=='10000'):
            if(result['content']['page']['isEnd']==0):
                for info in result['content']['roomInfos']:
                    self.list.append(str(info['roomId']))
                self.data['currentPage'] = self.data['currentPage']+1
                if( self.data['currentPage']+1<=2):
                      yield scrapy.Request(url=self.url,method='post',body=json.dumps(self.data))
        for roomId in self.list:

           pass
       
    def parse_detail(self,response):  # 解析详情
        pass

    def parse_position(self,response):  #  解析位置信息
        pass


    def parse_user(self,response):  #  解析房东信息
        pass


    def parse_user(self,response):  #  解析房屋配置信息
        pass






