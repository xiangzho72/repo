### 
### This will check if there are smart*csv in the directory /xsight/var/opt/xagg/tmp
### If there is such one,  it will get start_time, end_time, and duration of each row
### For each row,  if dur == 0 && start_time != end_time,  print it out
### use glob.glob() to search for wildcard files


import csv
import os
import glob
import time
directory = '/xsight/var/opt/xagg/tmp'
file_searched = os.path.join(directory, 'smart*csv')
prev_file = ""
while True:
        filenames = glob.glob( file_searched);
        if len(filenames) >0 :
            for filename in filter(lambda x: x!=prev_file,filenames):
		with open( filename) as csvfile:
                     readCSV = csv.reader(csvfile, delimiter=',')
                     for i,row in enumerate(readCSV):
                     if i == 0:
                        try:
                            start_index = row.index("start_time")
                        except:
                            print(" file :%s doesn't have start_time column" % filename)
                         continue;

                        end_index, dur_index = start_index + 1, start_index +2
                        print("filename as : %s" % filename)
                        continue

                     # get the start, end, dur of each row
                     # start with format : 2019-10-03 16:48:08.268731
                     start = row[start_index]
                     try :
                       start_ms = int(start.split(' ')[1].split('.')[1])
                     except IndexError:
                       print("start_time as %s" %start)
                       continue

                     end = row[end_index]
                     try:
                       end_ms = int(end.split(' ')[1].split('.')[1])
                     except IndexError:
                       print("end as :%s", end)
                       continue

                     dur = row[dur_index]

                     if ( dur == "0" and start != end and start_ms +1 !=  end_ms ):
                         print(row[start_index],row[end_index],row[dur_index])
                     prev_file = filename
        else:
            time.sleep(2)

