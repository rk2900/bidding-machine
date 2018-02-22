#!/usr/bin/python
from dataset import Dataset
import config
import sys

if len(sys.argv) > 1:
    config.campaign_list = [int(sys.argv[1])]

fo = open("../output/statistics.csv", 'w')
header = "camp_id\tdataset\tmax_price\tctr\tecpc\tecpm\tclk_sum\tcost_sum\tsize\n"

fo.write(header)

for camp_id in config.campaign_list:
    train_dataset = Dataset(config.data_folder+`camp_id`+config.train_postfix, camp_id)
    tr_stat = train_dataset.get_statistics()
    
    test_dataset = Dataset(config.data_folder+`camp_id`+config.test_postfix, camp_id)
    te_stat = test_dataset.get_statistics()

    tr_line = "%d\t%s\t%d\t%f\t%d\t%d\t%d\t%d\t%d\n" % (camp_id, "train", tr_stat['max_price'], tr_stat['ctr'], 
                                                    tr_stat['ecpc'], tr_stat['ecpm'], tr_stat['clk_sum'], 
                                                    tr_stat['cost_sum'], tr_stat['size'])
    te_line = "%d\t%s\t%d\t%f\t%d\t%d\t%d\t%d\t%d\n" % (camp_id, "test", te_stat['max_price'], te_stat['ctr'], 
                                                    te_stat['ecpc'], te_stat['ecpm'], te_stat['clk_sum'], 
                                                    te_stat['cost_sum'], te_stat['size'])

    fo.write(tr_line)
    fo.write(te_line)

    del train_dataset
    del test_dataset

    print "Deleted " + `camp_id`
fo.close()

print "done"