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
    title = ["image","key","content","pre"]
    for col in range(len(title)):
        sheet.write(0, col, title[col])
    book.save(file)

#把image保存excel
def xls_image(file,image):
    workbook = xlrd.open_workbook(file, formatting_info=True)
    sheet = workbook.sheets()[0]
    newbook = copy(workbook)
    newsheet = newbook.get_sheet(0)
    rownum = sheet.nrows
    newsheet.write(rownum, 0, image)
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

def pretreatment(key):
    data = {'url':key}
    header = {"Content-Type": "application/json"}
    r = requests.post(base_url+'/customer/demo/pretreatment',data=json.dumps(data),headers=header)
    d = r.text
    s = json.loads(d)
    log.logger.info(s)
    pre_content = s["data"]["pretreatmentContent"]
    content = s["data"]["content"]
    key = s["data"]["url"]
    data_list = [key,content,pre_content]
    return data_list

def run(file):
    new_xls(file)
    df = pd.read_excel('../util/getQiniuKey/keys.xls')
    image = df['image'].values
    keys = df['key'].values
    keys_list = keys.tolist()
    list = image.tolist()
    for i,key in zip(list,keys_list):
        try:
            xls_image(file,i)
            data_list = pretreatment(key)
            xls(data_list,file)
        except Exception as e:
            log.logger.error(e)


if __name__ == '__main__':
    # 开始时间
    start = datetime.datetime.now()
    # 执行人保测评
    run('results-sun.xls')
    # 结束时间
    end = datetime.datetime.now()
    print('运行时长：' + str((end - start).seconds) + '秒')

