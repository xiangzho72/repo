from bs4 import BeautifulSoup
import urllib
import threading
import queue
import time 
import utility
import argparse

TABLE_NAME = 'Link'
MAX_LAYERS = 8
SIZE_UPQUEUE = 4000
SIZE_DOWNQUEUE = 100
stop_threads = False
    
class CrawlWorker(threading.Thread):
    """  This is the threads which will scrape the link got from downQueue
         and send back what's been scraped through upQueue
         All the workers share the same downQueue and upQueue
         Two type of CrawlWorker:  Worker will send back all it scraped
                                   PrototypeWorker will only send back the link which matches the matchStr 
    """  
    def __init__(self,downQueue,upQueue,matchStr,id = 0, type = 'Worker'):
        super(CrawlWorker,self).__init__()
        self.tableName = TABLE_NAME
        self.downQueue = downQueue
        self.upQueue = upQueue
        self.id = id
        self.type = type
        self.matchStr = matchStr
                
    def run(self):
        handled = 0
        while True:
            global stop_threads            
            if True == stop_threads: 
               break   
               
            if self.downQueue.empty():
               time.sleep(1)
               continue
               
            id,_,url = self.downQueue.get()
            handled += 1
            if handled % 10 == 0:
                print( "worker:%d handled %d tasks" %( self.id, handled))
            #Find the starting of id for the next layer
            nextId = id
            nextId = (nextId << 16) + 1 ;

            #Connect to the given url
            try: 
                resp = urllib.request.urlopen(url)
            except (urllib.error.HTTPError, urllib.error.URLError) as error:
                #print('Data not retrieved because %s\nURL: %s', error, url)
                continue

            soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'),features="lxml") 
            for link in soup.find_all('a', href=True) :
               linkText = utility.normalizeText(link.text)   
               linkUrl = utility.normalizeLink(url, link['href']) 

               if len(linkText)>0 and len(linkUrl) >0 : 
                  item = (nextId,linkText,linkUrl) 
                  if (self.type == 'Worker') or \
                     (self.type == 'PrototypeWorker' and linkText == self.matchStr):
                      self.upQueue.put(item)
                  nextId +=1;   
            



    
class CrawlManager(threading.Thread):
    """ This is the Mgr thread that send down the links to worker threads and get the results from upQueue
        For the returned links if it has some similarity with matchStr, it will send it down to a dedicated 
        worker: PrototypeWorker for quick evaluation.
        It handles all the operations of database 
    """ 
    def __init__(self,startUrl,matchStr,numberofWorkers):
        super(CrawlManager,self).__init__()        

        self.startUrl = startUrl
        self.matchStr = matchStr
        self.tableName = TABLE_NAME

        self.upQueue = queue.Queue(maxsize=SIZE_UPQUEUE)
        self.downQueue = queue.Queue(maxsize=SIZE_DOWNQUEUE)
        self.workers = [CrawlWorker(self.downQueue,self.upQueue,matchStr,id = i) \
                        for i in range(numberofWorkers)]
        # Only 1 prototypeWorker
        self.upPriQueue = queue.Queue(maxsize=SIZE_UPQUEUE)
        self.downPriQueue = queue.Queue(maxsize=SIZE_DOWNQUEUE)        
        self.prototypeWorker = CrawlWorker(self.downPriQueue,self.upPriQueue,matchStr, \
                                           id = numberofWorkers,type = 'PrototypeWorker') 

    
    def setupDatabase(self):
        conn = utility.create_connection('Links.db' )  
        ret = False
        if conn is not None:
            self.conn = conn
            utility.drop_tables(conn)
            
            urlText = self.startUrl.split('/')[-1]
            item = (1, urlText, self.startUrl)
            table = self.tableName + '0'
            ret = utility.create_table(conn, table) and utility.create_url_table(conn) 
            if ret:
               utility.insert_link(conn, table, item)
               utility.insert_url(conn, self.startUrl)
        return ret 
            
    def wakeupWorkers(self):
        self.prototypeWorker.start()
        for worker in self.workers:
            worker.start()
            
    def joinWorkers(self):
        global stop_threads
        stop_threads= True
        self.workers.append(self.prototypeWorker) 
        while len(self.workers) > 0:         
            for worker in self.workers:
                worker.join(timeout=1)       
            self.dropUpQueue()
            self.workers = [ worker for work in self.workers if work.is_alive == True ] 

  
    def dropUpQueue(self):
        while not self.upQueue.empty():
            self.upQueue.get()
            
    def processUpQueue(self,table):
        ret=()
        while not self.upQueue.empty():
            item = self.upQueue.get()
            _, linkText,linkUrl = item

            if utility.insert_url(self.conn,linkUrl):
               utility.insert_link(self.conn,table,item)  
               if linkText == self.matchStr:  
                  ret = item  
                  break; 
               elif utility.get_jaccard_sim(linkText,self.matchStr) > 0.1:
                  print("send likely link down", item )
                  self.downPriQueue.put(item)
            else:
               ret = ()
                
        if not self.upPriQueue.empty():
           ret = self.upPriQueue.get()
           nextTable = self.tableName + str(int(table[-1])+1)
           utility.create_table(self.conn, nextTable) 
           utility.insert_link(self.conn,nextTable,ret)
           print(nextTable, ret)
            
        return ret;        
    
    def dispatch(self,level):
        table = self.tableName + str(level)
        nextTable = self.tableName + str(level+1)
        utility.create_table(self.conn, nextTable)
        
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM ' + table) 
        ret = ()
        for i,row in enumerate(cur):  
             while len(ret) == 0:
                if not self.downQueue.full():
                   row = utility.transformBack(row) 
                   self.downQueue.put(row)
                   break;       
                elif self.upQueue.empty():
                    time.sleep(1)
                else:    
                    ret=self.processUpQueue(nextTable)
                                    
        count = 0
        while len(ret)==0: 
            if count == 3: 
               break;
            elif self.upQueue.empty(): 
               if self.downQueue.empty(): 
                  time.sleep(5)   # all tasks sent down, wait for 5s
                  count += 1
               else:
                  time.sleep(1)   # tasks still in queue, wait for 1s   
            else:    
                ret=self.processUpQueue(nextTable)
                count = 0           
        return ret

    def run(self):
        if not self.setupDatabase():
           return
    
        self.wakeupWorkers()
        ret = ()    
        level=0
        
        while len(ret) == 0:
            ret = self.dispatch(level) 
            level += 1
            print(".....Level is : %d....." % level)
           
            if level == MAX_LAYERS :
                print("reach to the maximum level: %d" % level)
                break;
                
        if len(ret) > 0:
            paths = crawlerMgr.findPaths(ret[0]) 
            spath=' '
            for i, path in enumerate(paths):
                spath = path if i == 0 else spath + " -> " +  path 
            print(spath)            
            self.joinWorkers()

            self.conn.close()
           
 

    def findPaths(self,id):
        """  Find the path baesd on id, where id is structured as:
             id_layer0 << (numberOfLayers) | id_layer1 << (numberOfLayers -1) | id_layer2
        """     
        stack = []
        while  id >0 :
            newId = id & 0xffff
            stack.append(newId)
            id = id >> 16
       
        lastId = 0    
        paths = []

        for i,id in enumerate(stack[::-1]):
            id = (lastId << 16) + id
            table = self.tableName + str(i)
            _,name,_=utility.select_link_by_id(self.conn,table,id)
            paths.append(name)
            lastId = id
        return paths


        
if __name__ == '__main__':  
    start_time = time.time()

    parser = argparse.ArgumentParser( description = "Find the shortest distance between two Wikipedia pages  only using other Wikipedia pages links; restricted to English Wikipedia pages. Note that page titles for wikipedia pages are case-sensitivei, and also that in general the shortest path is not unique.",
    epilog =  "For example: python wikipedia_game.py \"Binary tree\" \"History\"" )
    parser.add_argument( 'start_wiki', type = str, help = "Wikipedia page title where the search starts."  )
    parser.add_argument( 'destination_wiki', metavar = 'destination_wiki', type = str, help = "Wikipedia page title where the search ends."   )
    res    = parser.parse_args() 

    start  = res.start_wiki
    matchStr = res.destination_wiki.strip().lower()
    startUrl  = "https://en.wikipedia.org/wiki/" + "_".join( start.split(" "))

    crawlerMgr = CrawlManager(startUrl,matchStr,5)
    crawlerMgr.start()
    crawlerMgr.join()
    
    print("--- %s seconds ---" % (time.time() - start_time))
