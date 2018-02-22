#!/usr/bin/python
import os
import sys

def get_header(folder):
	files = os.listdir(folder)
	header = "camp_id\tmodel\tdataset\trevenue\tROI\tctr\tcpc\tauc\trmse\tcpm\tbids\timps\tclks\tlaplace\tinterval\tscale\tds_ratio\tbudget_prop\tmkt_alpha\tmkt_lambda"
	for f in files:
		if not f.endswith('.csv'):
			continue
		file_path = os.path.join(folder, f)
		fi = open(file_path)
		lines = fi.read().split('\n')
		if len(lines) < 2:
			continue
		header = lines[0]; break
	return header



if len(sys.argv) < 2:
	print "Usage: python yoyi_make_output.py folder/"
	exit(-1)

folder = sys.argv[1]
files = os.listdir(folder)

fo = open(folder + '/integration.txt', 'w')
header = get_header(folder)
fo.write(header + '\n')

for f in files:
	if not f.endswith('.csv'):
		continue
	file_path = os.path.join(folder, f)
	fi = open(file_path)
	lines = fi.read().split('\n')
	if len(lines) < 2:
		continue
	fo.write(lines[1] + '\n')
	fi.close()

fo.close()