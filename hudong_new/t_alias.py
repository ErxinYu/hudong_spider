#encoding=utf-8
# 从 t_page中对html解析，如果有同义词的字段，摘取存入 t_alias
import threading
import urllib
import bs4  
import re
import time
import MySQLdb
import Database
import time
import socket 
import sys

"""
@function 载入采集数据库的信息
@param mysql.property的路径
"""

def loadDatabase(filename):
	info_dict = {}
	f = open(filename)
	for line in f.readlines():
		info_dict[line.split("=")[0].strip()] =  line.split("=")[1].strip()
	return info_dict

"""
@function 给定页面，抽取同义词，插入到t_alias表中
@param {#p#} : 数据库句柄，页面html源码形成的beautifulsoup，页面Id号
"""
def fun(mydb, soup, entity_id): # 此处entity_id 即 page_id
    try:
        p_set = soup.findAll("p", id="unifypromptone")
        if len(p_set) > 0:
            p = list(p_set)[0]
            a_set = p.findAll('a')
            if len(a_set) > 0:
                # print(list(a_set)[1].text.encode("utf-8",'ignore'))
                alias_name = list(a_set)[1].text.encode("utf-8")
                try:
                    SQL = "SELECT MAX(alias_id) FROM t_alias"
                    mydb.cur.execute(SQL)
                    res = mydb.cur.fetchone()
                    alias_id = int(res['MAX(alias_id)']) + 1 # 插入页面id为当前最大id + 1
                except:
                    alias_id = 1                 # 找不到maxId, res['MAX(alias_id)'] = None,故初始化为1
                SQL = "INSERT INTO t_alias(alias_id,alias_name,entity_id) VALUES(%s,'%s',%s)" % (str(alias_id), MySQLdb.escape_string(alias_name), str(entity_id))
                mydb.cur.execute(SQL)
                mydb.commit()
    except Exception as e:
        print("Error: t_alias.fun", e)


"""
@function:给定t_page的区间段，抽取该区间段中的所有同义词 ，每一个页面对应一个entity
@param {#p#} : 区间的开始id号，结束id号
"""
def getAlias(start, end):
    database_info = loadDatabase("mysql.property.txt")
    mydb = Database.db(database_info['ip'], database_info['user'], database_info['pwd'], database_info['database'], int(database_info['port']))
    for pageId in range(int(start), int(end)):
        # print(pageId)
        SQL = "SELECT * FROM t_page WHERE page_id=%s" % (pageId) 
        mydb.cur.execute(SQL)
        res = mydb.cur.fetchone()
        if res is not None:
            soup = bs4.BeautifulSoup(res['snapshot']) 
            fun(mydb, soup, patgeId)


#getAlias(sys.argv[1])
