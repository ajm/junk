#!/usr/bin/env python
import sys, os, re, os.path, getopt

debug = False

PEAK_THRESHOLD = 3

sp = re.compile("^SCORE\-(\d\d)\_(\d+)\.ALL$")
sp_line = re.compile("^\s*\,\s*(\-?\d+\.\d+)\s*\,\s*(\-?\d+\.\d+)\s*\,\s*\,\s*(\-?\d+\.\d+)\s*\,\s*(\-?\d+\.\d+)")
sp_line2 = re.compile("^(\-\d+)")

last_neg_to_pos = None
look_for_neg_to_pos = True
peak = False
peak_value = -1
last = 0
marker_map = {}
mapfile = None

def usage() :
	print >> sys.stderr, "%s -m map_file [-l lod threshold (default is 3)] [-h]\n" % sys.argv[0]

# parse command line args
try:
	opts, args = getopt.getopt(sys.argv[1:], "hm:l:v", ["help", "map=", "lod=", "verbose"])
except getopt.GetoptError, err:
	print >> sys.stderr, str(err)
	usage()
	sys.exit(-1)

output = None
verbose = False
for o, a in opts:
	if o == "-v":
		debug = True
	elif o in ("-h", "--help"):
		usage()
		sys.exit()
	elif o in ("-m", "--map"):
		mapfile = a
	elif o in ("-l","--lod"):
		try :
			PEAK_THRESHOLD = int(a)
		except :
			print >> sys.stderr, "Error: peak must be an integer"
			sys.exit(-1)
	else:
		assert False, "unhandled option"


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
mf.readline()
for line in mf :
	data = line.split()
	probe_id = data[1]
	phys_pos = data[3]
	rs_id = data[4]
	marker_map[probe_id] = (phys_pos, rs_id)
mf.close()


# find chromosome directories
chromosomes = []
for chrdir in os.listdir('.') :
	if os.path.isdir(chrdir) and re.match("^c\d\d$", chrdir) :
		chromosomes.append(int(chrdir[1:]))

# for each chromosomes directory... (in order)
for c in sorted(chromosomes) :
	chrdir = "c%02d" % c
	# find all the score files
	filelist = filter(lambda x : sp.match(x), os.listdir(chrdir))
	largest = max(map(lambda x : int(sp.match(x).group(2)), filelist))
	for i in range(1, largest + 1) :
		filename = chrdir + os.sep + "SCORE-%02d_%d.ALL" % (c,i)
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
		
		for line in lines :
			# LOD score
			m = sp_line.match(line)
			if m :
				tmp.append(m.groups())
				continue
			# marker name
			m = sp_line2.match(line)
			if m :
				marker = m.group(1)
				for t in tmp:
					pos,loc = map(float, t[:2])

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
								phys_1, rs_1 = marker_map["SNP_A" + str(last_neg_to_pos)]
								phys_2, rs_2 = marker_map["SNP_A" + str(marker)]
								print "chr%d %s %s %s_%s_%f" % (c, phys_1, phys_2, rs_1, rs_2, peak_value)
								peak_value = -1
								# print out peak
					last = loc
				tmp = []

