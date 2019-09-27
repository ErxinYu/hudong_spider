#encoding=utf-8
import MySQLdb
import MySQLdb.cursors

class db:
    def __init__(self,host,user,passwd,db,port,charset="utf8"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        self.port = port
        self.charset = charset
        try:  
            self.con=MySQLdb.connect(host=self.host,
                                        user=self.user,
                                        passwd=self.passwd,
                                        port = self.port,
                                        db=self.db,
                                        cursorclass = MySQLdb.cursors.DictCursor) 
            self.con.set_character_set(self.charset)
            self.cur=self.con.cursor()  
        except MySQLdb.Error as e:  
            print("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        
    def query(self, p_table_name, p_name):
        if p_table_name == "category": 
            try:                    
                sqltext = "SELECT * FROM `%s` WHERE name ='%s'" %(p_table_name, p_name)            
                self.cur.execute(sqltext)                
                res =self.cur.fetchone()
            except:
                print("Mysql Error %d: %s" %(e.args[0],e.args[1]))
            if res is None:              
                return 0
            else:
                return int(res['id'])    
        elif p_table_name == "category_relatelinks":
            SQL1 = "SELECT * FROM `%s` WHERE id =%s and relateLinks=%s" % (p_table_name, str(p_name[0]), str(p_name[1]))        
            self.cur.execute(SQL1)
            res1 = self.cur.fetchone()
            SQL2 = "SELECT * FROM `%s` WHERE id =%s and relateLinks=%s" % (p_table_name, str(p_name[1]), str(p_name[0]))         
            self.cur.execute(SQL2)            
            res2 = self.cur.fetchone() 
            if res1 is not None or res2 is not None:            
                return 1
            else:
                return 0
        elif p_table_name == "category_inlinks":
            SQL1 = "SELECT * FROM `%s` WHERE id =%s and inLinks=%s" % (p_table_name, str(p_name[0]), str(p_name[1]))        
            self.cur.execute(SQL1)
            res1 = self.cur.fetchone()
            SQL2 = "SELECT * FROM `%s` WHERE id =%s and inLinks=%s" % (p_table_name, str(p_name[1]), str(p_name[0]))         
            self.cur.execute(SQL2)            
            res2 = self.cur.fetchone() 
            if res1 is not None or res2 is not None:            
                return 1
            else:
                return 0
        elif p_table_name == "page" or p_table_name == "page_copy":
            SQL = "SELECT * FROM `%s` WHERE name =\"%s\"" % (p_table_name,p_name)         
            self.cur.execute(SQL)            
            res = self.cur.fetchone() 
            if res is not None: 
                return int(res['id'])
            else:
                return 0
        elif p_table_name == "category_pages":
            SQL = "SELECT * FROM `%s` WHERE id =%s and pages=%s" % (p_table_name, str(p_name[0]), str(p_name[1]))        
            self.cur.execute(SQL)                  
            res = self.cur.fetchone() 
            if result is not None:            
                return 1
            else:
                return 0
    
    # 似乎没啥用
    def update(self, p_table_name, p_data):
        if p_table_name == "page":
            SQL ="UPDATE %s SET text ='%s' WHERE id=%s" % (p_table_name, p_data[1], p_data[0])
        return self.cur.execute(SQL) # 似乎少了commit
    
    def insert(self, p_table_name, p_data):        
        #插入一条记录 
        if len(p_data) == 5:
            SQL = "INSERT INTO page VALUES(%s,%s,'%s','%s',1)" % (p_data[0], p_data[1], p_data[2], p_data[3])
        elif p_table_name == "category" or p_table_name == "page_copy":
            SQL = "INSERT INTO " + p_table_name + " VALUES(" + str(p_data[0]) + "," + str(p_data[1]) + ',\"' + str(p_data[2]) + '\"' + ")"
        else:
            SQL = "INSERT INTO " + p_table_name + " VALUES(" + str(p_data[0]) + "," + str(p_data[1]) + ")"
        return self.cur.execute(SQL)  # 似乎少了commit
    
    def select(self, p_table_name, p_data):
        SQL = "SELECT name FROM %s WHERE id >%s" % (p_table_name, p_data)    
        self.cur.execute(SQL)
        return self.cur.fetchall()
    
    def rowcount(self, p_table_name):  
         SQL = "SELECT MAX(category_id) FROM " + p_table_name  
         self.cur.execute(SQL) 
         return self.cur.fetchone()

    def commit(self):  
         self.con.commit()  
  
    def close(self):  
         self.cur.close()  
         self.con.close()  
     
 
