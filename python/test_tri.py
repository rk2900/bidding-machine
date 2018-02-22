#!/usr/bin/python
from dataset import Dataset
from bid_landscape import BidLandscape
from em_model import EmModel
from eu_model import EuModel
from lin_market import LinMarket
from tri_model import TriModel
import sys
import config
import tool
import copy

def main():
	if len(sys.argv) < 7:
		print "Usage: python test_tri.py campaign_id model_name laplace x_scale ds_ratio budget_prop train_option mkt_alpha mkt_lambda"
		exit(-1)
	
	config.campaign_id = int(sys.argv[1])
	model_name = sys.argv[2]
	if not model_name in config.model_list:
		print "Wrong model name."
		exit(-1)
	config.model_name = model_name
	config.laplace = int(sys.argv[3])
	config.eu_scale = float(sys.argv[4])
	config.ds_ratio = float(sys.argv[5]) if float(sys.argv[5])>0 else 0
	config.budget_prop = int(sys.argv[6])
	train_option = int(sys.argv[7])
	config.market_alpha = float(sys.argv[8])
	config.market_lambda = float(sys.argv[9])
	
	print "cam_id\tmodel\tlaplace\tscale\tds_ratio\tbudget_prop\ttrain_option\tmkt_alpha\tmkt_lambda"
	print `config.campaign_id` + "\t" + `model_name` \
			+ "\t" + `config.laplace` + "\t" + `config.eu_scale` \
			+ "\t" + `config.ds_ratio` + "\t" + `config.budget_prop` \
			+ "\t" + `train_option` + "\t" + `config.market_alpha` + "\t" + `config.market_lambda`

	train_path = config.data_folder + `config.campaign_id` + "/train.yzx.txt"
	test_path = config.data_folder + `config.campaign_id` + "/test.yzx.txt"
	train_data = Dataset(train_path, config.campaign_id)
	train_data.shuffle() # make train data shuffled
	test_data = Dataset(test_path, config.campaign_id)

	# downsampling
	train_data_ds = train_data.down_sampling(config.ds_ratio) if config.ds_ratio > 0 else train_data
	print train_data_ds.get_statistics()
	print "Down sampled."

	# eu_model mkt_model tri_model
	eu_model = EuModel(train_data_ds, test_data)
	mkt_model = LinMarket(train_data, test_data)
	tri_model = TriModel(train_data_ds, test_data, eu_model, mkt_model, model_name)

	# unify the bid_strategy on ctr, mkt and tri_model
	eu_model.bid_strategy = tri_model.bid_strategy
	mkt_model.set_camp_v(eu_model.camp_v) # !!! nds camp value
	mkt_model.set_ctr_model(eu_model)
	mkt_model.set_bid_strategy(eu_model.get_bid_strategy())
	print "campaign v = " + `eu_model.camp_v`

	# bid landscape initialization
	# pre-train
	# 1. CTR pre-train
	# if train_option in {1, 3}:
	# 	# temporarily init counting-based landscape
	# 	BidLandscape(train_data, train_data.get_camp_id(), config.laplace)
	# 	train_data_ds.init_landscape(train_data.get_landscape())
	# 	eu_model.train()
	# 	eu_model.test()
	# 	# add back parameterized landscape
	if train_option in {1,3}:
		print "Begin ctr pre-training ..."
		# temporarily init counting-based landscape
		BidLandscape(train_data, train_data.get_camp_id(), config.laplace)
		train_data_ds.init_landscape(train_data.get_landscape())
		for i in range(0, config.eu_train_round):
			eu_model.train()
			eu_model.test()
			print "Round " + `i+1` + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
			if tool.judge_stop(eu_model.test_log):
				break;
		print "Ctr pre-training done."
		pre_train_round = len(eu_model.test_log)
	
	print "Pre_train_round: %d"%pre_train_round
	mkt_model = LinMarket(train_data, test_data)
	mkt_model.set_camp_v(eu_model.camp_v) # !!! nds camp value
	mkt_model.set_ctr_model(eu_model)
	mkt_model.set_bid_strategy(eu_model.get_bid_strategy())
	print "campaign v = " + `eu_model.camp_v`

	# add back parameterized landscape
	train_data_ds.set_landscape(mkt_model)
	train_data.set_landscape(mkt_model)

	# discard this method since poor performance.
	# # 2. MKT pre-train
	# if train_option > 1:
	# 	mkt_model.train()
	# 	train_anlp = mkt_model.calc_total_anlp(train_data)
	# 	test_anlp = mkt_model.calc_total_anlp(test_data)
	# 	#print "Market Model pre-train ANLP train: %.3f, test: %.3f." % (train_anlp, test_anlp)

	# train
	print "Begin training ..."
	config.PARAM_MARKET = True
	cur_round_log = []
	for i in range(0, config.em_round):
		#print "Tri Round starts:"
		del cur_round_log
		cur_round_log = []
		for j in range(0, config.eu_train_round):
			mkt_model.joint_train()
			test_anlp = mkt_model.calc_total_anlp(test_data)
			print "Joint Round " + `i+1` + " Round " + `j+1` + " test_anlp: " + `test_anlp`
			eu_model.train()
			eu_model.test()
			eu_model.test_log[-1]['test_anlp']=test_anlp
			cur_round_log.append(copy.deepcopy(eu_model.test_log[-1]))
			cur_round_log[-1]['mkt_weight']=copy.deepcopy(mkt_model.weight)
			#print "================================================"
			#print "yes" if 'weight' in eu_model.test_log[-1] else "no"
			#print "================================================"
			print "Joint Round " + `i+1` + " Round " + `j+1` + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
			#if(j+1 > 3):
			#	del recent_mkt_weight[0]
			#	del recent_ctr_weight[0]
			#recent_mkt_weight.append(copy.deepcopy(mkt_model.weight))
			#recent_ctr_weight.append(copy.deepcopy(eu_model.weight))
			if tool.judge_stop(eu_model.test_log):
				break;
		best_cur_log = tri_model.get_best_log(cur_round_log)
		mkt_model.weight = copy.deepcopy(best_cur_log['mkt_weight'])
		eu_model.weight = copy.deepcopy(best_cur_log['weight'])
		#mkt_model.weight = copy.deepcopy(recent_mkt_weight[0]) # re-assign the best weight
		#eu_model.weight = copy.deepcopy(recent_ctr_weight[0]) # re-assign the best weight
		tri_model.train()
		eu_model.test_log.append(copy.deepcopy(tri_model.em_log[-1]))
		#print "================================================"
		#print "yes" if 'weight' in eu_model.test_log[-1] else "no"
		#print "================================================"
		print "Tri Round " + `i+1` + "\t" + `tool.get_last_log(tri_model.em_log)['performance']`
		if tool.judge_stop(tri_model.em_log):
			break;
	print "Train done."

	# em_rr_2997_3_0.1_0.csv
	log_file = "tri_" + model_name \
				+ "_" + `config.campaign_id` \
				+ "_" + `config.budget_prop` \
				+ "_" + `config.laplace` \
				+ "_" + `config.eu_scale` \
				+ "_" + `config.ds_ratio` \
            			+ "_" + `config.market_alpha` \
            			+ "_" + `config.market_lambda` \
				+ ".csv"
	fo = open("../output/" + log_file, 'w')

	print "Begin log ..."
	header = "camp_id\tmodel\tdataset\trevenue\troi\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\tscale\tds_ratio\tbudget_prop\talpha\tlambda\tem_round\tmu"
	best_em_log = tri_model.get_best_log(tri_model.em_log)
	best_em_line = `config.campaign_id` + "\t" + "em"+model_name + "\ttest\t" \
					+ tool.gen_performance_line(best_em_log) + "\t" \
					+ `config.laplace` + "\t" + "None" + "\t" + `config.eu_scale` + "\t" \
					+ (`config.ds_ratio` if config.ds_ratio>0 else "None") + "\t" \
					+ `config.budget_prop` +"\t" \
					+ `config.market_alpha` +"\t" \
					+ `config.market_lambda` +"\t" \
					+ `len(tri_model.em_log)` + "\t" + `best_em_log['mu']`

	fo.write(header + "\n")
	fo.write(best_em_line + "\n")

	fo.write("Test with Budget Constraints\n")

	# # reset mu
	# em_model.mu = best_em_log['mu']
	# em_model.bid_strategy.set_mu(em_model.mu)
	# # replay
	# fo.write("prop\trevenue\troi\tctr\tcpc\tauc\trmse\tcpm\timps\tclks\n")
	# for prop in config.budget_props:
	#	 performance = em_model.replay(best_em_log['weight'], em_model.test_data, prop)
	#	 fo.write(`prop`); fo.write("\t")
	#	 fo.write(`performance['revenue']`); fo.write("\t")
	#	 fo.write(`performance['roi']`); fo.write("\t")
	#	 fo.write(`performance['ctr']`); fo.write("\t")
	#	 fo.write(`performance['cpc']`); fo.write("\t")
	#	 fo.write(`performance['auc']`); fo.write("\t")
	#	 fo.write(`performance['rmse']`); fo.write("\t")
	#	 fo.write(`performance['cpm']`); fo.write("\t")
	#	 fo.write(`performance['imps']`); fo.write("\t")
	#	 fo.write(`performance['clks']`); fo.write("\t")
	#	 fo.write("\n")


	fo.write("\n")

	fo.write("Round\trevenue\troi\tcpc\tctr\tauc\trmse\timps\ttruncate\tanlp\tmu\n")
	for i in range(len(eu_model.test_log)):
		tri_log = eu_model.test_log[i]
		line = `i+1` + "\t" + `tri_log['performance']['revenue']` + "\t" \
				+ `tri_log['performance']['roi']` + "\t" \
				+ `tri_log['performance']['cpc']` + "\t" \
				+ `tri_log['performance']['ctr']` + "\t" \
				+ `tri_log['performance']['auc']` + "\t" \
				+ `tri_log['performance']['rmse']` + "\t" \
				+ `tri_log['performance']['imps']` + "\t" \
				+ `tri_log['weight'][0]` + "\t"
		if 'test_anlp' in tri_log:
			line = line + `tri_log['test_anlp']`+ "\t"
		else:
			 line = line + " " + "\t"
		if 'mu' in tri_log:
			line = line + `tri_log['mu']` + "\t"
		else:
			line = line + " " + "\t"
		fo.write(line + "\n")
	#for i in range(0, len(tri_model.test_log)):
	#	test_log = tri_model.test_log[i]
	#	line = `i+1` + "\t" + `test_log['performance']['revenue']` + "\t" \
	#			+ `test_log['performance']['roi']` + "\t" \
	#			+ `test_log['performance']['cpc']` + "\t" \
	#			+ `test_log['performance']['ctr']` + "\t" \
	#			+ `test_log['performance']['auc']` + "\t" \
	#			+ `test_log['performance']['rmse']` + "\t" \
	#			+ `test_log['performance']['imps']` + "\t" \
	#			+ `test_log['weight'][0]`
	#	if 'm' in test_log:
	#		line = line + "\tm"
	#	fo.write(line + "\n")

	fo.close()
	
	weight_path = "tri_eu" +"_" + `config.campaign_id` \
			+"_" + `config.budget_prop` \
			+ "_" + `config.laplace` \
			+ "_" + `config.eu_scale` \
			+ "_" + `config.ds_ratio` \
			+ "_" + `config.market_alpha` \
			+ "_" + `config.market_lambda` \
			+ ".weight"
	eu_model.output_weight(best_em_log['weight'],"../output/"+weight_path)
	print "Log done."

if __name__ == '__main__':
	main()
