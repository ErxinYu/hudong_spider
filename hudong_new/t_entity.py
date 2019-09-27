#encoding=utf-8

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
import sys

"""
@function 载入采集数据库的信息
@param mysql.property的路径
"""
def loadDatabase(filename):
	info_dict ={}
	f = open(filename)
	for line in f.readlines():
		info_dict[line.split("=")[0].strip()] =  line.split("=")[1].strip()
	return info_dict


"""
@function: 解析每个页面是否是词条，是词条存入t_entity表
@param: 采集源数据的起始id号，终止id号
@usage: python t_entity.py 1 100000
"""
if __name__ == "__main__":
    start_index =int(sys.argv[1])
    max_index = int(sys.argv[2])
    database_info = loadDatabase("mysql.property.txt")
    mydb = Database.db(database_info['ip'],database_info['user'],database_info['pwd'],database_info['database'],int(database_info['port']))    
    total_list = {}
    forbidden_list =[0,-1]
    for index in range(start_index, max_index+1):
        print("---------start----%d-----" % (index)) 
        selectSQL = "SELECT * FROM t_page WHERE page_id=%s" % (index)
        mydb.cur.execute(selectSQL)
        urlRow = mydb.cur.fetchone()     
        selectEntitySQL ="SELECT * FROM t_entity WHERE entity_id=%s" % (index)
        mydb.cur.execute(selectEntitySQL)
        urlEntityRow = mydb.cur.fetchone()   
        isEntity = 0           
        if urlRow is not None and urlEntityRow is None:  
            if urlRow['creator'] is not None and len(urlRow['creator']) > 0:
                isEntity = 1          
            html = urlRow['snapshot']
            soup = bs4.BeautifulSoup(html, "lxml")
            attrs_list  = []
            url_list = []
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
                        # print(name)
                        if total_list.has_key(name):
                            url_list.append(total_list[name])                           
                        else:                                
                            flaggg = SQLquery(mydb, 't_page', 'title', name.strip(), 'page_id')                                                                    
                            if (flaggg not in url_list) and (str(flaggg)!= "None"):
                                total_list[name]= str(flaggg)                                                                
                                if flaggg not in forbidden_list: 
                                    url_list.append(str(flaggg))
                                        
            if isEntity or (isCitiaoEntity(mydb, soup) and (not SQLquery(mydb, "t_entity", "entity_id", str(urlRow['page_id']), "entity_id"))):
                # print(isEntity)
                SQL = "INSERT INTO t_entity(entity_id,entity_name,content,links,page_id) VALUES(%s,'%s','%s','%s',%s)" % (str(urlRow['page_id']), MySQLdb.escape_string(urlRow['title']), MySQLdb.escape_string(urlRow['snapshot']), ','.join(url_list), str(urlRow['page_id']))
                mydb.cur.execute(SQL)
                mydb.commit()
