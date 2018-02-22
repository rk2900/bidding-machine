import math
import random
import copy
import tool
import config
from model import Model
from dataset import Dataset
from lin_market import LinMarket

class QuadMarket(LinMarket):
	def __init__(self, train_data, test_data):
		LinMarket.__init__(self, train_data, test_data)
		self.B = 300
		self.low_bound = 20

	def get_probability(self, z, x):
		if config.DEBUG: print z
		alpha, sig = self.calc_alpha(x, False) # maximum of market price
		if config.DEBUG: print "alpha = " + `alpha`
		if z > alpha:
			prob = 1E-50
		else:
			prob = 2.0 / alpha - 2.0 * z / (alpha*alpha)
		if config.DEBUG: print "prob = " + `prob`
		return prob

	def get_win_probability(self, b, x):
		prob = 1E-50
		if b == 0:
			prob = 1E-50
		else:
			alpha, sig = self.calc_alpha(x, False)
			if b > alpha:
				prob = 1.0
			else:
				tmp = 1.0 * b / alpha
				prob = tmp * (2 - tmp)
		return prob

	# alpha(x; phi) = e^(phi^T*x)
	def calc_alpha(self, x, train_flag=False):
		product = tool.phi_t_x(self.weight, x, train_flag)
		if config.DEBUG: print "product = " + `product` 
		sig = tool.sigmoid(product)
		alpha = self.B * sig + self.low_bound
		return alpha, sig

	def calc_gradient_coeff(self, x, y, b, train_flag=True):
		alpha, sig = self.calc_alpha(x, True)
		if config.DEBUG: print "----------------> Alpha = " + `alpha`
		# if b > alpha: # may cause unpredictable results !!!
		# 	coeff = 1E-50
		# else:

		divide = 1.0 * b / alpha
		# if config.DEBUG: print "divide = " + `divide`
		# coeff = (4.0/3.0*b*math.pow(divide,2) - divide*b) - 2.0 * self.camp_v * y * (math.pow(divide, 2) - divide)
		coeff = ((4.0/3.0*b*math.pow(divide,2) - divide*b) - 2.0 * self.camp_v * y * (math.pow(divide, 2) - divide)) * (1 - sig) # * self.B
		
		# if config.DEBUG: print "coeff = " + `coeff`
		return coeff