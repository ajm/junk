$infile="./genotypes";
$pedfilepro="./pedfile.pro"

$chip="Illumina";
$genmap="Other";
$other_map_illumi="./map.txt";

$allfreq="Caucasian";
$freq_cauc_illumi="./maf.txt";

&ReadInfiles;
&CompareSampleIDs;
&CheckGender;

$skip_notinf=0
$del_errors=1;
$del_unlikely=1;
&Allegro;

$subsets=1;
$gh_ps2=0;
$gh_prog="ghm";
$maxsnp=200;

&Genehunter;
&Mega2

