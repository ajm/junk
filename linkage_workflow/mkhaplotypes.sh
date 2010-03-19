#!/bin/bash

if [[ $# != 1 ]]; then
	echo "Usage: mkhaplotypes.sh <chromosome>"
	echo
	exit -1
fi

chromo=$1

for i in `cut -f1 ../pedfile.pro | uniq` ; do 
	echo creating haplotype graph for family $i 
	HaploPainter1.043.pl -b -pedfile ../pedfile.pro -hapfile c$chromo/ihaplo.out -hapformat allegro -mapfile c$chromo/map.$chromo -mapformat 1 -family $i -paper A0 -outfile haplotypes_chr${chromo}_family-${i}_A0.pdf -outformat pdf 
done

