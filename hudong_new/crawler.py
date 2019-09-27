#encoding=utf-8
### 通过hudong数据库中已有的page信息中的内链采集新的数据，并对数据进行抽取
import threading
import urllib
import urlparse
import bs4  
import re
import time
import MySQLdb
import Database
import time
import socket 
from ll_getMorePage import *
import os
import sys
import t_alias
import t_page
import t_attribute_relation
#from urllib import parse      # python3
#from urllib import request    # python3
import unidecode
import chardet

"""
@param  
    mydb: mysql数据库句柄
    entry: 插入数据的dict
@return
    成功插入返回id号，否则返回0
"""
def insertInToPage(mydb, entry):
    try:
        SQL1 = "SELECT * FROM t_page WHERE title='%s'" % (entry['name'])
        mydb.cur.execute(SQL1)
        if mydb.cur.fetchone() is None: # 如果该页不在数据库中,则将该项插入t_page
            try:
                SQL2 = "SELECT MAX(page_id) FROM t_page"
                mydb.cur.execute(SQL2)
                res = mydb.cur.fetchone()
                currentID = int(res['MAX(page_id)']) + 1 # 插入页面id为当前最大id + 1
            except:
                currentID = 1  # 找不到maxId, res['MAX(alias_id)'] = None,故初始化为1

            title = entry['name']
            url = entry['url']
            snapshot = entry['snapshot']
            try:
                soup = bs4.BeautifulSoup(snapshot, "lxml")
            except:
                print("soup出问题")
            if isCitiao(mydb, soup): # 如果该页面内容是一个词条
                # print("Page %d is Citiao-----" % currentID)
                SQL3 = "INSERT INTO t_page(page_id,title,url,snapshot,count_view,count_modify) VALUES(%s,'%s','%s','%s',0,0)" % (currentID, MySQLdb.escape_string(title), MySQLdb.escape_string(url), MySQLdb.escape_string(snapshot))
                mydb.cur.execute(SQL3) # 插入
                mydb.commit()
                try:
                    t_alias.fun(mydb, soup, currentID)                ## 从页面中提取同义词
                    t_page.fun(mydb, soup, currentID)                ## 提取创建者，创建时间，创建次数
                    t_attribute_relation.fun(mydb, soup, currentID, MySQLdb.escape_string(title))  ## 提取词条属性，关系，所属开放分类
                except Exception as e:
                    print("t_alisa/t_page/t_attribute_relation.fun error！",e)
                return currentID # 插入成功，返回插入页面的id
            else:
                return 0 # 该页不是词条,返回id=0
        else:
            return 0 # 该页已经在数据库中,返回id=0
    except:
        print("insertInToPage-----error-----")
        return 0

"""
@function 更新t_page的snapshot字段
@param:  数据库句柄，插入的snapshot字段，插入字段的id号
"""

def updateSnapshot(mydb, snapshot, page_id):
    SQL = "UPDATE t_page SET snapshot='%s' WHERE page_id=%s" % (MySQLdb.escape_string(snapshot), page_id)
    mydb.cur.execute(SQL)
    mydb.commit()


"""
@function 载入采集数据库的配置信息
@param mysql.property的路径
"""
def loadDatabase(filename):
	info_dict ={}
	f = open(filename)
	for line in f.readlines():
		info_dict[line.split("=")[0].strip()] =  line.split("=")[1].strip()
	return info_dict


"""
@function: 解析每个页面的所有链接，符合baike页面的链接判断去重，插入t_page表后提取alias,category,property,creator等字段
@param: 采集源数据的起始id号，终止id号
@usage: python crawler.py 1 100000
"""
if __name__ == "__main__":
    start_index = int(sys.argv[1])
    max_index = int(sys.argv[2])
    database_info = loadDatabase("mysql.property.txt")
    mydb = Database.db(database_info['ip'], database_info['user'], database_info['pwd'], database_info['database'], int(database_info['port']))
    total_list = []
    forbidden_id_list =[0, -1] #     # 所有页面都会有的页面id号,遇到这些id不进行处理；若t_page为空，则从www.baike.com开始爬取所有的内链
    for index in range(start_index, max_index + 1):
        print("---------start----%d-----"  %(index))
        SQL = "SELECT * FROM t_page WHERE page_id=%s" % (index)
        mydb.cur.execute(SQL)
        res = mydb.cur.fetchone()
        if res is not None :
            snapshot = res['snapshot']
            if snapshot is None:
                snapshot = urllib.urlopen(res['url']).read()
                updateSnapshot(mydb, snapshot, index)
            soup = bs4.BeautifulSoup(snapshot, "lxml")
        else:
            initial_url = "http://www.baike.com"
            snapshot = urllib.urlopen(initial_url).read()
            soup = bs4.BeautifulSoup(snapshot, "lxml")
            # print(soup)
        attrs_list  = []
        url_list = []
        # 查找所有内链
        for a in soup.findAll('a'):
            if 'href' in a.attrs and (a.attrs['href'].startswith("//www.baike.com/wiki/") or a.attrs['href'].startswith("http://www.baike.com/wiki/")):  
                if a.attrs['href'].startswith("//www.baike.com/wiki/"):
                    attrs_url = 'http:' + a['href'].split("#")[0].strip().encode("utf-8")
                elif a.attrs['href'].startswith("http://www.baike.com/wiki/"):
                    attrs_url = a['href'].split("#")[0].strip().encode("utf-8")
                attrs_url = list(urlparse.urlsplit(attrs_url))
                attrs_url[2] = urllib.quote(attrs_url[2])
                attrs_url = urlparse.urlunsplit(attrs_url)
                if attrs_url not in attrs_list:
                    attrs_list.append(attrs_url)
                    name = urllib.unquote(urllib.unquote(attrs_url).split("wiki/")[1].split("?")[0])
                    name = urllib.unquote(" ".join(name.split("+")).split("&")[0])
                    #print(name)
                    if name not in total_list: # 判断是否已经采集, check是否在本页面多次出现
                        flaggg = SQLquery(mydb, 't_page', 'title', name.strip(), 'page_id')
                        if not flaggg: # 如果不在t_page中
                            entry = {}
                            entry['name'] = name.strip()
                            # print("---insert page----")                            
                            try:
                                try:
                                    # print(attrs_url)
                                    snapshot_new = urllib.urlopen(attrs_url).read()         # 采集新页面
                                except socket.timeout as e:
                                    print("---socket---timeout---")
                                entry['snapshot'] = snapshot_new
                                entry['url'] =  attrs_url
                                new_flaggg =  insertInToPage(mydb, entry) # 执行插入，check是否在数据库中多次出现
                                # if new_flaggg == 0:
                                    # print("---This page is not citiao----") 
                                if (flaggg not in url_list) and (flaggg not in forbidden_id_list) and (str(new_flaggg)!="None"):
                                    url_list.append(str(new_flaggg)) 
                                    total_list.append(name)                                     
                            except Exception as e:
                                print("----link error---", e)
                                break
                                            
                        if (flaggg not in url_list) and (str(flaggg) != "None"):
                            if flaggg not in forbidden_id_list:
                                url_list.append(str(flaggg))
                            total_list.append(name)

