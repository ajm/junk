#!/bin/bash

directory=`basename \`pwd\``
if [[ $directory = 'allegro' ]] ; then
	aflag='-a'
	lflag=`python -c "print \`awk '{ print $5 }' ../allegro_elod.txt\` - 1"`
	out="messner_allegro_lod$lflag.txt"
elif [[ $directory = 'gh_200' ]] ; then
	aflag='-g'
	lflag=`python -c "print \`awk '{ print $5 }' ../genehunter_elod.txt\` - 1"`
	out="messner_genehunter_lod$lflag.txt"
elif [[ $directory = 'mega2_200' ]] ; then
	aflag='-s'
	echo "For simwalk I think we should run messner manually because I did not have anything to test it on when I wrote this..."
	echo
	echo "Complain and I will fix it ;-)"
	echo "--ajm"
	echo
	exit -1
else
	echo "You do not appear to be in a valid results directory..."
	echo "(eg: allegro, gh_200, mega2_200)"
	exit -1
fi

messner2 -m ../map.txt -l $lflag $aflag > $out

