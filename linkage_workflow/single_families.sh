#!/bin/bash

# rename
if [[ -d allegro ]]; then
       mv allegro allegro-all
fi

# make allegro files for each family
mv pedfile.pro pedfile.pro.all
for i in `cut -f1 pedfile.pro.all | uniq`; do 
	echo processing family $i

	grep "^$i" pedfile.pro.all > pedfile.pro
	alohomora.pl -nogui -b /usr/local/bin/auto/stage4.pl

	mv allegro allegro-family$i

	cd allegro-family$i
	allegro_haplo.pl

	allegro_lod_all.pl
	mv allegro_lod_.ps allegro_lod_family-$i.ps
	ps2pdf allegro_lod_family-$i.ps
	cd ..
done

mv pedfile.pro.all pedfile.pro
# rename back
if [[ -d allegro-all ]] ; then
	mv allegro-all allegro
fi

