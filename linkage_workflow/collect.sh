#!/bin/bash

destdir=$1
mkdir -p $destdir/{preprocessing,pedigrees,grr,allegro,genehunter}

# pedigrees
cp family*pdf *elod.txt $destdir/pedigrees
# preprocessing
for i in `ls genotypes*ps`; do 
	ps2pdf $i
done
cp gendercheck.txt genotypes*pdf unlikely.all $destdir/preprocessing
# grr
cp grr_info*txt grr_screenshot*png $destdir/grr
# allegro
for i in `ls allegro/allegro_lod*ps`; do 
	out=`basename $i ps`
	echo Converting $i to allegro/${out}pdf
	ps2pdf $i allegro/${out}pdf
done
cp allegro/allegro_lod*pdf allegro/messner*txt $destdir/allegro
# genehunter
for i in `ls gh_200/gh_snp_lod*ps`; do 
	out=`basename $i ps`
	echo Converting $i to gh_200/${out}pdf
	ps2pdf $i gh_200/${out}pdf
done
cp gh_200/gh_snp_lod*pdf gh_200/messner*txt $destdir/genehunter

# convert for windows
unix2dos $destdir/*/*txt

clear
echo
echo CONTENTS OF $destdir
echo ------------------------------
echo
ls --color='always' -R $destdir
echo
