#!/bin/bash

python ../python/test_lrlin.py 1458 0.001 > ../output/lr_1458_0.001.log &
python ../python/test_lrlin.py 2259 0.1 > ../output/lr_2259_0.1.log &
python ../python/test_lrlin.py 2261 0.001 > ../output/lr_2261_0.001.log &
python ../python/test_lrlin.py 2821 0.1 > ../output/lr_2821_0.1.log &
python ../python/test_lrlin.py 2997 0.0005 > ../output/lr_2997_0.0005.log &
python ../python/test_lrlin.py 3358 0.01 > ../output/lr_3358_0.01.log &
python ../python/test_lrlin.py 3386 0.001 > ../output/lr_3386_0.001.log &
python ../python/test_lrlin.py 3427 0.005 > ../output/lr_3427_0.005.log &
python ../python/test_lrlin.py 3476 0.005 > ../output/lr_3476_0.005.log &
