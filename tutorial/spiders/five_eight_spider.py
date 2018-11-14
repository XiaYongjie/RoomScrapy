# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import js2xml
from lxml import etree

class FiveeightspiderSpider(scrapy.Spider):
    name = '58tc'
    details =[]
    count =0;
    headers = { 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'pragma': 'no-cache',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                ':authority':'sh.58.com',
                ':method':'GET ',
                }
    def start_requests(self):
        urls = [
            'https://sh.58.com/zufang/sub/l60/s3052_3053_3054_3055_3056/?pagetype=ditie&PGTID=0d3090a7-0000-29ab-dc7f-fc123ade3aa0&ClickID=2',
        ]
        for url in urls:
            yield scrapy.Request(url=url,headers =self.headers, callback=self.parse,dont_filter=True)

    def parse(self, response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        for des in soup.find_all('div',attrs={'class':'des'}):
            if '<a' not in str(des):
                continue
            else:
                strongboxs = des.find_all('a', attrs ={'class':'strongbox'})
                for strongbox in strongboxs:
                    print("https:"+strongbox.attrs['href'])
                    self.details.append("https:"+strongbox.attrs['href'])
     
        for url in self.details:
            #url = self.details[0]
            self.headers['referer'] ='https://sh.58.com/zufang/sub/l60/s3052_3053_3054_3055_3056/?pagetype=ditie&PGTID=0d3090a7-0000-29ab-dc7f-fc123ade3aa0&ClickID=2'
            yield scrapy.Request(url=url,headers =self.headers,callback=self.parse_detail,dont_filter=True)
    
    def parse_detail(self,response):
        self.count = self.count+1;
        print(self.count)
        print(len(self.details))
        pass

        
