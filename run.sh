#!/usr/bin/env bash
#BSUB -P durham
#BSUB -q bench1
#BSUB -n 1
#BSUB -J dhalo_cmh
#BSUB -oo ./log/log_%J.txt
#BSUB -eo ./log/err_%J.txt

make cmh
