#!/bin/bash
props="128 64 32 16 8 4 2 1"

for prop in $props; do
	sh run-em.sh $prop > ../output/$prop.log &
done