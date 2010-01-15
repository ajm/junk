#!/usr/bin/env python
import sys

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#                                                               #
# THIS ONLY FIXES SNPS PROVIDED IN A FILE AND AT THE MOMENT     #
# THE DECISION AS TO WHAT SNPS ARE IN ERROR MISSES AMBIGUOUS    #
# C/G AND A/T SNPS                                              #
#                                                               #
# realistically we should read the chip description to get the  #
# names of all the SNPs and then compare these SNPs in both     #
# dbSNP and hapmap databases                                    #
#                                                               #
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#

rsids = {}
f = open("inadvertent_SNP_call_fr.csv")
for line in f :
    rsids[ line.strip().split(',')[0] ] = 0
f.close()

f = open("Final_dat_RENAL_GEM_CT_datafile1.txt")
line = f.readline().strip()
ids = line.split('\t')

print line

indices = []

for i in range(len(ids)) :
    rs = ids[i]
    if rsids.has_key(rs) :
        indices.append(i)
#        print >> sys.stderr, rs,
#        print >> sys.stderr, i


for line in f :
    data = line.strip().split('\t')

    for i in indices :
        alleles = data[i-1].split()
        newalleles = []

        for a in alleles :
            if   a == 'A' :
                newalleles.append('T')
            elif a == 'T' :
                newalleles.append('A')
            elif a == 'C' :
                newalleles.append('G')
            elif a == 'G' :
                newalleles.append('C')
            else :
                newalleles.append('0')

        data[i-1] = ' '.join(newalleles)

    print '\t' + '\t'.join(data)

f.close()

