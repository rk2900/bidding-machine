#!/bin/bash

prop=$1
#"64 32 16 8 4 2 1"

python ../python/test_em.py 1458 rr 3 0.512 0 $prop
python ../python/test_em.py 1458 eu 3 90 0.1 $prop

python ../python/test_em.py 2259 eu 3 80 0.5 $prop
python ../python/test_em.py 2259 rr 3 2E-1 0.5 $prop

python ../python/test_em.py 2261 rr 10 0.01 0.5 $prop
python ../python/test_em.py 2261 eu 3 20 0.5 $prop

python ../python/test_em.py 2821 rr 3 0.128 0 $prop
python ../python/test_em.py 2821 eu 3 40 0.5 $prop

python ../python/test_em.py 2997 eu 3 80 0.5 $prop
python ../python/test_em.py 2997 rr 10 0.256 0 $prop

python ../python/test_em.py 3358 rr 10 0.016 0 $prop
python ../python/test_em.py 3358 eu 3 90 0.1 $prop

python ../python/test_em.py 3386 rr 10 0.04 0.5 $prop
python ../python/test_em.py 3386 eu 3 80 0.1 $prop

python ../python/test_em.py 3427 rr 3 0.5 0.5 $prop
python ../python/test_em.py 3427 eu 3 90 0.1 $prop

python ../python/test_em.py 3476 rr 3 0.032 0 $prop
python ../python/test_em.py 3476 eu 3 40 0.1 $prop
