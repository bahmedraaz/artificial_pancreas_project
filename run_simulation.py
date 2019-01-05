import json
import datetime
from subprocess import call
#from datetime import datetime,timedelta
import time
import os
from matplotlib import pyplot as plt
import random

fault_injected = 0

openaps_rate = []
wrapper_rate = []
running_temp = []

track_increase = {"iteration": 0, "num_of_increase":0}
track_decrease = {"iteration": 0, "num_of_decrease":0}

gt_target_visit_stat = 0
lt_target_rising_visit_stat = 0
lt_target_falling_visit_stat = 0
init_iob_pointer = 0

unsafe_action_occurance = 0

#Input to the algo_bw.js. algo_bw.js format all the info and send to glucosym server. An algorithm is running in glucosym server that calculated next glucose and send the value back.
algo_input_list = {"index":0,"BGTarget":95,"sens":45,"deltat_v":20,"dia":4,"dt":5.0,"time":6000,"bioavail":6.0,"Vg":253.0,"IRss":1.3,"events":{"bolus":[{ "amt": 0.0, "start":0}],"basal":[{ "amt":0, "start":0,"length":0}],"carb":[{"amt":0.0,"start":0,"length":0},{"amt":0.0,"start":0,"length":0}]}}

#write the algo_input_list to a file named algo_input.json so that algo_bw.js can read the input from that file
with open("../glucosym/closed_loop_algorithm_samples/algo_input.json", "w") as write_algo_input_init:
	json.dump(algo_input_list, write_algo_input_init, indent=4)
	write_algo_input_init.close()


suggested_data_to_dump = {}
list_suggested_data_to_dump = []

iteration_num = 200

#record the time 5 minutes ago, we need this time to attach with the recent glucose value
#time_5_minutes_back = ((time.time())*1000)-3000


for _ in range(iteration_num):

	fault_prob = random.randint(1,100)
	
	with open("../glucosym/closed_loop_algorithm_samples/algo_input.json") as update_algo_input:
		loaded_algo_input = json.load(update_algo_input)
		update_algo_input.close()
		
	loaded_algo_input_copy = loaded_algo_input.copy()
	loaded_algo_input_copy['index'] = _
	
	#print(loaded_algo_input_copy)
	
	with open("monitor/glucose.json") as f:
		data = json.load(f)
	
	
	data_to_prepend = data[0].copy()

	
	read_glucose_from_glucosym = open("../glucosym/closed_loop_algorithm_samples/glucose_output_algo_bw.txt", "r")
	loaded_glucose = read_glucose_from_glucosym.read()


	data_to_prepend["glucose"] = loaded_glucose 

## Fault_injection ############# permanent hardware fault injection #################################	
	#if _ > 10:	 
	#	data_to_prepend["glucose"] = 80

################### End of permanent fault section #################

## Fault_injection ############## This section is for injecting intermittent fault with some probability #############
#	fault_prob = random.randint(1,100)
#
#	if fault_prob <=90:
#		data_to_prepend["glucose"] = random.randint(1,300)
#		fault_injected = fault_injected+1
#	else:
#		data_to_prepend["glucose"] = loaded_glucose

############### End of intermittend fault injection section ##########################

		
	data_to_prepend["date"] = int(time.time())*1000

	#glucose:HOOK#
	#if _>10:
	#	glucose = 80
	
	data.insert(0, data_to_prepend)
	

	with open('monitor/glucose.json', 'w') as outfile:
		json.dump(data, outfile, indent=4)
		outfile.close()
	

	call("date -Ins -s $(date -Ins -d '+5 minute')", shell=True)
		
	
	#current_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S-07:00') ## Original
	current_timestamp = datetime.datetime.fromtimestamp(time.time()+4*60*60).strftime('%Y-%m-%dT%H:%M:%S-07:00') ## After time change

	with open('monitor/clock.json','w') as update_clock:
		json.dump(current_timestamp, update_clock)

	
	
	call(["openaps", "report", "invoke", "settings/profile.json"])
	call(["openaps", "report", "invoke", "monitor/iob.json"])
	
        #run openaps to get suggested tempbasal
	
	call(["openaps", "report", "invoke", "enact/suggested.json"])
	
#	current_timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%S-07:00')
	
	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggest	    ed data and dump make a list lf that and then dump it to all_suggested.json file		
	with open("enact/suggested.json") as read_suggested:
		loaded_suggested_data = json.load(read_suggested)
		#list_suggested_data_to_dump.insert(0,loaded_suggested_data)
		#list_suggested_data_to_dump.append(loaded_suggested_data)
		read_suggested.close()

	loaded_suggested_data["loaded_glucose"] = loaded_glucose
	
	## Fault_injection : Injection of fault in Controller output ######################
	## rate:HOOK##

	#loaded_suggested_data["rate"] = random.randint(0,5) # Activate for faulty system. For non_faulty system, comment this out 

#################################### Context table check #################################################################

	bg_target = 65
	
	if "IOB" in loaded_suggested_data:
		iob = loaded_suggested_data["IOB"]

	glucose = float(loaded_glucose)
		
	
	with open("monitor/temp_basal.json") as read_temp_basal:
		loaded_temp_basal = json.load(read_temp_basal)
		running_temp_rate = loaded_temp_basal ["rate"]

	loaded_suggested_data["running_temp"] = running_temp_rate

	#running_temp_rate = loaded_suggested_data["running_temp"]["rate"]
	
	basal = loaded_suggested_data["basal"]
	
	if _ == 0:
		prev_glucose = glucose
	
	bg = loaded_suggested_data["bg"]	

	if glucose < 39:
		init_iob_pointer = 0
	else:
		init_iob_pointer = init_iob_pointer + 1

	if _ == 0 and glucose >= 39:
		prev_iob = iob
	
	elif init_iob_pointer == 1:
		prev_iob = iob

	if _ == 0:
		prev_rate = loaded_suggested_data["rate"]
	#del_rate = loaded_suggested_data["rate"] - running_temp_rate
	del_rate = loaded_suggested_data["rate"] - prev_rate
	del_bg = glucose - prev_glucose
	del_iob = iob - prev_iob
	
	################# Context table 9th row (bg<70), zero_insulin must be delivered ########################
	
	if glucose >=39 and glucose < 75:
		if loaded_suggested_data["rate"] == 0:
			print("\n Safe_Action\n")
		else:
			loaded_suggested_data["fault"] = "yes"
			loaded_suggested_data["fault_reason"] = "row_38"	
			print("\n***************************************")
			print("********** Unsafe Action !!!!! *************")
			print("Reason: 39 =< glucose <=75; recommended rate is not zero")  	
			print("***************************************\n")
			unsafe_action_occurance += 1

	######################################## End of 9th row ######################################################################
	

####### Context table first and second row (bg>target and rising , iob is falling and stable)  ########################

	elif glucose >= 75:
		#recommended_change_rate = loaded_suggested_data["rate"] - running_temp_rate

		
		if glucose > bg_target and loaded_suggested_data["rate"]==0:
					
			loaded_suggested_data["fault"] = "yes"
			loaded_suggested_data["fault_reason"] = "row_37" 
			print("\n***************************************")
			print("********** Unsafe Action !!!!! *************")  	
			print("Reason: glucose > target and zero insulin is provided")
			print("***************************************\n")
			unsafe_action_occurance += 1

		elif glucose > bg_target and del_bg > 0: ## glucose is above target and rising

			if del_iob < 0 or del_iob == 0: ## checking if iob is falling or stable
				if del_rate < 0:
					
					if (del_iob)<0:
						
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_2"
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose>target and rising; iob is falling; rate should not be decreased")
						print("***************************************\n")
						unsafe_action_occurance += 1
					elif (del_iob) == 0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_3" 
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose>target and rising; iob is stable; rate should not be decreased")
						print("***************************************\n")
						unsafe_action_occurance += 1
	
				else:
					print("\nSafe Action\n")

	################################################# End of first and second row of the context table ################################

	################## Context table 3rd and 4th row (bg>target and stable, iob is falling and stable)################################

		elif glucose > bg_target and (del_bg)==0:

			if (del_iob) < 0 or (del_iob)==0:
				if del_rate < 0:
					
					if (del_iob)<0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_8"
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose>target and stable; iob is falling; rate should not be decreased")
						print("***************************************\n")
						unsafe_action_occurance += 1
					elif (del_iob) ==0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_9" 
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose>target and stable; iob is stable; rate should not be decreased")
						print("***************************************\n")
						unsafe_action_occurance += 1

				else:
					print("\nSafe Action\n")

	########################################### End of 3rd and 4th row ##############################################################

########################## Row 1, 4, 5, 6, 7 ; in this context, we are not sure about the unsafe control action, however we assume that providing corresponding control action will be hazardouws###

		elif glucose > bg_target and (del_bg)>0:

			if (del_iob) > 0:
				if del_rate < 0:
					
					loaded_suggested_data["fault"] = "yes"
					loaded_suggested_data["fault_reason"] = "row_1" 
					print("\n***************************************")
					print("********** Unsafe Action !!!!! *************")  	
					print("Reason: glucose>target and rising; iob is rising; rate should not be decreased")
					print("***************************************\n")
					unsafe_action_occurance += 1

				else:
					print("\nSafe Action\n")


		elif glucose > bg_target and (del_bg)<0:

			if (del_iob) > 0 or (del_iob < 0) or (del_iob)==0:
				if del_rate < 0:
					
					if (del_iob) == 0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_6"
					#elif (del_iob) < 0:
					#	loaded_suggested_data["fault_reason"] = "row_5" 
					#elif (del_iob) > 0:
					#	loaded_suggested_data["fault_reason"] = "row_4"

						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose<target and falling; iob is rising or stable; rate should not be increased")
						print("***************************************\n")
						unsafe_action_occurance += 1
				
	

############################## End of Row 1, 4, 5, 6, 7 ######################################### 

	################## Context table 5th and 6th row (bg<target and falling, iob is rising and stable)################################

		elif glucose < bg_target and (del_bg)<0:

			if (del_iob) > 0 or (del_iob)==0:
				if del_rate > 0:
					
					if (del_iob)>0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_31"
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose<target and falling; iob is rising; rate should not be increased")
						print("***************************************\n")
						unsafe_action_occurance += 1
					elif (del_iob) == 0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_33" 
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: glucose<target and falling; iob is stable; rate should not be increased")
						print("***************************************\n")
						unsafe_action_occurance += 1
					
				else:
					print("\nSafe Action\n")

		
	########################################### End of 5th and 6th row ##############################################################

	################## Context table 7th row (bg<target and stable, iob is rising)################################

		elif glucose < bg_target and (del_bg)==0:

			if (del_iob) > 0:
				if del_rate > 0:
					
					loaded_suggested_data["fault"] = "yes"
					loaded_suggested_data["fault_reason"] = "row_34" 
					print("\n***************************************")
					print("********** Unsafe Action !!!!! *************")  	
					print("Reason: glucose<target and stable; iob is rising; rate should not be increased")
					print("***************************************\n")
					unsafe_action_occurance += 1
					
				else:
					print("\nSafe Action\n")


	########################################### End of 7th row ##############################################################

######################### Row 28, 29, 30, 32, 35, 36; We are not sure about these rows, however we assumeed that delivering corresponding contol_action will cause hazard ################

		elif glucose < bg_target and (del_bg)>0:

			if (del_iob) > 0 or (del_iob<0) or (del_iob)==0:
				if del_rate > 0:
					
					if (del_iob)>0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_28"
						
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: ", loaded_suggested_data["fault_reason"])
						print("***************************************\n")
						unsafe_action_occurance += 1
						
					elif (del_iob) == 0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_30"
					#elif (del_iob<0):
					#	loaded_suggested_data["fault_reason"] = "row_29" 
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: ", loaded_suggested_data["fault_reason"])
						print("***************************************\n")
						unsafe_action_occurance += 1
				
		elif glucose < bg_target and (del_bg)<0:

			if (del_iob<0):
				if del_rate > 0:
					
					loaded_suggested_data["fault"] = "yes"
					loaded_suggested_data["fault_reason"] = "row_32" 
					print("\n***************************************")
					print("********** Unsafe Action !!!!! *************")  	
					print("Reason: ", loaded_suggested_data["fault_reason"])
					print("***************************************\n")
					unsafe_action_occurance += 1


		elif glucose < bg_target and (del_bg)==0:

			if (del_iob<0) or (del_iob)==0:
				if del_rate > 0:
					

					if (del_iob) < 0:
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_35"
						
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: ", loaded_suggested_data["fault_reason"])
						print("***************************************\n")
						unsafe_action_occurance += 1

					elif (del_iob == 0):
						loaded_suggested_data["fault"] = "yes"
						loaded_suggested_data["fault_reason"] = "row_36" 
						print("\n***************************************")
						print("********** Unsafe Action !!!!! *************")  	
						print("Reason: ", loaded_suggested_data["fault_reason"])
						print("***************************************\n")
						unsafe_action_occurance += 1

########################### End of Row 28, 29, 30, 32, 35, 36 #########################

	
		if glucose > bg_target:
			print("\nGlucose is above target\n")
		elif glucose < bg_target:
			print("\nGlucose is below target\n")
		elif glucose == bg_target:
			print("\nGlucose equals to target\n")

		del_bg = glucose - prev_glucose
		if del_bg < 0:
			print("\nglucose is falling\n")
		elif del_bg > 0:
			print("\nglucose is rising\n")	
		elif del_bg == 0:
			print("\nglucose is stable\n")
	
		del_iob = iob - prev_iob
		if del_iob < 0:
			print("\niob is falling\n")
		elif del_iob > 0:
			print("\niob is rising\n")	
		elif del_iob == 0:
			print("\niob is stable\n")


		if del_rate > 0:
			print("\ninsulin is increased\n")
		elif del_rate < 0:
			print("\ninsulin is decreased\n")
		elif del_rate == 0:
			print("\nNo change in insulin\n")


		print("\nprev_iob: ", prev_iob)
		print("iob: ", iob,"\n")
		print("\nprev_glucose: ", prev_glucose)
		print("loaded_glucose", glucose)
		print("\nbg\n", bg)
	
	if glucose >= 39:				
		prev_iob = iob
	
	prev_glucose = glucose
	prev_rate = loaded_suggested_data["rate"]	

	list_suggested_data_to_dump.insert(0,loaded_suggested_data)
	#read the output in suggested.json and append it to list_suggested_data_to_dump list. Basically we are trying to get all the suggest	    ed data and dump make a list lf that and then dump it to all_suggested.json file		
#	with open("enact/suggested.json") as read_suggested:
#		loaded_suggested_data = json.load(read_suggested)
#		list_suggested_data_to_dump.insert(0,loaded_suggested_data)
#		#list_suggested_data_to_dump.append(loaded_suggested_data)
#		read_suggested.close()
	
	
	#################### Update pumphistory at very begining ##################
	if _==0:
		if  'duration' in loaded_suggested_data.keys():
		
			with open("monitor/pumphistory.json") as read_pump_history:
				loaded_pump_history = json.load(read_pump_history) # read whole pump_history.json
				pump_history_0 = loaded_pump_history[0].copy()	#load first element
				pump_history_1 = loaded_pump_history[1].copy() #load second element, fist and second are both for one temp basal
				pump_history_0['duration (min)'] = loaded_suggested_data['duration'] #update the values
				pump_history_1['rate'] = loaded_suggested_data['rate']
				pump_history_0['timestamp'] = current_timestamp
				pump_history_1['timestamp'] = current_timestamp

				loaded_pump_history.insert(0, pump_history_1) # insert second element back to whatever we loaded from pumphistory
				loaded_pump_history.insert(0, pump_history_0) #insert first element back to whatever we loaded from pumphistory
	                    
				read_pump_history.close();
		
			with open("monitor/pumphistory.json", "w") as write_pump_history:
				json.dump(loaded_pump_history, write_pump_history, indent=4)
	
################ Update temp_basal.json with the current temp_basal rate and duration ####################
	
	#load temp_basal.json
	with open("monitor/temp_basal.json") as read_temp_basal:
		loaded_temp_basal = json.load(read_temp_basal)
		loaded_temp_basal['duration']-=5
		
		if loaded_temp_basal['duration']<=0:
			loaded_temp_basal['duration'] = 0
		
		if "doing nothing" not in loaded_suggested_data['reason']:

			if loaded_temp_basal['duration']==0:
				loaded_temp_basal['duration'] = loaded_suggested_data['duration']
				loaded_temp_basal['rate'] = loaded_suggested_data['rate']


				######################### Update input of glucosym based on new temp ##############
				if loaded_suggested_data['rate'] == 0 and loaded_suggested_data['duration'] == 0:
					loaded_algo_input_copy["events"]['basal'][0]['amt'] = loaded_suggested_data['basal']
					loaded_algo_input_copy["events"]['basal'][0]['length'] = 30
					loaded_algo_input_copy["events"]['basal'][0]['start'] = _*5
				else:
					
					loaded_algo_input_copy["events"]['basal'][0]['amt'] = loaded_suggested_data['rate']
					loaded_algo_input_copy["events"]['basal'][0]['length'] = loaded_suggested_data['duration']
					loaded_algo_input_copy["events"]['basal'][0]['start'] = _*5
				
				##################### Uppdate Pupmphistory ####################################
					
				with open("monitor/pumphistory.json") as read_pump_history:
					loaded_pump_history = json.load(read_pump_history) # read whole pump_history.json
					pump_history_0 = loaded_pump_history[0].copy()	#load first element
					pump_history_1 = loaded_pump_history[1].copy() #load second element, fist and second are both for one temp basal
					pump_history_0['duration (min)'] = loaded_suggested_data['duration'] # Activate for non_faulty system
					pump_history_1['rate'] = loaded_suggested_data['rate'] # Activate for non_faulty System
					pump_history_0['timestamp'] = current_timestamp
					pump_history_1['timestamp'] = current_timestamp

					loaded_pump_history.insert(0, pump_history_1) # insert second element back to whatever we loaded from pumphistory
					loaded_pump_history.insert(0, pump_history_0) #insert first element back to whatever we loaded from pumphistory
		                    
					read_pump_history.close();
			
				with open("monitor/pumphistory.json", "w") as write_pump_history:
					json.dump(loaded_pump_history, write_pump_history, indent=4)
				
			
			else:	
		    
				if loaded_temp_basal['rate']!=loaded_suggested_data['rate']:
					loaded_temp_basal['rate']=loaded_suggested_data['rate']
					loaded_temp_basal['duration']=loaded_suggested_data['duration']

					####################### Update input of glucosym based on new temp ###########
					
					loaded_algo_input_copy["events"]['basal'][0]['amt'] = loaded_suggested_data['rate']
					loaded_algo_input_copy["events"]['basal'][0]['length'] = loaded_suggested_data['duration']
					loaded_algo_input_copy["events"]['basal'][0]['start'] = _*5

					#################### Uppdate Pumphistory ############################
					
					with open("monitor/pumphistory.json") as read_pump_history:
						loaded_pump_history = json.load(read_pump_history)
						pump_history_0 = loaded_pump_history[0].copy()
						pump_history_1 = loaded_pump_history[1].copy()
						pump_history_0['duration (min)'] = loaded_suggested_data['duration']
						pump_history_1['rate'] = loaded_suggested_data['rate']
						pump_history_0['timestamp'] = current_timestamp
						pump_history_1['timestamp'] = current_timestamp
						loaded_pump_history.insert(0, pump_history_1)
						loaded_pump_history.insert(0, pump_history_0)
						read_pump_history.close();
				
					with open("monitor/pumphistory.json", "w") as write_pump_history:
						json.dump(loaded_pump_history, write_pump_history, indent=4)
		

#		else:
#			if loaded_temp_basal['duration']<=0:
#				loaded_temp_basal['duration'] = 0
		
		read_temp_basal.close()
	
	## Fault_injection: Injection of fault in temp_basal ###############################
	
	##temp_basal:HOOK##

	############################### End of Fault injection #############################
		
	with open("monitor/temp_basal.json", "w") as write_temp_basal:
		json.dump(loaded_temp_basal, write_temp_basal, indent=4)		
			
	
	#print(suggested_data_to_dump)
	#write the list_suggested_data_to_dump into all_suggested.json file
	with open("enact/all_suggested.json", "w") as dump_suggested:
		json.dump(list_suggested_data_to_dump, dump_suggested, indent=4)
		dump_suggested.close()	

	#if 'rate' in loaded_suggested_data.keys():
      	#update the insulin parameter input of glucosym. This insulin parameters is received from openaps(suggested.json)
	#	algo_input_list["events"]['basal'][0]['amt'] = loaded_suggested_data['rate']
	#	algo_input_list["events"]['basal'][0]['length'] = loaded_suggested_data['duration']
	#	algo_input_list["events"]['basal'][0]['start'] = _*5
	
	
	
	#os.chdir("../glucosym/closed_loop_algorithm_samples")
	
	####################### Write algo_input having the suggested output from openaps ##########################
	
	with open("../glucosym/closed_loop_algorithm_samples/algo_input.json", "w") as write_algo_input:
		json.dump(loaded_algo_input_copy, write_algo_input, indent=4)
	
	
	call(["node", "../glucosym/closed_loop_algorithm_samples/algo_bw.js"]);
	
		
	#This part is for ploting glucose and insulin data over the time. This section starts after all the iteration is finished
if _ == iteration_num:
	with open("enact/all_suggested.json") as read_all_suggested:
		loaded_all_suggested = json.load(read_all_suggested)
   #y_list = [{"a":1, "b":1},{"a":4, "b":2},{"a":9, "b":3},{"a":16, "b":4}] 
  
   #print(loaded_all_suggested)

glucose = []
insulin = []
time = []

time_index = 0

for _ in loaded_all_suggested:
	if 'bg' in _.keys() and 'rate' in _.keys():
		glucose.insert(0,_['bg'])
		insulin.insert(0,_['rate'])
		time.append(time_index)
		time_index+=5
plt.plot(time, glucose)
plt.plot(time, insulin)
plt.ylabel("glucose and Insulin")
plt.xlabel("time")
plt.show()

print("\n ########################################")
print("Fault injected: ", fault_injected)
print("Fault Occurrence:", unsafe_action_occurance, " times")
print("########################################\n")

