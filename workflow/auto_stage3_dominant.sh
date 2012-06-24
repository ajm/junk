#!/bin/bash

time=`date | sed s/\ /\-/g`

if [[ -d allegro ]]; then
       mv allegro allegro-$time
fi
if [[ -d gh_200 ]]; then
	mv gh_200 gh_200-$time
fi
if [[ -d mega2_50 ]]; then
	mv mega2_50 mega2_50-$time
fi

# create linkage files
# make allegro files
# make genehunter files
# make simwalk2 files
alohomora.pl -nogui -b /usr/local/bin/auto/stage3_dominant.pl

