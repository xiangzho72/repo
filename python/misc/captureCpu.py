#!/usr/bin/python
# -*- coding: UTF-8 -*-
import subprocess
import sys
import csv
import time

threadPositiveFilter = ["S1MME", "Gtp"]
cmdFilterOutUnrequiredLins = " | grep -v Average | grep -v xcp.probed | grep -v civetweb | grep -v Command | grep -v HbCfgEvent0 | grep -v ClntReqDispatch | grep -v _x86_64_ | grep -v -e '^[[:space:]]*$'"

def checkOutput(cmd):
    #print "running cmd ....: " + cmd
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if stderr != '':
       print stderr
    return stdout.strip()


#return a list which has the cpu usage for threads in threadDict{id:name}
def captureThread( cmdGetThreadsCpu, threadDict ):

    retOfcmdGetThreadsCpu = checkOutput(cmdGetThreadsCpu)
    
    threadCpus = { id:cpu for _, id, cpu, _ in ( map(str, line.split()) for line in retOfcmdGetThreadsCpu.splitlines())}
    retThreadCpus = [] 
    retThreadCpus.append( retOfcmdGetThreadsCpu.splitlines()[0].split()[0] )  #Get the timestamp from 1st line 1st field
    
    for key in threadCpus: 
        retThreadCpus.append(threadCpus[key])
   
    return retThreadCpus
    


if __name__ == '__main__':
    if len(sys.argv) == 2:
       logFile= sys.argv[1]
    else:
       sys.stderr.write("usage: " + sys.argv[0] + " <logFile>\n")
       sys.exit(1)


    
    xcpProcessId = checkOutput("top -b -n 1 | grep xcp.probed | awk '{print $1}'")
    
    # index 1 is the time,5th is the tid, 9th is the cpu, 11th is the threadName
    cmdGetThreadsName = "pidstat -p " + xcpProcessId + " -t 1 1 " + cmdFilterOutUnrequiredLins  + "| awk '{print $1,$5 , $9, $11}' "
    
    #Apply filters if any
    if len(threadPositiveFilter) > 0 :
        cmdGetThreadsName += " | grep -i  "
        for filter in threadPositiveFilter:  
            cmdGetThreadsName += " -e " + filter

    retOfcmdGetThreadsName = checkOutput(cmdGetThreadsName)
    
    threadDict = {id: name[3:] for _, id, _ , name in (map(str, line.split()) for line in retOfcmdGetThreadsName.splitlines())}
    print (threadDict)
    
    with open(logFile,'w') as handle:
        writer = csv.writer(handle)
        
        indexes = ["date"] + [ name for id, name in threadDict.items()]
        
        writer.writerow(indexes)

        while True:        
            threadCpus = captureThread(cmdGetThreadsName, threadDict)

            writer.writerow(threadCpus)
            handle.flush()
            time.sleep(1)
    
    #
         

    