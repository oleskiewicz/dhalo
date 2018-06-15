#!/bin/sh

for G in GR F6 F5 F4; do
	for S in 045 032 022 009 000; do
		for f in 001 002 010 050; do
			GRAV=${G} SNAP=${S} NFW_f=${f} bsub < ./run.sh
		done;
	done;
done;

