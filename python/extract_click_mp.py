import sys
import random
import math
import operator
import tool

if len(sys.argv) < 3:
	print "python extract_click_mp.py test.yzx.txt camp_click.txt"
	exit(-1)

test_file = open(sys.argv[1], 'r')
out_file = open(sys.argv[2], 'w')

for line in test_file:
	li = tool.ints(line.replace(':1','').split())
	clk = li[0]
	mp = li[1]
	out_file.write(`clk` + "\t" + `mp` + "\n")

test_file.close()
out_file.close()