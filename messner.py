#!/usr/bin/env python
import sys, os, re, os.path, getopt

version = 0.2

debug = False
PEAK_THRESHOLD = 3.0
filename_pat = None

#simwalk_filename_pat = re.compile("^SCORE\-(\d\d)\_(\d+)\.ALL$")
simwalk_line_pat = re.compile("^\s*\,\s*(\-?\d+\.\d+)\s*\,\s*(\-?\d+\.\d+)\s*\,\s*\,\s*(\-?\d+\.\d+)\s*\,\s*(\-?\d+\.\d+)")
simwalk_line_pat2 = re.compile("^(\-\d+)")

#gh_filename_pat = re.compile("^gh_(\d+).out$")
#gh_line_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)$")
gh_line_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*\((\-?\d+\.\d+)\,\ (\-?\d+\.\d+)\)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)")
#al_line_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(rs\d+)")
al_line_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(rs\d+)")

mode = "simwalk"
map_format = "decode"

last_neg_to_pos = None
look_for_neg_to_pos = True
peak = False
peak_value = -1
last = 0
marker_map = {}
physical_positions = {}
phys2marker = {}
mapfile = None

def usage() :
	print >> sys.stderr, "usage: ./%s -m map_file [-sgh] [-l lod threshold]" % sys.argv[0]
	print >> sys.stderr, "\t-m, --map\t\tmap file location (MANDATORY)"
	print >> sys.stderr, "\t-x, --mapformat:\tformat of map file [decode (default), illumina]"
	print >> sys.stderr, "\t-l, --lod:\t\tset lod threshold, (default = 3)"
	print >> sys.stderr, "\t-s, --simwalk:\t\tparse simwalk output files (cannot be used in combination with -g or -a)"
	print >> sys.stderr, "\t-g, --genehunter:\tparse genehunter output files (cannot be used in combination with -s or -a)"
	print >> sys.stderr, "\t-a, --allegro:\t\tparse allegro output files (cannot be used in combination with -g or -s)"
	print >> sys.stderr, "\t-f, --force:\t\tignore warnings and carry on regardless\
				\n\t\t\t\t(use of this option implies you are no longer doing science...)"
	print >> sys.stderr, "\t-h, --help:\t\tsee usage info\n"

def find_phys(positions, chromosome, pos):
	#print "find_phys: %f, chr: %d" % (pos, chromosome)
	pos *= 1e6
	
	poz = positions[chromosome]
	index = len(poz) / 2
	next_jump = index / 2

	while 1 :
		phys1 = poz[index]
		next_jump /= 2

		if next_jump < 1 :
			next_jump = 1
		#else :
		#	print next_jump

		if pos < phys1 :
			index -= next_jump
		else :
			index += next_jump

		if index == len(poz) :
			return poz[-1], poz[-1]
		if index == 0 :
			return poz[0], poz[0]

		try :
			phys2 = poz[index]
		except Exception, e:
			print "==========="
			print index
			print next_jump
			print len(poz)
			print str(e)
			sys.exit(-1)

		if (next_jump == 1) :
			if (phys1 < phys2) and (phys1 < pos) and (phys2 > pos):
				return phys1,phys2
			
			if (phys2 < phys1) and (phys2 < pos) and (phys1 > pos):
				return phys2,phys1


# parse command line args
try:
	opts, args = getopt.getopt(sys.argv[1:], "hm:x:l:vsgaf", ["help","map=","mapformat=","lod=","verbose","simwalk","genehunter","allegro","force"])
except getopt.GetoptError, err:
	print >> sys.stderr, str(err)
	usage()
	sys.exit(-1)

output = None
verbose = False
genehunter_flag = False
simwalk_flag = False
allegro_flag = False
formats = ("illumina","decode")
format = "decode"
force_flag = False

for o, a in opts:
	if o == "-v":
		debug = True
	elif o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-f","--force"):
		force_flag = True
	elif o in ("-m", "--map"):
		mapfile = a
	elif o in ("-s","--simwalk"):
		simwalk_flag = True
	elif o in ("-g","--genehunter"):
		genehunter_flag = True
	elif o in ("-a","--allegro"):
		allegro_flag = True
	elif o in ("-x","--mapformat"):
		format = a.lower()
		if format not in formats :
			print >> sys.stderr, "Error: illegal map file format (see -h for details): %s" % format
			sys.exit(-1)
	elif o in ("-l","--lod"):
		try :
			PEAK_THRESHOLD = float(a)

		except :
			print >> sys.stderr, "Error: lod score must be a number"
			sys.exit(-1)
	else:
		assert False, "unhandled option"

if (not (simwalk_flag ^ genehunter_flag ^ allegro_flag)) :
	print >> sys.stderr, "%s: only one output file format can be specified" % sys.argv[0]
	sys.exit(-1)
elif genehunter_flag :
	mode = "genehunter"
elif allegro_flag :
	mode = "allegro"
else :
	mode = "simwalk"


if mapfile == None :
	print >> sys.stderr, "Error: map file not specified"
	usage()
	sys.exit(-1)

try :
	mf = open(mapfile)
except IOError, err:
	print >> sys.stderr, str(err)
	sys.exit(-1)


# parse map file
header = mf.readline()
num_columns = len(header.split())
if (((num_columns == 4 and format != "illumina")) or ((num_columns == 8 and format != "decode"))) and (force_flag != True):
	print >> sys.stderr, "warning: are you sure %s is in %s format?" % (mapfile,format)
	print >> sys.stderr, "\tif I'm wrong about this, then rerun with the -f or --force flag to run anyway\n"
	sys.exit(-1)

for line in mf :
	data = line.split()
	
	if format == "decode":
		probe_id = data[1]
		phys_pos = data[3]
		rs_id = data[4]
		chromosome = data[0]
	elif format == "illumina":
		probe_id = data[0]
		phys_pos = data[3]
		rs_id = data[0]
		chromosome = data[2]

	try :	
		if not physical_positions.has_key(int(chromosome)) :
			physical_positions[int(chromosome)] = []

		physical_positions[int(chromosome)].append(int(phys_pos))
		marker_map[probe_id] = (phys_pos, rs_id)	
		phys2marker[(int(chromosome), int(phys_pos))] = probe_id
	except ValueError :
		continue		
mf.close()

#physical_positions.sort()
#for i in physical_positions :
#	print i
#
#sys.exit(-1)


# find chromosome directories
chromosomes = []
for chrdir in os.listdir('.') :
	if os.path.isdir(chrdir) and re.match("^c\d\d$", chrdir) :
		chromosomes.append(int(chrdir[1:]))

# for each chromosomes directory... (in order)
for c in sorted(chromosomes) :
	chrdir = "c%02d" % c
	
	# find all the score files
	if mode == "simwalk" :
		filename_pat = re.compile("^SCORE\-%02d\_(\d+)\.ALL$" % c)
	elif mode == "genehunter" :
		filename_pat = re.compile("^gh_(\d+).out$")
	elif mode == "allegro" :
		filename_pat = re.compile("^linall_mpt\.(\d+)$")
	
	filelist = filter(lambda x : filename_pat.match(x), os.listdir(chrdir))
	results_indices = map(lambda x : int(filename_pat.match(x).group(1)), filelist)
	
	if len(results_indices) == 0 :
		print >> sys.stderr, "no results files in %s/ (are you sure this is output from %s?)" % (chrdir, mode)
		continue

	largest = max(results_indices)
	gh_xsum = 0.0

	if mode == "allegro":
		largest = 1

	for i in range(1, largest + 1) :
		filename = chrdir + os.sep
		if mode == "simwalk":
			filename += "SCORE-%02d_%d.ALL" % (c,i)
		elif mode == "genehunter":
			filename += "gh_%d.out" % i
		elif mode == "allegro":
			filename += "param_mpt.%02d" % c
			#filename += "linall_mpt.%02d" % c

		if debug :
			print filename
		
		try :
			f = open(filename)
		except :
			print >> sys.stderr, "could not open file: %s" % filename
			sys.exit(-1)
		
		lines = f.readlines()
		f.close()

		# find markers and LOD scores
		tmp = []
		gh_max_x = 0.0
		
		for line in lines :
			if mode == "simwalk":
				# simwalk LOD score
				m = simwalk_line_pat.match(line)
				if m :
					tmp.append(m.groups())
					continue
				# simwalk marker name
				m = simwalk_line_pat2.match(line)
			elif mode == "genehunter":
				line.replace("-INFINITY", "-99.99")
				line.replace("NaN", "-0.5")
				line.replace("nan", "-0.5")
				m = gh_line_pat.match(line)
			elif mode == "allegro":
				m = al_line_pat.match(line)

			if m :
				if mode == "simwalk" :
					marker = m.group(1)
				elif mode == "genehunter" :
					tmp.append(m.groups())
					marker = m.group(1)
				elif mode == "allegro":
					tmp.append(m.groups())
					marker = m.group(5)

				for t in tmp:
					pos,loc = map(float, t[:2])

					if mode == "genehunter" :
						if gh_max_x < pos :
							gh_max_x = pos
						pos += gh_xsum
						marker = pos
						#print marker
						#marker = str(float(marker) + gh_xsum)

					if debug :
						print marker,
						print t

					# is this a peak, if the same peak update the score
					if (loc > PEAK_THRESHOLD) and (loc > peak_value) :
						peak_value = loc
						if debug and not peak :
							print "peak of %f found @ %s" % (peak_value, str(marker))
						peak = True

					# do the LOD scores go from neg -> pos?
					if look_for_neg_to_pos :
						if loc >= 0 and last <= 0 :
							last_neg_to_pos = marker
							look_for_neg_to_pos = False
							if debug :
								print "neg -> pos (%f --> %f)" % (last,loc)
					# else do they go from pos -> neg? (this is to record crossing the x-axis)
					else :
						if last >= 0 and loc <= 0 :
							look_for_neg_to_pos = True

							if debug :
								print "pos -> neg (%f --> %f)" % (last,loc)

							# if we are descending a peak, print the data
							if peak :
								peak = False
								prefix = ""
								if mode == "simwalk" and format != "illumina":
									prefix = "SNP_A"
								elif mode == "genehunter":
									pa1,pa2 = find_phys(physical_positions, c, float(last_neg_to_pos))
									pb1,pb2 = find_phys(physical_positions, c, float(marker))

									last_neg_to_pos = phys2marker[c,pa1]
									marker 		= phys2marker[c,pb2]
									prefix = ""

								phys_1, rs_1 = marker_map[prefix + str(last_neg_to_pos)]
								phys_2, rs_2 = marker_map[prefix + str(marker)]
								
								print "chr%d %s %s %s_%s_%f" % (c, phys_1, phys_2, rs_1, rs_2, peak_value)
								#print "\t%s %s" % (str(last_neg_to_pos),str(marker))
								peak_value = -1
								# print out peak
					last = loc
				tmp = []

		gh_xsum += gh_max_x
		
