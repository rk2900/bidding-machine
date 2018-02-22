#!/usr/bin/python
import config
import tool
from dataset import Dataset
from bid_landscape import BidLandscape
from interval_landscape import IntervalLandscape
from lr_model import LrModel
import sys


def main():
	if len(sys.argv) < 3:
		print "Usage python test_lr.py campaign_id learn_rate (budget_prop)"
		exit(-1)
	data_folder = "../../make-ipinyou-data/"
	config.campaign_id = int(sys.argv[1])
	# print config.campaign
	# print config.campaign_id
	# exit(-1)
	config.lr_alpha = float(sys.argv[2])
	if len(sys.argv) == 4:
		config.budget_prop = int(sys.argv[3])
	train_path = data_folder + `config.campaign_id` + "/train.yzx.txt"
	test_path = data_folder + `config.campaign_id` + "/test.yzx.txt"
	
	train_data = Dataset(train_path, config.campaign_id)
	train_data.shuffle() # make train data shuffled
	test_data = Dataset(test_path, config.campaign_id)
	print "Load done."
	
	lr_model = LrModel(train_data, test_data)
	print "campaign v = " + `lr_model.camp_v`
	print "learn_rate = " + `config.lr_alpha`
	print "budget = " + `lr_model.budget`

	if config.ds_ratio > 0:
		print "Need calibration."
	else:
		print "No calibration."

	print "Begin training ..."
	for i in range(0, config.lr_train_round):
		lr_model.train()
		lr_model.test()
		print "Round " + `i+1` + "\t" + `tool.get_last_log(lr_model.test_log)['performance']`
		if tool.judge_stop(lr_model.test_log):
			break;
	print "Train done."


	log_file = `config.campaign_id` + "_lr_" + `config.lr_alpha` + "_" + `config.budget_prop` + ".csv"
	fo = open("../output/"+log_file, 'w')
	
	print "Begin log ..."
	header = "camp_id\tmodel\tdataset\trevenue\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\tlearn_rate\tnds_ratio\tbudget_prop"
	best_test_log = lr_model.get_best_test_log()
	best_test_line = `config.campaign_id` + "\t" + "LR\ttest\t" \
						+ tool.gen_performance_line(best_test_log) + "\t" \
						+ 'None' + "\t" + "None" + "\t" + `config.lr_alpha` + "\t" \
						+ "None" + "\t" + `config.budget_prop`
	fo.write(header+"\n")
	fo.write(best_test_line+"\n")

	fo.write("\n")

	fo.write("Round\tTest\tctr\tcpc\tauc\trmse\tcpm\tclks\timps\tbids\n")
	for i in range(0, len(lr_model.test_log)):
		test_log = lr_model.test_log[i]
		line = `i+1` + "\t" + `test_log['performance']['revenue']` \
				+ "\t" + `test_log['performance']['ctr']` \
				+ "\t" + `test_log['performance']['cpc']` \
				+ "\t" + `test_log['performance']['auc']` \
				+ "\t" + `test_log['performance']['rmse']` \
				+ "\t" + `test_log['performance']['cpm']` \
				+ "\t" + `test_log['performance']['clks']` \
				+ "\t" + `test_log['performance']['imps']` \
				+ "\t" + `test_log['performance']['bids']`
		fo.write(line + "\n")
	fo.close()
	print "Log done."

	weight_path = `config.campaign_id` + "_" + "lr_best_weight" \
				+ "_" + `config.lr_alpha` + "_" + `config.budget_prop` \
				+ ".weight"
	lr_model.output_weight(best_test_log['weight'], "../output/" + weight_path)

if __name__ == '__main__':
	main()