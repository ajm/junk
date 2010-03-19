#!/bin/bash

numfamilies=`cut -f1 pedfile.pro | uniq | wc -l`
if [[ $numfamilies = 1 ]] ; then
	echo "only one family..."
	exit 0
fi

# rename
if [[ -d allegro ]]; then
       mv allegro allegro-all
fi

# make allegro files for each family
mv pedfile.pro pedfile.pro.all
for i in `cut -f1 pedfile.pro.all | uniq`; do 
	echo processing family $i

#	grep "^$i" pedfile.pro.all > pedfile.pro
#	alohomora.pl -nogui -b /usr/local/bin/auto/stage4.pl

#	rm -rf allegro-family$i
#	mv allegro allegro-family$i

	cd allegro-family$i
#	allegro_haplo.pl

	allegro_lod_all.pl
	mv allegro_lod_.ps allegro_lod_family-$i.ps
	ps2pdf allegro_lod_family-$i.ps

	chromosomes.sh allegro
	for j in `ls allegro_lod_chr*ps`; do
		bn=`basename $j .ps`
		mv $j ${bn}_family-$i.ps
		ps2pdf ${bn}_family-$i.ps
	done

	cd ..
done

mv pedfile.pro.all pedfile.pro
# rename back
if [[ -d allegro-all ]] ; then
	mv allegro-all allegro
fi

