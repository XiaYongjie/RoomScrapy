# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import js2xml
from lxml import etree
import pymysql 
class HizhuSpider(scrapy.Spider):
    name = 'hizhu'
    details=[]; 
    headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'pragma': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            
                }
    url = 'http://www.hizhu.com/shanghai/dtlist4/a4/b107/c15/d0/e0/f9/g0/h0/'
    def start_requests(self):
       
        yield scrapy.Request(url=self.url,headers =self.headers,callback=self.parse,dont_filter=True)

    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        list_data = soup.find("div",attrs={'class':'list_main_data'})
      
        if list_data is not None:
            main_datas = list_data.find_all('div',attrs={'class':'data_list_main'})
            
            for main_data in main_datas:
               
                self.details.append(main_data.find('a',attrs={'class':'house_left'}).attrs['href'])
        page_tool = soup.find('div',attrs={'class':'ui-paging-container'})
      
        if page_tool is not None:
            lis = page_tool.find_all('li')
            length = len(lis)
            if length>1 and lis[length-1] is not None:
                li = lis[length-1]
                if li.find('a') is not None and li.find('a').text =='下一页':
                    url = self.url + li.find('a').attrs['href']
                    yield scrapy.Request(url=url,headers =self.headers,callback=self.parse,dont_filter=True)
                else:
                    #for detail in self.details:
                        room ={"url":self.details[0]}
                        yield scrapy.Request(url=self.details[0],meta=room,headers =self.headers,callback=self.parse_detail,dont_filter=True)


    def parse_detail(self,response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        room  = response.meta
        common_w = soup.find("div",attrs={'class':'common_w'})
        if common_w is not None:
            ## 房源信息
            detail_mess = common_w.fond('div',attrs={"class",'detail_mess cf'}) 
            if detail_mess is not None:
                room_detail = detail_mess.find('div',attrs ={'class':"d_mess_l fl"}).find('div',attrs={'id':'mess'})
                if room_detail is not None:
                    room['title']=room_detail.find('h3').text
        print(soup)
        pass

