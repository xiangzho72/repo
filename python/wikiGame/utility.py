import sqlite3
from sqlite3 import Error
import urllib.parse
import re  

########################################################
#The following funs handle 2* 8 bytes number to 1 * 16 byte.
###########################################################
def splitNumberBy8Bytes( num ):
    oriNum = num
    numHi = num >> 64
    numLo = oriNum & 0xffffffffffffffff
    return (numHi, numLo)

    
def combine2Of8Bytes( numHi, numLo ):
    num = (numHi << 64) | numLo    
    return num
    
def transformToDatabase(row):
    id, linkText,linkUrl = row
    idHi,idLo = splitNumberBy8Bytes(id)
    return ( idHi, idLo, linkText,linkUrl )

def transformBack(row):
    idHi,idLo, linkText,linkUrl = row
    id = combine2Of8Bytes(idHi,idLo)
    return ( id,linkText,linkUrl)    

############################################
# The following funs handle normalization
##############################################
def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True
    
    
def normalizeText(text):
    if isEnglish(text):
        if len(text) < 3:
           return ''
    
        excludedTexts=['edit', 'log in','contact','help','support', 'changes','download'\
                         'upload','privacy', 'policy','team','terms', 'community','print' \
                        'disclaimers','cookie statement','mobile view','developers'  \
                         ]
        
        text = text.strip().lower().replace('"','')
        for filter in map(lambda x:x.lower(),excludedTexts): 
            if -1 != text.find(filter) :
               return ''
        return text
    else:
        return ''

def normalizeLink(baseUrl, url):
      ret = ''
      if '?' in url  or '#' in url or 'http' in url:
          return ret

      try: 
           #ret = url_normalize( url if 'http' in url else urllib.parse.urljoin(baseUrl,url))
           ret = urllib.parse.urljoin(baseUrl,url)
      except KeyError:
           print("KEY ERROR : " + url)   
      return ret      

def get_jaccard_sim(str1, str2):

    a = set(re.split('[-_ ]',str1)) 
    b = set(re.split('[-_ ]',str2))
    
    c = a.intersection(b)
    return float(len(c)) / (len(a) + len(b) - len(c)) 

####################################
# The following fun handles database
#################################### 
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return None


def create_table(conn, table):
    sql_create_table = 'CREATE TABLE IF NOT EXISTS '+ table + """(  
                                        idHi integer , 
                                        idLo integer ,                                        
                                        name text NOT NULL,            
                                        link text NOT NULL,
                                        PRIMARY KEY (idHi,idLo)
                                        
                                    )""";     
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
        return True
    except Error as e:
        print(e)
        return False

def create_url_table(conn):
    sql_create_table = """CREATE TABLE IF NOT EXISTS URL (    
                                        url TEXT NOT NULL UNIQUE       
                                    )""";     
    try:
        c = conn.cursor()
        c.execute(sql_create_table)
        return True
    except Error as e:
        print(e)
        return False

        
def insert_link(conn, table, item):
    sql = 'INSERT INTO ' + table + '(idHi,idLo,name,link) VALUES(?,?,?,?) '
    cur = conn.cursor()
    try:
        item = transformToDatabase(item)
        cur.execute(sql, item)
        return cur.lastrowid
    except Error as e:
        print(e, sql)

def insert_url(conn, url):
    sql = 'INSERT INTO URL (url) VALUES(?) '
    cur = conn.cursor()
    try:
        cur.execute(sql, (url,))
        return True
    except Error as e:
        return False

        
def select_link_by_id(conn, table, id):
    cur = conn.cursor()
    (idHi, idLo) = splitNumberBy8Bytes(id)
    sql = "SELECT * FROM " + table + " WHERE idHi == "+ str(idHi) \
                                    + " AND  idLo == "+ str(idLo)          
    try:
        cur.execute(sql)
        row = cur.fetchone()
        return transformBack(row)
    except Error as e:
        print(e, sql)
        return [] 
    
def drop_tables(conn):
    cursor=conn.cursor()
    sql = "DROP TABLE IF EXISTS URL"
    cursor.execute(sql)
    for i in range(10):
        table = 'Link' + str(i)
        sql = "DROP TABLE IF EXISTS " + table 
        cursor.execute(sql)   
        