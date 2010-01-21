#!/usr/bin/env python
import sys

if len(sys.argv) != 3 :
    print >> sys.stderr, "Usage: %s <messner output> <program>\n" % sys.argv[0]
    sys.exit(-1)

if not sys.argv[2] in ['simwalk2','genehunter','allegro'] :
    print >> sys.stderr, "%s is not a supported program," % sys.argv[2]
    print >> sys.stderr, "only simwalk2, genehunter and allegro are supported...\n"
    sys.exit(-1)

program = sys.argv[2]
chromosomes = set()

f = open(sys.argv[1])

for line in f :
    line = line.strip()
    if len(line) == 0 :
        continue
    try :
        ch = line.split()[0]
        chromosomes.add( int(ch[3:]) )
    except :
        print >> sys.stderr, "bad messner input"
        sys.exit(-1)

f.close()

for c in chromosomes :
    chromo = "%02d" % c 
    if program == 'allegro' :
        os.system("allegro_lod_single.pl %s" % chromo)
        os.system("ps2pdf allegro_lod_%s.ps" % chromo)

    elif program == 'genehunter' :
        os.system("gh_snp_lod_single.pl %s" % chromo)
        os.system("ps2pdf gh_snp_lod_%s.ps" % chromo)

    elif program == 'simwalk2' :
        os.system("sw_snp_lod_single.pl %s" % chromo)
        os.system("ps2pdf sw_snp_lod_%s.ps" % chromo)

