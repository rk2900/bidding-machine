#!/usr/bin/python
from dataset import Dataset
from bid_landscape import BidLandscape
from lin_market import LinMarket
from eu_model import EuModel
import sys
import config
import tool

def main():
    if len(sys.argv) < 5:
        print "Usage: python test_stat_bin.py campaign_id laplace eu_scale ds_ratio train_option (DEBUG)"
        exit(-1)
    
    weight_path_dict = {'1458': 'campaign_1458_alpha_1e-9_beta_1e-4.txt',
                        '2259': 'campaign_2259_alpha_1e-9_beta_5e-3.txt',
                        '2261': 'campaign_2261_alpha_5e-9_beta_1e-4.txt',
                        '2821': 'campaign_2821_alpha_1e-9_beta_5e-7.txt',
                        '2997': 'campaign_2997_alpha_5e-9_beta_1e-7.txt',
                        '3358': 'campaign_3358_alpha_1e-9_beta_1e-8.txt',
                        '3386': 'campaign_3386_alpha_5e-10_beta_5e-5.txt',
                        '3427': 'campaign_3427_alpha_5e-10_beta_1e-2.txt',
                        '3476': 'campaign_3476_alpha_5e-10_beta_5e-3.txt'}

    config.campaign_id = int(sys.argv[1]) if int(sys.argv[1]) in config.campaign_list else config.campaign_id
    config.laplace = int(sys.argv[2]) if int(sys.argv[2])>0 else config.laplace
    config.eu_scale = float(sys.argv[3]) if float(sys.argv[3])>0 else config.eu_scale
    config.ds_ratio = float(sys.argv[4]) if float(sys.argv[4])>0 else 0
    if len(sys.argv) > 8:
    	config.DEBUG = bool(sys.argv[8])
    
    if len(sys.argv) > 5:
    	options = {0,1,2,3}
    	option_dict = {
    		0: 'directly joint train',
        	1: 'CTR pre-train',
        	2: 'MKT pre-train',
        	3: 'all pre-train' }
        train_option = int(sys.argv[5])
        if not train_option in options:
            print "ERROR: Train Option Error!"
            exit(-1)
        config.mkt_weight_path = '../lin_weight/' + weight_path_dict[`config.campaign_id`]
    print "camp_id\tlaplace\tscale\tds_ratio\ttrain_option\tmkt_alpha\tmkt_lambda"
    print `config.campaign_id` + "\t" \
    		+ `config.laplace` + "\t" \
    		+ `config.eu_scale` + "\t" \
    		+ `config.ds_ratio` + "\t" \
    		+ option_dict[train_option] + "\t" \
    		+ `config.mkt_weight_path`

    train_path = config.data_folder + `config.campaign_id` + "/train.yzx.txt"
    test_path = config.data_folder + `config.campaign_id` + "/test.yzx.txt"
    train_data = Dataset(train_path, config.campaign_id)
    train_data.shuffle() # make train data shuffled
    test_data = Dataset(test_path, config.campaign_id)
    print "Dataset load done."

    # downsampling
    if config.ds_ratio>0:
        train_data_ds = train_data.down_sampling(config.ds_ratio)
    else:
        train_data_ds = train_data
    print "Down sampled."
    print train_data_ds.get_statistics()

    eu_model = EuModel(train_data_ds, test_data)
    mkt_model = LinMarket(train_data, test_data)
    if mkt_model.load_weight(config.mkt_weight_path):
        test_anlp = mkt_model.calc_total_anlp(test_data)
        print "Market model weight loaded. The overall ANLP = " + `test_anlp`
    mkt_model.set_camp_v(eu_model.camp_v) # !!! nds camp value
    mkt_model.set_ctr_model(eu_model)
    mkt_model.set_bid_strategy(eu_model.get_bid_strategy())
    print "campaign v = " + `eu_model.camp_v`

    # bid landscape initialization
    # pre-train
    # 1. CTR pre-train
    if train_option in {1, 3}:
    	# temporarily init counting-based landscape
    	BidLandscape(train_data, train_data.get_camp_id(), config.laplace)
    	train_data_ds.init_landscape(train_data.get_landscape())
    	eu_model.train()
    	eu_model.test()
    	print "Round 0" + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
    	# add back parameterized landscape

    # 2. MKT pre-train
    if train_option > 1:
    	mkt_model.train()
    	train_anlp = mkt_model.calc_total_anlp(train_data)
    	test_anlp = mkt_model.calc_total_anlp(test_data)
    	print "Market Model pre-train ANLP train: %.3f, test: %.3f." % (train_anlp, test_anlp)

    train_data_ds.set_landscape(mkt_model)
    train_data.set_landscape(mkt_model)

    # # set up bid landscape model
    # mkt_model = LinMarket(train_data_ds, test_data)
    # if mkt_model.load_weight(weight_path): print "Market parameter loaded."
    # train_data_ds.init_landscape(mkt_model)
    # print mkt_model.weight[0]
    # print "Parameterized landscape initialized."

    # raw_input("pause ...")

    # train
    print "Begin training ..."
    config.PARAM_MARKET = True
    for i in range(0, config.eu_train_round):
    	# mkt_model.joint_train()
    	print "Round " + `i+1` + " test_anlp: " + `test_anlp`
        eu_model.train()
        eu_model.test()
        print "Round " + `i+1` + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
        if tool.judge_stop(eu_model.test_log):
            break;
    print "Train done."

    # eu_2997_3_0.1_0.05.csv
    log_file = `config.campaign_id` + "_eu" \
                + "_" + `config.laplace` \
                + "_" + `config.eu_scale` \
                + "_" + `config.ds_ratio` \
                + ".stat.csv"
    fo = open("../output/"+log_file, 'w')
    
    print "Begin log ..."
    header = "camp_id\tmodel\tdataset\trevenue\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\teu_scale\tnds_ratio"
    best_test_log = eu_model.get_best_test_log()
    best_test_line = `config.campaign_id` + "\t" + "EU-stat\ttest\t" \
                        + tool.gen_performance_line(best_test_log) + "\t" \
                        + `config.laplace` + "\t" + "None" + "\t" + `config.eu_scale` + "\t" + `config.ds_ratio`
    fo.write(header+"\n")
    fo.write(best_test_line+"\n")

    fo.write("\n")

    fo.write("Round\tTest\tctr\tcpc\tauc\trmse\tcpm\tclks\timps\tbids\n")
    for i in range(0, len(eu_model.test_log)):
        test_log = eu_model.test_log[i]
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

    weight_path = `config.campaign_id` + "_" + "eu_best_weight" \
                + "_" + `config.laplace` \
                + "_" + `config.eu_scale` \
                + "_" + `config.ds_ratio` \
                 + ".stat_ctr.weight"
    eu_model.output_weight(best_test_log['weight'], "../output/" + weight_path)


if __name__ == '__main__':
    main()