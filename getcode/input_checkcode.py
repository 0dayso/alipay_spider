#coding=utf-8
from bs4 import BeautifulSoup
import requests
from io import BytesIO
from PIL import Image
from pytesseract import image_to_string
from CheckCode import  *
from recognition_func import getCaptcha
import os
import pdb
import time
from ..public.basic_request import Request,Session

cur_dir=os.path.dirname(__file__)
train_path=os.path.join(cur_dir,'TrainSet.csv')

current_milli_time = lambda:int(round(time.time() * 1000))




class code(object):

    def __init__(self,browser):
        self.result={}
        self.html= browser.page_source
        self.headers={
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ('
                          'KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Host': 'omeo.alipay.com'
        }
        self.cookies = {}
        self.browser=browser
        for cookie_dict in self.browser.get_cookies():
            self.cookies[cookie_dict['name']] = cookie_dict['value']
        self.result['cookies']=self.cookies


    def checkinfo(self):
        #url="https://omeo.alipay.com/service/checkcode?sessionID =87c770f931d1c90deaa7830fca73356e&t=0.9494155923457824"
        bsoup = BeautifulSoup(self.html, 'lxml')
        url=bsoup.find("img", {"id": "J-checkcode-img"})["src"]

        options={'method':'get','url':url,'headers':self.headers,
                 'cookies':self.cookies}

        self.result['url']=url
        print url
        response=Request.basic(options)
        if response:
            print "get code success....."
            return self.getImage(response.content)

    def getImage(self,content):
        file = BytesIO(content)
        img = Image.open(file)
        checkcode=getCaptcha(img)
        if checkcode:
            self.result['code']=checkcode
            return self.result


    #对获得的验证码进行判断(没有获得想要的数据暂时没用用这个函数)
    def check_Code(self,code):
        url='https://authzth.alipay.com/login/verifyCheckCode.json'
        form_data={
            'checkCode':'ubd9',
            'idPrefix':'',
            'timestamp':'1485137462670',
            '_input_charset':'utf-8',
            'ctoken':'IK8H6gPwH3SIXZxT'
        }
        self.headers['Host']='authzth.alipay.com'
        self.headers['Referer']='https://authzth.alipay.com/login/index.htm'
        self.headers['Origin']='https://authzth.alipay.com'
        form_data['checkCode']=code
        form_data['timestamp']=current_milli_time()
        options = {'method': 'post', 'url': url, 'form':form_data, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}

        respose=Request.basic(options)
        if respose:
            print respose.content
            return code


def codeApi(browser):
    c=code(browser)
    result_dict=c.checkinfo()
    return result_dict











