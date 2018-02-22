#!/usr/bin/python
from dataset import Dataset
from bid_landscape import BidLandscape
from eu_model import EuModel
import sys
import config
import tool

def main():
    if len(sys.argv) < 5:
        print "Usage: python test_eu.py campaign_id laplace eu_scale ds_ratio"
        exit(-1)
    
    config.campaign_id = int(sys.argv[1]) if int(sys.argv[1]) in config.campaign_list else config.campaign_id
    config.laplace = int(sys.argv[2]) if int(sys.argv[2])>0 else config.laplace
    config.eu_scale = float(sys.argv[3]) if float(sys.argv[3])>0 else config.eu_scale
    config.ds_ratio = float(sys.argv[4]) if float(sys.argv[4])>0 else 0
    print "camp_id\tlaplace\tscale\tds_ratio"
    print `config.campaign_id` + "\t" + `config.laplace` + "\t" + `config.eu_scale` + "\t" + `config.ds_ratio`

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

    # train
    print "Begin training ..."
    for i in range(0, config.eu_train_round):
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
                + ".csv"
    fo = open("../output/"+log_file, 'w')
    
    print "Begin log ..."
    header = "camp_id\tmodel\tdataset\trevenue\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\teu_scale\tnds_ratio"
    best_test_log = eu_model.get_best_test_log()
    best_test_line = `config.campaign_id` + "\t" + "EU\ttest\t" \
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
                 + ".weight"
    eu_model.output_weight(best_test_log['weight'], "../output/" + weight_path)


if __name__ == '__main__':
    main()