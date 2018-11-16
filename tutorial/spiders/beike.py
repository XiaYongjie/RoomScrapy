# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import js2xml
from lxml import etree
import pymysql

class BeikeSpider(scrapy.Spider):
    name = 'beike'
    details=[]; 
    base_url = 'https://sh.zu.ke.com/'
    headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'pragma': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            
                }
    url = 'https://sh.zu.ke.com/ditiezufang/li143685059s100021926/rt200600000001l2l1/'
    def start_requests(self):
        yield scrapy.Request(url=self.url,callback= self.parse,method='GET',headers=self.headers,dont_filter=True)
       
    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        content = soup.find('div',attrs={'class':'content__list'}) 
        if content is not None:
            content_lists = content.find_all('div',attrs={'class':'content__list--item'})
            for content_list in content_lists:
                a = content_list.find('a',attrs={'class':'','target':'_blank'})
                room = {'room_url':self.base_url+a.attrs['href'],'title':a.text}
                self.details.append(room)
            content__pg = soup.find('div',attrs ={'class':'content__pg'})
            print(content__pg)
        if content__pg is not None:
            data_totalpage = content__pg.attrs['data-totalpage']
            if data_totalpage is not None:
                if data_totalpage>=2:
                    for i in range(2,data_totalpage):
                        url= "https://sh.zu.ke.com/ditiezufang/li143685059s100021926/pg"+i+"rt200600000001l2l1/"
                        yield scrapy.Request(url=url,callback= self.parse,method='GET',headers=self.headers,dont_filter=True)

    def request_detail(self):
        for detail in self.details:
            pass
            # yield scrapy.Request(url=detail['room_url'],callable =self.parse,meta=detail)    