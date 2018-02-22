#!/usr/bin/python

class Model:
	def __init__(self, train_data, test_data):
		self.set_train_data(train_data)
		self.set_test_data(test_data)

	def set_train_data(self, train_data):
		self.train_data = train_data

	def set_test_data(self, test_data):
		self.test_data = test_data

	def train(self):
		pass

	def converged(self):
		pass
		return False

	def test(self):
		pass

	def calc_performance(self, dataset):
		pass

def main():
	print "main method."

if __name__ == '__main__':
	main()