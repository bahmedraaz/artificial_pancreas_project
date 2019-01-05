import os
import os.path
import numpy as np
import time
from sys import argv

def inject_fault(fileName):
	in_file = fileName+'.txt'
	sceneLine  = fileName.split('_')
	#sceneNum = sceneLine[len(sceneLine)-1]
	sceneNum = int(sceneLine[2])
	sceneNum_str = str(sceneNum)
	# if os.path.isfile("updated_ct_script_iob_based_backup.py") != True:
		# cmd = 'cp '+'updated_ct_script_iob_based.py'+' updated_ct_script_iob_based_backup.py'
		# os.system(cmd)

	# faultObj = open(in_file, 'r')
	# sourceObj = open("updated_ct_script_iob_based.py", 'r')
	# destObj = open("updated_ct_script_iob_based_backup.py", 'w')
	need_indent = 0
	name_end = 0

	name_id = []
	fileNames = os.listdir("./result")
	#rint("Num of Line",len(fileNames))
	if len(fileNames) == 0:
		name_end = 0
	else:
		for name in fileNames:
			name_id.append(int(((name.split('_')[1])).split('.')[0]))
		name_end = max(name_id)


	faultObj = open(in_file, 'r')
	for line in faultObj:
		if os.path.isfile("updated_ct_script_iob_based_backup.py") != True:
			cmd = 'cp '+'updated_ct_script_iob_based.py'+' updated_ct_script_iob_based_backup.py'
			os.system(cmd)
	
		sourceObj = open("updated_ct_script_iob_based.py", 'r')
		destObj = open("updated_ct_script_iob_based_backup.py", 'w')
		
		if "fault" in line:	
			name_end = name_end+1
			name_end_str = str(name_end)

			line = line.split('//')
			del line[0]
			#print("fileName.split ",fileName.split("_"))
			print("sceneNum: ",sceneNum)
			print("sceneLen: ", len(sceneLine))

			for source_line in sourceObj:
				destObj.write(source_line)
				if ("glucose:HOOK" in source_line) and ((sceneNum is 1) or (sceneNum is 2)):
					destObj.write("	"+line[0]+"\n")
					destObj.write("		"+line[1])				
				elif "temp_basal:HOOK" in source_line and ((sceneNum is 3) or (sceneNum is 4)):
					destObj.write("	"+line[0]+"\n")
					destObj.write("		"+line[1])
				elif "rate:HOOK" in source_line and ((sceneNum is 5) or (sceneNum is 6)):
					destObj.write("	"+line[0]+"\n")
					destObj.write("		"+line[1])

			cmd = 'python '+ 'updated_ct_script_iob_based_backup.py'
			os.system(cmd)
			cmd = '> '+'data.csv'
			os.system(cmd)
			cmd = 'python '+'updated_collected.py'
			os.system(cmd)
			cmd = 'cp '+'data.csv'+' ./result/data_%s.csv'%name_end_str
			os.system(cmd)	
	

if len(argv)>1:
	inject_fault(argv[1])
#else:
#	print("Fault library filename is missing, pass the filename as argument")

#print '\n\n Total runtime: %f seconds' % (time.time()-start)
