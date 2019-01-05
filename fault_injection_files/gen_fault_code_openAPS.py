import os
import numpy as np
import random

	
# def gen_add_code(trigger, trigger_time, variable, stuck_value):
	# code = 'if %s>=%s:'%(trigger,trigger_time)
	# l = '//%s+=%s' % (variable,stuck_value)
	# code = code + l
	# return code


# def gen_sub_code(trigger, trigger_time, variable, stuck_value):
	# code = '//if %s>=%s:'%(trigger,trigger_time)
	# l = '//%s-=%s' % (variable,stuck_value)
	# code = code + l
	# return code

	
def gen_stuck_code(trigger, trigger_time, variable, stuck_value):
	code = 'if %s>=%s:'%(trigger,trigger_time)
	l = '//%s=%s' % (variable,stuck_value)
	code = code + l
	return code
	
def gen_intermittent_code(variable, trigger, trigger_prob, random_value):
	code = 'fault_prob = random.randint(1,100)'
	code_1 = '//if %s<=%s:'%(trigger,trigger_prob)
	l = '//%s=%s' % (variable,random_value)
	code = code + code_1 + l
	return code
	
### Write codes to fault library file
def write_to_file(code, exp_name, target_file, faultLoc):
	if os.path.isdir('fault_library') != True:
		os.makedirs('fault_library')
	fileName = 'fault_library/scenario_'+str(sceneNum)
	out_file = fileName+'.txt'
	#param_file = fileName+'_params.csv'

	with open(out_file, 'w') as outfile:
		#print out_file
		outfile.write('title:' + exp_name + '\n')
		outfile.write('location//' + target_file+ '//'+faultLoc + '\n')
		for i, line in enumerate(code):
			outfile.write('fault ' + str(i+1) + '//' + line + '\n')
		outfile.write('Total number of fault cases: '+str(i+1))

	with open('run_fault_inject_campaign.sh', 'a+') as runFile:
		runFile.write('python run_openAPS.py '+fileName+'\n')
		

# def gen_glucose_add_fault(sceneNum):
	# title = str(sceneNum)+'_glucose-add'
	# #faultLibFile = 'fault_library/dRelPlantRad'
	# fileLoc = 'updated_ct_script_iob_based.py'
	# faultLoc = '#glucose:HOOK#'
	# trigger = '_'
	# trigger_time = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	# #trigger_code = ''
	# code = []
	# #param = []
	# variable = "glucose"
	# deltaRange = np.arange(0,300,20)
	# for i in deltaRange:
		# delta = i
		# #code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		# code.append(gen_add_code(trigger, trigger_time, variable, delta))
		# #param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	# write_to_file(code, title, fileLoc, faultLoc)

# def gen_glucose_sub_fault(sceneNum):
	# title = str(sceneNum)+'_glucose-sub'
	# #faultLibFile = 'fault_library/dRelPlantRad'
	# fileLoc = 'updated_ct_script_iob_based.py'
	# faultLoc = '#glucose:HOOK#'
	# trigger = '_'
	# trigger_time = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	# #trigger_code = ''
	# code = []
	# #param = []
	# variable = "glucose"
	# deltaRange = np.arange(0,300,20)
	# for i in deltaRange:
		# delta = i
		# #code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		# code.append(gen_sub_code(trigger, trigger_time, variable, delta))
		# #param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	# write_to_file(code, title, fileLoc, faultLoc)

def gen_glucose_stuck_fault(sceneNum):
	title = str(sceneNum)+'_glucose-stuck'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#glucose:HOOK#'
	trigger = '_'
	trigger_time = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "glucose"
	deltaRange = np.arange(0,300,20)
	for i in deltaRange:
		delta = i
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_stuck_code(trigger, trigger_time, variable, delta))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)


def gen_glucose_intermittent_fault(sceneNum):
	title = str(sceneNum)+'_glucose-intermittent'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#glucose:HOOK#'
	trigger = 'fault_prob'
	random_value = 'random.randint(0,300)'
	#trigger_prob = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "glucose"
	ProbabilityRange = np.arange(10,100,10)
	for trigger_prob in ProbabilityRange:
		#delta = random.randint(0,300)
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_intermittent_code(variable, trigger, trigger_prob, random_value))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)


def gen_temp_basal_stuck_fault(sceneNum):
	title = str(sceneNum)+'_temp_basal_stuck'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#temp_basal:HOOK#'
	trigger = '_'
	trigger_time = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "temp_basal"
	deltaRange = np.arange(0,6,1)
	for i in deltaRange:
		delta = i
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_stuck_code(trigger, trigger_time, variable, delta))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)


def gen_temp_basal_intermittent_fault(sceneNum):
	title = str(sceneNum)+'_temp_basal-intermittent'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#temp_basal:HOOK#'
	trigger = 'fault_prob'
	random_value = 'random.randint(0,6)'
	#trigger_prob = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "temp_basal"
	ProbabilityRange = np.arange(10,100,10)
	for trigger_prob in ProbabilityRange:
		#delta = random.randint(0,300)
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_intermittent_code(variable, trigger, trigger_prob, random_value))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)


	
def gen_controller_output_stuck_fault(sceneNum):
	title = str(sceneNum)+'_controller_output_stuck'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#rate:HOOK#'
	trigger = '_'
	trigger_time = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "rate"
	deltaRange = np.arange(0,6,1)
	for i in deltaRange:
		delta = i
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_stuck_code(trigger, trigger_time, variable, delta))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)
	

def gen_controller_output_intermittent_fault(sceneNum):
	title = str(sceneNum)+'_controller_output-intermittent'
	#faultLibFile = 'fault_library/dRelPlantRad'
	fileLoc = 'updated_ct_script_iob_based.py'
	faultLoc = '#rate:HOOK#'
	trigger = 'fault_prob'
	random_value = 'random.randint(0,6)'
	#trigger_prob = 10 # 10 is an arbitrary number, I want the fault be injected after 10th iteration
	#trigger_code = ''
	code = []
	#param = []
	variable = "rate"
	ProbabilityRange = np.arange(10,100,10)
	for trigger_prob in ProbabilityRange:
	    #delta = random.randint(0,300)
		#code.append(gen_add_code(trigger_code, trigger, t1, t2, variable, [delta], '//if '+variable[0]+'>=255:'+'//  '+variable[0]+'= 254'))
		code.append(gen_intermittent_code(variable, trigger, trigger_prob, random_value))
		#param.append(','.join(['relative distance',str(t1),str(dt),str(delta)]))

	write_to_file(code, title, fileLoc, faultLoc)

	
###_main_###

with open('run_fault_inject_campaign.sh', 'w') as runFile:
    runFile.write('#Usage: python run_openAPS.py target_fault_library\n')
	
scenarios = {
1 : gen_glucose_stuck_fault,
2 : gen_glucose_intermittent_fault,
3 : gen_temp_basal_stuck_fault,
4 : gen_temp_basal_intermittent_fault,
5 : gen_controller_output_stuck_fault,
6 : gen_controller_output_intermittent_fault
}

for sceneNum in [1,2,3,4,5,6]:
	scenarios[sceneNum](sceneNum)

