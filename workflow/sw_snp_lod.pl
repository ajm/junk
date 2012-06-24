#!/usr/bin/perl

#
# sw_snp_lod.pl :  Prepare Simwalk2 Lodscores for displaying with gnuplot
# Syntax    :  sw_snp_lod.pl [-h] [-clean] [<extension>]
# Infiles   :  <simwalks_score.out> 
# Outfiles  :  swlod.gp, chr_line.plt and lod.plt
# 

use Cwd;
use File::Basename;

################################   V A R I A B L E S   ##################################

my $maxlines = 999999; 	# Maximum number of lines (input-file)

my $xsum = 0.0;
my $xmin = 0;
my $ymax = 3;
my $ymin = -2;
my @xsums=();
my $lastxsum=0.;

my $pfad=cwd();
my $datum = scalar localtime;
my @map=();
my $set=0;
my %chrlabel=();


######################################  M A I N  #######################################
print "\n\n";
print " * * * * * * * * * * * * *  SW_SNP_LOD.PL v1.0  * * * * * * * * * * * * * \n";
print " * * * * * * * * * *  View SIMWALK2 LODs with GNUPLOT * * * * * * * * * * \n\n";

if ($ARGV[0] =~ "-h" ) { eval version;}
if ($ARGV[0] =~ "-v" ) { eval version;}
if ($ARGV[0] =~ "-clean" ) { eval clean;}
if ($#ARGV == "0") {$postfix = $ARGV[0];} else {$postfix = "ALL";}

print "Please wait ...\n\n";
$titel = "$pfad - SW2 LODs Family: $postfix - $datum";

open (out4,"> lod.plt") || die "could not open lod.plt :$!\n";

#foreach ${chr} ("15") {
foreach ${chr} ("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22") {
	if ( -d "c$chr") {
		print "\n";
		$set=0;
		$sw_run=0;
		@maps=glob("c${chr}/map_*.$chr");
		foreach (@maps){
			$basename=basename($_);
			@feld =	split('_',$basename);
			if ($set < $feld[1]) {$set=$feld[1];}
		}
		
		foreach my $i ( 1..$set) {
			$in_file = "c${chr}/SCORE-${chr}_${i}\.${postfix}";
			$map="c${chr}/map_${i}\.${chr}";
			&get_locus_names;
			if ( -f "$in_file") {&readlod;$sw_run=1;}
			else { print "\n"; $miss{$chr}++;}
		} 
####
		if ($sw_run==1) {		# chromosome label
			my $xpos=(($lastxsum + $xsum)/2);
			my $var=$chr; $var =~ s/c0//;$var =~ s/c//;
			if ($var eq "23"){$var = "X";}
			if ($var > 9){ $xpos -=30;}
			else { $xpos -=5;}
			$chrlabel{$var}=$xpos;
			$lastxsum=$xsum;
		}
####
		push (@xsums,$xsum);
		print out4 "\n";  
		        
    }
	else { print "Chromosome $chr not exists \n"; }
} # end foreach

close (out4);

&print_chr_line;
&pr_batch;
print "\nYou can now view results by \"gnuplot swlod.gp\" \n\n";
system "gnuplot swlod.gp";
&clean;

#########################################  S U B s  ##########################################

sub readlod {
  open (infile, "$in_file") || die "could not open $in_file :$!\n";

  $jetzt = $maxlines;
  $xmax = 0.0;
  print " : $in_file   \n"; 

  while (<infile>){
  	next if /^$/;
  	next if /^\#/;
	chop();
	s/,//g;		# new simwalk format is not useful
	@feld =	split(' ',$_);

    if ($feld[0] eq $firstlocus) { $jetzt = $.;}
    if ($feld[0] eq $lastlocus) { $jetzt = $maxlines;}
    if (($. > $jetzt) && ($#feld >= 2)){
		printf(out4 "%7.4f  %s\n", ($feld[0] + $xsum), $feld[1]);
		if ($feld[0] > $xmax) { $xmax = $feld[0];}  
		if ($feld[1] > $ymax) { $ymax = $feld[1];}
    }  
  } # end while

  $xsum = $xsum + $xmax;
  printf out4 "\n";

  close (infile);

} ## end readlod

######################   P R I N T  C H R _ L I N E S   ######################
sub print_chr_line {

#	$xsum = 3700;		# for a fixed axle in every picture
	$ymax += 1;						# y-achse auf ganze HLOD-Zahl bringen
	@buff =	split('\.',$ymax);		# round to integer
	$ymax=$buff[0];
	
	open (out3,"> chr_line") || die "could not open chr_line :$!\n";

	if ($hline=1){
		for (my $i=-2; $i<$ymax;$i++) {	# horizontale Linien bei LODs = 1,2,3,4,..
			print out3 "0 $i\n$xsum $i\n\n";
		}
	}

	foreach (@xsums){	# vertikale Linien Chromosomenende 1,2,3,4,...22,x,xy
		print out3 "$_ $ymin \n$_ $ymax \n\n";         
	}
	close (out3);
}
###-----------------------  P R I N T  G N U P L O T  B A T C H   -----------------------###
sub pr_batch {

#	$xsum = 3600;
	open (out5,"> swlod.gp") || die "could not open swlod.gp :$!\n";

	print out5 "set autoscale\n";
	print out5 "set nokey\n";
	print out5 "set title \"$titel\\n\"\n" ;
#	print out5 "set xlabel \"MB\"\n";
	print out5 "set xlabel \"cM\"\n";
	print out5 "set ylabel \"LOD\"\n";
	my $ypos = $ymax + (($ymax-$ymin)/14);
	foreach (keys %chrlabel) {print out5 "set label \"$_\" at $chrlabel{$_}\,$ypos font \"Ariel,8\"\n";}
	print out5 "set size 1,0.6\n";
	print out5 "set terminal postscript color\n";
	print out5 "set output \"sw_snp_lod_$postfix.ps\"\n";
	print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'lod.plt\' with lines, \'chr_line\' with lines\n";
	print out5 "set terminal x11\n";
	print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'lod.plt\' with lines, \'chr_line\' with lines\n";
	print out5 "\npause -1 \"Hit return to continue\"\n\n";

	close (out5);

} ## end pr_batch
																
###------------------   G E T  F I R S T and L A S T  L O C U S   ----------------------###
sub get_locus_names {
	print "Mapfile $map  ";
	$first=0;
	open (infile2, "$map") || die "could not open Mapfile $map :$!\n";
	while (<infile2>){
  		next if /^$/;
  		next if /^\#/;
  		next if /cM/;
  		chop();
  		@feld =	split(' ',$_);
  		if ($#feld > 1){
  			if ($first==0) { $firstlocus = $feld[2];$first=1;}
  			$lastlocus = $feld[2];
		}
	}
	close (infile2);
	if (length($firstlocus) > 8) { $firstlocus=substr($firstlocus,(length($firstlocus)-8),8);}
	if (length($lastlocus) > 8) { $lastlocus=substr($lastlocus,(length($lastlocus)-8),8);}
} # end last_locus

###----------------   G E T  O R I G I N A L  F A M I L Y  N U M B E R   ---------------###
sub get_org_fam_nr {
  open (infile3, "$in_file") || die "could not open $in_file :$!\n";
  while (<infile3>){
  	next if /^$/;
  	next if /^\#/;
	chop();
	@feld =	split(' ',$_);
        if (( $feld[5] =~ /named:/) && ( $feld[4] =~ /pedigree/)) { $oldname=$feld[6]; last;}
  }
  close (infile3);
} ##

###------------------------------------- V E R S I O N ---------------------------------###

sub version {
print "\n\n";
print " * * * * * * Created by Franz Rueschendorf   1-Mar-2004 * * * * * * \n";
print " * * * * * * * * * *  IMBIE, University of Bonn  * * * * * * * * * * \n";
print " * * * * * * * * *  email: fruesch\@mdc-berlin.de   * * * * * * * * * \n";
print "\n     Usage        : sw_snp_lod.pl [-h] [-clean] [<extension>]\n";
print "     Infiles      : SCORE-<nn>\.<mmm>\n";
print "     Outfiles     : swlod.gp, chr_line.plt lod.plt \n" ;
print "     View results : gnuplot swlod.gp\n\n";
exit 0;
}


###-------------------------------------- C L E A N  ---------------------------------###

sub clean { 
#unlink glob("*.plt");
#unlink glob("chr_line");
#unlink glob("*.gp");
exit 0;
}

### end sw_snp_lod.pl

############################################  E N D   ##########################################
