import math
import random
import copy
import config
from model import Model

class MarketModel(Model):
	def __init__(self, train_data, test_data):
		Model.__init__(self, train_data, test_data)
		self.init_weight()

	def init_parameters(self):
		self.camp_v = self.train_data.get_statistics()['ori_ecpc'] if config.ds_flag else self.train_data.get_statistics()['ecpc']
		self.test_log = []

	def init_weight(self):
		self.weight = {}
		self.best_weight = {}

	def set_camp_v(self, camp_v):
		self.camp_v = camp_v

	def set_ctr_model(self, ctr_model):
		self.ctr_model = ctr_model

	def set_bid_strategy(self, strategy):
		self.bid_strategy = strategy

	def get_probability(self, b, x):
		pass

	def get_win_probability(self, b, x):
		pass

	def calc_gradient_coeff(self, x, y, b):
		pass

	def update(self, x, y, b):
		pass

	def calc_nlp(self, x, z):
		prob = self.get_probability(z,x)
		if config.DEBUG: print `z` + '\t' + `prob`
		nlp = -1.0 * math.log(prob)
		return nlp

	def calc_total_anlp(self, dataset):
		idx = dataset.init_index()
		anlp = 0.0
		counter = 0
		while not dataset.reached_tail(idx):
			counter += 1
			data = dataset.get_next_data(idx)
			z = data[1]
			x = data[2:len(data)]
			anlp += self.calc_nlp(x, z)
		anlp /= counter
		return anlp

	def train(self):
		pass

	def joint_train(self):
		random.seed(10)
		train_data = self.train_data
		ctr_model = self.ctr_model
		bid_strategy = self.bid_strategy
		iter_id = train_data.init_index()
		while not train_data.reached_tail(iter_id):
			data = train_data.get_next_data(iter_id)
			y = data[0]
			feature = data[2:len(data)]
			ctr = ctr_model.estimate_ctr(ctr_model.get_weight(), feature, train_flag=True, ctr_avg=ctr_model.train_data.get_statistics()['ctr'])
			bp = self.bid_strategy.bid(ctr)
			self.update(feature, y, bp)

	def test(self):
		anlp = self.calc_total_anlp(self.test_data)
		log = self.make_log(self.weight, anlp)
		self.test_log.append(log)
		return anlp

	def make_log(self, weight, anlp):
		log = {}
		log['weight'] = copy.deepcopy(weight)
		log['anlp'] = anlp
		return log