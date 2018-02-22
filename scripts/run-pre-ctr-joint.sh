#!/bin/bash
camps=$1
laplace="3"
scale="10 20 30 40 60 80 90"
ratio="0 0.1 0.5"
alpha="1e-12 5e-11 1e-11 5e-10 1e-10 5e-9 1e-9 5e-8 1e-8"
beta="5e-8 1e-8 5e-7 1e-7 5e-6 1e-6 5e-5 1e-5 5e-4 1e-4 5e-3 1e-3 5e-2 1e-2"

for camp in $camps; do
	for lap in $laplace; do
		for sca in $scale; do
			for rat in $ratio; do
				for al in $alpha; do
					for be in $beta; do
						echo $camp $lap $sca $rat $al $be
						python ../python/test_prectr_joint.py $camp $lap $sca $rat $al $be
					done
				done
			done
		done
	done
done
