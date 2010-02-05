$infile="./genotypes";
$pedfilepro="./pedfile.pro"

$chip="Illumina";
$genmap="Other";
$other_map_illumi="./map.txt";

$allfreq="Caucasian";
$freq_cauc_illumi="./maf.txt";

$del_errors=0;
&ReadInfiles;

&CompareSampleIDs;
&CheckGender;
&PrintGRRFile;

#&PedCheck;
#&PlotPedCheckErr;

#$del_errors=1;
#&Merlin;

#chdir("merlin");
#system("merlin_start.pl");
#chdir("..");
#&CreMerlinErrList;

#$del_unlikely=1;

#&Allegro;


