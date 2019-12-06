#!/usr/bin/python
# -*- coding: UTF-8 -*-
import subprocess
import sys
from collections import OrderedDict

#Example of a input 
#  xcommon = 361
#  xenrich = 513
#  xagg-libs-2.0 = 292
#  stringencoders = 380
#  xcp      = 380
#  xup      = 292
#  xagg-2.0  = 292


version = {} 

# component tracks the name of component and the number of rpms to be installed 
components = OrderedDict()
components["napatech3-xprobe"] = "1"
components["xmlconfigparser"] = "1"
components["xcommon"] = "1"
components["xenrich"] = "1"
components["xagg-libs-2.4"] = "1"
components["stringencoders"] = "1"
components["xpi"] = "2"
components["xcp"] = "2"
components["feedpostprocess"] = "2"
#components["xagg-2.1"] = "1"
#components["xup"]= "1"

def checkOutput(cmd):
    print "running cmd ....: " + cmd    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if stderr != '':
       print stderr
    return stdout.strip() 



if __name__ == '__main__':

    
    if len(sys.argv) == 2:
       filename= sys.argv[1]

    else:
       sys.stderr.write("usage: " + sys.argv[0] + " <file>\n")
       sys.exit(1)

    NUM = len(components)

    #Read in the component version from input file
    with open(filename,'r') as fh:
         line = fh.readline()
         while line:
	    line = line.strip()
            
            i = 0
            for component in components.keys():
	        i += 1	
		if component in line: 
		   version[component] = line.split('=')[-1].strip()
                   break;
                
		if i == NUM :
		   print "unknown components: " + line
                   sys.exit(1)
	    line = fh.readline()
         fh.close()


    #remove all rpms
    removedComponents = components.keys()[::-1]

    for component in removedComponents:

        cmd = "rpm -qa | grep " + component
        ver = checkOutput(cmd)
        if ver != '':
           vers = ver.split('\n')
           if components[component] == "1": 
              #if component == "xcommon" and len(vers) == 1:   # If there is only one xcommon there, don't remove it as it's required by xpi
              #   continue

              cmd = "rpm -e " + vers[0]
              checkOutput(cmd)
           elif components[component] == "2":
	        if len(vers) == 2 :   
	  	   if "ena" in vers[1]:
		      ena = vers[1]
                      run = vers[0]
		   elif "ena" in vers[0]:
		      ena = vers[0]
                      run = vers[1]
                 
                   cmd = "rpm -e " + ena
                   checkOutput(cmd)
                   cmd = "rpm -e " + run
                   checkOutput(cmd)
	        else:
                   print "componen: " + component + " has more than 2 rpms"
                   sys.exit(1)
    					
    # install all new rpms

    for component in components.keys():
        #check if the current directoy has the version specified

        cmd = "ls *rpm | grep " + component + " | grep " + version[component] + " | wc -l "
        num = checkOutput(cmd)
        if ( num != components[component] ):
            print component + "only have: " + num + " rpms"
            sys.exit(1)


        cmd = "ls *rpm | grep " + component + " | grep " + version[component] 

        ver = checkOutput(cmd)
        vers = ver.split('\n')
        if components[component] == "1":
	   cmd = "rpm -ivh " + vers[0] + "  --force"
           checkOutput(cmd)
        elif components[component] == "2":
            if "ena" in vers[1]:
               ena = vers[1]
               run = vers[0]
            elif "ena" in vers[0]:
               ena = vers[0]
               run = vers[1]

               cmd = "rpm -ivh " + run + " --force"
               checkOutput(cmd)
               cmd = "rpm -ivh " + ena + " --force"
               checkOutput(cmd)

   #remove 'nqc' and 'lz-xfer-xagg" from component.xml
    cmd = " sed -e '/nqc/,+4d' < /xsight/etc/opt/xps/components.xml > /xsight/etc/opt/xps/1.txt"
    checkOutput(cmd) 
    cmd = " sed -e '/lz-xfer-xagg/,+4d' < /xsight/etc/opt/xps/1.txt > /xsight/etc/opt/xps/components.xml" 
    checkOutput(cmd)
  
    cmd = "xs-agent stop; xs-agent start"
    checkOutput(cmd)

  #restart everything
  #  cmd = "xs stop; xs start"
  #  checkOutput(cmd)
 
    
