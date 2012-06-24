#!/bin/bash
set -e

trap "{ echo \"Killed by user\"; kill -TERM -`pgrep -o simple_run_dominant.sh`; }" EXIT

# make sure the files are all UNIX text files
# just in case of any \r\n nonsense
dos2unix genotypes
dos2unix maf.txt
dos2unix map.txt
dos2unix pedfile.pro

# stage 1:
# 	make pedigree PDFs
# 	check genders (dies if fails)
# 	run GRR (user needs to kill if bad)
auto_stage1.sh &
wait $!

# stage 2:
# 	run pedcheck
#	make merlin input files + run merlin + create unlikely genotypes list
auto_stage2_dominant.sh &
wait $!

# show the user mendelian error graph
evince genotypes_*.ps &

# graph merlin results
cd merlin
merlin_lod_all.pl 
cd ..

# stage 3 :
#	make allegro, genehunter, simwalk input files
auto_stage3_dominant.sh &
wait $!

sleep 3


###########################
#  allegro                #
###########################
cd allegro

#clodhopper.py allegro > ../allegro_elod.txt
allegro_haplo.pl &
wait $!

run_messner.sh
allegro_lod_all.pl
chromosomes.sh allegro

for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 ; do
	mkhaplotypes.sh $i
done

cd ..

single_families_allegro.sh &
wait $!

sleep 3


###########################
#  genehunter             #
###########################
cd gh_200

#clodhopper.py genehunter > ../genehunter_elod.txt

if [ `tail -1 gh_start.sh` != 'fi' ] ; then
	echo "cd .." >> gh_start.sh
	echo "fi" >> gh_start.sh
fi

chmod +x gh_start.sh
./gh_start.sh &
wait $!

run_messner.sh
gh_snp_lod_all.pl
chromosomes.sh genehunter

cd ..

single_families_genehunter.sh &
wait $!

