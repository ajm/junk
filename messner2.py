#!/usr/bin/env python
import sys, os, re, os.path, getopt, glob

version = 0.3

verbose         = False
debug           = False
force_flag      = False
genehunter_flag = False
simwalk_flag    = False
allegro_flag    = False

#format          = None
mapfile         = None
mode            = "simwalk"
formats         = ("illumina","decode")
PEAK_THRESHOLD  = 3.0

probe_map           = {}
marker_map          = {}
physical_map        = {}
physical_positions  = {}

# simwalk
simwalk_rsid = re.compile("^rs|s|\d\d+$")
#imwalk_rsid_illumina = re.compile("^rs|s|\d\d+$")
#imwalk_rsid_decode = re.compile("^(\-\d+)$")
simwalk_lod = re.compile("^\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\
\s*\,\s*(\-?\d+\.\d+)\
\s*\,\s*(\-?\d+\.\d+)")
# genehunter
gh_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*\((\-?\d+\.\d+)\,\ (\-?\d+\.\d+)\)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)")
# allegro
al_pat = re.compile("^\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(rs\d+)")


class map_entry :
    def __init__(self, rs, chromosome, phypos, probeid) :
        self.rs = rs
        self.chromosome = chromosome
        self.physical_position = phypos
        self.probeid = probeid

# this is a horrible hack, (at least it takes log(n) iterations)
# the idea is that genehunter positions do not match any physical positions
# hence we need to find the closest position that contains a valid marker 
# from the map - annoyingly many markers map to the same positions reported
# by genehunter (annecdotally, the first 5 positions in a gh file I am working
# on are all 0.00)
def find_phys(position_list, pos):
    pos *= 1e6
    pos = int(pos)

    #poz = physical_positions[chromosome]
    poz = position_list
    index = len(poz) / 2
    next_jump = index

    while 1 :
        phys1 = poz[index]
        next_jump /= 2

        if next_jump < 1 :
            next_jump = 1

        if pos < phys1 :
#            print "-"
            index -= next_jump
        else :
#            print "+"
            index += next_jump

        if index == len(poz) :
            return poz[-1]#, poz[-1]
        if index == 0 :
            return poz[0]#, poz[0]

        try :
            phys2 = poz[index]
        except Exception, e:
            print >> sys.stderr, "i=%d jump=%d poz=%d : %s" % (index, next_jump, len(poz), str(e))
            sys.exit(-1)

#        print "[%d]\tindex = %d,\tjump = %d,\tpos = %d,\trs = %s" % (pos, index, next_jump, poz[index], physical_map[(chromosome,poz[index])].rs)
#        print "phy1 = %d, phy2 = %d" % (phys1,phys2)

        if (next_jump == 1) :
            if ((phys1 - pos)**2) < ((phys2 - pos)**2) :
#                print "return 1"
                return phys1
            else :
#                print "return 2"
                return phys2


def usage() :
    print >> sys.stderr, "usage: %s -m map_file [-sgh] [-l lod threshold]" % sys.argv[0]
    print >> sys.stderr, "\t-m, --map\t\tmap file location (MANDATORY)"
#    print >> sys.stderr, "\t-x, --mapformat:\tformat of map file [decode (default), illumina]"
    print >> sys.stderr, "\t-l, --lod:\t\tset lod threshold, (default = 3)"
    print >> sys.stderr, "\t-s, --simwalk:\t\tparse simwalk output files\t(cannot be used in combination with -g or -a)"
    print >> sys.stderr, "\t-g, --genehunter:\tparse genehunter output files\t(cannot be used in combination with -s or -a)"
    print >> sys.stderr, "\t-a, --allegro:\t\tparse allegro output files\t(cannot be used in combination with -g or -s)"
    print >> sys.stderr, "\t-f, --force:\t\tignore warnings and carry on regardless\
\n\t\t\t\t(use of this option implies you are no longer doing science...)"
    print >> sys.stderr, "\t-h, --help:\t\tsee usage info\n"

# create tuples of (rsid,phypos,lod score)
def read_simwalk(c, fname) :
    #global format
    data = []
    chr_str = "%02d" % c

    try :
        f = open(fname)
    except :
        print >> sys.stderr, "could not open file: %s" % fname
        sys.exit(-1)
    lines = f.readlines()
    f.close()

    tmp = []
    for line in lines :
        # lod score
        m = simwalk_lod.match(line)
        if m :
            #print m.groups()
            tmp.append(m.groups())
            continue

        m = simwalk_rsid.match(line)
        if m :
            #print line,
            stripped = line.strip()
            if stripped.startswith('rs') :
                marker = stripped
            elif stripped.startswith('s') :
                marker = 'r' + stripped
            else :
                marker = 'rs' + stripped
        
            me = marker_map[marker]
            for t in tmp :
                data.append((marker, me.physical_position, float(t[1])))
                #print marker,
                #print me.physical_position,
                #print t[1]
            tmp = []
            
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

def read_genehunter(c, fname, current_pos_sum) :
    data = []
    chr_str = "%02d" % c

    try :
        f = open(fname)
    except :
        print >> sys.stderr, "could not open file: %s" % fname
        sys.exit(-1)
    lines = f.readlines()
    f.close()

    tmp = []
    markers = []
    physical_list = None

    for line in lines :
        if line.startswith("marker rs") :
            rs = line.strip().split()[1]
            markers.append(rs)
            continue

        line.replace("-INFINITY", "-99.99")
        line.replace("NaN", "-0.5")
        line.replace("nan", "-0.5")

        m = gh_pat.match(line)
        if m :
            if physical_list == None :
                physical_list = []
                for mk in markers :
                    physical_list.append( int(marker_map[mk].physical_position) )
                physical_list.sort()

            pos,lod = map(float, m.groups()[:2])
            phys = find_phys(physical_list, current_pos_sum + pos) # find the closest physical position
            me = physical_map[(chr_str,phys)]       # find the marker at this position

            if me.rs not in markers :
                print >> sys.stdout, "%s : %s not in possible marker list" % (fname,me.rs)

            data.append((me.rs, me.physical_position, float(lod)))

    return data, current_pos_sum + pos

def read_all_genehunter(c) :
    chrdir = "c%02d" % c
    files = glob.glob(chrdir + os.sep + "gh*out")
    largest = max(map(lambda x : int(x[x.index('_')+1 : x.index('.')]), files))
    all_data = []

    pos_sum = 0.0

    for i in range(1, largest + 1) :
        fname = chrdir + os.sep + "gh_%d.out" % (i)
        tmp,current_sum = read_genehunter(c, fname, pos_sum)
        all_data += tmp
        pos_sum = current_sum

    return all_data

def read_all_allegro(c) :
    chrdir = "c%02d" % c
    all_data = []
    f = open(chrdir + os.sep + "param_mpt.%02d" % c)
    for line in f :
        # create tuples of (rsid,phypos,lod score)
        m = al_pat.match(line)
        if m :
            marker = m.group(5)
            me = marker_map[marker]
            all_data.append((marker, me.physical_position, float(m.group(2))))

    return all_data

try:
    #opts, args = getopt.getopt(sys.argv[1:], "hm:x:l:vsgaf", ["help","map=","mapformat=","lod=","verbose","simwalk","genehunter","allegro","force"])
    opts, args = getopt.getopt(sys.argv[1:], "hm:l:vsgaf", ["help","map=","lod=","verbose","simwalk","genehunter","allegro","force"])
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
#    elif o in ("-x","--mapformat"):
#        format = a.lower()
#        if format not in formats :
#            print >> sys.stderr, "Error: illegal map file format (see -h for details): %s" % format
#            sys.exit(-1)
    elif o in ("-l","--lod"):
        try :
            PEAK_THRESHOLD = float(a)

        except :
            print >> sys.stderr, "Error: lod score must be a number"
            sys.exit(-1)
    else:
        assert False, "unhandled option"

if (not (simwalk_flag ^ genehunter_flag ^ allegro_flag)) :
    print >> sys.stderr, "%s: exactly one output file format must be specified" % sys.argv[0]
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
#if (((num_columns == 4 and format != "illumina")) \
#        or ((num_columns == 8 and format != "decode"))) \
#        and (force_flag != True):
#    print >> sys.stderr, "warning: are you sure %s is in %s format?" % (mapfile,format)
#    print >> sys.stderr, "\tif I'm wrong about this, then rerun with the -f or --force flag to run anyway\n"
#    sys.exit(-1)

for line in mf :
    data = line.split()

    probe_id    = data[1]
    phys_pos    = data[3]
    rs_id       = data[4]
    chromosome  = data[0]

    if not rs_id.startswith('rs') :
        continue

    if len(rs_id) > 10 :
        print >> sys.stderr, "Warning: %s is longer than 10 characters, so it is ambiguous in simwalk output files which truncates it to 8 characters" % rs_id

    me = map_entry(rs_id, chromosome, phys_pos, probe_id)

    probe_map[probe_id] = me
    marker_map[rs_id] = me
    physical_map[(chromosome,int(phys_pos))] = me

    if not physical_positions.has_key(chromosome) :
        physical_positions[chromosome] = []

    physical_positions[chromosome].append(int(phys_pos))
    
mf.close()

if debug :
    print >> sys.stderr, mapfile + " read in..."


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
                        (c, lastnegtopos_phypos, pos, lastnegtopos_marker, marker, peak_value)
                    peak = False
                    peak_value = -1
            
        last_lod = lod

