import sys
import os
import multiprocessing

settings = {}

def run_exp(setting):
	os.system(setting)

def run_camp(camp):
	global settings
	for setting in settings[camp]:
		run_exp(setting)
		print "Done, " + setting
	return "Finished, " + camp

def main():
	# for i in range(10):
	# 	os.system("python test.py " + `i`)
	log_file = "../../filtered.log"
	#log_file = "../../test_log"
	fi = open(log_file)

	global settings
	settings = {'1458':[],'2259':[], '2261':[], '2821':[], '2997':[], '3358':[], '3386':[], '3427':[], '3476':[]}
	#settings={'2259':[]}
	camps = settings.keys()
	print camps

	for line in fi:
		contents = line.split()
		camp = contents[0]
		lap = contents[13]
		sca = contents[15]
		rat = contents[16]
		al = contents[17]
		be = contents[18]
		budget_props = [2,4,8,16,32,64]
		for i in budget_props:
			cmd = "python test_tri.py" + " " + camp + " eu " + lap + " " + sca + " " + rat + " "+`i`+" 1 " + al + " " + be
			log_file = "../output/" + camp + "_eu_" + lap + "_" + sca + "_" + rat + "_"+`i`+"_1_" + al + "_" + be + ".log"
			cmd = cmd + " > " + log_file
			settings[camp].append(cmd)
	                print settings[camp][-1]
		# cmd = "python test_tri.py" + " " + camp + " eu " + lap + " " + sca + " " + rat + " 1 1 " + al + " " + be
		# for i in range(len(contents)):
		# 	print `i` + ": " + contents[i]
#	exit(0)
	cores = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(processes=cores)
	print pool.map(run_camp, camps)




if __name__ == '__main__':
    main()
