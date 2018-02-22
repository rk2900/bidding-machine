import os
import sys

if len(sys.argv) < 2:
	print "Usage: python stat_pos_neg.py make-ipinyou-data-folder"
	exit(-1)

path = sys.argv[1]

# path above campaign folders
campaign_list = [1458, 2259, 2261, 2821, 2997, 3358, 3386, 3427, 3476]
stat_dict = dict((camp, (0,0)) for camp in campaign_list)

for camp in campaign_list:
	count_pos = 0
	count_neg = 0

	data_path = path + '/' + `camp` + '/' + 'test.yzx.txt'
	with open(data_path) as fi:
		for line in fi:
			li = line.split()
			y = int(li[0])
			if y>0:
				count_pos += 1
			else:
				count_neg += 1
	print "%d\t%d\t%d" % (camp, count_pos, count_neg)
