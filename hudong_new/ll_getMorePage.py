#encoding=utf-8
import threading
import urllib
import bs4  
import re
import time
import MySQLdb
import Database
import time
import socket 
from  t_page import *

# 从属性表里面的属性放进 t_property中，并且查找相应的entity表,将property_entity 关系放进 t_entity_property表中

def countRow(mydb, colum_name, table_name):
    # 计算行数
    # 查询列名， 表名
    SQL = "SELECT MAX(%s) FROM %s" % (colum_name, table_name)
    mydb.cur.execute(SQL) 
    res =  mydb.cur.fetchone()
    return res

def isCitiaoEntity(mydb, soup):# 跟下面一个的区别在哪？
    if soup is None:
        return False
    divs = soup.findAll('div', class_="gray80 ser-guo clearfix")
    divs2 = soup.findAll('div', class_="no-result")
    title = soup.findAll('title')
    if len(list(title)) > 0 and list(title)[0].text == "400 Bad Request":
        print(0)
        return False
    if len(list(divs2)) > 0:
        print(2)
        return False
    if len(list(divs)) > 0:
        print(3)
        return False
    return True

def isCitiao(mydb, soup): # 跟上面一个的区别在哪？
    # 判断是否是词条
    if soup is None:
        return False
    #divs = soup.findAll('div',class_="gray80 ser-guo clearfix")
    divs2 = soup.findAll('div', class_="no-result")
    title = soup.findAll('title')
    if len(list(title)) > 0 and list(title)[0].text == "400 Bad Request":
        return False
    if len(list(divs2)):
        return False
    #if len(list(divs)):
    #        return False
    return True

def SQLquery(mydb, table_name, colum_name, content, result_colum):
    # print content
    # 查询接口
    # 表名，查询输入列，查询输入内容，查询输出列
    SQL = "SELECT * FROM %s WHERE %s='%s'" % (table_name, colum_name, MySQLdb.escape_string(content))
    #SQL = "SELECT * FROM %s WHERE %s='%s'" % (table_name, colum_name, content) # python3

    mydb.cur.execute(SQL)
    res = mydb.cur.fetchone()
    if res is None:
        return 0
    else:        
        if table_name == "Tmp_Url" or table_name == "t_entity":
            return 1
        else:
            soup = bs4.BeautifulSoup(MySQLdb.escape_string(res['snapshot']), "lxml")
            if  isCitiao(mydb, soup):
                return res['page_id']
            else:
                return -1 
	

def other_query(mydb, entity_id, property_id, value):
    SQL = "SELECT * FROM t_entity_property WHERE entity_id=%s AND property_id=%s AND value='%s'" % (entity_id, property_id, value)
    mydb.cur.execute(SQL)
    res = mydb.cur.fetchone()
    return 0 if res is None else 1

def insertInTPAGE(mydb, entry):
    SQL = "SELECT MAX(page_id) FROM t_page"
    mydb.cur.execute(SQL)
    res = mydb.cur.fetchone()
    currentID = int(res['MAX(page_id)']) + 1
    # print(currentID)
    title = entry['name']
    # print(title)
    url = entry['url']
    # print(url)
    snapshot = entry['snapshot']
    soup = bs4.BeautifulSoup(snapshot, "lxml")
    if isCitiao(mydb, soup):
        # print("isCitiao-----")
        SQL = "INSERT INTO t_page(page_id,title,url,snapshot,count_view,count_modify) VALUES(%s,'%s','%s','%s',0,0)" % (currentID, MySQLdb.escape_string(title), MySQLdb.escape_string(url), MySQLdb.escape_string(snapshot))
        mydb.cur.execute(SQL)
        mydb.commit()
       
def tmpPageInsert():  
    timeout = 10  
    mydb = Database.db("localhost", "root", "poisson@123", "hudong_baike", 3306)
    print("connected")
    start = 196
    L_tabel_name = 't_page' 
    maxid = int(countRow(mydb, 'page_id', L_tabel_name)['MAX(page_id)'])
    print(maxid)
    for pageid in range(start, maxid):  
        print('-------------%d-----' %(pageid))
        SQL = "SELECT * FROM %s WHERE page_id=%s" % (L_tabel_name, pageid)        
        mydb.cur.execute(SQL)
        print(SQL)
        res = mydb.cur.fetchone()            
        if res is not None:
            soup = bs4.BeautifulSoup(res['snapshot'], "lxml")
            for a in soup.findAll('a'):         
                if a.attrs.has_key('href'):   
                    if a.attrs['href'].startswith("http://www.baike.com/wiki/"):
                        try:
                            snapshot = urllib.urlopen(a.attrs['href']).read()
                            soup_new = bs4.BeautifulSoup(snapshot, "lxml")
                            h1_set = soup_new.findAll('h1')                             
                            if len(list(h1_set)) == 1:
                                name = list(h1_set)[0].text.encode("utf-8")
                                flaggg = SQLquery(mydb,'t_page', 'title', name.strip(), 'page_id')
                                if not flaggg:                                                         
                                    entry = {}
                                    entry['name'] = name.strip()
                                    entry['url'] = a.attrs['href']   
                                    entry['snapshot'] = snapshot
                                    insertInTPAGE(mydb, entry)  
                                elif flaggg > 0:
                                    print("-----update----")
                                    updateSQL(mydb, snapshot, flaggg)                                
                        except socket.timeout as e:
                            print('----error----')   
                        
                                                                           
#tmpPageInsert()
