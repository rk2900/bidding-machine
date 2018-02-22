#!/bin/bash

cd /home/rk/Code/optimal-ctr-bidding/scripts/
pwd

echo "run"
sh run-lr.sh "1458 2261 2821" > ../output/log_parallel/lr_1458_2261_2821.log &
sh run-rr.sh "1458 2261 2821" > ../output/log_parallel/rr_1458_2261_2821.log &
sh run-eu.sh "1458 2261 2821" > ../output/log_parallel/eu_1458_2261_2821.log &
sh run-lr.sh "2997 3358 3386" > ../output/log_parallel/lr_2997_3358_3386.log &
sh run-rr.sh "2997 3358 3386" > ../output/log_parallel/rr_2997_3358_3386.log &
sh run-eu.sh "2997 3358 3386" > ../output/log_parallel/eu_2997_3358_3386.log &
sh run-lr.sh "3427 3476 2259" > ../output/log_parallel/lr_3427_3476_2259.log &
sh run-rr.sh "3427 3476 2259" > ../output/log_parallel/rr_3427_3476_2259.log &
sh run-eu.sh "3427 3476 2259" > ../output/log_parallel/eu_3427_3476_2259.log &
#sqlr
sh run-sqlr.sh "1458 2261 2821" > ../output/log_parallel/sqlr_1458_2261_2821.log &
sh run-sqlr.sh "2997 3358 3386" > ../output/log_parallel/sqlr_2997_3358_3386.log &
sh run-sqlr.sh "3427 3476 2259" > ../output/log_parallel/sqlr_3427_3476_2259.log &

echo "done"