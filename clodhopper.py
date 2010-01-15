#!/usr/bin/env python
# perform elod calculations
import sys, os, shutil, commands

def usage() :
    print >> sys.stderr, "Usage: python %s program [homozygous length]" % sys.argv[0]
    print >> sys.stderr, "\tprogram can be simwalk, genehunter or allegro"
    sys.exit(-1)

if len(sys.argv) != 2 and len(sys.argv) != 3 : #or sys.argv[1] not in ['simwalk','genehunter','allegro'] :
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

    g = open('elod/pedin.21', 'w')

    # find affected individuals
    # find both unaffected + unaffacted siblings of affected
    affecteds = {}
    for line in lines :
        line = line.strip()
        data = line.split()
        affected = int(data[5]) == 2

        if affected :
            affecteds[data[1]] = (data[2], data[3])

    for line in lines :
        line = line.strip()
        data = line.split()
        affected = int(data[5]) == 2

        i = len(data[6:])
        if (i % 2) != 0 :
            print >> sys.stderr, "error, uneven number of alleles, are these haploid? (%d)" % i
            sys.exit(-1)

        hetero = ['1','2'] * (i / 2)
        homo1  = ['1','1'] * (homozygous_length * 2)
        homo2  = ['2','2'] * (homozygous_length * 2)

        print >> g, ' '.join(data[:6]),
        if not affected :
            if (data[2],data[3]) in affecteds.values() :
                l = ((i / 2) - homozygous_length)
                aff = (hetero[:l] + homo2 + hetero[l:])[:len(hetero)]
                print >> g, ' '.join(aff)
            else :
                print >> g, ' '.join(hetero)
        else :
            l = ((i / 2) - homozygous_length)
            aff = (hetero[:l] + homo1 + hetero[l:])[:len(hetero)]
            print >> g, ' '.join(aff)

    g.close()
    os.chdir('elod')
    os.system('allegro allegro.in &> /dev/null')
    s,o = command.getstatusoutput('grep -v "LOD" param_mpt.21 | awk \'{ print $2 }\' | sort -nr | head -1')

    print "Allegro Estimated LOD = %s" % o

elif program == 'genehunter' :
    raise NotImplemented

elif program == 'simwalk' :
    raise NotImplemented


