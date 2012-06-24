#!/bin/bash

numfamilies=`awk '{ printf "%s\n", $1 }' pedfile.pro | sed '/^\W*$/d' | uniq | wc -l`
if [[ $numfamilies = 1 ]] ; then
	echo only one family...
	exit 0
fi

cd gh_200

for i in `awk '{ printf "%s\n", $1 }' ../pedfile.pro | sed '/^\W*$/d' | uniq`; do
	echo processing family $i
	
	rm -rf ../genehunter-family$i
	mkdir ../genehunter-family$i

	gh_snp_fam_lod.pl $i
	mv gh_snp_lod_family-$i.ps ../genehunter-family$i/

	for j in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 ; do
		gh_snp_fam_lod_single.pl $i $j
	done

	mv gh_snp_lod_family-${i}_chr*ps ../genehunter-family$i/
done

cd ..
