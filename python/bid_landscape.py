#!/usr/bin/python

class BidLandscape:
	'''The landscape making and storage class.'''

	def __init__(self, dataset, camp_id, laplace=1):
		self.dataset = dataset
		self.dataset.init_landscape(self)
		self.camp_id = camp_id
		self.laplace = laplace if laplace>1 else 1
		self.init_distribution()
		self.make_distribution()
		print "Inited Bid Landscape."

	def get_campaign_id(self):
		return self.camp_id

	def init_distribution(self):
		self.max_price = self.dataset.get_max_price()
		self.distribution = [0.0*i for i in range(0, self.max_price+1)]

	def get_distribution(self):
		return self.distribution

	def make_distribution(self): # make the original distribution with laplace smoothing
		mp_dict = {}
		iter_id = self.dataset.init_index()
		while not self.dataset.reached_tail(iter_id):
			data = self.dataset.get_next_data(iter_id)
			mp = data[1]
			if mp in mp_dict:
				mp_dict[mp] = mp_dict[mp] + 1
			else:
				mp_dict[mp] = 1
		total_num = self.dataset.get_size() + (self.max_price + 1) * self.laplace
		for p in range(0, self.max_price+1):
			if p not in mp_dict:
				self.distribution[p] = 1.0 * self.laplace / total_num
			else:
				self.distribution[p] = 1.0 * (mp_dict[p] + self.laplace) / total_num
		print "Landscape made."

	def get_probability(self, price): # get the probability of the given price in the landscape
		price = int(price)
		probability = 0.0
		if price > self.max_price:
			probability = self.distribution[self.max_price]
		elif price < 0:
			probability = self.distribution[0]
		else:
			probability = self.distribution[price]
		return probability




def main():
	print "main method."

if __name__ == '__main__':
	main()