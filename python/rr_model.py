from eu_model import EuModel
from bid_landscape import BidLandscape
from bid_strategy import BidStrategy
from dataset import Dataset
import math
import random
import tool
import config

class RrModel(EuModel):
    def __init__(self, train_data, test_data):
        EuModel.__init__(self, train_data, test_data)

    def train(self):
        random.seed(10)
        train_data = self.train_data
        progress = 0.0
        iter_id = train_data.init_index()
        while not train_data.reached_tail(iter_id):
            data = train_data.get_next_data(iter_id)
            y = data[0]
            feature = data[2:len(data)]
            ctr = tool.estimate_ctr(self.weight, feature, train_flag=True)
            phi = 1.0 / (1.0 + self.mu)
            bp = self.bid_strategy.bid(ctr)
            pz = self.train_data.landscape.get_probability(bp)
            # print `bp` + '\t' + `pz`
            scale_x = (phi * ctr - y) * phi * math.pow(self.camp_v, 2) * pz * config.eu_scale
            for idx in feature:
                self.weight[idx] = self.weight[idx] * self.reg_update_param - config.lr_alpha * scale_x
            # prg = train_data.get_progress(iter_id)
            # if prg < 0.9 and prg > (progress + config.train_progress_unit - 1E-3):
            #     self.test()
            #     progress += config.train_progress_unit
