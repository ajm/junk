#!/bin/bash
set -e

auto_stage1.sh
auto_stage2_dominant.sh

evince genotypes_*.ps &

cd merlin
merlin_lod_all.pl
cd ..

auto_stage3_dominant.sh

sleep 3

###########################
#  allegro                #
###########################
cd allegro

clodhopper.py allegro > ../allegro_elod.txt
allegro_haplo.pl

run_messner.sh
allegro_lod_all.pl
chromosomes.sh allegro

for i in `cut -f1 -d' ' messner*.txt | uniq | sed 's/chr//' | awk '{ printf "%02d\n", $1 }'`; do
	mkhaplotypes.sh $i
done

cd ..

single_families_allegro.sh

sleep 3

###########################
#  genehunter             #
###########################
cd gh_200

clodhopper.py genehunter > ../genehunter_elod.txt
chmod +x gh_start.sh
echo "cd .." >> gh_start.sh
echo "fi" >> gh_start.sh
./gh_start.sh

run_messner.sh
gh_snp_lod_all.pl
chromosomes.sh genehunter

cd ..
single_families_genehunter.sh

