# -*- coding:utf-8 -*-
import pymysql
import pandas as pd

class OperationMysql:
    def __init__(self,sql):
        self.sql = sql

    #查询数据，结果为列表返回
    def selectSQL(self):
        conn = pymysql.connect(user='root', passwd='flins123', db='evaluation', port=3306, host='192.168.5.108',charset='utf8')
        cursor = conn.cursor()
        cursor.execute(self.sql)
        results = cursor.fetchall()
        lists = list(results)
        # conn.commit()
        cursor.close()
        conn.close()
        return lists

    #写入数据
    def insertSQL(self):
        conn = pymysql.connect(user='root', passwd='123456', db='cathy', port=3306, host='localhost',
                               charset='utf8')
        cursor = conn.cursor()
        effect_row = cursor.execute(self.sql)
        conn.commit()
        cursor.close()
        conn.close()
        return effect_row



if __name__ == '__main__':

    df = pd.read_excel('../predictModel-zhangli/labels2.xls')
    image = df['image'].values
    keys = df['key'].values
    score = df['score'].values
    keys_list = keys.tolist()
    list = image.tolist()
    scores = score.tolist()
    for i, key2 ,score in zip(list, keys_list,scores):
        print(i)
        print(key2)
        print(score)
        sql = 'INSERT INTO content_tieba(image,qiniu_key,score) VALUES("%s","%s","%s")' %(i,key2,score)
        o = OperationMysql(sql)
        result = o.insertSQL()
        print(result)


