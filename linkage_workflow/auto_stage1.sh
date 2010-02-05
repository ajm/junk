#!/bin/bash

if [[ $# != 1 ]] ; then
	project=`basename \`pwd\``
else
	project=$1
fi

# create pedigree diagrams from pedfile.pro
mkpedigrees pedfile.pro

# run gender check + get GRR input file
alohomora.pl -nogui -b /usr/local/bin/auto/stage1.pl

# are the genders correct?
if [[ `grep -c '###' gendercheck.txt ` != 0 ]] ; then
	echo ; echo ; echo Errors during gender check...
	echo
	grep '###' gendercheck.txt
	echo
	exit -1
fi

# run GRR
autogrr_multiple $project

