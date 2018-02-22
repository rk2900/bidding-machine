import sys
import random
import math
import operator
import tool

if len(sys.argv) < 3:
	print "python integrate_click.py bid_mp_file click_file output_file"
	exit(-1)

bid_mp_file = open(sys.argv[1], 'r')
click_file = open(sys.argv[2], 'r')
out_file = open(sys.argv[3], 'w')

bi_list = zip(bid_mp_file, click_file)

for (line_a, line_b) in bi_list:
	li_a = tool.ints(line_a.split())
	li_b = tool.ints(line_b.split())
	clk = li_b[0]
	bi = li_a[0]
	mp = li_a[1]
	out_file.write(`bi` + "\t" + `mp` + "\t" + `clk` + "\n")

bid_mp_file.close()
click_file.close()
out_file.close()