'''
Created on Dec 14, 2015

@author: rk
'''
from lr_model import LrModel
from bid_landscape import BidLandscape
from opt_bid import OptBid
from dataset import Dataset
import math
import random
import tool
import config

class EuModel(LrModel):
    def __init__(self, train_data, test_data):
        LrModel.__init__(self, train_data, test_data)
        
    def init_parameters(self):
        self.camp_v = self.train_data.get_statistics()['ecpc']
        if config.ds_ratio > 0:
            self.ori_camp_v = self.train_data.get_statistics()['ori_ecpc']
        self.budget = int(self.test_data.get_statistics()['cost_sum'] / config.budget_prop)
        self.mu = 0.0
    
    def init_bid_strategy(self):
        self.bid_strategy = OptBid(self.camp_v, self.mu)

    def train(self):
        random.seed(10)
        train_data = self.train_data
        progress = 0.0
        iter_id = train_data.init_index()
        while not train_data.reached_tail(iter_id):
            data = train_data.get_next_data(iter_id)
            y = data[0]
            feature = data[2:len(data)]
            ctr = self.estimate_ctr(self.weight, feature, train_flag=True, ctr_avg=train_data.get_statistics()['ctr'])
            # tool.estimate_ctr(self.weight, feature, train_flag=True)
            phi = 1.0 / (1.0 + self.mu)
            bp = self.bid_strategy.bid(ctr)
            if config.PARAM_MARKET:
                pz = self.train_data.landscape.get_probability(bp, feature)
            else:
                pz = self.train_data.landscape.get_probability(bp)
            # print `bp` + '\t' + `pz`
            scale_x = (phi * ctr - y) * phi * math.pow(self.camp_v, 2) * pz * ctr * (1 - ctr) * config.eu_scale
            for idx in feature:
                self.weight[idx] = self.weight[idx] * self.reg_update_param - config.lr_alpha * scale_x
            # prg = train_data.get_progress(iter_id)
            # if prg < 0.9 and prg > (progress + config.train_progress_unit - 1E-3):
            #     self.test()
            #     progress += config.train_progress_unit

    def estimate_ctr(self, weight, feature, train_flag = False, ctr_avg=0.125):
        value = 0.0
        for idx in feature:
            if idx in weight:
                value += weight[idx]
            elif train_flag:
                if idx == 0:
                    weight[idx] = - math.log(1.0 / (ctr_avg) - 1.0)
                else:
                    weight[idx] = tool.next_init_weight()
        ctr = tool.sigmoid(value)
    #   print "Estimated CTR \t" + `ctr`
        return ctr