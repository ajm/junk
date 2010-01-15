#!/usr/bin/env python
import sys
# for allegro haplotype analysis
# to identify regions of homozygosity in
# affected individuals vs non-affecteds

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#                                                                                   #
# BADLY WRITTEN AND ILL-CONCEIVED                                                   #
#                                                                                   #
# THIS SIMPLY DOES NOT WORK, THE NUMBERS DO NOT DO WHAT I THOUGHT THEY DID!         #
# HOWEVER THE CODE TO PARSE ihaplo.out FROM ALLEGRO MIGHT BE USEFUL IN THE FUTURE   #
#                                                                                   #
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#

if len(sys.argv) != 3 :
    print >> sys.stderr, "Usage: python %s <haplotype file> <map file>" % sys.argv[0]
    sys.exit(-1)

rs2pos = {}
markers = []
indices = []
affected   = {}
unaffected = {}

# haplotype information
# read all rs ids, (printed vertically!)
hapfile = open(sys.argv[1])
tmp = []
for line in hapfile :
    tmp.insert(0,line)
    tmp2 = set(line.strip().split())
    if tmp2 == set(['r']) :
        break

# make 'markers' list of all markers 
# in order
lasti = 0
i = tmp[0].find('r', lasti)
while i != -1 :
    indices.append(i)

    s = ""
    for j in range(len(tmp)) :
        s += tmp[j][i]

    markers.append(s.strip())

    lasti = i + 1
    i = tmp[0].find('r', lasti)

# read all the people in the haplotype 
# file
for line in hapfile :
    line = line.strip()
    if len(line) == 0 :
        continue

    data = line.split()
    personid = data[1]
    affected_status = data[5]

    # exclude ones that are not genotyped
    # (ids starting with a 2 is just our convention)
    if not personid.startswith('2') :
        continue

    # separate affected and unaffected
    if int(affected_status) == 2 :
        tmp = affected
    else :
        tmp = unaffected

    # fill out data structure for new person
    if personid not in tmp :
        tmp[personid] = {}
        for m in markers :
            tmp[personid][m] = []

    # each indices is a marker
    # each person has two alleles
    for i in range(len(indices)) :
        num = int(line[indices[i]])
        rsid = markers[i]
        tmp[personid][rsid].append(num)


hapfile.close()

# check for stretches of homozygosity
homoz = False
homoz_allele = None
for i in range(len(markers))[1:-1] :
    m = markers[i]
    tmp = []

    for p in affected.keys() :
        for a in affected[p][m] :
            tmp.append(a)

    a = tmp[0]
    
    if len(set(tmp)) == 1 :
        het = True
        x = []

        for p in unaffected.keys() :
            alleles = unaffected[p][m]
            x += unaffected[p][m]
            if not ((a in alleles) and (len(set(alleles)) == 2)) :
                het = False
                #break

        if het :
            if not homoz :
                homoz = True
                homoz_allele = a
                print "\nstart: disease = %s, unaffected = %s" % (str(a), str(x))
                print markers[i-1]
            else :
                if homoz_allele != a :
                    homoz = False
                    print "end: %s -> %s" % (str(homoz_allele), str(a))
                    print m
        else :
            if homoz :
                homoz = False
                print "end: unaffected not all hetro %s" % str(x)
                print m


        
    else :
        if homoz :
            homoz = False
            print "end: affected not homo"
            print m

if homoz :
    print "end"
    print markers[-1]
    #print len(markers)

sys.exit()

# read map
mapfile = open(sys.argv[2])

mapfile.readline() # header
for line in mapfile :
    chr,genpos,rsid,phypos,nr = line.strip().split()
    genpos = float(genpos)
    chr,phypos,nr = map(int, [chr,phypos,nr])
    rs2pos[rsid] = phypos

mapfile.close()

