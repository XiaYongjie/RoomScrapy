import scrapy

import json
import pymysql 
import time

class TutorialSpide(scrapy.Spider):
    name='mgzf'
    data = { 'cityId' : '289' ,'currentPage':"1",'rentTypes':'3','stationIds':'113,114,115'}
    list =[]
    url = "https://api.mgzf.com/mogoroom-find/v2/find/getRoomListByCriteria"
    basic_infor ="https://api.mgzf.com/mogoroom-find/v2/find/roomDetail/basicInfo"
    owner_platform_ensure_info ="https://api.mgzf.com/mogoroom-find/v2/find/roomDetail/ownerPlatformEnsureInfo"
    subway_location = "https://api.mgzf.com/mogoroom-find/v2/find/roomDetail/subwayLocation"
    roomId_configs = "https://api.mgzf.com/mogoroom-find/v2/find/roomDetail/roomConfigs"
    head = {"Accept-Language":"en-US,en;q=0.8",
            "AppVersion":"6.0.0",
            "Channel":"1",
            "DeviceId":"99001187030271",
            "Market":"mi",
            "Model":"MI 8 UD",
            "OS":"Android",
            "OSVersion":"8.1.0",
            "RegId":"1104a897928667055eb",
            "Server":"{m=api.mgzf.com,v=1.0}",
            "Timestamp":1542074824199,
            "Token":"",
            "UUID":"374a97a33022dc08",
            "User-Agent":"MogoRenter/59",
            "Signature":"8dc108747428e82a92668307e11c483c",
            "UserId":"",
            "debug":"1",
            "renterId":"",
            "Content-Type":"application/x-www-form-urlencoded",
            "Host":"api.mgzf.com",
            "Connection":"Keep-Alive",
            "Accept-Encoding":"gzip",
            "Cache-Control":"no-cache"}
    def start_requests(self):
        yield scrapy.FormRequest(url=self.url,method='post',formdata = self.data,dont_filter=True,callback = self.parse)

    def parse(self,response):
        result = json.loads(response.text)       
        if(result['code']=='10000'):
            if(result['content']['page']['isEnd']==0):
                for info in result['content']['roomInfos']:
                    self.list.append(str(info['roomId']))
                self.data['currentPage'] = str(int(self.data['currentPage'])+1)
                if( int(self.data['currentPage'])+1<=1):
                    self.head["Timestamp"] = int(time.time())
                    yield scrapy.FormRequest(url=self.url,method='post',callback=self.parse,formdata=self.data,dont_filter=True)
                else:
                    for roomId in self.list:
                        basic_data={"roomId":str(roomId),"sourceType":"1"}
                        room = {"roomId":roomId}
                        self.head["Timestamp"] = int(time.time())
                        yield scrapy.FormRequest(url=self.basic_infor,method='post',meta = room,formdata =basic_data,callback=self.parse_detail,headers=self.head,dont_filter=True)
            else:
              for roomId in self.list:
                  basic_data={"roomId":str(roomId),"sourceType":"1"}
                  room = {"roomId":roomId}
                  self.head["Timestamp"] = int(time.time())
                  yield scrapy.FormRequest(url=self.basic_infor,method='post',meta = room,formdata =basic_data,callback=self.parse_detail,headers=self.head,dont_filter=True)
       
    def parse_detail(self,response):  # 解析详情
        result = json.loads(response.text)
        room = response.meta;
        if(result['code']=='200'):
            if("content" in result):      
                if("roomIntroAttrDTO" in result["content"]):
                    room["community"] = result["content"]["roomIntroAttrDTO"]["communityName"]
                    room["title"] = result["content"]["roomIntroAttrDTO"]["title"]
                    room["price_method"] = result["content"]["roomIntroAttrDTO"]["payTypes"][0]["payDisplayValue"]
                    if("amountNew" in result["content"]["roomIntroAttrDTO"]["payTypes"][0]):
                        room["price"] = result["content"]["roomIntroAttrDTO"]["payTypes"][0]["amountNew"]["payDetail"][0]["amountDetail"]
                        room["deposit"] = result["content"]["roomIntroAttrDTO"]["payTypes"][0]["amountNew"]["deposit"]
                    else:
                        room["price"] = result["content"]["roomIntroAttrDTO"]["payTypes"][0]["salePrice"]
                        room["deposit"] = result["content"]["roomIntroAttrDTO"]["payTypes"][0]["foregiftAmount"]
                    room['service_free'] =''
                    if(len(result["content"]["roomIntroAttrDTO"]["payTypes"][0]["amountNew"]["payDetail"])>2):
                        room['service_free'] =result["content"]["roomIntroAttrDTO"]["payTypes"][0]["amountNew"]["payDetail"][1]["amountDetail"]
                    room["rent_type"] = result["content"]["roomIntroAttrDTO"]["rentTypeName"]
                    room["floor"] = result["content"]["roomIntroAttrDTO"]["floorNum"]
                    room["area"] =""
                    for config in result["content"]["roomDetailConfig"]:
                        if("户型" in config["key"]):
                            room["area"] =   room["area"]+str(config["value"])
                        if("建筑面积" in config['key']):
                            room["area"] =   room["area"]+"--"+str(config["value"])
                    room["room_url"] = result["content"]["shareContent"]["shareUrl"]
                    room["pic_list"] = ""
                    for group in result["content"]["pictureGroupList"]:
                        for piclist in group["pictures"]:
                            room["pic_list"] = room["pic_list"]+","+piclist["path"]
                    req_data ={"roomId":room["roomId"],"sourceType":"1","brokerId":str(result['content']['roomIntroAttrDTO']['brokerId'])}
                    self.head["Timestamp"] = int(time.time())
                    yield scrapy.FormRequest(url=self.owner_platform_ensure_info,method='post',meta = room,formdata =req_data,callback=self.parse_broker,headers=self.head,dont_filter=True) 
      

    def parse_broker(self,response):
         result = json.loads(response.text)
         room = response.meta;
         if result['code']=='200':
            if "content" in result and 'brokerInfo' in result['content']:
                 room["woner"] = result["content"]["brokerInfo"]["name"]
                 room["phone"] = result["content"]["brokerInfo"]["virtualNum"]
                 req_data ={"roomId":room["roomId"],"sourceType":"1"}
                 self.head["Timestamp"] = int(time.time())
                 yield scrapy.FormRequest(url=self.subway_location,method='post',meta = room,formdata =req_data,callback=self.parse_position,headers=self.head,dont_filter=True) 
                 


    def parse_position(self,response):  #  解析位置信息
        result = json.loads(response.text)
        room = response.meta;
        if result['code']=='200':
            if "content" in result :
                room["address"] = result['content']['address']
                room["address_dec"] = result['content']['subwayStation']
                room['lat'] = str(result['content']['lat'])
                room['lng'] = str(result['content']['lng'])
                room['subwayLocation'] = ""
                room['subway'] =""
                if ("subwayInfoList" in result['content']):
                    for subway in result['content']['subwayInfoList']:
                        if(subway['subwayName'] not in room['subway']):
                            room['subway']=room['subway']+"," +subway['subwayName']
                        if(subway['stationName'] not in room['subwayLocation']):
                            room['subwayLocation']=room['subwayLocation']+"," +subway['stationName']
                req_data ={"roomId":room["roomId"],"sourceType":"1"}
                self.head["Timestamp"] = int(time.time())
                yield scrapy.FormRequest(url=self.roomId_configs,method='post',meta = room,formdata =req_data,callback=self.parse_config,headers=self.head,dont_filter=True)
                          
    def parse_config(self,response):  #解析房屋配置信息
        result = json.loads(response.text)
        room = response.meta;
        if result['code']=='200':
            room['decoration'] =''
            if 'content' in result and 'roomFeatures' in result['content']:
                for des in result['content']['roomFeatures']:
                    room['decoration'] = room['decoration']+","+des
            if 'content'in result and 'roomConfig' in result['content']:
                for config in result['content']['roomConfig']:
                    if(config['highlight']):
                        room['decoration'] = room['decoration']+","+config['value']
        #self.insertDB(room)

    def insertDB(self,room):
        db= pymysql.connect(host="localhost",user="root",charset='utf8',
        password="password",db="db_rm",port=3306)
        cursor = db.cursor()
        sql = 'insert into room(source,city,area,lat,lng,community,decoration,phone,pic_list,price,price_method,address_dec,woner, subwayLocation,subway,room_url,deposit,service_free,title,rent_type,floor,address)        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            cursor.execute(sql,('蘑菇租房','上海',room['area'],room['lat'],room['lng'],room['community'],room['decoration'],room['phone'],room['pic_list'],room['price'],room['price_method'],room['address_dec'],room['woner'],room['subwayLocation'],room['subway'],room['room_url'],room['deposit'],room['service_free'],room['title'],room['rent_type'],room['floor'],room['address']))
            db.commit()
        except  : 
            print()
            print("---------------------插入失败------------------------")
            db.rollback()
        db.close()



