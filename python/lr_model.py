#!/usr/bin/python
import copy
import random
from model import Model
from mcpc_bid import McpcBid
import tool
import config
from sklearn.metrics import roc_auc_score
from sklearn.metrics import mean_squared_error
import math

class LrModel(Model):
	def __init__(self, train_data, test_data):
		Model.__init__(self, train_data, test_data)
		self.init_parameters()
		self.init_weight()
		self.init_bid_strategy()
		self.reg_update_param = 1 - config.lr_alpha * config.lr_lambda
		# print self.reg_update_param
		self.train_log = []
		self.test_log = []

	def init_weight(self):
		self.weight = {}
		self.best_weight = {}

	def init_bid_strategy(self):
		self.bid_strategy = McpcBid(self.camp_v)

	def init_parameters(self):
		self.camp_v = self.train_data.get_statistics()['ecpc']
		self.mu = 0.0
		self.budget = int(self.test_data.get_statistics()['cost_sum'] / config.budget_prop)
		# print "camp_v \t " + `self.camp_v`

	def get_weight(self):
		if self.weight == None:
			print "ERROR: Please init the CTR model weight!"
		return self.weight

	def get_bid_strategy(self):
		if self.bid_strategy == None:
			print "ERROR: Please init bid strategy first."
		return self.bid_strategy

	def train(self): # train with one traversal of the full train_data
		random.seed(10)
		train_data = self.train_data
# 		print "Train data \t" + `train_data` + "\tsize \t" + `train_data.get_size()`
		progress = 0.0
		iter_id = train_data.init_index()
		while not train_data.reached_tail(iter_id):
			data = train_data.get_next_data(iter_id)
			y = data[0]
			feature = data[2:len(data)]
			ctr = tool.estimate_ctr(self.weight, feature, train_flag=True)
			for idx in feature: # update
				self.weight[idx] = self.weight[idx] * self.reg_update_param - config.lr_alpha * (ctr - y)
			# prg = train_data.get_progress(iter_id)
			# if prg < 0.9 and prg > (progress + config.train_progress_unit - 1E-3):
			# 	self.test()
			# 	progress += config.train_progress_unit

	def test(self):
		parameters = {'weight':self.weight}
		performance = self.calc_performance(self.test_data, parameters)
		# record performance
		log = self.make_log(self.weight, performance)
		self.test_log.append(log)

	def make_log(self, weight, performance):
		log = {}
		log['weight'] = copy.deepcopy(weight)
		log['performance'] = copy.deepcopy(performance)
		log['mu'] = self.mu
		return log

	def calc_performance(self, dataset, parameters): # calculate the performance w.r.t. the given dataset and parameters
		weight = parameters['weight']
		# budget = parameters['budget']
		bid_sum = 0
		cost_sum = 0
		imp_sum = 0
		clk_sum = 0
		revenue_sum = 0
		labels = []
		p_labels = []
		iter_id = dataset.init_index()
		while not dataset.reached_tail(iter_id): #TODO no budget set
			bid_sum += 1
			data = dataset.get_next_data(iter_id)
			y = data[0]
			market_price = data[1]
			feature = data[2:len(data)]
			ctr = tool.estimate_ctr(weight, feature, train_flag=False)
			labels.append(y)
			p_labels.append(ctr)
			if config.ds_ratio > 0: # down sampled, needs to calibrate
				bid_price = self.bid_strategy.bid_calib(self.ori_camp_v, self.mu, ctr)
			else:
				bid_price = self.bid_strategy.bid(ctr)
			if bid_price > market_price:
				cost_sum += market_price
				imp_sum += 1
				clk_sum += y
				if config.ds_ratio > 0:
					revenue_sum = int(revenue_sum - market_price + y * self.ori_camp_v * 1E3)
				else:
					revenue_sum = int(revenue_sum - market_price + y * self.camp_v * 1E3)
			if cost_sum >= self.budget:
				break
		cpc = 0.0 if clk_sum == 0 else 1.0 * cost_sum / clk_sum * 1E-3
		cpm = 0.0 if imp_sum == 0 else 1.0 * cost_sum / imp_sum
		ctr = 0.0 if imp_sum == 0 else 1.0 * clk_sum / imp_sum
		roi = 0.0 if cost_sum == 0 else 1.0 * (revenue_sum) / cost_sum
		auc = roc_auc_score(labels, p_labels)
		rmse = math.sqrt(mean_squared_error(labels, p_labels))
		performance = {'bids':bid_sum, 'cpc':cpc, 'cpm':cpm, 
						'ctr': ctr, 'revenue':revenue_sum, 
						'imps':imp_sum, 'clks':clk_sum,
						'auc': auc, 'rmse': rmse,
						'roi': roi}
		return performance

	def get_best_train_log(self):
		return self.get_best_log(self.train_log)
	
	def get_best_test_log(self):
		return self.get_best_log(self.test_log)

	def get_best_log(self, logs):
		best_log = {}
		if len(logs) == 0:
			print "ERROR: no record in the log."
		else:
			best_revenue = -1E30
			for log in logs:
				revenue = log['performance']['revenue']
				if revenue > best_revenue:
					best_revenue = revenue
					best_log = log
		return best_log

	def output_weight(self, weight, path):
		fo = open(path, 'w')
		for idx in weight:
			fo.write(`idx` + '\t' + `weight[idx]` + '\n')
		fo.close()

	def lin_bid(self, weight):
		params = range(30, 100, 5) + range(100, 400, 10) + range(400, 800, 50)
		base_ctr = self.train_data.get_statistics()['ctr']
		dataset = self.test_data
		opt_param = 3000
		opt_revenue = -1E10
		for param in params:
			bid_sum = 0
			cost_sum = 0
			imp_sum = 0
			clk_sum = 0
			revenue_sum = 0
			labels = []
			p_labels = []
			iter_id = dataset.init_index()
			while not dataset.reached_tail(iter_id): #TODO no budget set
				bid_sum += 1
				data = dataset.get_next_data(iter_id)
				y = data[0]
				market_price = data[1]
				feature = data[2:len(data)]
				ctr = tool.estimate_ctr(weight, feature, train_flag=False)
				labels.append(y)
				p_labels.append(ctr)
				bid_price = int(param * ctr / base_ctr)
				if bid_price > market_price:
					cost_sum += market_price
					imp_sum += 1
					clk_sum += y
					revenue_sum = int(revenue_sum - market_price + y * self.camp_v * 1E3)
				if cost_sum >= self.budget:
					break
			cpc = 0.0 if clk_sum == 0 else 1.0 * cost_sum / clk_sum * 1E-3
			cpm = 0.0 if imp_sum == 0 else 1.0 * cost_sum / imp_sum
			ctr = 0.0 if imp_sum == 0 else 1.0 * clk_sum / imp_sum
			roi = 0.0 if cost_sum == 0 else 1.0 * (revenue_sum) / cost_sum
			auc = roc_auc_score(labels, p_labels)
			rmse = math.sqrt(mean_squared_error(labels, p_labels))
			performance = {'bids':bid_sum, 'cpc':cpc, 'cpm':cpm, 
							'ctr': ctr, 'revenue':revenue_sum, 
							'imps':imp_sum, 'clks':clk_sum,
							'auc': auc, 'rmse': rmse,
							'roi': roi}
			if performance['revenue'] > opt_revenue:
				opt_revenue = performance['revenue']
				opt_param = param
		self.opt_param = opt_param
		return opt_param

	def replay(self, weight, test_data, budget_prop):
		budget = int(1.0 * test_data.get_statistics()['cost_sum'] / budget_prop)
		base_ctr = self.train_data.get_statistics()['ctr']
		label = []
		p_labels = []
		bid_sum = 0
		cost_sum = 0
		imp_sum = 0
		clk_sum = 0
		revenue_sum = 0
		labels = []
		p_labels = []
		iter_id = test_data.init_index()
		while not test_data.reached_tail(iter_id):
			data = test_data.get_next_data(iter_id)
			bid_sum += 1
			y = data[0]
			mp = data[1]
			feature = data[2:len(data)]
			ctr = tool.estimate_ctr(weight, feature, train_flag=False)
			labels.append(y)
			p_labels.append(ctr)
			bp = int(self.opt_param * ctr / base_ctr)
			# bp = self.bid_strategy.bid(ctr)
			if bp > mp:
				cost_sum += mp
				imp_sum += 1
				clk_sum += y
				revenue_sum = int(revenue_sum - mp + y * self.camp_v * 1E3)
			if cost_sum >= budget:
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
		return performance
