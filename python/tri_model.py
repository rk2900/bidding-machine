from lr_model import LrModel
from opt_bid import OptBid
from lin_market import LinMarket
from eu_model import EuModel
from dataset import Dataset
import math
import random
import copy
import tool
import config
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error


class TriModel(LrModel):
    def __init__(self, train_data, test_data, ctr_model, mkt_model, model):
        LrModel.__init__(self, train_data, test_data)
        if not model in config.model_list:
            print "Wrong model name when initializing EM model."
            exit(-1)
        self.model = model
        self.em_log = []
        self.ctr_model=ctr_model
        self.mkt_model=mkt_model

    def init_parameters(self):
        self.camp_v = self.train_data.get_statistics()['ecpc']
        if config.ds_ratio > 0:
            self.ori_camp_v = self.train_data.get_statistics()['ori_ecpc']
        self.mu = 0.0
        self.budget = int(self.test_data.get_statistics()['cost_sum'] / config.budget_prop)
        # budget is only used in test phase or M-step

    def init_bid_strategy(self):
        self.bid_strategy = OptBid(self.camp_v, self.mu)

    def train(self):
        #e_stop = False
        #loop = 0
        #while not e_stop:
        #    self.e_step()
        #    self.test()
        #    print "E step loop " + `loop+1` + "\t" + `self.test_log[len(self.test_log)-1]['performance']`
        #    e_stop = tool.judge_stop(self.test_log)
        #    loop += 1
        # self.test_log.pop(); self.test_log.pop() # delete the last two points
        #best_log = self.get_best_e_log(self.test_log)
        #print "Changed weight to the best one. the best revenue in last E phase is " + `best_log['performance']['revenue']`
        #self.weight = best_log['weight']
        #print "E step done."
        self.m_step()
        print "Optimal mu = " + `self.mu`
        print "M step done."

    def e_step(self):
        random.seed(10)
        train_data = self.train_data
        progress = 0.0
        iter_id = train_data.init_index()
        while not train_data.reached_tail(iter_id):
            data = train_data.get_next_data(iter_id)
            y = data[0]
            feature = data[2:len(data)]
            #ctr = tool.estimate_ctr(self.weight, feature, train_flag=True)
            ctr = self.ctr_model.estimate_ctr(self.ctr_model.weight, feature, train_flag = True)
            phi = 1.0 / (1.0 + self.mu)
            bp = self.bid_strategy.bid(ctr)
            pz = self.mkt_model.get_probability(bp, feature)
            scale_x = (phi * ctr - y) * phi * math.pow(self.camp_v, 2) * pz * config.em_scale
            if config.model_name == 'eu':
                scale_x = ctr * (1 - ctr) * scale_x
            # prg = train_data.get_progress(iter_id)
            # if prg < 0.9 and prg > (progress + config.train_progress_unit - 1E-3):
            #     self.test()
            #     progress += config.train_progress_unit

    def m_step(self):
        opt_mu = self.mu
        opt_revenue = -1E10
        opt_performance = {}
        test_data = self.test_data
        for mu in config.mu_range:
            bid_sum = 0
            cost_sum = 0
            imp_sum = 0
            clk_sum = 0
            revenue_sum = 0
            labels = []
            p_labels = []
            self.bid_strategy.set_mu(mu)
            iter_id = test_data.init_index()
            while not test_data.reached_tail(iter_id):
                data = test_data.get_next_data(iter_id)
                bid_sum += 1
                y = data[0]
                mp = data[1]
                feature = data[2:len(data)]
                ctr = self.ctr_model.estimate_ctr(self.ctr_model.weight, feature, train_flag = True)
                labels.append(y)
                p_labels.append(ctr)
                if config.ds_ratio > 0: # down sampled, needs to calibrate
                    bp = self.bid_strategy.bid_calib(self.ori_camp_v, mu, ctr)
                else:
                    bp = self.bid_strategy.bid(ctr)
                # bp = self.bid_strategy.bid(ctr)
                if bp > mp:
                    cost_sum += mp
                    imp_sum += 1
                    clk_sum += y
                    # revenue_sum = int(revenue_sum - mp + y * self.camp_v * 1E3)\
                    if config.ds_ratio > 0:
                        revenue_sum = int(revenue_sum - mp + y * self.ori_camp_v * 1E3)
                    else:
                        revenue_sum = int(revenue_sum - mp + y * self.camp_v * 1E3)
                if cost_sum >= self.budget:
                	break
            cpc = 0.0 if clk_sum == 0 else 1.0 * cost_sum / clk_sum * 1E-3
            cpm = 0.0 if imp_sum == 0 else 1.0 * cost_sum / imp_sum
            ctr = 0.0 if imp_sum == 0 else 1.0 * clk_sum / imp_sum
            roi = 0.0 if cost_sum == 0 else 1.0 * revenue_sum / cost_sum
            auc = roc_auc_score(labels, p_labels)
            rmse = math.sqrt(mean_squared_error(labels, p_labels))
            performance = {'bids':bid_sum, 'cpc':cpc, 'cpm':cpm,
                        'auc': auc, 'rmse': rmse,
                        'ctr': ctr, 'revenue':revenue_sum,
                        'imps':imp_sum, 'clks':clk_sum,
                        'roi': roi}
            print "current mu = " + `mu` + "\t" + `performance`
            if performance['revenue'] > opt_revenue:
                opt_revenue = performance['revenue']
                opt_performance = performance
                opt_mu = mu
        # reset the value of mu in both bidding function and model inner parameter
        self.bid_strategy.set_mu(opt_mu)
        self.mu = opt_mu
        log = self.make_log(self.ctr_model.weight, opt_performance)
        log['m'] = True
        self.test_log.append(log)
        self.em_log.append(log)

    def make_log(self, weight, performance):
        log = {}
        log['weight'] = copy.deepcopy(weight)
        log['performance'] = copy.deepcopy(performance)
        log['mu'] = self.mu
        return log

    def get_best_e_log(self, logs):
        best_log = {}
        if len(logs) == 0:
            print "ERROR: no record in the log."
        else:
            best_revenue = -1E10
            idx = len(logs)-1
            while idx>=0 and not 'm' in logs[idx]:
                log = logs[idx]
                revenue = log['performance']['revenue']
                if revenue > best_revenue:
                    best_revenue = revenue
                    best_log = log
                idx -= 1
        return best_log

    # def replay(self, weight, test_data, budget_prop):
    #     budget = int(1.0 * test_data.get_statistics()['cost_sum'] / budget_prop)
    #     mu = self.mu
    #     label = []
    #     p_labels = []
    #     bid_sum = 0
    #     cost_sum = 0
    #     imp_sum = 0
    #     clk_sum = 0
    #     revenue_sum = 0
    #     labels = []
    #     p_labels = []
    #     iter_id = test_data.init_index()
    #     while not test_data.reached_tail(iter_id):
    #         data = test_data.get_next_data(iter_id)
    #         bid_sum += 1
    #         y = data[0]
    #         mp = data[1]
    #         feature = data[2:len(data)]
    #         ctr = tool.estimate_ctr(weight, feature, train_flag=False)
    #         labels.append(y)
    #         p_labels.append(ctr)
    #         if config.ds_ratio > 0: # down sampled, needs to calibrate
    #             bp = self.bid_strategy.bid_calib(self.ori_camp_v, mu, ctr)
    #         else:
    #             bp = self.bid_strategy.bid(ctr)
    #         # bp = self.bid_strategy.bid(ctr)
    #         if bp > mp:
    #             cost_sum += mp
    #             imp_sum += 1
    #             clk_sum += y
    #             # revenue_sum = int(revenue_sum - mp + y * self.camp_v * 1E3)\
    #             if config.ds_ratio > 0:
    #                 revenue_sum = int(revenue_sum - mp + y * self.ori_camp_v * 1E3)
    #             else:
    #                 revenue_sum = int(revenue_sum - mp + y * self.camp_v * 1E3)
    #         if cost_sum >= budget:
    #             break
    #     cpc = 0.0 if clk_sum == 0 else 1.0 * cost_sum / clk_sum * 1E-3
    #     cpm = 0.0 if imp_sum == 0 else 1.0 * cost_sum / imp_sum
    #     ctr = 0.0 if imp_sum == 0 else 1.0 * clk_sum / imp_sum
    #     roi = 0.0 if cost_sum == 0 else 1.0 * revenue_sum / cost_sum
    #     auc = roc_auc_score(labels, p_labels)
    #     rmse = math.sqrt(mean_squared_error(labels, p_labels))
    #     performance = {'bids':bid_sum, 'cpc':cpc, 'cpm':cpm,
    #                 'auc': auc, 'rmse': rmse,
    #                 'ctr': ctr, 'revenue':revenue_sum,
    #                 'imps':imp_sum, 'clks':clk_sum,
    #                 'roi': roi}
    #     return performance
