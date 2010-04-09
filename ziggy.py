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
    -m, --map:           filename of map file
    -x, --genotypes:     filename of genotype file
    -h, --help:          show this help info
""" % sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hl:gsam:x:", ["help", "lod=", "genehunter", "simwalk", "allegro", "map=", "genotypes="])

except getopt.GetoptError, err:
    print >> sys.stderr, str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(-1)

lod = 3.0
verbose = False
program_arg = '-a'
mapfilename = "../map.txt"
genotypefilename = "../genotypes"
markermap = {}

for o, a in opts:
    if o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-l", "--lod"):
        lod = a
    elif o in ("-g", "--genehunter"):
        program_arg = o
    elif o in ("-a", "--allegro"):
        program_arg = o
    elif o in ("-s", "--simwalk"):
        program_arg = o
    elif o in ("-m", "--map") :
        mapfilename = a

f = open(mapfilename)
f.readline() # header
linenum = 1
for line in f :
    data = line.strip().split()
    rsid = data[1]
    markermap[rsid] = linenum
    linenum += 1
f.close()

f = open(genotypefile)
header = f.readline()
patients = header.strip().split()[1:]
for line in f :
    pass # rsid, patient1, patient2...
f.close()

o,s = commands.getstatusoutput("messner2 -m ../map.txt -l %f %s" % (lod, program_arg))

for line in o.split('\n') :
    data = line.strip().split()
    chr,start,stop,guff = data
    m1,m2,lodscore = guff.split('_')

    # do stuff...

