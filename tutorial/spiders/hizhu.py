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
                    for detail in self.details:
                        room ={"url":detail}
                        yield scrapy.Request(url=detail,meta=room,headers =self.headers,callback=self.parse_detail,dont_filter=True)


    def parse_detail(self,response):
        soup = BeautifulSoup(response.body,'lxml',from_encoding='utf-8')
        room  = response.meta
        common_w = soup.find("div",attrs={'class':'common_w'})
        if common_w is not None:
            ## 房源信息d
            detail_mess = common_w.find('div',attrs={"class",'detail_mess cf'}) 
            if detail_mess is not None:
                room_detail = detail_mess.find('div',attrs ={'class':"d_mess_l fl"}).find('div',attrs={'id':'mess'})
                if room_detail is not None:
                    room['title']=room_detail.find('h3').text
                    house_msg = room_detail.find('ul',attrs={'class':'house_mes'})
                    if house_msg is not None:
                        house_msg_list = house_msg.find_all('li')
                        for house_list in house_msg_list:
                            if house_list.find('span').text == '朝向':
                                room['decoration'] = house_list.find('p').text
                            if house_list.find('span').text == '楼层':
                                room['floor'] = house_list.find('p').text
                            if house_list.find('span').text == '户型':
                                room['area'] = house_list.find('p').text
                            if house_list.find('span').text == '小区':
                                room['community'] = house_list.find('p').text
                            if house_list.find('span').text == '地址':
                                room['address'] = house_list.find('p').text
                            if house_list.find('span').text == '更新':
                                room['release_time'] = house_list.find('p').text
                            if house_list.find('span').text == '交通':
                                room['address_dec'] = house_list.find('p').text
                                traffics = house_list.find('div',attrs={'class':'others_jt'}).find('p')
                                room['subwayLocation'] =''
                                room['subway'] = ''
                                for traffic in traffics:
                                    traffic_strs =  traffic.split('-')
                                    if traffic_strs[0] not in room['subway']:
                                         room['subway'] =  room['subway']+","+traffic_strs[0].replace('距', '')
                                    if traffic_strs[1] not in room['subwayLocation']:
                                        room['subwayLocation'] = room['subwayLocation']+','+traffic_strs[1]
                    price_cf = room_detail.find('p',attrs={'class':'price cf'})
                    if price_cf is not None:
                        prices = price_cf.find_all('span')
                        prices_length = len(prices)
                        if prices_length>1:
                            room['price'] =prices[0].text
                        if prices_length>2:
                            room['rent_type'] = prices[1].text 
                        if prices_length > 3 :
                            room['area'] =room['area']+"--"+ prices[2].text
                    room_lables = room_detail.find('p',attrs={'class':'label'})
                    if room_lables is not None:
                        room_lable = room_lables.find_all('span')
                        for lable in room_lable:
                            room['decoration'] = room['decoration']+","+lable.text
                room_equipment = detail_mess.find('div',attrs ={'class':"d_mess_l fl"}).find('div',attrs={'class':'private_fac common_fac'}).find('ul',attrs={'class':'cf'})
                if room_equipment is not None:
                    equipments = room_equipment.find_all('li')
                    for equipment in equipments:
                         room['decoration'] = room['decoration']+","+equipment.find('span').string
                ##轮播
                img_slide =detail_mess.find('div',attrs ={'class':"d_mess_r fr"}).find('div',attrs={'class':'x-slide'});
                if img_slide is not None:
                    swiper_wrapper = img_slide.find('div',attrs={'class':'view'}).find('div',attrs={'class':'swiper-container'}).find('div',attrs={'class':'swiper-wrapper'}) 
                    # print(swiper_wrapper)
                    img_swiper = swiper_wrapper.find_all('div',attrs={'class':'swiper-slide'})
                    room['pic_list'] = ''
                    for swiper_slide in img_swiper:
                        room['pic_list'] = room['pic_list']+","+swiper_slide.find('img').attrs['src']
            address_map = common_w.find('div',attrs={'class':'map'})
            if address_map is not None:
                room['lat'] = address_map.find('input',attrs={'id':'js_latitude'}).attrs['value']
                room['lng'] = address_map.find('input',attrs={'id':'js_longitude'}).attrs['value']
        self.insertDB(room)

    def insertDB(self,room):
        print(room)
        db= pymysql.connect(host="localhost",user="root",charset='utf8', password="password",db="db_rm",port=3306)
        cursor = db.cursor()
        sql = 'insert into room(source,city,area,lat,lng,community,decoration,pic_list,price,address_dec,subwayLocation,subway,room_url,title,rent_type,floor,address) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            cursor.execute(sql,('嗨住租房','上海',room['area'],room['lat'],room['lng'],room['community'],room['decoration'],room['pic_list'],room['price'],room['address_dec'],room['subwayLocation'],room['subway'],room['url'],room['title'],room['rent_type'],room['floor'],room['address']))
            db.commit()
        except: 
            print(e)
            print("---------------------插入失败------------------------")
            db.rollback()
        db.close()

                


