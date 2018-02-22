from scipy.stats import ttest_ind
import os
import sys

def t_test(alist, blist):
	value = ttest_ind(alist, blist)
	return value

def read_file(path):
	li = []
	with open(path, 'r') as fi:
		li.append(fi.readline())

def main():
	if len(sys.argv) < 3:
		print "python t_test.py alist.txt blist.txt"
		exit(-1)

	alist = []
	blist = []

	v = t_test(alist, blist)

	print v

if __name__ == '__main__':
	main()