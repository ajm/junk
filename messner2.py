#!/usr/bin/env python
import sys, os, re, os.path, getopt, glob

version = 0.3

verbose         = False
force_flag      = False
genehunter_flag = False
simwalk_flag    = False
allegro_flag    = False

format          = None
mapfile         = None
mode            = "simwalk"
formats         = ("illumina","decode")
PEAK_THRESHOLD  = 3.0

probe_map           = {}
marker_map          = {}
physical_map        = {}
physical_positions  = {}

# simwalk
simwalk_rsid_decode = re.compile("^rs|s|\d\d+$")
simwalk_rsid_illumina = re.compile("^(\-\d+)$")
simwalk_lod = re.compile("^\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\s*(\-?\d+\.\d+)")
# genehunter
gh_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*\((\-?\d+\.\d+)\,\ (\-?\d+\.\d+)\)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)")
# allegro
al_line_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(rs\d+)")


class map_entry :
    def __init__(self, rs, chromosome, phypos, probeid) :
        self.rs = rs
        self.chromosome = chromosome
        self.physical_position = phypos
        self.probeid = probeid

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

# create tuples of (rsid,phypos,lod score)
def read_simwalk(c, fname) :
    global format
    data = []

    try :
        f = open(fname)
    except :
        print >> sys.stderr, "could not open file: %s" % filename
        sys.exit(-1)
    lines = f.readlines()
    f.close()

    tmp = []
    for line in lines :
        # lod score
        m = simwalk_lod.match(line)
        if m :
            tmp.append(m.groups())
            continue
        
        # marker name (a small nightmare, this depends on what alohomora uses...)
        if format == 'decode' :
            m = simwalk_rsid_decode.match(line)
            if m :
                marker = "SNP_A" + m.group(1)
                marker = marker2rsid[marker]

        elif format == 'illumina' :
            m = simwalk_rsid_illumina.match(line)
            if m :
                if m.group(1).startswith('rs') :
                    marker = m.group(1)
                elif m.group(1).startswith('s') :
                    marker = 'r' + m.group(1)
                else :
                    marker = 'rs' + m.group(1)
        
        if m :
            marker = m.group(1)
            for t in tmp :
                me = physical_map[(c, float(t[0]))]
                data.append((marker, me.physical_position, float(t[1])))
            
    return data

def read_all_simwalk(c) :
    chrdir = "c%02d" % c
    files = glob.glob(chrdir + os.sep + "SCORE*_*.ALL")
    largest = max(map(lambda x : int(x[x.index('_')+1 : x.index('.')]), files))
    all_data = []
    
    for i in range(1, largest + 1) :
        fname = chrdir + os.sep + "SCORE-%02d_%d.ALL" % (c,i)
        all_data += read_simwalk(c, fname)

    return all_data

def read_all_genehunter(dir) :
    pass

def read_all_allegro(chr) :
    pass


try:
    opts, args = getopt.getopt(sys.argv[1:], "hm:x:l:vsgaf", ["help","map=","mapformat=","lod=","verbose","simwalk","genehunter","allegro","force"])
except getopt.GetoptError, err:
    print >> sys.stderr, str(err)
    usage()
    sys.exit(-1)


# handle command line args
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


# read map file
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
if (((num_columns == 4 and format != "illumina")) \
        or ((num_columns == 8 and format != "decode"))) \
        and (force_flag != True):
    print >> sys.stderr, "warning: are you sure %s is in %s format?" % (mapfile,format)
    print >> sys.stderr, "\tif I'm wrong about this, then rerun with the -f or --force flag to run anyway\n"
    sys.exit(-1)

for line in mf :
    data = line.split()

    if format == "decode":
        probe_id    = data[1]
        phys_pos    = int(data[3])
        rs_id       = data[4]
        chromosome  = int(data[0])
    elif format == "illumina":
        probe_id    = data[0]
        phys_pos    = int(data[3])
        rs_id       = data[0]
        chromosome  = int(data[2])

    me = map_entry(rs_id, chromosome, phys_pos, probe_id)

    probe_map[probeid] = me
    marker_map[rs_id] = me
    physical_map[(chromosome,phys_pos)] = me

    if not physical_positions.has_key(chromosome) :
        physical_positions[chromosome] = []

    physical_positions[chromosome].append(int(phys_pos))
    
mf.close()


# find chromosome directories
chromosomes = []
for chrdir in os.listdir('.') :
    if os.path.isdir(chrdir) and re.match("^c\d\d$", chrdir) :
        chromosomes.append(int(chrdir[1:]))

# for each chromosomes directory... (in order)
for c in sorted(chromosomes) :
    #chrdir = "c%02d" % c

    if mode == 'simwalk' :
        data = read_all_simwalk(c)
    elif mode == 'genehunter' :
        data = read_all_genehunter(c)
    elif mode == 'allegro' :
        data = read_all_allegro(c)

    peak = False
    last_lod = 0
    look_for_neg_to_pos = True
    peak_value = -1
    lastnegtopos_marker = None
    lastnegtopos_phypos = None

    for marker,pos,lod in data :

        # is this a peak, if the same peak update the score
        if (lod > PEAK_THRESHOLD) and (lod > peak_value) :
            peak_value = lod
            if debug and not peak :
                print >> sys.stderr, "peak of %f found @ %s" % (peak_value, str(marker))
            peak = True
        
        # do the LOD scores go from neg -> pos?
        if look_for_neg_to_pos :
            if lod >= 0 and last_lod <= 0 :
                lastnegtopos_marker = marker
                lastnegtopos_phypos = pos
                look_for_neg_to_pos = False

                if debug :
                    print >> sys.stderr, "neg -> pos (%f --> %f)" % (last_lod, lod)
        # else do they go from pos -> neg? (this is to record crossing the x-axis)
        else :
            if last_lod >= 0 and lod <= 0 :
                look_for_neg_to_pos = True

                if debug :
                    print >> sys.stderr, "pos -> neg (%f --> %f)" % (last,lod)

                # if we are descending a peak, print the data
                if peak :
                    print "chr%d %s %s %s_%s_%f" % \
                        (c, lastnegtopos_phypos, pos, lastnegtopos, marker, peak_value)
                    peak = False
                    peak_value = -1
            
        last_lod = lod

