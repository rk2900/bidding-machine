#!/usr/bin/python
import os
import tool
import copy
import random

class Dataset:
	'''The class for data loading and storage.'''

	def __init__(self, file_path, camp_id):
		self.file_path = file_path
		self.camp_id = camp_id
		self.init_statistics()
		self.load()
		self.iterators = []

	def load(self): # load data from the specified file path
		print "Loading data ..."
		self.dataset = []
		if not os.path.isfile(self.file_path):
			print "ERROR: file not exist. " + self.file_path
			exit(-1)
		size = 0
		cost_sum = 0
		clk_sum = 0
		max_price = -1
		fi = open(self.file_path, 'r')
		for line in fi:
			li = tool.ints(line.replace(':1','').split())
			if self.camp_id < 0:
				li.append(-1)
			self.dataset.append(li)
			y = li[0]
			mp = li[1]
			size += 1
			cost_sum += mp
			max_price = mp if mp > max_price else max_price
			clk_sum += y
		fi.close()
		self.statistics['size'] = size
		self.statistics['cost_sum'] = cost_sum
		self.statistics['clk_sum'] = clk_sum
		self.statistics['ecpm'] = 1.0 * cost_sum / size
		self.statistics['ecpc'] = int(cost_sum / clk_sum * 1E-3)
		self.statistics['ctr'] = 1.0 * clk_sum / size
		self.statistics['max_price'] = max_price
		print "Loaded."
		print self.get_statistics()		

	def shuffle(self):
		random.seed(200)
		random.shuffle(self.dataset)

	def init_statistics(self): # init all the statistic elements
		self.statistics = {'size':0, 'cost_sum':0, 'clk_sum':0, 
							'ecpm':0, 'ecpc':0, 'ctr':0.0, 'max_price':0}
	
	def update_statistics(self):
# 		print "update statistics \t" + `self`
		size = 0
		cost_sum = 0
		clk_sum = 0
		max_price = -1
		for data in self.dataset:
			y = data[0]
			mp = data[1]
			size += 1
			cost_sum += mp
			max_price = mp if mp > max_price else max_price
			clk_sum += y
		self.statistics['size'] = size
		self.statistics['cost_sum'] = cost_sum
		self.statistics['clk_sum'] = clk_sum
		self.statistics['ecpm'] = 1.0 * cost_sum / size
		self.statistics['ori_ecpc'] = self.statistics['ecpc']
		self.statistics['ecpc'] = cost_sum / clk_sum * 1E-3
		self.statistics['ctr'] = 1.0 * clk_sum / size
		self.statistics['max_price'] = max_price

	def init_landscape(self, landscape): # record the bid landscape into the dataset instance
		self.landscape = landscape

	def set_landscape(self, landscape):
		self.landscape = landscape

	def down_sampling(self, ratio):
# 		print "original dataset \t " + `self`
		ds_dataset = copy.deepcopy(self)
# 		print "downsampled dataset \t" + `ds_dataset`
		ds_dataset.self_down_sampling(ratio)
		return ds_dataset
	
	def self_down_sampling(self, ratio):
		random.seed(20)
		ds_dataset = []
		neg_dataset = []
		pos_num = self.statistics['clk_sum']
		neg_num = self.get_size() - pos_num
		desired_neg_num = int(neg_num * ratio) # desired_neg_num if desired_neg_num < neg_num else neg_num 
		for data in self.dataset:
			y = data[0]
			if y == 1:
				ds_dataset.append(copy.deepcopy(data))
			else:
				neg_dataset.append(copy.deepcopy(data))
		ds_dataset += random.sample(neg_dataset, desired_neg_num)
		#TODO update statistics, e.g. size
		self.dataset = ds_dataset
		self.update_statistics()
		random.shuffle(ds_dataset)
		self.init_all_iterators()

	def get_camp_id(self):
		return self.camp_id

	def get_statistics(self):
		return self.statistics

	def get_landscape(self):
		if self.landscape == None:
			print "ERROR: Please init landscape first. [Dataset.init_landscape(landscape)]"
		return self.landscape

	def get_dataset(self):
		return self.dataset

	def init_index(self): # initialize an iterator and store it
		self.iterators.append(0)
		iter_id = len(self.iterators) - 1
		return iter_id
	
	def init_all_iterators(self):
		iter_num = len(self.iterators)
		if iter_num > 0:
			for idx in range(0, iter_num):
				self.iterators[idx] = 0

	def get_next_data(self, iter_id): # get the next data in the dataset
		if self.iterators[iter_id] >= self.get_size():
			self.iterators[iter_id] = 0
		data = self.dataset[self.iterators[iter_id]]
		self.iterators[iter_id] = self.iterators[iter_id] + 1
		return data

	def get_progress(self, iter_id):
		progress = 1.0 * self.iterators[iter_id] / self.get_size()
		return progress

	def get_size(self): # get the volume size of the dataset
		return self.statistics['size']

	def get_max_price(self):
		return self.statistics['max_price']

	def reached_tail(self, iter_id): # judge whether the last data have been reached
		flag = (self.iterators[iter_id] >= self.get_size())
		return flag


def main():
	print "main method."

if __name__ == '__main__':
	main()
