#!/usr/bin/env bash

file_in="./output/ids.txt"
file_out="./output/mah.tsv"
echo "nodeIndex\tsnapshotNumber\tparticleNumber" > $file_out
for id in `more $file_in`; do
	bsub -P durham \
		-n 1 \
		-q bench1 \
		-J "mah_$id" \
		-oo ./log/log.txt \
		-eo ./log/err.txt \
		python ./src/tree.py $id $file_out
done

