#!/bin/bash
echo "run"
camps=$1
steps="1E-4 1E-5 1E-3 5E-3 5E-5 5E-4 1E-2 5E-2 1E-1"
for camp in $camps; do
	for step in $steps; do
	    echo $camp
	    python ../python/test_lr.py $camp $step
	done
done
