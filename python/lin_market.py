import math
import tool
import config
from model import Model
from market_model import MarketModel


class LinMarket(MarketModel):
	def __init__(self, train_data, test_data):
		Model.__init__(self, train_data, test_data)
		self.init_parameters()
		self.init_weight()
		self.reg_update_param = 1 - config.market_alpha * config.market_lambda
		print "Linear Market Model camp_v: " + `self.camp_v`
		print "reg_update_param: " + `self.reg_update_param`

	def get_probability(self, z, x):
		result = 1E-50
		# if z == 0:
		# 	result = 1E-50
		# else:
		exp = tool.phi_t_x(self.weight, x)
		ma = math.exp(exp) # maximum of market price
		if z > ma:
			result = 1E-50
		else:
			result = 1.0 / ma
		return result

	def get_win_probability(self, b, x):
		result = 1E-50
		if b == 0:
			result = 1E-50
		else:
			exp = tool.phi_t_x(self.weight, x)
			ma = math.exp(exp) # maximum of market price
			if b > ma:
				result = 1.0
			else:
				result = 1.0 * b / ma
		return result

	def calc_gradient_coeff(self, x, y, b, train_flag=True):
		exp = tool.phi_t_x(self.weight, x, train_flag)
		if config.DEBUG: print "exp: " + `exp`
		exp_result = math.exp(exp) # MAX market price
		if config.DEBUG: print "exp_result: " + `exp_result`
		coeff = (b * b / 2 - self.camp_v * y * b) * (-1.0) / exp_result
		return coeff

	def update(self, x, y, b):
		gradient_coeff = self.calc_gradient_coeff(x, y, b, train_flag=True)
		if config.DEBUG: print "gradient_coeff: " + `gradient_coeff`
		for idx in x:
			if idx not in self.weight:
				self.weight[idx] = tool.next_init_weight()
			else:
				self.weight[idx] = self.weight[idx] * self.reg_update_param - config.market_alpha * gradient_coeff # * 1 of weight[idx]

	# Note: This is the self-train function, with ground truth market price z.
	def train(self):
		idx = self.train_data.init_index()
		count = 0
		while not self.train_data.reached_tail(idx):
			# count += 1
			# if count > 1000:
			# 	exit(0)
			data = self.train_data.get_next_data(idx)
			y = data[0]
			z = data[1]
			x = data[2:len(data)]
			self.update(x, y, z)

	def load_weight(self, path):
		self.weight = tool.load_weight(path)
		if self.weight == None:
			print "Error: load weight error!"
			exit(-1)
		else:
			return True