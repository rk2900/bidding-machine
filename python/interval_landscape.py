#!/usr/bin/python
from bid_landscape import BidLandscape

class IntervalLandscape(BidLandscape):
	'''The interval style bid landscape.'''

	def __init__(self, dataset, campaign_id, laplace=1, interval=2):
		BidLandscape.__init__(self, dataset, campaign_id, laplace)
		self.interval = interval if not (interval > self.max_price) else (self.max_price + 1)

	#TODO test the interval mode
	def get_probability(self, price):
		if price > self.max_price:
			return self.get_probability(self.max_price)
		left_index = int(price / self.interval) * self.interval
		idx = left_index + self.interval
		right_index = len(self.distribution) if len(self.distribution) < idx else idx
		probability = 0.0
		for p in range(left_index, right_index):
			probability += self.distribution[p]
		return probability

def main():
	print "main method."

if __name__ == '__main__':
	main()