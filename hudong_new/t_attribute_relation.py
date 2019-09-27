#encoding=utf-8
## 用来实现page page_categories category person_relation person_attribute
#encoding=utf-8
import urllib
import bs4  
import re
import time
import MySQLdb
import Database
import os
import sys
import socket 

"""
@function 载入采集数据库的信息
@param mysql.property的路径
"""
def loadDatabase(filename):
    info_dict = {}
    f = open(filename)
    for line in f.readlines():
        info_dict[line.split("=")[0].strip()] = line.split("=")[1].strip()
    return info_dict


"""
@function 给定sql语句，插入数据
"""
def insertSQL(mydb, SQL):          
    mydb.cur.execute(SQL)
    mydb.con.commit()
    

"""
@function 获取pageid
"""    
def getId(mydb, table_name, title):
    key = "MAX(%s)" %(title)
    SQL = "SELECT " + key + " FROM " + table_name 
    mydb.cur.execute(SQL)
    res = mydb.cur.fetchone()
    if res[key] is None:
        return 1    
    else:                    
        return  int(res[key])+1  


"""
@function 抽取开放分类字段
"""
def getCategory(mydb, soup, pageId):  
    categorylist = []                  
    div_set = soup.findAll("div", class_="relevantinfo")
    dds = []
    if len(div_set)==0:
        return 
    else:
        div = list(div_set)[len(div_set)-1]
        dl_set = div.findAll("dl", id="show_tag")
        if len(dl_set) > 0:
            dds = list(dl_set)[0].findAll("dd")
            for dd in dds:
                for a in dd.findAll("a"):
                    word = a.text.encode("utf-8",'ignore').strip().split("\\n")[0]
                    SQL = "SELECT * FROM t_category WHERE category_name='%s'" % (MySQLdb.escape_string(word))
                    mydb.cur.execute(SQL)
                    categoryRow = mydb.cur.fetchone()
                    if categoryRow is not None:
                        categoryId = categoryRow['category_id']
                    else:
                        categoryId = getId(mydb, "t_category", "category_id")
                        url = "http://fenlei.baike.com/" + word
                        SQL ="INSERT INTO t_category VALUES(%s,'%s','%s',0)" % (categoryId, MySQLdb.escape_string(word), MySQLdb.escape_string(url))
                        insertSQL(mydb, SQL)
                    ## 插入 category_entity表
                    getPageCategory(mydb, pageId, categoryId)  

 
"""
@function 插入到category_entity关系表
"""   
def getPageCategory(mydb, entityId, categoryId):    
    SQL = "SELECT * FROM t_entity_category WHERE entity_id=%s AND category_id=%s" % (entityId, categoryId)
    mydb.cur.execute(SQL)
    pagecategoryRow = mydb.cur.fetchone()
    if pagecategoryRow is None:     
        SQL = "INSERT INTO t_entity_category(entity_id,category_id) VALUES(%s,%s)" % (entityId, categoryId)
        insertSQL(mydb, SQL)


"""
@function 插入属性到t_property 表
"""
def insertPropertyEntity(mydb, strong, span, page_id):
    SQL = "SELECT * FROM t_property WHERE property_name_raw ='%s'" % (strong.strip())            
    mydb.cur.execute(SQL)                
    res =mydb.cur.fetchone()
    if res is not None:               
        propertyId = res['property_id']                             
    else:         
        propertyId = getId(mydb, "t_property", "property_id")
        insert_text = "INSERT INTO t_property(property_id,property_name_raw,property_name_norm) VALUES(%s,'%s','')" % (propertyId, strong.strip())
        insertSQL(mydb, insert_text)                    
    SQL = "SELECT * FROM t_entity_property WHERE entity_id=%s AND property_id=%s AND value='%s'" % (page_id, propertyId, span)
    mydb.cur.execute(SQL)
    entity_propertyRow = mydb.cur.fetchone()
    if entity_propertyRow is None:
        currentEntityProperty = page_id
        value = span
        SQL = "INSERT INTO t_entity_property(entity_id,property_id,value,type) VALUES(%s,%s,'%s',%s)" % (str(currentEntityProperty), str(propertyId), MySQLdb.escape_string(value), str(1))
        insertSQL(mydb, SQL)


"""
@function 抽取关系字段到 t_property_entity 
"""        
def getOneRelation(mydb, person, divs, page_id):
   uls = divs.findAll("ul", id="fi_opposite")   
   if len(uls) > 0:
       li_set = list(uls)[0].findAll("li")
       for li in li_set:
           other = MySQLdb.escape_string(li.a.text.encode("utf-8"))
           relation = ""
           if len(li.contents)>2:                
               relation =  MySQLdb.escape_string(li.contents[2].encode("utf-8"))            
           if relation.strip() != "" and relation.strip() != '\\n' and other != "":                       
               insertPropertyEntity(mydb, relation.split('\\n')[0], other.split('\\n')[0], page_id)     
"""
@function 同上，抽取反向关系
"""
def getOppositeRelation(mydb, person, divs, page_id):
    divs = divs.findAll("div", class_="text_dir")
    if len(divs) > 0:
        divs = list(divs)[0]
        lis = divs.findAll("li")
        for li in lis:
            other =  MySQLdb.escape_string(li.a.text.encode("utf-8"))
            relation = ""
            if len(li.contents) > 2:                
                relation =  MySQLdb.escape_string(li.contents[2].encode("utf-8"))
            if relation.strip() != "" and relation.strip() != '\\n' and other != "":                      
                insertPropertyEntity(mydb, relation.strip(), other.strip(),page_id)  

"""
@function 抽取关系
"""
def getRelation(mydb, soup, person, page_id):
    divs = soup.findAll("div", id="figurerelation")
    #print relations
    if len(divs) > 0:
        divs = list(divs)[0]
        getOneRelation(mydb, person, divs, page_id)
        getOppositeRelation(mydb, person, divs, page_id)


"""
@function 抽取属性表
"""        
def getTable(mydb, soup, person, page_id):
    divs = soup.findAll("div", class_="module zoom")
    if len(divs) > 0:        
        divs = list(divs)[0]
        tds = divs.findAll("td")
        for td in tds:
            strong_set = td.findAll("strong")
            if len(strong_set):                   
                strong = list(strong_set)[0].text.encode("utf-8",'ignore')
                strong = MySQLdb.escape_string(strong)
                if strong.find("：") >= 0:
                    strong = strong[:-3]                
                span = list(td.findAll("span"))[0].text.encode("utf-8",'ignore').strip()
                span = MySQLdb.escape_string(span)
                insertPropertyEntity(mydb, strong, span, page_id)


"""
@function 给定pageid，将页面的属性，关系，分类，存入相应数据库表中
"""
def fun(mydb, soup, pageId, title):
    try:
        getTable(mydb, soup, title, pageId)                  
        getRelation(mydb, soup, title, pageId)
        getCategory(mydb, soup, pageId)
    except Exception as e:
        print("Error: t_attribute_relation.fun", e)




