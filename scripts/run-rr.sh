#!/bin/bash
camps=$1
laplace="3 10"
scale="0.005 0.01 0.02 0.03 0.04 0.06 0.08 0.1 0.2 0.5"  #"0.005 0.01 0.012 0.016 0.032 0.05 0.064 0.128 0.256 0.512 1.0"
ratio="0.1 0.01 0.5" #"0"

for camp in $camps; do
	for lap in $laplace; do
		for sca in $scale; do
			for rat in $ratio; do
				echo $camp $lap $sca $rat
				python ../python/test_rr.py $camp $lap $sca $rat
			done
		done
	done
done
