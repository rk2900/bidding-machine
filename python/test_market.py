import os
import sys
import random
import config
import tool
import copy
from dataset import Dataset
from eu_model import EuModel
from lin_market import LinMarket
from quad_market import QuadMarket
from opt_bid import OptBid
import matplotlib.pyplot as pl

def main():
	if len(sys.argv) < 3:
		print "Usage: python test.py campaign_id budget_div market_alpha market_lambda market_para DEBUG"
		exit(-1)
	# python test_market.py 2997 4 5E-3 1E-4 0 0
	config.campaign_id = sys.argv[1]
	budget_div = int(sys.argv[2]) # now has no meanings
	config.market_alpha = float(sys.argv[3])
	config.market_lambda = float(sys.argv[4])
	market_para=int(sys.argv[5])
	if len(sys.argv) > 6:
		config.DEBUG = bool(sys.argv[6])

	# read in data, setup dataset
	train_path = config.data_folder + config.campaign_id + "/train.yzx.txt"
	test_path = config.data_folder + config.campaign_id + "/test.yzx.txt"

	train_data = Dataset(train_path, config.campaign_id)
	train_data.shuffle()
	test_data = Dataset(test_path, config.campaign_id)

	print "Data loaded."

	# (down-sampling)
	# if config.ds_ratio>0:
	# 	train_data_ds = train_data.down_sampling(config.ds_ratio)
	# 	config.ds_flag = True
	# else:
	# 	train_data_ds = train_data
	# train_data = train_data_ds # reassigned
	# print "Down sampled."
	# print train_data_ds.get_statistics()
	print "DS Flag = " + `config.ds_flag`

	# initialize hyper/parameters for market model
	if market_para == 0: 
		market_model = LinMarket(train_data, test_data)
	elif market_para == 1:
		market_model=QuadMarket(train_data,test_data)
	result_weight={}

	# train
	train_log = []
	test_log = []
	
	optimal_train_anlp=1000000
	optimal_test_anlp=1000000
	round_num=0
	for i in range(0, config.market_train_round):
		market_model.train()
		train_anlp = market_model.calc_total_anlp(train_data)
		train_log.append(train_anlp)
		test_anlp = market_model.calc_total_anlp(test_data)
		test_log.append(test_anlp)
		print "round " + `i+1` + " ends. train: %.3f, test: %.3f" % (train_anlp, test_anlp)
		round_num += 1
		if(round_num>=5):
			optimal_train_anlp=min(optimal_train_anlp,train_anlp)
			if(optimal_test_anlp > test_anlp):
				result_weight=copy.deepcopy(market_model.weight)
				optimal_test_anlp=test_anlp
		# judge early stop
		if round_num >=10 and tool.judge_market_stop(test_log): break

	output_dir="../../output" + ("/Quadratic" if market_para == 1 else "/Linear")
	tool.output(["campaign:%s_alpha:%s_beta:%s: %f"%(sys.argv[1],sys.argv[3],sys.argv[4],optimal_train_anlp)],output_dir+"/optimal_train_anlp.log")
	tool.output(["campaign:%s_alpha:%s_beta:%s: %f"%(sys.argv[1],sys.argv[3],sys.argv[4],optimal_test_anlp)],output_dir+"/optimal_test_anlp.log")
	tool.output_weight(result_weight,output_dir+("/model-weight/campaign_%s_alpha_%s_beta_%s.txt"%(sys.argv[1],sys.argv[3],sys.argv[4])))

	pl.figure(1)
	pl.plot([j for j in range(round_num)],train_log,'sb-')
	pl.plot([j for j in range(round_num)],test_log,'+r-')
	pl.xlabel('train_round')
	pl.ylabel('ANLP')
	pl.title('Learning Curve')
	pl.legend(['train','test'],loc='lower left')
	pl.savefig(output_dir+('/learning-curves/%s_%s_%s.pdf'%(sys.argv[1],sys.argv[3],sys.argv[4])), dpi=300)

	# print "Total ANLP is " + `anlp`


if __name__ == '__main__':
	main()
