#!/usr/bin/env python
import sys, os, getopt, commands
# the idea of ziggy is to find the stretches of homozygosity that surround a lod score peak 
# (where 'peak' is defined by a threshold)

def usage() :
    print >> sys.stderr, \
"""Usage: %s [-l N] [-hgsa]
    -l, --lod:           set lod threshold
    -g, --genehunter:    expect genehunter output files
    -a, --allegro:       expect allegro output files
    -s, --simwalk:       expect simwalk output files
        (only one of -g, -s and -a can be used at once)
    -m, --map:           filename of map file
    -x, --genotypes:     filename of genotype file
    -p, --pedfile:       filename of pedigree file
    -h, --help:          show this help info
""" % sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hl:gsam:x:p:", ["help", "lod=", \
            "genehunter", "simwalk", "allegro", "map=", "genotypes=", "pedfile="])

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


# map
print >> sys.stderr, "reading map file..."
markers = []
marker_index = {}
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
    rsid = data[1]

    markers.append(rsid)
    marker_index[rsid] = linenum
    linenum += 1
f.close()

# ped
print >> sys.stderr, "reading pedigree file..."
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
    if int(aff) == 1 :
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

header = f.readline()
patients = header.strip().split()[1:]
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
            continue
        
        genotypes[m][ affection[patients[i]] ].add( current )

f.close()

print >> sys.stderr, "running messner..."
program_name = "python /home/ajm/code/bioinformatics-tools/messner2.py"
#program_name = "messner2"
s,o = commands.getstatusoutput("%s -m %s -l %f %s" % (program_name, mapfilename, lod, program_arg))

print >> sys.stderr, "looking for homozygosity..."
for line in o.split('\n') :
    line = line.strip()
    if len(line) == 0 :
        continue
    data = line.split()
    chr,start,stop,guff = data
    m1,m2,lodscore = guff.split('_')

    print line,
    peak_start = marker_index[m1]
    peak_end   = marker_index[m2]

    # do stuff...
    start_point = -1
    for i in range(peak_start, peak_end) :
        if markers[i] not in genotypes : # ie: this marker was removed by pedcheck or something...
            continue
        affected_g = genotypes[markers[i]][True]
        if (len(affected_g) == 1) and (affected_g[0] == 'AA' or affected_g[0] == 'BB') :
            start_point = i
            hmode = affected_g[0]
            break

    if start_point == -1 :
#        print line,
        print ": no homozygosity"
        continue

    # go as far left as possible
    next = start_point - 1
    while 1 :
        if (next >= 0) and (len(affected_g) == 1) and (affected_g[0] == hmode) :
            next -= 1
        else :
            break

    homoz_start = markers[next + 1]

    next = start_point + 1
    # go as far right...
    while 1 :
        if (next < len(markers)) and (len(affected_g) == 1) and (affected_g[0] == hmode) :
            next += 1
        else :
            break

    homoz_end = markers[next - 1]

#    print line,
    print homoz_start,
    print "--",
    print homoz_end

