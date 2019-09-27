#encoding=utf-8
## 对page的创建者，次数，人数，时间字段的补充
import urllib
import bs4  
import re
import time
import MySQLdb
import Database
import time
import socket 

##对url是空的进行补充
def updateSQL(mydb, snapshot, pageId):
    soup = bs4.BeautifulSoup(snapshot) 
    divs = soup.findAll("div", class_="rightdiv cooperation cooperation_t")
    count_modify = '1'
    count_view = '1'
    modify_time = time.strftime("%Y-%m-%d %X", time.localtime())
    creator = ""
    if len(divs) > 0:
        div = list(divs)[0]
        lis = div.findAll("li")                       
        for li in lis:
            straa = li.text.encode("utf-8").split()[0].split("：")
            if straa[0] == "创建者":
                creator = straa[1].strip()                                        
            elif straa[0] == "编辑次数":
                count_modify = straa[1][:-3]
                if count_modify == '':
                    count_modify = '1'
                print(count_modify.decode("utf-8").encode("gbk",'ignore'))
            elif straa[0] == "参与编辑人数":
                count_view = straa[1][:-3]
                if count_view == '':
                    count_view = '1'                        
            elif straa[0] == "最近更新时间":
                modify_time = straa[1] + ' ' + li.text.encode("utf-8").split(" ")[1]                 
        SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (MySQLdb.escape_string(creator), count_modify, count_view, modify_time, str(pageId))                
        try:
            mydb.cur.execute(SQL)
            mydb.commit()
        except:
            for li in lis:
                new_str =[]
                for line in li.text.encode("utf-8").split('\n'):
                    if len(line.strip()) > 0:
                        new_str.append(line.strip())
                straa = new_str                         
                if straa[0] == "创建者：":
                    creator = straa[1].strip()                                    
                elif straa[0] == "编辑次数：":
                    count_modify = straa[1] [:-3]                                    
                elif straa[0] == "参与编辑人数：":
                    count_view = straa[1][:-3]
                elif straa[0].find("最近更新时间")>=0:
                    modify_time = straa[0].split("：")[1]                     
            SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (MySQLdb.escape_string(creator), count_modify, count_view, modify_time, str(pageId))                
            mydb.cur.execute(SQL)
            mydb.commit()

    else:
        SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (creator, count_modify, count_view, modify_time, str(pageId))                
        mydb.cur.execute(SQL)
        mydb.commit()


"""
@function 指定字段抽取创建者，编辑次数，编辑人数，更新时间
@param 数据库句柄，页面html的soup,页面id
"""
def fun(mydb, soup, pageId):
    divs = soup.findAll("div", class_="rightdiv cooperation cooperation_t")
    divs_creator = soup.findAll("div", class_="rightdiv gongxianbang")     # 创建者信息在该块中
    count_modify = '1'
    count_view = '1'
    modify_time = time.strftime("%Y-%m-%d %X", time.localtime())
    creator = ""
    if len(divs) > 0:
        div = list(divs)[0]
        lis = div.findAll("li")
        div_creator = list(divs_creator)[0]
        lis_creator = div_creator.findAll("li")
        try:
            for li_creator in lis_creator:
                straa_creator = li_creator.text.encode("utf-8").split()[0].split("：")
                if straa_creator[0] == "创建者":        # 创建者不在("div", class_="rightdiv cooperation cooperation_t")块中
                    creator = straa_creator[1].strip()
        except Exception as e:
            print("Error", e)
        for li in lis:
            # print(li)
            straa = li.text.encode("utf-8").split()[0].split("：")
            if straa[0] == "编辑次数":
                count_modify = straa[1][:-3]
                if count_modify == '':
                    count_modify = '1'
            elif straa[0] == "参与编辑人数":
                count_view = straa[1][:-3]
                if count_view == '':
                    count_view = '1'                                           
            elif straa[0] == "最近更新时间":
                modify_time = straa[1] + ' ' + li.text.encode("utf-8").split(" ")[1]    
        SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (creator, count_modify, count_view, modify_time, str(pageId))                
        try:
            mydb.cur.execute(SQL)
            mydb.commit()
        except:
            for li in lis:
                new_str =[]
                for line in li.text.encode("utf-8").split('\n'):
                    if len(line.strip())>0:
                        new_str.append(line.strip())
                straa = new_str        
                if straa[0] == "创建者：":
                    creator = straa[1].strip()
                elif straa[0] == "编辑次数：":
                    count_modify = straa[1] [:-3]
                elif straa[0] == "参与编辑人数：":
                    count_view = straa[1][:-3]
                    print(count_view.decode("utf-8").encode("gbk",'ignore'))                                         
                elif straa[0].find("最近更新时间") >= 0:
                    modify_time = straa[0].split("：")[1]                        
            SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (MySQLdb.escape_string(creator),count_modify,count_view,modify_time,str(pageId))                
            mydb.cur.execute(SQL)
            mydb.commit()
    else:
        # print("---enter")
        SQL = "UPDATE t_page SET creator='%s',count_view=%s,count_modify=%s,lastmodify='%s' WHERE page_id=%s" % (creator,count_modify,count_view,modify_time,str(pageId))                
        mydb.cur.execute(SQL)
        mydb.commit()


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

def crawPage(start, end):             
    database_info = loadDatabase("mysql.property.txt")
    mydb = Database.db(database_info['ip'], database_info['user'], database_info['pwd'], database_info['database'], int(database_info['port']))
    for pageId in range(int(start), int(end)):
        print("------------start pageId ----%s----"  % (str(pageId)))
        SQL = "SELECT * FROM t_page WHERE page_id=%s" % (str(pageId))            
        mydb.cur.execute(SQL)                
        ss = mydb.cur.fetchone()   
        if ss is not None:
            soup = bs4.BeautifulSoup(ss['snapshot'])
            fun(mydb, soup, pageId)

# crawPage(sys.argv[1],sys.argv[2])

