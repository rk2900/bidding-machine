import os
import sys


def dump(folder, file_name):
	endfix = '.csv'
	name_params = file_name.split(endfix)[0].split('_')
	length = len(name_params)
	mkt_alpha = name_params[length - 2]
	mkt_lambda = name_params[length - 1]
	print mkt_alpha, mkt_lambda
	#--- read in ---#
	file_path = folder + "/" + file_name
	if not file_path.endswith(endfix):
		return 0
	print file_path
	# raw_input("Pause ...")
	log = []
	fi = open(file_path)
	for line in fi:
		log.append(line)
	fi.close()
	#--- process ---#
	fo = open(file_path, 'w')
	fo.write(log[0].split('\n')[0] + "\tmkt_alpha\tmkt_lambda" + "\n")
	fo.write(log[1].split('\n')[0] + "\t" + mkt_alpha + "\t" + mkt_lambda + "\n")
	log = log[2:]
	for line in log:
		fo.write(line)
	fo.close()
	print "Done.\t" + file_name

def main():
	if len(sys.argv) < 2:
		print "The script will add the two market model parameters to the best performance log.\n" \
				+ "Usage: python fix_mkt_param_log.py folder/"
		exit(-1)
	folder = sys.argv[1]
	print "Folder: " + folder
	files = os.listdir(folder)
	print files
	for f in files:
		dump(folder, f)


if __name__ == '__main__':
    main()