from bid_strategy import BidStrategy
import config

class OptBid(BidStrategy):
	def __init__(self, camp_v, mu):
		self.mu = mu
		self.phi = 1.0 / (1.0 + self.mu)
		self.camp_v = camp_v

	def set_camp_value(self, v):
		self.camp_v = v

	def set_mu(self, mu):
		self.mu = mu
		self.phi = 1.0 / (1.0 + self.mu)

	def calibrate(self, ctr):
		ctr_calib = ctr / (ctr + (1 - ctr) / config.ds_ratio)
		return ctr_calib

	def bid_calib(self, camp_v, mu, ctr):
		bid_price = int(camp_v * self.calibrate(ctr) / (1.0 + mu) * 1E3)
		return bid_price

	# b = 1.0 / (1.0 + mu) * ctr
	def bid(self, ctr):
		bid_price = int(1.0 / (1.0 + self.mu) * self.camp_v * ctr * 1E3)
		return bid_price