#!/usr/bin/python
from bid_strategy import BidStrategy

class McpcBid(BidStrategy):
	def __init__(self, camp_v):
		self.camp_v = camp_v

	def set_camp_value(self, v):
		self.camp_v = v

	def bid(self, ctr):
		bid_price = int(self.camp_v * ctr * 1E3)
# 		print "bid price \t" + `bid_price`
		return bid_price

def main():
	print "main method."

if __name__ == '__main__':
	main()