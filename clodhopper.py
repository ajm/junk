#!/usr/bin/env python
# perform elod calculations
import sys, os, shutil, commands

def usage() :
    print >> sys.stderr, "Usage: python %s program [homozygous length]" % sys.argv[0]
    print >> sys.stderr, "\tprogram can be simwalk, genehunter or allegro"
    sys.exit(-1)


if len(sys.argv) != 2 and len(sys.argv) != 3 :
    usage()

if sys.argv[1] not in ['simwalk','genehunter','allegro'] :
    usage()


program = sys.argv[1]
if len(sys.argv) == 2 :
    homozygous_length = 100
else :
    try :
        homozygous_length = int(sys.argv[2])
    except ValueError, ve :
        print >> sys.stderr, "error, bad value for length of homozygous region : %s" % str(ve)
        sys.exit(-1)

if not os.path.isdir('c21') :
    print >> sys.stderr, "error, could not find c21 directory, exiting..."
    sys.exit(-1)

try :
    os.rmdir('elod')
    os.mkdir('elod')
except :
    pass

if program == 'allegro' :
    shutil.copy('c21/datain.21', 'elod')
    shutil.copy('c21/pedin.21',  'elod/old_pedin.21')
    shutil.copy('c21/map.21',    'elod')

    f = open('elod/old_pedin.21')
    lines = f.readlines()
    f.close()

    # find affected individuals + remember their parents
    # so later we will know who is the sibling of an affected
    affecteds = {}
    for line in lines :
        data = line.strip().split()
        affected = int(data[5]) == 2

        if affected :
            affecteds[data[1]] = (data[2], data[3]) # affecteds[ child ] = ( mother, father )


    # rewrite pedin
    g = open('elod/pedin.21', 'w')
    for line in lines :
        data = line.strip().split()
        affected = int(data[5]) == 2

        i = len(data[6:])
        if (i % 2) != 0 :
            print >> sys.stderr, "error, uneven number of alleles, are these haploid? (%d)" % i
            sys.exit(-1)

        hetero = ['1','2'] * (i / 2)
        homo1  = ['1','1'] * homozygous_length
        homo2  = ['2','2'] * homozygous_length

        splice = (i / 2) - homozygous_length

        # ids, status, etc
        print >> g, ' '.join(data[:6]),

        if not affected :
            if ( data[2], data[3] ) in affecteds.values() :                
                aff = hetero[:splice] + homo2 + hetero[-splice:]
                print >> g, ' '.join(aff)
            else :
                print >> g, ' '.join(hetero)
        else :
            aff = hetero[:splice] + homo1 + hetero[-splice:]
            print >> g, ' '.join(aff)

    g.close()
    os.chdir('elod')
    s,o = commands.getstatusoutput('allegro allegro.in')
    if s != 0 :
        print >> sys.stderr, "allegro did not run successfully!"
        print >> sys.stderr, o
        sys.exit(-1)

    s,o = commands.getstatusoutput('grep -v "LOD" param_mpt.21 | awk \'{ print $2 }\' | sort -nr | head -1')
    print "Allegro Estimated LOD = %s" % o

elif program == 'genehunter' :
    raise NotImplemented

elif program == 'simwalk' :
    raise NotImplemented


