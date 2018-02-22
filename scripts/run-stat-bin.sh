#!/bin/bash
camps=$1
laplace="3"
scale="10 20 25 30 35 40 50 60 70 80 85 90 95 100 105 110"
ratio="0 0.1 0.5"

for camp in $camps; do
	for lap in $laplace; do
		for sca in $scale; do
			for rat in $ratio; do
				echo $camp $lap $sca $rat
				python ../python/test_stat_bin.py $camp $lap $sca $rat 0
			done
		done
	done
done
