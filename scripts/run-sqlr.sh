camps=$1
steps="1 10 20 30 40 50 60"

for camp in $camps; do
	for step in $steps; do
		echo $camp $step
		python ../python/test_sqlr.py $camp $step
	done
done