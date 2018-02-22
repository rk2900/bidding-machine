#!/usr/bin/python
from dataset import Dataset
from bid_landscape import BidLandscape
from eu_model import EuModel
from lin_market import LinMarket
from tri_model import TriModel
import sys
import config
import tool
import copy

def main():
    if len(sys.argv) < 5:
        print "Usage: python test_prectr_joint.py campaign_id laplace eu_scale ds_ratio mkt_alpha mkt_lambda"
        exit(-1)

    config.campaign_id = int(sys.argv[1]) if int(sys.argv[1]) in config.campaign_list else config.campaign_id
    config.laplace = int(sys.argv[2]) if int(sys.argv[2])>0 else config.laplace
    config.eu_scale = float(sys.argv[3]) if float(sys.argv[3])>0 else config.eu_scale
    config.ds_ratio = float(sys.argv[4]) if float(sys.argv[4])>0 else 0
    config.market_alpha = float(sys.argv[5])
    config.market_lambda = float(sys.argv[6])
    print "camp_id\tlaplace\tscale\tds_ratio\tmkt_alpha\tmkt_lambda"
    print `config.campaign_id` + "\t" \
            + `config.laplace` + "\t" \
            + `config.eu_scale` + "\t" \
            + `config.ds_ratio` + "\t" \
            + `config.market_alpha` + "\t" \
            + `config.market_lambda`

    # judge if log and weight existed !!!
    log_file = `config.campaign_id` + "_prectr_joint" \
                + "_" + `config.laplace` \
                + "_" + `config.eu_scale` \
                + "_" + `config.ds_ratio` \
                + "_" + `config.market_alpha` \
        + "_" + `config.market_lambda`\
                + ".csv"
    if tool.judge_file_exists("../output/", log_file):
        print "Existed " + log_file
        exit(0)

    train_path = config.data_folder + `config.campaign_id` + "/train.yzx.txt"
    test_path = config.data_folder + `config.campaign_id` + "/test.yzx.txt"
    train_data = Dataset(train_path, config.campaign_id)
    train_data.shuffle() # make train data shuffled
    test_data = Dataset(test_path, config.campaign_id)
    if config.INTVL:
        IntervalLandscape(train_data, train_data.get_camp_id(), config.laplace, 3)
        IntervalLandscape(test_data, test_data.get_camp_id(), config.laplace, 3)
    else:
        BidLandscape(train_data, train_data.get_camp_id(), config.laplace)
        BidLandscape(test_data, test_data.get_camp_id(), config.laplace)
    print "Load done."

    # downsampling
    if config.ds_ratio>0:
        train_data_ds = train_data.down_sampling(config.ds_ratio)
    else:
        train_data_ds = train_data
    print "Down sampled."
    print train_data_ds.get_statistics()

    eu_model = EuModel(train_data_ds, test_data)
    print "campaign v = " + `eu_model.camp_v`

    # pre-train
    print "Begin ctr pre-training ..."
    pre_train_log=[]
    for i in range(0, config.eu_train_round):
        eu_model.train()
        eu_model.test()
	pre_train_log.append(copy.deepcopy(eu_model.test_log[-1]))
        print "Round " + `i+1` + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
        if tool.judge_stop(eu_model.test_log):
            break;
    print "Ctr pre-training done."
    pre_train_round = len(eu_model.test_log)
    tri_model = TriModel(train_data_ds, test_data, eu_model, None, 'eu')
    eu_model.weight = copy.deepcopy(tri_model.get_best_log(pre_train_log)['weight'])

    mkt_model = LinMarket(train_data, test_data)
    mkt_model.set_camp_v(eu_model.camp_v) # !!! nds camp value
    mkt_model.set_ctr_model(eu_model)
    mkt_model.set_bid_strategy(eu_model.get_bid_strategy())
    print "campaign v = " + `eu_model.camp_v`

    train_data_ds.set_landscape(mkt_model)
    train_data.set_landscape(mkt_model)

    # train
    print "Begin joint training ..."
    config.PARAM_MARKET = True
    recent_eu_weight=[]
    all_anlp=[]
    for i in range(0, config.eu_train_round):
        mkt_model.joint_train()
        test_anlp = mkt_model.calc_total_anlp(test_data)
        print "Round " + `i+1` + " test_anlp: " + `test_anlp`
        all_anlp.append(test_anlp)
        eu_model.train()
        eu_model.test()
        print "%d %d"%(len(all_anlp), len(eu_model.test_log))
        if i+1 > 3:
            del recent_eu_weight[0]
        recent_eu_weight.append(copy.deepcopy(eu_model.weight))
        print "Round " + `i+1` + "\t" + `tool.get_last_log(eu_model.test_log)['performance']`
        if tool.judge_stop(eu_model.test_log):
            break;
    if(len(recent_eu_weight) == 3):
        eu_model.weight = recent_eu_weight[0]
    print "Joint train done."


    fo = open("../output/"+log_file, 'w')

    print "Begin log ..."
    header = "camp_id\tmodel\tdataset\trevenue\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\teu_scale\tnds_ratio"
    best_test_log = eu_model.get_best_test_log()
    best_test_line = `config.campaign_id` + "\t" + "PRECTR_JOINT\ttest\t" \
                        + tool.gen_performance_line(best_test_log) + "\t" \
                        + `config.laplace` + "\t" + "None" + "\t" + `config.eu_scale` + "\t" + `config.ds_ratio` + "\t" \
                        + `config.market_alpha` + "\t" + `config.market_lambda`
    fo.write(header+"\n")
    fo.write(best_test_line+"\n")

    fo.write("\n")

    fo.write("Ctr Pre-train Log:")
    fo.write("Round\tTest\tctr\tcpc\tauc\trmse\tcpm\tclks\timps\tbids\n")
    for i in range(0, pre_train_round):
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
    print "Pre-train Log done."

    fo.write("Train Log:")
    fo.write("Round\tTest\tctr\tcpc\tauc\trmse\tcpm\tclks\timps\tbids\tanlp\n")
    for i in range(0, len(all_anlp)):
        test_log = eu_model.test_log[pre_train_round + i]
        line = `i+1` + "\t" + `test_log['performance']['revenue']` \
                + "\t" + `test_log['performance']['ctr']` \
                + "\t" + `test_log['performance']['cpc']` \
                + "\t" + `test_log['performance']['auc']` \
                + "\t" + `test_log['performance']['rmse']` \
                + "\t" + `test_log['performance']['cpm']` \
                + "\t" + `test_log['performance']['clks']` \
                + "\t" + `test_log['performance']['imps']` \
                + "\t" + `test_log['performance']['bids']` \
                + "\t" + `all_anlp[i]`
        fo.write(line + "\n")
    fo.close()
    print "Train Log done."


    weight_path = `config.campaign_id` + "_" + "prectr_joint_best_weight" \
                + "_" + `config.laplace` \
                + "_" + `config.eu_scale` \
                + "_" + `config.ds_ratio` \
        + "_" + `config.market_alpha` \
        + "_" + `config.market_lambda` \
                 + ".weight"
    eu_model.output_weight(best_test_log['weight'], "../output/" + weight_path)


if __name__ == '__main__':
    main()
