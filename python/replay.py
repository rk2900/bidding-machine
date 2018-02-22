import config
from dataset import Dataset
from opt_bid import OptBid
import sys
import os
import tool
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
import math

nds_ratio = 0.01
camp_v = 36000

# header_dataset = "camp_id\tnds_ratio\tcamp_v\tsize\tcost_sum\tclk_sum\tecpc\tcpm\tctr\tmax_price\n"
def make_dataset_record(dataset, camp_id):
	stat = dataset.get_statistics()
	line = `camp_id` + "\t" + `nds_ratio` + "\t" + \
			`camp_v` + "\t" + `stat['size']` + "\t" + \
			`stat['cost_sum']` + "\t" + `stat['clk_sum']` + "\t" + \
			`stat['ecpc']` + "\t" + `stat['ecpm']` + "\t" + \
			`stat['ctr']` + "\t" + `stat['max_price']` + "\n"
	return line

# header_log = "progress\trevenue\tctr\twin_rate\tauc\trmse\tecpc\tcpm\tclk_sum\timp_sum\tbid_sum\n"
def make_log_record(log):
	line = `log['progress']` + "\t" + `log['revenue']` + "\t" + \
			`log['ctr']` + "\t" + `log['win_rate']` + "\t" + \
			`log['auc']` + "\t" + `log['rmse']` + "\t" + \
			`log['cpc']` + "\t" + `log['cpm']` + "\t" + \
			`log['clks']` + "\t" + `log['imps']` + "\t" + \
			`log['bids']` + "\n"
	return line

def make_performance(progress, bid_sum, cost_sum, imp_sum, clk_sum, revenue_sum, labels, p_labels):
	log = {}
	log['progress'] = progress
	log['bids'] = bid_sum
	log['imps'] = imp_sum
	log['clks'] = clk_sum
	log['revenue'] = revenue_sum
	log['auc'] = roc_auc_score(labels, p_labels)
	log['rmse'] = math.sqrt(mean_squared_error(labels, p_labels))
	log['cpc'] = 0.0 if clk_sum == 0 else 1.0 * cost_sum / clk_sum * 1E-3
	log['cpm'] = 0.0 if imp_sum == 0 else 1.0 * cost_sum / imp_sum
	log['ctr'] = 0.0 if imp_sum == 0 else 1.0 * clk_sum / imp_sum
	log['win_rate'] = 0.0 if bid_sum == 0 else 1.0 * imp_sum / bid_sum
	print log
	return log

def calibrate_ctr(pctr):
	cal_pctr = pctr / (pctr + (1 - pctr) / nds_ratio)
	return cal_pctr

def bid_cal(ctr):
	cal_ctr = calibrate_ctr(ctr)
	bid_price = int(camp_v * cal_ctr * 1E3)
	return bid_price

def bid(ctr):
	bid_price = int(camp_v * ctr * 1E3)
	print camp_v
	return bid_price

def check_file(path):
	if not os.path.isfile(path):
		print "ERROR: file not exist. " + path
		exit(-1)

def read_weight(path):
	weight = {}
	check_file(path)
	fi = open(path, 'r')
	for line in fi:
		k_v = line.split()
		key = int(k_v[0])
		value = float(k_v[1])
		weight[key] = value
	return weight

def main():
	if len(sys.argv) < 6:
		print "Usage: python replay.py camp_id(yoyi=-1) budget_prop weight.txt test.yzx.txt log.csv (calib)"
		exit(-1)

	camp_id = int(sys.argv[1])
	print "Campaign ID = " + `camp_id`
	budget_prop = int(sys.argv[2])
	weight_path = sys.argv[3]
	data_path = sys.argv[4]
	log_path = sys.argv[5]
	global nds_ratio
	global camp_v
	if len(sys.argv) == 7:
		nds_ratio = float(sys.argv[6])
		if not nds_ratio > 0:
			print "No calibration."

	dataset = Dataset(data_path, camp_id)
	weight = read_weight(weight_path)
	budget = int(dataset.get_statistics()['cost_sum'] / budget_prop)
	if camp_id > 0:
		camp_v = dataset.get_statistics()['ecpc']

	# init the metrics
	logs = []
	labels = []
	p_labels = []
	bid_sum = 0
	cost_sum = 0
	imp_sum = 0
	clk_sum = 0
	revenue_sum = 0

	detail_fo = open("../detail/" + `camp_id` + ".txt", 'w')

	# replay
	progress = 0.0
	total_num = dataset.get_statistics()['size']
	iter_id = dataset.init_index()
	while not dataset.reached_tail(iter_id):
		data = dataset.get_next_data(iter_id)
		bid_sum += 1
		y = data[0]
		mp = data[1]
		feature = data[2:len(data)]
		ctr = tool.estimate_ctr(weight, feature, train_flag=False)
		labels.append(y)
		p_labels.append(ctr)
		if camp_id < 0 or nds_ratio > 0:
			bid_price = bid_cal(ctr)
		else:
			bid_price = bid(ctr)
		if bid_price > mp:
			cost_sum += mp
			imp_sum += 1
			clk_sum += y
			revenue_sum = revenue_sum - mp + int(camp_v * y * 1E3)
		detail_fo.write(`bid_price` + "\t" + `mp` + "\t" + `y` + "\n")
		# prg = 1.0 * bid_sum / total_num
		# if prg > (progress + config.test_progress_unit - 1E-5):
		# 	progress += config.test_progress_unit
		# 	performance = make_performance(prg, bid_sum, cost_sum, imp_sum, clk_sum, revenue_sum, labels, p_labels)
		# 	logs.append(performance)
		if cost_sum > budget:
			performance = make_performance(prg, bid_sum, cost_sum, imp_sum, clk_sum, revenue_sum, labels, p_labels)
			logs.append(performance)
			break
	performance = make_performance(1.0, bid_sum, cost_sum, imp_sum, clk_sum, revenue_sum, labels, p_labels)
	logs.append(performance)

	detail_fo.close()

	# make record
	log_file = open(log_path, 'w')
	header_dataset = "camp_id\tnds_ratio\tcamp_v\tsize\tcost_sum\tclk_sum\tecpc\tcpm\tctr\tmax_price\n"
	header_log = "progress\trevenue\tctr\twin_rate\tauc\trmse\tecpc\tcpm\tclk_sum\timp_sum\tbid_sum\n"
	log_file.write(header_dataset)
	log_file.write(make_dataset_record(dataset, camp_id))
	log_file.write(header_log)
	for log in logs:
		log_file.write(make_log_record(log))


if __name__ == '__main__':
	main()
