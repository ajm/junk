#!/usr/bin/perl

#
# gh_snp_fam_lod.pl :  Prepare Genehunter output for displaying with gnuplot
# Usage     :  gh_snp_fam_lod.pl [-h] [-clean] [<family>]
# Infiles   :  gh_<v>.out (default)
# Outfiles  :  myghlod.gp, chr_line and lod.plt
# Modified  : 12-Aug-2003	FR

use Cwd;

print "\n\n";
print " * * * * * * * * * * * GH_SNP_FAM_LOD.PL v1.0  * * * * * * * * * * * *\n";
print " * * * * * * * *  View Genehunter results with GNUPLOT * * * * * * * * \n";

if ($ARGV[0] =~ "-h" ) { &Help;}
if ($ARGV[0] =~ "-v" ) { &Help;}
if ($ARGV[0] =~ "-clean" ) { &Clean;}

if ($#ARGV == "0") {$famnr = $ARGV[0];} 
else { print "Need Pedigreenumber! \n";
       print "Usage: gh_snp_fam_lod.pl <pednr> \n";
       exit 0;
}




print "\nPlease wait ...\n";

my $maxlines = 999999; 	# Maximum number of lines (input-file)

my @xsums=();
my $xsum = 0.0;
my $xmin = 0;

my $ymax = 2;
my $ymin = -3;

my $lastxsum=0.;
my %chrlabel=();

my $pfad = getcwd();
my $datum = scalar localtime;

open (out4,">$pfad/lod.plt") || die "could not open lod.plt :$!\n";

foreach my $dir (c01,c02,c03,c04,c05,c06,c07,c08,c09,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,cx,c24,cxy) {
	if (-d $dir) {
		$gh_tsh=0;	# is there a total stat het for this chrom
		foreach my $i ( 1..1000) {	# edit this line if more than 40 subsets 
			$ghout="gh_$i\.out";	
			$in_file = "$dir/$ghout";
			if (-f "$in_file") {	  
				print "File: $in_file"; 
				&ReadLod(); 
			}
		} 
		if ($gh_tsh==1) {		# chromosome label
			my $xpos=(($lastxsum + $xsum)/2);
			my $var=$dir; $var =~ s/c0//;$var =~ s/c//;
			if ($var > 9){ $xpos -=30;}
			else { $xpos -=5;}
			if ($var == 23){$var="X";}
			$chrlabel{$var}=$xpos;
			$lastxsum=$xsum;
		}
		push (@xsums,$xsum);
		print out4 "\n";  
	}
	else { print "$dir not existing \n";
	}
} # end foreach

close (out4);
&print_chr_line;
&pr_batch;

print "\nYou can now view results by \"gnuplot myghlod.gp\" \n\n";
system ("gnuplot myghlod.gp");

print "\nready ...\n\n";
&Clean ();

#################################   R E A D L O D   #################################  

sub ReadLod {
	my @data=();	# Array infile (Genehunter outfile)
	my @v=();
	my $jetzt = $maxlines;
	my $xmax = 0.0;
  	my $schalt = 0;
	my $count=0;
	my $c_fam=0;	# 

	open (infile, "$in_file") || die "could not open ghfile $in_file :$!\n";
	while (<infile>){
		chomp;
		$_ =~ s/,-/, -/g;
		$_ =~ s/-INFINITY/-99.99/g;
		push (@data,$_);
	}
	close (infile);

 	foreach $line (@data) {
		@feld =	split(' ',$line);
		$count++;
		@v=split('\.',$feld[2]);	# Punkte abtrennen
		if (($feld[0] =~ /analyzing/) and ($v[0] eq $famnr))   { 
			$schalt = 1;	
			$c_fam++;			
		}
		if ($_ =~ /SKIPPING/) {$schalt=0;}	

		if (($schalt==1) and ($feld[0] =~ /position/))  { 
			$jetzt = $count;
			$schalt=2;
			print " Read LODs of Family $famnr \n";
			$gh_tsh=1;
		}

		if (($#feld < 1) or ($feld[0] =~ /OBSERVED/)) { 
			if ($schalt == 2) {
				$jetzt = $maxlines;
				$schalt = 0;   		
			}
		}

		if ($count > $jetzt) {
			printf out4 ("%f %s\n", ($feld[0] + $xsum), $feld[1]);
			if ($feld[0] > $xmax) { $xmax = $feld[0];}  
			if ($feld[1] > $ymax) { $ymax = $feld[1];}
		}
	} # end while


	$xsum = $xsum + $xmax;
	if ($c_fam > 1) { print "$in_file hat mehr als eine Analyse fuer Familie $famnr\n";}
} ## end ReadLod

######################   P R I N T  C H R _ L I N E S   ######################
sub print_chr_line {

#	$xsum = 3700;				# x-Achse auf festen Wert begrenzen
	$ymax += 1;				# y-achse auf ganze LOD-Zahl bringen
	my @buff =	split('\.',$ymax);	# round to integer
	$ymax=$buff[0];
	
	open (out3,"> chr_line") || die "could not open chr_line :$!\n";

	for (my $i=-2; $i<$ymax;$i++) {			# horizontale Linien bei LODs = 1,2,3,4,..
		print out3 "0 $i\n$xsum $i\n\n";
	}
	foreach (@xsums){						# vertikale Linien Chromosomenende 1,2,3,4,...22,x,xy
		print out3 "$_ $ymin \n$_ $ymax \n\n";         
	}
	close (out3);
}

###-----------------------  P R I N T  G N U P L O T  B A T C H   -----------------------###
sub pr_batch {

	my $titel = "$pfad - Genehunter LODs of Family $famnr   - $datum";
	open (out5,"> myghlod.gp") || die "could not open myghlod.gp :$!\n";

	print out5 "set autoscale\n";
	print out5 "set nokey\n";
	print out5 "set title \"$titel\"\n" ;
	print out5 "set xlabel \"MB\"\n";
	print out5 "set ylabel \"LOD\"\n";
	my $ypos = $ymax - (($ymax-$ymin)/20);
	foreach (keys %chrlabel) {print out5 "set label \"$_\" at $chrlabel{$_}\,$ypos font \"Ariel,8\"\n";}
	print out5 "set size 1,0.6\n";
	print out5 "set terminal postscript color 11\n";
	print out5 "set output \"gh_snp_lod_family-${famnr}.ps\"\n";
	print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'lod.plt\' with lines, \'chr_line\' with lines\n";
#	print out5 "set terminal x11\n";
#	print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'lod.plt\' with lines, \'chr_line\' with lines\n";
#	print out5 "\npause -1 \"Hit return to continue\"\n\n";

	close (out5);

} ## end pr_batch
					

#################################   H E L P   #################################  
sub Help {

print " * * * * * * Created by Franz Rueschendorf 2-Jan-2003  * * * * * * \n";
print " * * * * * * * * * Max-Delbrueck-Center, Berlin  * * * * * * * * * \n";
print " * * * * * * * * * email: fruesch\@mdc-berlin.de  * * * * * * * * * \n\n";
print "  Usage        : perl [path]gh_snp_fam_lod.pl [-h] [-clean] [<famnr>]\n";
print "  Infiles      : gh_<v>.out (default) \n";
print "  Outfiles     : myghlod.gp, chr_line and lod.plt \n" ;
print "  View results : gnuplot myghlod.gp\n\n";
exit 0;
}

################################   C L E A N   ################################  

sub Clean { 
unlink glob("*.plt");
unlink glob("*.gp");
unlink glob("chr_line");
exit 0;
}

### end gh_snp_fam_lod.pl
