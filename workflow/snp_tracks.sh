#!/bin/bash
for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 ; do 
	x=`echo $i | sed 's/^0//'`
	echo "track name='chr$x snps' description='snps used'" >  ct_map_chr$i.track
	for j in `seq 1 \`ls gh_200/c$i/map_* | xargs -I {} basename {} .$i | sed 's/map_//' | sort -n | tail -1\``; do
		grep -v "Genpos" gh_200/c$i/map_$j.$i | awk '{ printf "chr%d\t%s\t%s\t%s\n", $1, $4, $4, $3 }' 
	done >> ct_map_chr$i.track ; 
		
	(echo "track name='chr$x borders' description='borders'" && grep -v "^track" ct_map_chr$i.track | uniq -c | sed 's/^\W*//' | grep "^2" | awk '{ printf "%s\t%s\t%s\t%s\n", $2,$3,$4,$5 }') > ct_borders_chr$i.track ; 
done
