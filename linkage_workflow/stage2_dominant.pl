$infile="./genotypes";
$pedfilepro="./pedfile.pro"

$chip="Illumina";
$genmap="Other";
$other_map_illumi="./map.txt";

$allfreq="Caucasian";
$freq_cauc_illumi="./maf.txt";

$skip_nopos=1;
$del_errors=0;
&ReadInfiles;

&CompareSampleIDs;
&CheckGender;

&PedCheck;
&PlotPedCheckErr;

$skip_notinf=1
$del_errors=1;
$pvf2=1.0;
&Merlin;

chdir("merlin");
system("merlin_start.pl");
chdir("..");
&CreMerlinErrList;



