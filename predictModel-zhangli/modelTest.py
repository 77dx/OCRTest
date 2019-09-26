# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime
import requests
import xlrd
from xlutils.copy import copy
import pandas as pd
import os
from util.logger import Loggers
import xlwt
import json
import base64

log = Loggers(level='info')
base_url = "http://192.168.5.111"

#新建excel文件
def new_xls(file):
    try:
        if os.path.exists(file):
            os.remove(file)
    except :
        log.logger.warning(file+"不存在")
    book = xlwt.Workbook()
    sheet = book.add_sheet("sheet1")
    title = ["image","btext","cutWord","content","originpredict","prediction"]
    for col in range(len(title)):
        sheet.write(0, col, title[col])
    book.save(file)

#把content保存excel
def xls_content(file,rep_list):
    workbook = xlrd.open_workbook(file, formatting_info=True)
    sheet = workbook.sheets()[0]
    newbook = copy(workbook)
    newsheet = newbook.get_sheet(0)
    rownum = sheet.nrows
    for col in range(len(rep_list)):
        newsheet.write(rownum, col, rep_list[col])
    newbook.save(file)

#把image保存excel
def xls_image(file,image):
    workbook = xlrd.open_workbook(file, formatting_info=True)
    sheet = workbook.sheets()[0]
    newbook = copy(workbook)
    newsheet = newbook.get_sheet(0)
    rownum = sheet.nrows
    newsheet.write(rownum, 0, image)
    newbook.save(file)

#把key保存excel
def xls_key(file,image):
    workbook = xlrd.open_workbook(file, formatting_info=True)
    sheet = workbook.sheets()[0]
    newbook = copy(workbook)
    newsheet = newbook.get_sheet(0)
    rownum = sheet.nrows
    newsheet.write(rownum-1, 1, image)
    newbook.save(file)

#把测评结果保存excel
def xls(data_list,file):
    workbook = xlrd.open_workbook(file, formatting_info=True)
    sheet = workbook.sheets()[0]
    newbook = copy(workbook)
    newsheet = newbook.get_sheet(0)
    rownum = sheet.nrows
    for col in range(len(data_list)):
        newsheet.write(rownum-1, col+1, data_list[col])
    newbook.save(file)


#获取七牛token
def get_qiniuToken():
    header = {"Accept":"application/json, text/javascript, */*; q=0.01","Content-Type":"application/json"}
    r = requests.post(base_url+"/business/rb/getQiNiuToken",headers=header)
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["data"]["qiNiuToken"]

#图片转base64
def open_image(filename):
    f = open(filename,'rb')
    res = f.read()
    s = base64.b64encode(res)
    return s

#上传图片数据流
def upload(qiniu_token,base):
    data = base
    header = {"Authorization":"UpToken "+qiniu_token,"Content-Type":"application/octet-stream"}
    r = requests.post('https://upload-z2.qiniup.com/putb64/-1',data=data,headers=header)
    d = r.text
    s = json.loads(d)
    key = s["key"]
    log.logger.info(s)
    return key

def baiduOCR(key):
    header = {"Content-Type": "application/json"}
    r = requests.get(base_url+'/customer/demo/baiduOCR?url='+key,headers=header)
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["data"]

#根据Yuchuli返回结果
def Yuchuli(content):
    r = requests.post("http://192.168.5.215:5676/Yuchuli",data=json.dumps(content))
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["BText"]

#分词
def replace(contents):
    header = {"Content-Type": "application/json"}
    data = {'content': contents}
    r = requests.post("http://192.168.5.111/customer/demo/replace",data=json.dumps(data),headers=header)
    d = r.text
    s = json.loads(d)
    dict = {"cutWord":s["data"]["cutWord"],"content":s["data"]["content"]}
    log.logger.info(s)
    return dict

#根据prediction返回结果d
def originpredict(content):
    data = {'BText':content}
    r = requests.post("http://192.168.5.215:5676/originpredict",data=json.dumps(data))
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["prediction"]

#prediction == 0
def cutwordlowpredict(cutWord):
    data = {'BText': cutWord}
    r = requests.post("http://192.168.5.215:5676/cutwordlowpredict",data=json.dumps(data))
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["prediction"]

#prediction == 1
def originhighpredict(content):
    data = {'BText': content}
    r = requests.post("http://192.168.5.215:5676/originhighpredict",data=json.dumps(data))
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    return s["prediction"]


def run(file,image_url):
    new_xls(file)
    df = pd.read_excel('labels2.xls')
    image = df['image'].values
    keys = df['key'].values
    keys_list = keys.tolist()
    list = image.tolist()
    for i,key in zip(list,keys_list):
        try:
            xls_image(file,i)
            #baiduOCR
            contents = baiduOCR(key)
            #预处理
            btext = Yuchuli(contents)
            #replace
            dict = replace(btext)
            cutWord = dict["cutWord"]
            content = dict["content"]
            #去掉[]
            s = content.replace('[','').replace(']','')
            origin = originpredict(s)
            if origin == 0:
                data_list = cutwordlowpredict(cutWord)
                rep_list = [btext, cutWord, s,origin,data_list]
                xls(rep_list,file)
            elif origin == 1:
                data_list = originhighpredict(s)
                rep_list = [btext, cutWord, s, origin, data_list]
                xls(rep_list, file)
        except Exception as e:
            log.logger.error(e)


if __name__ == '__main__':
    # 开始时间
    start = datetime.datetime.now()
    # 执行人保测评
    run("results.xls","D:/samples2")
    # 结束时间
    end = datetime.datetime.now()
    print('运行时长：' + str((end - start).seconds) + '秒')







