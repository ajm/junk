#!/bin/bash

time=`date | sed s/\ /\-/g`
if [[ -d merlin ]] ; then
	mv merlin merlin-$time
fi

# run pedcheck,
# run merlin, 
# generate unlikely genotypes list, 
alohomora.pl -nogui -b /usr/local/bin/auto/stage2.pl

# convert postscript files from pedcheck
for i in `ls genotype*ps` ; do
	ps2pdf $i &> /dev/null
done

