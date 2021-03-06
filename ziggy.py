#!/usr/bin/env python
import sys, os, getopt, commands
# the idea of ziggy is to find the stretches of homozygosity that surround a lod score peak 
# (where 'peak' is defined by a threshold given to messner)

def usage() :
    print >> sys.stderr, \
"""Usage: %s [-l N] [-hgsa]
    -l, --lod:           set lod threshold
    -g, --genehunter:    expect genehunter output files
    -a, --allegro:       expect allegro output files
    -s, --simwalk:       expect simwalk output files
        (only one of -g, -s and -a can be used at once, default: allegro)
    -m, --map:           filename of map file
    -x, --genotypes:     filename of genotype file
    -p, --pedfile:       filename of pedigree file
    -f, --family:        id of family (default: use all found in pedigree file)
    -t, --threshold:     minimum stretch of homozygosity (default: 1)
    -h, --help:          show this help info
    -v, --verbose:       be more verbose
""" % sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hl:gsam:x:p:vt:", ["help", "lod=", \
            "genehunter", "simwalk", "allegro", "map=", "genotypes=", "pedfile=", \
            "verbose", "threshold=", "family="])

except getopt.GetoptError, err:
    print >> sys.stderr, str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(-1)

lod = 3.0
verbose = False
program_arg = '-a'
mapfilename = "../map.txt"
pedfilename = "../pedfile.pro"
genotypefilename = "../genotypes"
family = None
report_threshold = 0
debug = False

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-l", "--lod"):
        lod = float(a)
    elif o in ("-g", "--genehunter"):
        program_arg = o
    elif o in ("-a", "--allegro"):
        program_arg = o
    elif o in ("-s", "--simwalk"):
        program_arg = o
    elif o in ("-m", "--map") :
        mapfilename = a
    elif o in ("-p", "--pedfile") :
        pedfilename = a
    elif o in ("-x", "--genotypes") :
        genotypefilename = a
    elif o in ("-v", "--verbose") :
        debug = True
    elif o in ("-t", "--threshold") :
        try :
            report_threshold = int(a) - 1
        except ValueError, ve :
            print >> sys.stderr, "%s not an appropriate homozygosity stretch threshold" % a
            sys.exit(-1)
        if report_threshold < 0 :
            print >> sys.stderr, "homozygosity stretch threshold must be at least 1 (you set it to %d)" % (report_threshold + 1)
            sys.exit(-1)

    elif o in ("-f", "--family") :
        try :
            family = int(a)
        except ValueError, ve :
            print >> sys.stderr, "%s not an appropriate family id" % a
            sys.exit(-1)

# map
print >> sys.stderr, "reading map file..."
markers = {}
marker_index = {}
physical_positions = {}
try :
    f = open(mapfilename)
except IOError, e :
    print >> sys.stderr, "%s" % str(e)
    print >> sys.stderr, "you probably need to specify the map file with the -m flag...\n"
    sys.exit(-1)

f.readline() # header
linenum = 0
for line in f :
    data = line.strip().split()
    chr,rsid = data[:2]

    try :
        chr = int(chr)
    except :
        pass # ie: X, XY, Y

    if chr not in markers :
        markers[chr] = []
        marker_index[chr] = {}
        linenum = 0

    markers[chr].append(rsid)
    marker_index[chr][rsid] = linenum

    physical_positions[rsid] = int(data[3])

    linenum += 1
f.close()

# ped
if family == None :
    print >> sys.stderr, "reading pedigree file..."
else :
    print >> sys.stderr, "reading pedigree file for family %d ..." % family

affection = {}
try :
    f = open(pedfilename)
except IOError, e :
    print >> sys.stderr, "%s" % str(e)
    print >> sys.stderr, "you probably need to specify the pedigree file with the -p flag...\n"
    sys.exit(-1)

f.readline()
for line in f :
    line = line.strip()
    if len(line) == 0 :
        continue
    data = line.split()
    fam,pid,pat,mat,sex,aff = data

    if family != None :
        if family != int(fam) :
            continue

    if int(aff) == 2 :
        affection[int(pid)] = True
    else :
        affection[int(pid)] = False
f.close()

# geno
print >> sys.stderr, "reading genotype file..."
genotypes = {}
try :
    f = open(genotypefilename)
except IOError, e :
    print >> sys.stderr, "%s" % str(e)
    print >> sys.stderr, "you probably need to specify the genotypes file with the -x flag...\n"
    sys.exit(-1)

omitted = set()
header = f.readline()
patients = map(int, header.strip().split()[1:])
for line in f :
    # rsid, patient1, patient2...
    line = line.strip()
    if len(line) == 0 :
        continue
    data = line.split()
    m = data[0]
    g = data[1:]
    
    genotypes[m] = {}
    genotypes[m][True] = set()
    genotypes[m][False] = set()
    for i in range(len(patients)) :
        current = g[i]
        if current == 'NC':
            continue
        current = ''.join(sorted(g[i]))
        if patients[i] not in affection :
            omitted.add(patients[i])
            continue
        
        genotypes[m][ affection[patients[i]] ].add( current )

f.close()

#print >> sys.stderr, "\tomitted = %s" % str(omitted)

print >> sys.stderr, "running messner..."
#program_name = "python /home/ajm/code/bioinformatics-tools/messner2.py"
program_name = "messner2"
s,o = commands.getstatusoutput("%s -m %s -l %f %s" % (program_name, mapfilename, lod, program_arg))

#print o
#print "\n"

current_markers = None
current_marker_index = None

print >> sys.stderr, "looking for homozygosity..."

print "track name='ziggy' description='ziggy'"
for line in o.split('\n') :
    line = line.strip()
    if len(line) == 0 :
        continue
    data = line.split()
    chr,start,stop,guff = data
    m1,m2,lodscore = guff.split('_')

    chr = chr[3:]
    try :
        chr = int(chr)
    except :
        pass
    current_markers = markers[chr]
    current_marker_index = marker_index[chr]

    #print line
    peak_start = current_marker_index[m1]
    peak_end   = current_marker_index[m2]

    # do stuff...
    while True :
        if debug :
            print ""

        if peak_end - peak_start <= 0 :
            break

#        print "peak_start = %d" % peak_start
#        print "peak_end   = %d" % peak_end

        start_point = -1
        for i in range(peak_start, peak_end) :
            if current_markers[i] not in genotypes : # ie: this marker was removed by pedcheck or something...
                if debug :
                    print "\t[ignore] %s not found" % (current_markers[i])
                continue
            affected_g = genotypes[current_markers[i]][True]
            if (len(affected_g) == 1) and (('AA' in affected_g) or ('BB' in affected_g)) :
                if list(affected_g)[0] not in genotypes[current_markers[i]][False] :
                    if debug :
                        print "\t[bingo ] %s homozygous in affected only (%s , %s)" \
                                % (current_markers[i], str(tuple(affected_g)), str(tuple(genotypes[current_markers[i]][False])))
                    peak_start = start_point = i
                    hmode = list(affected_g)[0]
                    break
                else :
                    if debug :
                        print "\t[ skip ] %s homozygous, but not just in affected (%s , %s)" \
                                % (current_markers[i], str(tuple(affected_g)), str(tuple(genotypes[current_markers[i]][False])))
            else :
                if debug :
                    print "\t[ skip ] %s not homozygous in affected (%s , %s)" \
                            % (current_markers[i], str(tuple(affected_g)), str(tuple(genotypes[current_markers[i]][False])))

        if start_point == -1 :
#            print line,
            #print ": no homozygosity"
            break

        # go as far left as possible
        next = start_point
        while True :
            next -= 1
            if next < 0 :
                break
            if current_markers[next] not in genotypes :
                if debug :
                    print "\t[ignore] %s not found" % (current_markers[next])
                continue
            g_aff = list(genotypes[current_markers[next]][True])
            g_non = list(genotypes[current_markers[next]][False])
            if (len(g_aff) == 1) and (g_aff[0] == hmode) and (hmode not in g_non) :
                if debug :
                    print "\t[homoz ] %s ( <-- )" % current_markers[next]
                #next -= 1
            else :
                if debug :
                    print "\t[ end  ] ( <-- )"
                break

        homoz_start = current_markers[next + 1]

        next = start_point
        # go as far right...
        while True :
            next += 1
            if next > len(current_markers) :
                break
            if current_markers[next] not in genotypes :
                if debug :
                    print "\t[ignore] %s not found" % (current_markers[next])
                continue
            g_aff = list(genotypes[current_markers[next]][True])
            g_non = list(genotypes[current_markers[next]][False])
            if (len(g_aff) == 1) and (g_aff[0] == hmode) and (hmode not in g_non) :
                if debug :
                    print "\t[homoz ] %s ( --> )" % current_markers[next]
                #next += 1
            else :
                if debug :
                    print "\t[ end  ] ( --> )"
                break

        homoz_end = current_markers[next - 1]

#        print line,
        if current_marker_index[homoz_end] - current_marker_index[homoz_start] >= report_threshold :
            print "chr%s\t%d\t%d\t%s" % (str(chr), physical_positions[homoz_start], physical_positions[homoz_end], '_'.join([homoz_start, homoz_end, lodscore]))

        peak_start = next

    if debug :
        print ""

#    sys.exit()
if debug :
    print "done"

