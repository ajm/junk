#!/usr/bin/perl

#
# allegro_lod.pl :  Prepare Allegro output for displaying with gnuplot
# Syntax    :  perl allegro_lod.pl [-h] [-clean] [-hlod]
# Infiles   :  <Argument1> (default)
# Outfiles  :  myplot.gp, chr_line hlod.plt and lod.plt
# Modified  : 11-Sept-2006	FR

use Cwd;

print "\n\n";
print " * * * * * * * * * * * ALLEGRO_LOD.PL v1.2  * * * * * * * * * * * *\n";
print " * * * * * * * * View Allegro results with GNUPLOT  * * * * * * * *\n";

my $nodelete=0;
my $hline=1;
my $hlod=0;
my $legend=1;
my $label=1;
my $title=1;
my $xtics=1;

for ($i=0;$i<=$#ARGV;$i++) {
	if ($ARGV[$i] eq "-h" ) { &Help;}
	elsif ($ARGV[$i] eq "-v" ) { &Help;}
	elsif ($ARGV[$i] eq "-nd" ) { $nodelete=1;}
	elsif ($ARGV[$i] eq "-clean" ) { &Clean;}
	elsif ($ARGV[$i] eq "-noxtics" ) {$xtics=0;}
	elsif ($ARGV[$i] eq "-nohline" ) {$hline=0;}
	elsif ($ARGV[$i] eq "-nl" ) {$legend=0;}
	elsif ($ARGV[$i] eq "-nolabel" ) {$label=0;}
	elsif ($ARGV[$i] eq "-nt" ) {$title=0;}
	elsif ($ARGV[$i] =~ /-hlod/ ) {$hlod=1;}
	else {print "Argument: $ARGV[$i]\n";}
}

print "\nRead ...\n";
my $pfad = getcwd();
my $datum = scalar localtime;
my $in_file="";

my $xsum = 0.0;
my $xmin = 0;

my $ymax = 2;
my $ymin = -3;

my @xsums=();
my $lastxsum=0.;
my %chrlabel=();
my $status=0;

#######################################    M A I N   #############################															
open (out1,">$pfad/lod.plt") || die "could not open lod.plt :$!\n";
open (out2,">$pfad/hlod.plt") || die "could not open hlod.plt :$!\n";

# foreach my $dir (c21) {
foreach my $dir (c01,c02,c03,c04,c05,c06,c07,c08,c09,c10,c11,c12,c13,c14,c15,c16,c17,c18,c19,c20,c21,c22,c23,cx) { # c24
	if (-d $dir) {
		$status=0;
		my $chr=$dir;
		$chr=~ s/c//;
		$in_file = "${dir}/param_mpt\.${chr}";	# no sets of markers, one outfile per chromosome
		if (-f "$in_file") {	  
			&ReadLod();
		}
		else { 
			my @set=glob("${dir}/param_mpt_*.*"); # moving window with sets of markers
			my $nr=$#set+1;
			foreach my $i ( 1..$nr) {		
				$in_file = "${dir}/param_mpt_${i}\.${chr}";
				if (-f "$in_file") {	  
					&ReadLod(); 
				}
			}
		} 
		if ($status == 1) {
			my $xpos=(($lastxsum + $xsum)/2);
			my $var=$dir; $var =~ s/c0//;$var =~ s/c//;
			if ($var > 9){ $xpos -=30;}
			else { $xpos -=5;}
			if ($var eq "23") {$var = "X";}
			if ($var == "24") {$var = "XY";}
			$chrlabel{$var}=$xpos;
			$lastxsum=$xsum;
		}
		push (@xsums,$xsum);
	}
	else { print "$dir not existing \n";
	}
} # end foreach

close (out1);
close (out2);
&print_chr_line;
&pr_batch;

# print "\nYou can now view results by \"gnuplot myplot.gp\" \n\n";
system ("gnuplot myplot.gp");

if ($nodelete == 0) { &Clean ();}

#################################   R E A D L O D   #################################  

sub ReadLod {
	my @v=();
	my $xmax = 0.0;
	open (IN, "$in_file") || die "could not open $in_file :$!\n";
	print "File: $in_file\n"; 
	$status =1;
	while (<IN>){
		$_ =~ s/-Inf/-99\.99/g;
		$_ =~ s/-Infinity/-99\.99/g;
		$_ =~ s/-inf/-99\.99/g;
		$_ =~ s/nan/-99\.99/g;
		chomp;
		@v = split(' ',$_);
		if ($. > 1) {
			printf(out1 "%f %s\n", ($v[0] + $xsum), $v[1]);
			printf(out2 "%f %s\n", ($v[0] + $xsum), $v[3]);
			if ($v[0] > $xmax) { $xmax = $v[0];}  
			if ($v[1] > $ymax) { $ymax = $v[1];}
			if ($v[3] > $ymax) { $ymax = $v[3];}
		}
	} # end foreach
	close (IN);
	$xsum = $xsum + $xmax;
} ## end ReadLod

######################   P R I N T  C H R _ L I N E S   ######################
sub print_chr_line {

#	$xsum = 3700;		# for a fixed axle in every picture
	$ymax += 1;						# y-achse auf ganze HLOD-Zahl bringen
	my @buff =	split('\.',$ymax);		# round to integer
	$ymax=$buff[0];
	
	if ($hlod ==1) {$ymin=0.0;}
	open (out3,"> chr_line") || die "could not open chr_line :$!\n";

	if ($hline=1){
		for (my $i= $ymin+1; $i<$ymax;$i++) {	# horizontale Linien bei LODs = 1,2,3,4,..
			print out3 "0 $i\n$xsum $i\n\n";
		}
	}
	pop @xsums;
	foreach (@xsums){				# vertikale Linien Chromosomenende 1,2,3,4,...22,x,xy
		print out3 "$_ $ymin \n$_ $ymax \n\n";         
	}
	close (out3);
}
###-----------------------  P R I N T  G N U P L O T  B A T C H   -----------------------###
sub pr_batch {

	if ($hlod == 1) {$titel = "$pfad - Allegro HLOD  - $datum";}
	else {$titel = "$pfad - Allegro LOD   - $datum";}
	
	open (out5,"> myplot.gp") || die "could not open myplot.gp :$!\n";

	print out5 "set autoscale\n";
	print out5 "set nokey\n";
	if ($title == 1) { print out5 "set title \"$titel\"\n";}
	#print out5 "set xlabel \"cM\"\n";
	print out5 "set xlabel \"MB\"\n";
	if ($label == 1) {
		my $ypos = $ymax + (($ymax-$ymin)/35);
		foreach (keys %chrlabel) {print out5 "set label \"$_\" at $chrlabel{$_}\,$ypos font \"Ariel,8\"\n";}
	}
	print out5 "set ytics $ymin,1,$ymax\n";
	if ($xtics == 0) {print out5 "set noxtics\n";}
	print out5 "set size 1,0.6\n";

	if ($legend == 0){ print out5 "set nokey\n";}
	print out5 "set terminal postscript color solid 11\n";
	if ($hlod == 1) {
		print out5 "set ylabel \"HLOD\"\n";
		print out5 "set output \"allegro_hlod.ps\"\n";
		print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'chr_line\' notitle with lines lt 0,  \'hlod.plt\' title 'HLOD' with lines lt 3\n";
	}
	else {
		print out5 "set ylabel \"LOD\"\n";
		print out5 "set output \"allegro_lod_${chr}.ps\"\n";
		print out5 "plot \[$xmin\:$xsum\] \[$ymin\:$ymax\]  \'chr_line\' notitle with lines lt 0, \'lod.plt\' title 'LOD' with lines lt 1\n";
	}		
	print out5 "set terminal x11\n";
	print out5 "replot\n";
	print out5 "\npause -1 \"Hit return to continue\"\n\n";

	close (out5);

} ## end pr_batch
					

#################################   H E L P   #################################  
sub Help {

print " * * * * * * Created by Franz Rueschendorf 19-Sept-2004  * * * * * * \n";
print " * * * * * * * * * Max-Delbrueck-Center, Berlin  * * * * * * * * * \n";
print " * * * * * * * * * email: fruesch\@mdc-berlin.de  * * * * * * * * * \n\n";
print "  Usage        : perl [path]allegro_lod.pl [<options>]\n";
print "  Infiles      : param_mpt.chr (default) \n";
print "  Outfiles     : myplot.gp, chr_line, hlod.plt and lod.plt \n" ;
print "  View results : gnuplot myplot.gp\n\n";
exit 0;
}

################################   C L E A N   ################################  
#
# removes files in the current folder with the extension *.plt *.gp and chr_line
#
sub Clean { 
unlink glob("*.plt");
unlink glob("*.gp");
unlink "chr_line";
exit 0;
}

### end end allegro_lod.pl
