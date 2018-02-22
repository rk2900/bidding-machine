#!/bin/bash
camps=$1
laplace="3"
scale="10 20 30 40 60 80 90"
ratio="0 0.1 0.5"

for camp in $camps; do
	for lap in $laplace; do
		for sca in $scale; do
			for rat in $ratio; do
				echo $camp $lap $sca $rat
				python ../python/test_eu.py $camp $lap $sca $rat
			done
		done
	done
done