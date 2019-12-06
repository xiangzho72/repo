#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import sys
from dateutil import parser
from datetime import datetime
from datetime import timedelta

# Category to collect data 
#categories = ["S1MME", "GTPv1", "GTPv2", "Diameter", "SBcAP", "Dns", "Lcsap", "SGsAP","Iu","Gb","Sip"]
categories = ["S1MME", "GTPv2"]
modulecategories = [ "stats.CCaptureModule", "stats.CXpiPublisherModule" ]

numOfPointsFor24Hrs = 60*24
numOfPointsForOneLoop = 60*6   # 6 hrs
threshold = 0.02    

thresholdMem = 5000  # 5M bytes
searchRange = 2   # 2 mins


#-----------------------------------------
#  Iterate through obj hierarchy to find out key hierarchy
#  Only get one leg at one time
#  Input:  obj:  a dict 
#  Output: key for one leg  
#          None if all keys has been generated
#-----------------------------------------
def iterKey(obj):

    if False  == isinstance(obj, dict): 
       print "ERROR:  obj is not a dict"

    keys = obj.keys()
    for key in keys:
        value = obj[key]
        if True == isinstance(value,dict):
           tmp = iterKey(value)
           if None != tmp:
              return key + "/" + tmp
           else:
              continue
        else:
           if "MARKED" != value:
              obj[key] = "MARKED"
              return key
           else: 
              continue

    #If we get here, all keys has been iterated
    return None


#-----------------------------------------------
#  check if given obj belongs to the category
#  Output:  True/False
#---------------------------------------------
def isObjInCategory(categoryToLookup,obj):

    # Get the key/value
    value = categoryToLookup.values()[0]
    key = categoryToLookup.keys()[0]

    valueInObj = findKey(obj, key)

    if ( None != valueInObj and value == str(valueInObj) ):
         return True
    else: 
         return False

#------------------------------------------
#  Use 1st obj which belongs to the required category to discover all the keys
#  Output:  a list with all the discovered keys
#----------------------------------------------
def genItemToLookups(categoryToLookup,objs):
    
    if ( len(categoryToLookup) > 1 ): 
         sys.stderr.write("Only one category supported to collect data at one time")
         sys.exit(1) 

    # Get the 1st object matching with key/value
    for obj in objs: 
        if ( True == isObjInCategory(categoryToLookup,obj) ):
             break;

    #go down to the required level of hirerchary 
    keyList = categoryToLookup.keys()[0].split("/")[0:-1]
    keyStr = '/'.join(keyList)
    target = findKey(obj, keyStr)


    #generate itemToLookups from that object 
    key = iterKey(target)    

    itemToLookups=[] 
    while (  None != key  ):
       itemToLookups.append(keyStr + '/' + key)
       key = iterKey(target)

    return itemToLookups

            




#--------------------------------------------------------------
#reformat file into file.json so that it can be parsed by python
# input: file with the same format as  xcp.probed_status.log
# output: json objs for all the items in the file
#-------------------------------------------------------------
def reformat(filename):

    fileJson = filename + ".json"

    # reformat status_log to a standard jason file
    #  Add "[ " at the 1st line
    #  Add "]" at the end of file
    #  Add "," at the end of each line
    with open(filename, 'r') as fp:

       with open(fileJson, 'w') as fpJson:

            line = fp.readline().strip()

            line = "[" + line
            while line:

               nextLine = fp.readline()
               if ( nextLine ):
                  line = line + "," + "\n"
               else:
                  line = line + "]"

               fpJson.write(line)
               line = nextLine.strip()


    with open(fileJson, 'r') as fpJson:
         objs = json.load(fpJson)

    return objs

#-----------------------------------------------------
# check if a dic has a key, if it is, return the value, 
# otherwise return None
# input :  item: a dict object
#          key:  key to look in the dict obj
#----------------------------------------------------
def hasKey(item,key):
 
    if item.has_key(key):
       return item[key]
    else:
       return None
   
#----------------------------------------------- 
# use the key to go through json obj to find
# if found, return value for the key
# otherwise return None
# input:  obj:  a dict obj with multi layer hierarchy
#         key:  a key with multi layer hierarchy   
# Output:  None: if no such key founded in the obj
#          or return obj found        
#--------------------------------------------------
def findKey(obj, key):
        
    keyItems = key.split('/')

    target = obj
    isFound = True

    for key in keyItems:
        target =  hasKey(target, key)
        if ( None == target ):
             isFound = False
             break
   
    if isFound == True:
       return target
    else:
       return None 


#----------------------------------------------
# This like new in C++ 
#---------------------------------------------
def allocateFinding(currentTime, index):

    finding=[]

    finding.append(currentTime)
    for i in range(index): 
        finding.append("")

    return finding

#-----------------------------------------------
# use itemToLookup to look up all objs
# input : objs : all json objs in the file
#         itemToLookup : all keys
#         categoryToLookup: to only collect data from obj in the required category 
# output: a list with  all matches  
#----------------------------------------------
def parse(objs,itemToLookups,categoryToLookup):
    
    findings=[]
    isInited = False

    global finding 

    for obj in objs:
        if isObjInCategory(categoryToLookup,obj) == False: 
           continue

        currentTime = obj["date"].split('.')[0]
        # when time changes,  publish finding and reinitiate it: 
        if ( False == isInited ):

             finding = allocateFinding(currentTime,len(itemToLookups)) 
             isInited = True  

        elif (  currentTime != finding[0] ):

             findings.append(finding)
             finding = allocateFinding(currentTime, len(itemToLookups))
             # For DEBUG purpse :  to check if everything populated is correct 
             #if len(findings) <= 3:
             #   print findings

        
        i=1
        for item in itemToLookups: 
            
            value = str(findKey(obj,item))
            if ( "None" != value ):
                 finding[i] = value
            i+=1
    #For the final 'finding', we have to push it into 'findings' ourselves. 
    findings.append(finding)
    return findings
 

#----------------------------------------------------------
# This will output findings into a file, along with the head 
#-----------------------------------------------------------
def output(filename, itemToLookups, findings):
    
    outputFile = filename + ".out"

    with open(outputFile, 'w') as fp:

         #print header
         outStr = "date" +  "  ,  "
         for items in itemToLookups:
             outStr = outStr + items + " ,   "
         outStr = outStr + '\n'
         fp.write(outStr)

         #print content             
         for finding in findings:
             outStr =""
             for item in finding: 
                 outStr = outStr + item + " ,   "
             outStr += "\n"

             fp.write(outStr)

#-------------------------------------------------------
# This is to check if a string is a number(float)
#-------------------------------------------------------
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


#----------------------------------------------------------------------------
# This will find the max in the 1st 24 hours value as the baseline value, 
# then find the max in each segments and compare with baseline, 
# If it's larger than baseline, then record the index
#
# Input:  aList:  a list of element (number)
# Output: results:  a list of the index which points out the maximum 
#----------------------------------------------------------------------------
def findMax(aList):


    results = []

    # set up baseline  from the 1st 24 hrs data
    maximum = max(aList[ 0 : numOfPointsFor24Hrs ])    
    maxIndex = aList[ 0 : numOfPointsFor24Hrs].index(maximum)
    results.append(maxIndex)
    baseMax = float(maximum) * (1+threshold)

    numOfSegs = int( (len(aList) - numOfPointsFor24Hrs)/numOfPointsForOneLoop) + 1 
   
    #print "numOfSegs : " + str(numOfSegs) 

    for  i in range (0,numOfSegs):
         startIndex = i*numOfPointsForOneLoop + numOfPointsFor24Hrs
         endIndex = (i+1)*numOfPointsForOneLoop-1 + numOfPointsFor24Hrs

         maximum =  max(aList[startIndex: endIndex])
         maxIndex = aList[startIndex:endIndex].index(maximum) + startIndex
         #print "[" + str(startIndex) + " : " + str( endIndex) + "]" + ": max : " + str(maximum) + ",maxIndex: " + str(maxIndex)         
 
         if maximum > baseMax:
            #print "    Appended : "  
            results.append((maxIndex))
   
    return results     

#--------------------------------------------------------------------------
# This will output 'suspicious' container in the findings: 
# Input:  filename:  
#         itemToLookups:  a list of itemToLookup (which will be used to print header)
#         findings:       a list of finding for every data point(i.e. every min), and finding is a list of data of measurement
#         times:          a list of timeing when the 'footstep' in the mem tread occurs
# Output: Wrtie 'suspicious' container into filename.summary
#------------------------------------------------------------------------
def outputSummary(filename, itemToLookups, findings, times):


    outputFile = filename + ".summary"

    with open(outputFile, 'w') as fp:

         i=1
         for items in itemToLookups:
             
             # skip the un-numbers
             if False == is_number(findings[0][i]):
                i+=1
                continue

             # produce the list
             aList=[]
             for finding in findings:
                 aList.append(float(finding[i]))
             
             # Find the maximums in the list    
             results = findMax(aList)

             # Only print the one which has more than one item, which is baseline 
             if len(results) > 1:

                isHeadPrinted = False 

                for result in results:
                    dtResult = parser.parse(findings[result][0])
                    isInTimeRange = False
  
                    for time in times: 
                        timeDt = parser.parse(time)  # convert string to datetime format
                        timeDtMin = timeDt - timedelta(minutes=searchRange)
                        timeDtMax = timeDt + timedelta(minutes=searchRange) 

                        if withinTimeRange(dtResult, timeDtMin, timeDtMax) == True: 
                           isInTimeRange = True
                           break  
                    
                    if isInTimeRange == False: 
                       continue;
     
                    if isHeadPrinted == False:
                       fp.write("\n\n")
                       fp.write("summary for " + items + "\n")
                       isHeadPrinted = True

                    #Only print the one which is in the timeranges
                    outStr = "   " + findings[result][0]   +  "     "  + findings[result][i] + "\n"
                    fp.write(outStr)

             i+=1;


#--------------------------------------------------
# This will parse the xcp_memcheck.log 
# it will skip 1st 24 hrs data, 
# and then find out the time when delta of memeory is above threahold
# Input:  filename:  it's the name of xcp_memcheck.log
#         threahold :  it's the size of memory (unit: KB)
# Output: a list of time of 'footstep' point in the memlog
#----------------------------------------------------
def parseMemLog(filename,threahold):


    isInited = False
    results = []
    with open(filename, 'r') as fp:

         line = fp.readline().strip()
         i = 0
         while line:
           # skip 1st 24 hrs data
           if  i < numOfPointsFor24Hrs: 
               line = fp.readline().strip()
               i+=1
               continue



           time = line.split(',')[0]
           memory = line.split('-')[-1]
           memoryInt = int(memory.split('K')[0])
         
           if False == isInited: 
              lastMemInt = memoryInt
              isInited = True

           Delta = memoryInt - lastMemInt

 
           if memoryInt - lastMemInt > threahold: 
              results.append(time) 

           lastMemInt = memoryInt
         
           line = fp.readline().strip()

    return results   



#-----------------------------------------------------
# Input:  dt:  the datetime
#         rangeMin:  the datatime of low end of range
#         rangeMax:  the datatime of high end of range
# Output: True if it's in the range 
#----------------------------------------------------
def withinTimeRange(dt, rangeMin, rangeMax):
    return dt > rangeMin and dt < rangeMax 


                 
#---------------------------------------------------------

if __name__ == '__main__':


    times = []
    filenameLog=""
    if len(sys.argv) == 2:
       filename= sys.argv[1]
    elif len(sys.argv) == 3:
       filename = sys.argv[1]
       filenameLog =  sys.argv[2]
       times = parseMemLog(filenameLog, thresholdMem)
       print "The timing of footstep point: " + str(times)

    else:
       sys.stderr.write("usage: " + sys.argv[0] + " <xcp.probed_stats.log>   <xcp_memcheck.log>\n")
       sys.exit(1)

    objs = reformat(filename)

    categoryToLookup={}
    for category in categories:

        print " Analyzing data for : " + category
        categoryToLookup["xcp/measurements/pipeline_name"] = category
 
        itemToLookups = genItemToLookups(categoryToLookup,objs)
   
        findings = parse(objs,itemToLookups,categoryToLookup)
    
        categoryFile = filename + "." + category
        print "   Generating file ... "

        output(categoryFile, itemToLookups, findings)

        if len(findings) > (numOfPointsForOneLoop + numOfPointsFor24Hrs) and len(filenameLog) > 0 :  
           outputSummary(categoryFile, itemToLookups, findings, times)


    categoryToLookup={}       
    for category in modulecategories:

        print " Analyzing data for : " + category
        categoryToLookup["xcp/module"] = category
 
        itemToLookups = genItemToLookups(categoryToLookup,objs)
   
        findings = parse(objs,itemToLookups,categoryToLookup)
    
        categoryFile = filename + "." + category
        print "   Generating file ... "

        output(categoryFile, itemToLookups, findings)           
    
