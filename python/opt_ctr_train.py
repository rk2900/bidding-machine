#!/usr/bin/python
import sys
import random
import math
import operator
import config
import tool

DEBUG = True
UNIFORM = False
LR = True 			# train LR simultaneously
SCALEMODE = False 	# search in range
INTVL = False 		# interval mode in bid landscape
DOWNSAMP = False 	# downsampling method

# part1: learning framework parameters
volume = 150000 	# auction data volume
proportion = 1 		# budget setting proportion
emRounds = 50 		# em train rounds
random.seed(10)
initWeight = 0.5
stopThr = 0.0005
interval = 5
scale = 0.05

# part2: hyper parameters
lamb = 1E-4
alpha = 0.005 # learning rate
updateParam = 1-alpha*lamb
laplaceK = 100
print 'updateParam = ' + `updateParam`

camp_v = -7000 		# eCPC
muRegion = [0.1*t for t in range(-10,0,1)] + [0.1*t for t in range(0, 20 ,1)]

# part3: parameters
mu = 0.0 # default parameter value in bidding function under 2nd-price
phi = 1.0 # update when mu is updated
featWeight = {} # empty feature weights
lrWeight = {}
landscape = [] # bid landscape p(z)

def ints(li):
	ili = []
	for value in li:
		ili.append(int(value))
	return ili

def nextInitWeight():
	return (random.random() - 0.5) * initWeight

# parameter in bidding function
def phiCalc():
	return 1.0 / (1+mu)

# sigmoid function
def sigmoid(z):
	value = 0.5
	try:
		value = 1.0 / (1.0 + math.exp(-z))
	except:
		config.math_err_num += 1
		value = 0.5
	return value

# winning function
def winningRate(b):
	prob = 0.0
	if b >= len(landscape):
		prob = 1.0
	else:
		for i in range(0, b+1):
			prob += landscape[i]
	return prob

# non-parametric method for making bid landscape p(z)
def makeBidLandscape(trainData, laplace):
	bidLand = []
	mpDict = {}
	maxPrice = 0
	totalNum = 0
	if DEBUG and UNIFORM:
		for data in trainData:
			maxPrice = data[1] if maxPrice < data[1] else maxPrice
		uniProb = 1.0/(maxPrice+1)
		bidLand = [uniProb for i in range(0, maxPrice+1)]
	else:
		for data in trainData:
			totalNum += 1
			mp = data[1]
			if mp > maxPrice:
				maxPrice = mp
			if mp in mpDict:
				mpDict[mp] = mpDict[mp] + 1
			else:
				mpDict[mp] = 1
		totalNum += (maxPrice+1)*laplace
		bidLand = [0.0 for i in range(0, maxPrice+1)]
		for p in range(0, maxPrice+1):
			if p not in mpDict:
				bidLand[p] = 1.0 * laplace / totalNum
			else:
				bidLand[p] = 1.0 * (mpDict[p]+laplace) / totalNum	
	return bidLand

def downsampling(trainData, ratio):
	downData = []
	posSet = []
	negSet = []
	for data in trainData:
		y = data[0]
		if int(y)==1:
			posSet.append(data)
		else:
			negSet.append(data)
	posLength = len(posSet)
	negLength = int(posLength/ratio)
	if negLength>=len(negSet):
		downData = trainData
	else:
		downData = posSet + random.sample(negSet, negLength)
	random.shuffle(downData)
	return downData

# market price PDF p_z(z)
def mktPrcProb(z):
	z = int(z)
	prob = landscape[len(landscape)-1]
	if z >= len(landscape):
		z = len(landscape)-1
	if not INTVL:
		prob = landscape[z]
	else:
		leftIndex = int(z/interval) * interval
		idx = leftIndex + interval
		rightIndex = len(landscape) if len(landscape)<idx else idx
		prob = 0.0
# 		print `leftIndex` + '\t' + `rightIndex`
		for i in range(leftIndex, rightIndex):
			prob += landscape[i]
	return prob

# gradient update procedure
def gradientUpdate(theta, x, y):
	ctr = ctrEstimate(theta, x, trainFlag=True)
	b = bidPrice(ctr, mu)
	pz = mktPrcProb(b)
	scaleX = (phi*ctr-y)*phi*math.pow(camp_v,2)*pz*scale *ctr*(1-ctr) # Eq.10
	# print '%d\t%.2f\t%.2f\t%.4f\t%.4f\t%.4f' % (b, phi, math.pow(camp_v,2), pz, phi*math.pow(camp_v,2)*pz, scaleX)
	for vT in x:
		theta[vT] = theta[vT] * updateParam - alpha * scaleX
	# updateParam = 1-alpha*lamb
	# theta[vX] = theta[vX] - alpha * (scaleX*1.0 + lamb*theta[vX])
	return theta

def LRUpdate(theta, x, y):
	ctr = ctrEstimate(theta, x, trainFlag=True)
	for vT in x:
		theta[vT] = theta[vT] * updateParam - alpha * (ctr - y)
	return theta

def LRSEUpdate(theta, x, y):
	ctr = ctrEstimate(theta, x, trainFlag=True)
	for vT in x:
		theta[vT] = theta[vT] * updateParam - alpha * (ctr - y) * 100 * ctr * (1-ctr)
	return theta

# ctr f(x) calculation
def ctrEstimate(theta, x, trainFlag=False):
	ctr = 0.0
	value = 0.0
	for vX in x:
		if vX not in theta:
			if trainFlag:
				theta[vX] = nextInitWeight()
				value += theta[vX]
			# else: print 'Feature weight has no value in the index '+`vX`
		else:
			value += theta[vX]
	# print 'value = ' + `value`
	ctr = sigmoid(value)
	return ctr

# bidding function (with price mode parameter)
def bidPrice(ctr, muV, mode=2):
	if mode == 1:
		return 0
	if mode == 2:
		return int(1.0 * camp_v * 1E3 * ctr / (1.0 + muV))
	else:
		print 'Please input correct auction mode as 1 or 2.'
		return 0

def trainPhaseE(weight, trainData):
	for data in trainData:
		y = data[0]
		x = data[2:len(data)]
		try:
			weight = gradientUpdate(weight, x, y)
		except:
			continue
	return weight

def trainLR(weight, trainData):
	for data in trainData:
		y = data[0]
		x = data[2:len(data)]
		weight = LRUpdate(weight, x, y)
	return weight

def trainLRSE(weight, trainData):
	for data in trainData:
		y = data[0]
		x = data[2:len(data)]
		weight = LRSEUpdate(weight, x, y)
	return weight

def trainPhaseMByNumeric(weight, trainData, budget, volume):
	lossMin = -100
	muOpt = mu
	for muV in muRegion:
		cost = 0
		for data in trainData:
			x = data[2:len(data)]
			ctr = ctrEstimate(weight, data)
			bp = bidPrice(ctr, mu, 2)
			cost += intzpz(bp)
		cost /= len(trainData)
		loss = math.fabs(budget/volume - cost) / (budget/volume)
		if loss < lossMin:
			muOpt = mu
			lossMin = loss
	return muOpt


def trainPhaseMByProfit(weight, trainData, budget, volume):
	profitMin = 9E100
	muOpt = -1
	for muV in muRegion:
		profit = 0 # campaign total profit
		cost = 0 # campaign total cost
		count = 0
		winCount = 0
		for data in trainData:
			count += 1
			y = data[0]
			mp = data[1]
			x = data[2:len(data)]
			ctr = ctrEstimate(weight, x)
			bid = bidPrice(ctr, muV, 2)
			if bid > mp: # won the auction
				winCount += 1
				cost += mp
				profit += y * camp_v - mp*1E-3
			if cost > budget:
				print 'out of budget'
				break
			if count>volume:
				print 'out of volume'
				break
		print 'win proportion = ' + `(1.0*winCount/count)`
		print 'profit = ' + `profit`
		if profitMin > -profit:
			profitMin = -profit
			muOpt = muV
	return muOpt

#####################################
# integral of zp(z) [int_0^b zp_z(z)dz]
def intzpz(b):
	value = 0.0
	if b >= len(landscape):
		b = len(landscape)-1
	for i in range(0, b+1):
		value += (i*landscape[i])
	return value

def utility(theta, x, y, loop):
	ctr = ctrEstimate(theta, x)
	bp = bidPrice(ctr, mu, 2)
	u = camp_v*y*winningRate(bp) - intzpz(bp)
	return u

# utility calculation
def utilityTotal(theta, dataSet, loop):
	ut = 0
	for data in dataSet:
		y = data[0]
		x = data[2:len(data)]
		u = utility(theta, x, y, loop)
		ut += u
	return ut

def performance(theta, dataSet, loop):
	winCount = 0
	pt = 0.0
	for data in dataSet:
		y = data[0]
		mp = data[1]
		x = data[2:len(data)]
		ctr = ctrEstimate(theta, x)
		bp = bidPrice(ctr, mu, 2)
		gain = 0.0
		if bp>=mp: # won the auction
			winCount += 1
			gain = y*camp_v*1E3 - mp
		pt += gain
	winRate = 1.0 * winCount / len(dataSet)
	return (winRate, pt)

#####################################

def outputWeight(weight, camp, dataSetLabel, param):
	weightFile = '../output/' + camp + '.' + dataSetLabel + param + '.weight.txt'
	featValue = sorted(weight.iteritems(), key=operator.itemgetter(0))
	fo = open(weightFile, 'w')
	for fv in featValue:
		fo.write(`fv[0]`+'\t'+`fv[1]`+'\n')
	fo.close()

def outputCtr(weight, dataSet, camp, dataSetLabel, param):
	predFile = '../output/' + camp + '.' + dataSetLabel + param + '.pred.txt'
	fo = open(predFile, 'w')
	for data in dataSet:
		x = data[2:len(data)]
		ctr = ctrEstimate(weight, x)
		fo.write(str(ctr)+'\n')
	fo.close()

#==============================================================#
if len(sys.argv) < 4:
	print 'Usage: python opt_ctr_train campaignId laplaceK scale (interval) (downsampling_ratio) \
	[ex. python ./opt_ctr_train 1458 3 0.1] [if interval/downsampling is set, the invertal mode will be on if interval>0]'
	exit(-1)

campaignId = int(sys.argv[1])
laplaceK = int(sys.argv[2])
scale = float(sys.argv[3])
folder = '../../make-ipinyou-data/' + `campaignId` + '/'
if len(sys.argv) == 5:
	INTVL = True
	interval = int(sys.argv[4])
elif len(sys.argv) == 6:
	DOWNSAMP = True
	ratio = float(sys.argv[5])
	interval = int(sys.argv[4])
	if interval > 0:
		INTVL = True

# load train data
trainFile = folder + 'train.yzx.txt'
print 'loading TRAIN data ...'
print 'train data file in ' + trainFile
trainData = []
trainCostSum = 0
trainClkSum = 0
trainDataSize = 0

fi = open(trainFile, 'r')
for line in fi:
	li = ints(line.replace(':1','').split())
	clk = li[0]
	mp = li[1]
	trainClkSum += clk
	trainCostSum += mp
	trainData.append(li)
fi.close()
print 'train data loaded.'
trainDataSize = len(trainData)
trainEcpc = int(trainCostSum / trainClkSum * 1E-3) # transform to click level instead of cpm level
camp_v = trainEcpc
originDataset = list(trainData)
landscape = makeBidLandscape(trainData, laplaceK)
if DOWNSAMP: trainData = downsampling(trainData, ratio)
# Q: why use latest data for training (reverse)?
print 'train data size is ' + `trainDataSize`
print 'train eCPC: ' + `trainEcpc`
print 'revenue(camp_v) of campaign: ' + `camp_v`

# load test data
testFile = folder + 'test.yzx.txt'
print 'loading TEST data ...'
print 'test data file in '+ testFile
testCostSum = 0
testClkSum = 0
testData = []
testDataSize = 0
fi = open(testFile, 'r')
for line in fi:
	li = ints(line.replace(':1','').split())
	clk = li[0]
	mp = li[1]
	testCostSum += mp
	testClkSum += clk
	testData.append(li)
fi.close()
testDataSize = len(testData)
# testEcpc = int(testCostSum / testClkSum * 1E-3)

volume = testDataSize / proportion
print 'test data volume is ' + `volume`
budget = testCostSum / proportion

print 'Data loaded, begin training ...'
header = "{optWinRate:>6}\t{lrWinRate:>6}\t{optPerformance:>16}\t{lrPerformance:>16}\t{testOptPerformance}\t{testLrPerformance}".format(
		optWinRate = 'WinningRate(OPT)',
		lrWinRate = 'WinningRate(LR)',
		optPerformance = 'Performance(OPT)',
		lrPerformance = 'Performance(LR)',
		testOptPerformance = 'Test_Performance(OPT)',
		testLrPerformance = 'Test_Performance(LR)'
	)

# train

#--- best laplace parameter searching ---#

# laplaceCand = [1*t for t in range(1,10)] + [10*t for t in range(1,11)]
# laplaceK = 2000
# bestPerf = 0.0
# for k in laplaceCand:
# 	landscape = makeBidLandscape(trainData, k)
# 	featWeight = {}
# 	betterPerf = 0.0
# 	for trainLoop in range(0, emRounds+1):
# 		phi = phiCalc()
# 		featWeight = trainPhaseE(featWeight, trainData)
# 		(optWinRate, optPerformance) = performance(featWeight, trainData, trainLoop)
# 		print `optWinRate` + '\t' + `optPerformance`
# 		betterPerf = optPerformance if optPerformance > betterPerf else optPerformance
# 	if betterPerf > bestPerf:
# 		bestPerf = betterPerf
# 		laplaceK = k
# 	print `k` + '\t' + `betterPerf`

# print 'best perf in train = ' + `bestPerf`
# print 'best k = ' + `laplaceK`


# for trainLoop in range(1,emRounds):
# 	lrWeight = trainLR(lrWeight, trainData)


#--- LR vs LR (cross entropy & squared error) ---#

# print 'compare cross entropy and squared loss function ...'
# print 'lrWinRate\tlrseWinRate\tlrPerformance\tlrsePerformance'
# lrWeight = {}
# lrseWeight = {}
# for trainLoop in range(0, emRounds+1):
# 	lrWeight = trainLR(lrWeight, trainData)
# 	lrseWeight = trainLRSE(lrseWeight, trainData)
# 	(lrWinRate, lrPerformance) = performance(lrWeight, trainData, trainLoop)
# 	(lrseWinRate, lrsePerformance) = performance(lrseWeight, trainData, trainLoop)
# 	print `lrWinRate` + '\t' + `lrseWinRate` + '\t' + `lrPerformance` + '\t' + `lrsePerformance`

# print 'test phase'
# (lrWinRate, lrPerformance) = performance(lrWeight, testData, trainLoop)
# (lrseWinRate, lrsePerformance) = performance(lrseWeight, testData, trainLoop)

# print 'lrWinRate\tlrseWinRate\tlrPerformance\tlrsePerformance'
# print `lrWinRate` + '\t' + `lrseWinRate` + '\t' + `lrPerformance` + '\t' + `lrsePerformance`

#--- OPT vs LR(cross entropy) ---#

scaleParams = range(10, 1000, 10) if SCALEMODE else [scale]
bestPerf = 0.0
bestScale = 1
bestLrPerf = 0.0
bestWeight = {}
bestLrWeight = {}
print 'OPT feature update and LR method ...'
print 'laplace K = ' + `laplaceK`

for s in scaleParams:
	scale = s
	print 'scale param = ' + `scale`
	print header
	for trainLoop in range(0, emRounds+1):
		phi = phiCalc()
		# e step
		featWeight = trainPhaseE(featWeight, trainData)
		lrWeight = trainLR(lrWeight, originDataset)

		(optWinRate, optPerformance) = performance(featWeight, trainData, trainLoop)
		(lrWinRate, lrPerformance) = performance(lrWeight, trainData, trainLoop) if LR else (0.0, 0.0)

		(testOptWinRate, testOptPerformance) = performance(featWeight, testData, trainLoop)
		(testLrWinRate, testLrPerformance) = performance(lrWeight, testData, trainLoop) if LR else (0.0, 0.0)

		if testOptPerformance>bestPerf:
			bestPerf = testOptPerformance
			bestScale = scale
			bestWeight = featWeight.copy()
		if testLrPerformance>bestLrPerf:
			bestLrPerf = testLrPerformance
			bestLrWeight = lrWeight.copy()

		print '%.4f\t%.4f\t%.2f\t%.2f\t%.2f\t%.2f' % (optWinRate, lrWinRate, optPerformance, lrPerformance, testOptPerformance, testLrPerformance)
if config.math_err_num>0: print 'math error number = ' + `config.math_err_num`
print 'best performance of OPT = ' + `bestPerf`
print 'best scale of OPT = ' + `bestScale`
print 'train done.'
print 'train loop number ' + `trainLoop+1`



# outputWeight(featWeight, campaignId, 'train', 'opt')
# outputCtr(featWeight, testData, campaignId, 'test', 'opt')
# if LR:
# 	outputWeight(lrWeight, campaignId, 'train', 'lr')
# 	outputCtr(lrWeight, testData, campaignId, 'test', 'lr')
# print 'feature weight and predicted ctr output done.'

#--- test phase ---#

budgetProportion = [1]
algos = ['mcpc', 'opt']
print 'proportion\tbudget\talgo\trevenue\tbids\timps\tcost\tcpc\tcpm\tctr'
for prop in budgetProportion:
	budget = int(testCostSum / prop)
	for algo in algos:
		revenue = 0.0
		ctrs = 0
		bids = 0
		imps = 0
		cost = 0
		clks = 0
		for data in testData:
			clk = data[0]
			mp = data[1]
			ctr = 0.0
			bp = 0
			x = data[2:len(data)]
			bids += 1
			if algo == 'mcpc':
				ctr = ctrEstimate(bestLrWeight, x)
			elif algo == 'opt':
				ctr = ctrEstimate(bestWeight, x)
			else:
				print 'wrong bidding strategy name'
				sys.exit(-1)
			bp = bidPrice(ctr, mu, 2)
			if bp >= mp: # won the auction
				imps += 1
				clks += clk
				cost += mp
				revenue += (camp_v*clk*1E3 - mp)
			if cost >= budget:
				break
		cpc = 0.0 if clks==0 else 1.0*cost/clks
		cpm = 0.0 if imps==0 else 1.0*cost/imps
		ctr = 0.0 if imps==0 else 1.0*clks/imps
		print `proportion` + '\t' + `budget` + '\t' + algo + '\t' + `revenue` + '\t' + `bids` + '\t' + `imps` + '\t' + `cost` + '\t' + `cpc` + '\t' + `cpm` + '\t' + `ctr`

#--- some trial ---#

#for i in range(0, len(landscape)):
#	print `i` + '\t' + `mktPrcProb(i)`


# print INTVL
# print interval
# print DOWNSAMP
# print ratio
# print len(trainData)
# pos = 0
# neg = 0
# for data in trainData:
# 	y = data[0]
# 	if y == 1:
# 		pos += 1
# 	elif y == 0:
# 		neg +=1
# print `pos` + '\t' + `neg` + '\t' + `1.0*pos/neg`
