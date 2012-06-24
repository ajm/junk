#!/bin/bash

set -e

numfamilies=`awk '{ printf "%s\n", $1 }' pedfile.pro | sed '/^\W*$/d' | uniq | wc -l`
if [[ $numfamilies = 1 ]] ; then
        echo only one family...
        exit 0
fi

for i in `awk '{ printf "%s\n", $1 }' pedfile.pro | sed '/^\W*$/d' | uniq`; do
        echo processing family $i
        
        rm -rf allegro-family$i
        mkdir allegro-family$i
	for j in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 ; do
                mkdir allegro-family$i/c$j
		grep "^$i\W" allegro/c$j/fparam_mpt.$j | \
			awk '{ printf "%s\t%s\t%s\n", $2, $3, $4 }' > \
			allegro-family$i/c$j/param_mpt.$j
        done
	
	cd allegro-family$i
	allegro_lod_all.pl
	chromosomes.sh allegro
	cd ..
done

