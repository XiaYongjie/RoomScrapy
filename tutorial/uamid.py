# -*- coding: utf-8 -*-#
# �������ģ��
import random
# ����settings�ļ��е�UPPOOL
from .settings import UPPOOL
# ����ٷ��ĵ���Ӧ��HttpProxyMiddleware
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware

class Uamid(UserAgentMiddleware):
    # ��ʼ�� ע��һ��Ҫuser_agent����Ȼ���ױ���   
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    # ������
    def process_request(self, request, spider):
        # �����ѡ��һ���û�����
        thisua = random.choice(UPPOOL)
        request.headers.setdefault('User-Agent',thisua)