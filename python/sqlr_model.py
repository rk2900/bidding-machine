from lr_model import LrModel
from bid_landscape import BidLandscape
from opt_bid import OptBid
from dataset import Dataset
import math
import random
import tool
import config

class SqlrModel(LrModel):
	def __init__(self, train_data, test_data):
		LrModel.__init__(self, train_data, test_data)

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
			ctr = self.estimate_ctr(self.weight, feature, train_flag=True, ctr_avg=train_data.get_statistics()['ctr'])
			for idx in feature: # update
				self.weight[idx] = self.weight[idx] * self.reg_update_param - config.lr_alpha * (ctr - y) * ctr * (1-ctr)
			# prg = train_data.get_progress(iter_id)
			# if prg < 0.9 and prg > (progress + config.train_progress_unit - 1E-3):
			# 	self.test()
			# 	progress += config.train_progress_unit
	
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