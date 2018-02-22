project_folder="/home/rk/Code/optimal-ctr-bidding/"
cd $project_folder/python
budget_props="1 4 8 16 32"

name=$1
model=$2
test_file=$3
output_folder=$4

echo $name
echo $model
echo $test_file
echo $output_folder

for prop in $budget_props; do
	echo $prop
	python replay.py -1 $prop $model $test_file $output_folder/$prop\_$name\_perf.csv
done
