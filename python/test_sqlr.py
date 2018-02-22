#!/usr/bin/python
import config
import tool
from dataset import Dataset
from bid_landscape import BidLandscape
from interval_landscape import IntervalLandscape
from sqlr_model import SqlrModel
import sys


def main():
	if len(sys.argv) < 3:
		print "Usage python test_sqlr.py campaign_id learn_rate (budget_prop)"
		exit(-1)
	data_folder = "../../make-ipinyou-data/"
	config.campaign_id = int(sys.argv[1])
	config.lr_alpha = float(sys.argv[2])
	if len(sys.argv) == 4:
		config.budget_prop = int(sys.argv[3])
	train_path = data_folder + `config.campaign_id` + "/train.yzx.txt"
	test_path = data_folder + `config.campaign_id` + "/test.yzx.txt"
	print "Camp_id\tlearn_alpha"
	print `config.campaign_id` + "\t" + `config.lr_alpha`
	
	train_data = Dataset(train_path, config.campaign_id)
	train_data.shuffle()
	test_data = Dataset(test_path, config.campaign_id)
	print "Load done."
	
	lr_model = SqlrModel(train_data, test_data)
	print "campaign v = " + `lr_model.camp_v`
	print "budget = " + `lr_model.budget`

	log_file = `config.campaign_id` + "_sqlr_" + `config.lr_alpha` + "_" + `config.budget_prop` + ".csv"
	fo = open("../output/"+log_file, 'w')

	print "Begin training ..."
	for i in range(0, config.lr_train_round):
		lr_model.train()
		lr_model.test()
		print "Round " + `i+1` + "\t" + `tool.get_last_log(lr_model.test_log)['performance']`
		if tool.judge_stop(lr_model.test_log):
			break;
	print "Train done."

	print "Begin log ..."
	header = "camp_id\tmodel\tdataset\trevenue\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\tlearn_rate\tnds_ratio"
	best_test_log = lr_model.get_best_test_log()
	best_test_line = `config.campaign_id` + "\t" + "SQ\ttest\t" \
						+ tool.gen_performance_line(best_test_log) + "\t" \
						+ `config.laplace` + "\t" + "None" + "\t" \
						+ `config.lr_alpha` + "\t" + "None"
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
	
	# weight_path = `config.campaign_id` + "_sqlr_best_weight_" + `config.lr_alpha` + "_" + `config.budget_prop` + ".txt"
	# lr_model.output_weight(best_test_log['weight'], "../output/" + weight_path)

	weight_path = `config.campaign_id` + "_" + "sqlr_best_weight" \
				+ "_" + `config.laplace` \
				+ "_" + `config.eu_scale` \
				+ "_" + `config.ds_ratio` \
				+ ".weight"
	lr_model.output_weight(best_test_log['weight'], "../output/" + weight_path)
	

if __name__ == '__main__':
	main()
