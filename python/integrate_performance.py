import tool
import config
import sys
import os
import matplotlib.pyplot as pl

def draw(camp, metric, performances, folder):
	print camp
	pl.figure(figsize=(5, 5))
	legend = []
	min_y = 1E10
	max_y = 0
	for model in performances:
		perf = performances[model]
		legend.append(model.upper())
		pl.plot(range(0, len(perf), 1), perf, config.colors[model])
		mi = min(perf)
		ma = max(perf)
		min_y = mi if mi < min_y else min_y
		max_y = ma if ma > max_y else max_y
	pl.xlabel("Training Rounds")
	pl.ylabel(metric)
	min_y = min_y - abs(int(0.05*min_y))
	max_y = max_y + abs(int(0.05*max_y))
	pl.ylim([min_y, max_y])
	pl.title('Learning curve in Camp. ' + camp)
	path = os.path.join(folder, camp+"_"+metric+".pdf")
	pl.grid(True)
	pl.legend(legend, loc = 'lower right')
	# pl.show()
	pl.savefig(path, dpi=300)
	pl.close()

def read_values(file_path, metric):
	if metric == 'revenue':
		metric = 'Test'
	fi = open(file_path, 'r')
	lines = fi.read().split('\n')
	fi.close()
	count_flag = False
	metric_index = 1 # defaultly count on revenue
	perf_list = []
	for line in lines:
		args = line.split('\t')
		if args[0] == 'Round':
			count_flag = True
			try:
				metric_index = args.index(metric)
			except ValueError:
				print "No such metric name."
				print ValueError
				exit(-1)
			continue
		if count_flag and not args[0] == '':
			perf_list.append(float(args[metric_index]))
	return perf_list

def main():
	if len(sys.argv) < 4:
		print "Usage: python draw_camp_perf.py ../output revenue 1458"
		exit(-1)

	folder = sys.argv[1] # '../output/'
	metric = sys.argv[2] # 'revenue'
	camp = sys.argv[3] # '1458'
	print camp
	files = os.listdir(folder)

	performances = {}

	for f in files:
		if not f.endswith('.csv'):
			continue
		params = f.split('_')
		camp_id = params[0]
		if not camp_id == camp:
			continue
		model = params[1]
		perf_list = read_values(os.path.join(folder, f), metric)
		performances[model] = perf_list

	print performances
	# folder = "./"
	# camp = "1458"
	# metric = "revenue"
	# performances = {'eu': [1,3,5,7,9],
	# 				'rr': [2,2,6,8,19,13],
	# 				'lr': [1,2,5,5],
	# 				'sqlr': [0,3,4,5,8]}
	# print performances
	# draw(camp, metric, performances, folder)

if __name__ == '__main__':
	main()