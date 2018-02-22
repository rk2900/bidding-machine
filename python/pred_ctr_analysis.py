#!/usr/bin/python
import sys
import os
import random
import math
import operator
import matplotlib as mpl
import matplotlib.pyplot as ppl

BASE = math.log(10)

def makeDist(li, num, diff, top): # li: list; num: number of array; top: the largest index of returned array
	dic = {}	
	statY = [0 for i in range(0, num)]
	for value in li:
		index = binaryFit(0,num,value,diff)
		if index<0:
			print 'The largest value '+`value`+'\'s index is less than zero.'
		else:
			statY[index] = statY[index]+1
	return statY[0:top]

def binaryFit(left, right, value, diff=1):
	if left == right-1:
		return left
	mediate = int((left+right)/2)
	if mediate*diff == value:
		return mediate
	if value >= left*diff and value < (mediate*diff):
		return binaryFit(left, mediate, value, diff)
	if value >= (mediate*diff) and value <= right*diff:
		return binaryFit(mediate, right, value, diff)
	else:
		return -1

num = 1000000
top = 40000
ctrPredFile = '../../make-ipinyou-data/1458/test.yzx.txt.lr.pred'
if len(sys.argv) == 2:
	ctrPredFile = sys.argv[1]
fi = open(ctrPredFile, 'r')

# read in predicted CTRs
ctrs = []
for line in fi:
	ctrs.append(float(line.strip()))
maxV = -100000.0;
minV = 100000.0;
for value in ctrs:
	if value > maxV:
		maxV = value
	if value < minV:
		minV = value
diff = (maxV-minV)/num
print 'max value is ' + `maxV`
print 'min value is ' + `minV`
print 'diff value is ' + `diff`
print 'size of all ctrs is ' + `len(ctrs)`

# make statistics
maxY = 0
statY = makeDist(ctrs, num, diff, top)
statX = []
for i in range(0, len(statY)):
	maxY = (statY[i] if maxY < statY[i] else maxY)
	statX.append(i*diff)
	# statY[i] = math.log(statY[i])

# print statY
# print len(statY)

# # test phase
# print binaryFit(2,100,7.5,0.1)

ppl.scatter(statX, statY)#, 'b-', label='Predicted CTR')
ppl.ylabel('Statistic Number')
ppl.xlabel('Predicted CTR')
ppl.xlim(0,statX[len(statX)-1])
ppl.ylim(0,100*math.ceil(maxY*1.0/100))
ppl.show()