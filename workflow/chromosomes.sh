#!/bin/bash

function usage {
	echo "Usage: chromosomes.sh <program>"
	echo "where program is simwalk, genehunter or allegro"
	echo
}

if [[ $# != 1 || $1 = '-h' ]] ; then
	usage
	exit -1
fi

program=$1

if [[ $program = 'allegro' ]] ; then
	command=allegro_lod_single.pl
elif [[ $program = 'genehunter' ]] ; then
	command=gh_snp_lod_single.pl
elif [[ $program = 'simwalk' ]] ; then
	#echo "simwalk not implemented yet..."
	#echo "bug me about it and i will fix it ;-)"
	#echo
	#exit -1
	command=sw_snp_lod_single.pl
else 
	usage
	exit -1
fi

#for i in `ls -d c*`; do
#	if [[ $i = 'cX' || $i = 'cY' || $i = 'cXY' || $i = 'elod' ]]; then
#		continue
#	fi
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 ; do
	$command $i
done

