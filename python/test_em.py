#!/usr/bin/python
from dataset import Dataset
from bid_landscape import BidLandscape
from em_model import EmModel
import sys
import config
import tool

def main():
    if len(sys.argv) < 7:
        print "Usage: python test_em.py camp_id model_name laplace x_scale ds_ratio budget_prop"
        exit(-1)

    config.campaign_id = int(sys.argv[1])
    model_name = sys.argv[2]
    if not model_name in config.model_list:
        print "Wrong model name."
        exit(-1)
    config.model_name = model_name
    config.laplace = int(sys.argv[3])
    config.em_scale = float(sys.argv[4])
    config.ds_ratio = float(sys.argv[5]) if float(sys.argv[5]) > 0 else 0
    config.budget_prop = int(sys.argv[6])
    print "camp_id\tmodel\tlaplace\tscale\tds_ratio\tbudget_prop"
    print `config.campaign_id` + "\t" + `model_name` \
            + "\t" + `config.laplace` + "\t" + `config.em_scale` \
            + "\t" + `config.ds_ratio` + "\t" + `config.budget_prop`

    train_path = config.data_folder + `config.campaign_id` + "/train.yzx.txt"
    test_path = config.data_folder + `config.campaign_id` + "/test.yzx.txt"
    train_data = Dataset(train_path, config.campaign_id)
    train_data.shuffle() # make train data shuffled
    test_data = Dataset(test_path, config.campaign_id)
    
    # no interval setting
    BidLandscape(train_data, train_data.get_camp_id(), config.laplace)
    BidLandscape(test_data, test_data.get_camp_id(), config.laplace)
    print "Load done."

    # downsampling
    train_data_ds = train_data.down_sampling(config.ds_ratio) if config.ds_ratio>0 else train_data
    print train_data_ds.get_statistics()
    print "Down sampled."

    em_model = EmModel(train_data_ds, test_data, model_name)
    print "campaign v = " + `em_model.camp_v`

    # train
    print "Begin training ..."
    for i in range(0, config.em_round):
        em_model.train()
        print "EM Round " + `i+1` + "\t" + `tool.get_last_log(em_model.em_log)['performance']`
        if tool.judge_stop(em_model.em_log):
            break;
    print "Train done."

    # em_rr_2997_3_0.1_0.csv
    log_file = "em_" + model_name \
                + "_" + `config.campaign_id` \
                + "_" + `config.budget_prop` \
                + "_" + `config.laplace` \
                + "_" + `config.em_scale` \
                + "_" + `config.ds_ratio` \
                + ".csv"
    fo = open("../output/" + log_file, 'w')

    print "Begin log ..."
    header = "camp_id\tmodel\tdataset\trevenue\troi\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\tscale\tds_ratio\tbudget_prop\tem_round\tmu"
    best_em_log = em_model.get_best_log(em_model.em_log)
    best_em_line = `config.campaign_id` + "\t" + "em"+model_name + "\ttest\t" \
                    + tool.gen_performance_line(best_em_log) + "\t" \
                    + `config.laplace` + "\t" + "None" + "\t" + `config.em_scale` + "\t" \
                    + (`config.ds_ratio` if config.ds_ratio>0 else "None") + "\t" \
                    + `config.budget_prop` +"\t" \
                    + `len(em_model.em_log)` + "\t" + `best_em_log['mu']`

    fo.write(header + "\n")
    fo.write(best_em_line + "\n")

    fo.write("Test with Budget Constraints\n")

    # # reset mu
    # em_model.mu = best_em_log['mu']
    # em_model.bid_strategy.set_mu(em_model.mu)
    # # replay
    # fo.write("prop\trevenue\troi\tctr\tcpc\tauc\trmse\tcpm\timps\tclks\n")
    # for prop in config.budget_props:
    #     performance = em_model.replay(best_em_log['weight'], em_model.test_data, prop)
    #     fo.write(`prop`); fo.write("\t")
    #     fo.write(`performance['revenue']`); fo.write("\t")
    #     fo.write(`performance['roi']`); fo.write("\t")
    #     fo.write(`performance['ctr']`); fo.write("\t")
    #     fo.write(`performance['cpc']`); fo.write("\t")
    #     fo.write(`performance['auc']`); fo.write("\t")
    #     fo.write(`performance['rmse']`); fo.write("\t")
    #     fo.write(`performance['cpm']`); fo.write("\t")
    #     fo.write(`performance['imps']`); fo.write("\t")
    #     fo.write(`performance['clks']`); fo.write("\t")
    #     fo.write("\n")


    fo.write("\n")

    fo.write("Round\trevenue\troi\tcpc\tctr\tauc\trmse\timps\ttruncate\tmu\n")
    for i in range(0, len(em_model.em_log)):
        em_log = em_model.em_log[i]
        line = `i+1` + "\t" + `em_log['performance']['revenue']` + "\t" \
                + `em_log['performance']['roi']` + "\t" \
                + `em_log['performance']['cpc']` + "\t" \
                + `em_log['performance']['ctr']` + "\t" \
                + `em_log['performance']['auc']` + "\t" \
                + `em_log['performance']['rmse']` + "\t" \
                + `em_log['performance']['imps']` + "\t" \
                + `em_log['weight'][0]` + "\t" \
		+ `em_log['mu']`
        fo.write(line + "\n")
    fo.write("\n")
    for i in range(0, len(em_model.test_log)):
        test_log = em_model.test_log[i]
        line = `i+1` + "\t" + `test_log['performance']['revenue']` + "\t" \
                + `test_log['performance']['roi']` + "\t" \
                + `test_log['performance']['cpc']` + "\t" \
                + `test_log['performance']['ctr']` + "\t" \
                + `test_log['performance']['auc']` + "\t" \
                + `test_log['performance']['rmse']` + "\t" \
                + `test_log['performance']['imps']` + "\t" \
                + `test_log['weight'][0]`
        if 'm' in test_log:
            line = line + "\tm"
        fo.write(line + "\n")

    fo.close()
    print "Log done."

if __name__ == '__main__':
    main()
