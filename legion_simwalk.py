#!/usr/bin/env python
import re
import os
import sys
import shutil
from glob import glob

# bit of a quick'n'dirty script to preprocess data using mega2
# then generate jobs scripts and submit them using qsub
# TODO: check what the default score file name is for call to write_job_script on line 125 

CONSORTIUM='consortium'
PROJECT='project'
jobscript_name = 'jobscript'

jobscript = """#!/bin/bash -l
#PBS -l nodes=1:ppn=1
#PBS -l pvmem=2000mb
#PBS -l walltime=06:00:00
#PBS -j oe
#PBS -A ucl/%s/%s

set -v

cd %s
date
simwalk2
date
cp %s ../%s
"""

jobscript_noproject = """#!/bin/bash -l
#PBS -l nodes=1:ppn=1
#PBS -l pvmem=2000mb
#PBS -l walltime=06:00:00
#PBS -j oe

set -v

cd %s
date
simwalk2
date
cp %s ../%s
"""

def _system(command) :
    print command
    return # XXX
    if os.system(command) != 0 :
        print >> sys.stderr, "os.system failure: %s" % command
        sys.exit(-1)

def submit_job(j) :
    _system("qsub %s" % j)
    

def write_job_script(path, scorefile, scorefile2) :
    global CONSORTIUM, PROJECT, jobscript_name
    global jobscript, jobscript_noproject

    #tmp = jobscript % (CONSORTIUM, PROJECT, path, scorefile, scorefile2)
    tmp = jobscript_noproject % (path, scorefile, scorefile2)

    f = open(path + os.sep + jobscript_name, 'w')
    print >> f, tmp
    f.close()

def write_mega2_input(path) :
    abspath = path + os.sep + "mega2_in.tmp"

    try :
        f = open(abspath, 'w')
    except IOError, ioe:
        print >> sys.stderr, str(ioe)
        sys.exit(-1)

    print >> f, "1\n00\n0\n1\n2\n0\n0\n0" # '00' is the file extention
    f.close()

    return abspath

def run_mega2(inputfile, path, chromo) :
    command = "cd %s ; mega2 < %s > /dev/null 2> /dev/null ; cd - > /dev/null 2> /dev/null" % (path, inputfile)
    os.system(command)

    missing = []
    files = {
            'sw2_pedigree.%s' % chromo : 'PEDIGREE.DAT',
            'sw2_locus.%s' % chromo    : 'LOCUS.DAT',
            'sw2_pen.%s' % chromo      : 'PEN.DAT',
            'sw2_batch.%s' % chromo    : 'BATCH2.DAT',
            'sw2_map.%s' % chromo      : 'MAP.DAT'
    }
    
    for oldfilename,newfilename in files.items() :
        if not os.path.exists(path + os.sep + oldfilename) :
            missing.append(oldfilename)
        else :
            os.rename(path + os.sep + oldfilename, path + os.sep + newfilename)

    if len(missing) != 0 :
        print >> sys.stderr, "%s not found after running mega2" % ','.join(missing)
        sys.exit(-1)


def process(path) :
    global jobscript_name

    dir_re   = re.compile(".*c(\d+)$")
    input_re = re.compile("^datain_(\d+)\..*")

    listing = filter(lambda x : os.path.isdir(x) and dir_re.match(x), glob(path + os.sep + "*"))
    mega2_input = write_mega2_input(path)

    for dir in listing :
        chromo = dir_re.match(dir).group(1)
        inputfiles = glob(dir + os.sep + 'datain_*')

        for f in inputfiles :
            dirname,filename = os.path.split(f)
            m = input_re.match(filename)
            if not m :
                continue

            fragmentnumber = m.group(1)

            resultsfile = dirname + os.sep + ("SCORE-%s_%s.ALL" % (chromo, fragmentnumber))
            if os.path.exists(resultsfile) :
                print "skipping chromosome %s, fragment %s results file present : %s" % (chromo, fragmentnumber, resultsfile)
                continue

            fragmentdirectory = dirname + os.sep + fragmentnumber
            if os.path.exists(fragmentdirectory) :
                try :
                    shutil.rmtree(fragmentdirectory)
                except :
                    pass
            try :
                os.mkdir(fragmentdirectory)
            except OSError, ose :
                print >> sys.stderr, str(ose)
                sys.exit(-1)

            shutil.copy(dir + os.sep + ("datain_%s.%s" % (fragmentnumber,chromo)),  fragmentdirectory + os.sep + "datain.00")
            shutil.copy(dir + os.sep + ("pedin_%s.%s" % (fragmentnumber,chromo)),   fragmentdirectory + os.sep + "pedin.00")
            shutil.copy(dir + os.sep + ("map_%s.%s" % (fragmentnumber,chromo)),     fragmentdirectory + os.sep + "map.00")

            run_mega2(mega2_input, fragmentdirectory, chromo)
            write_job_script(fragmentdirectory, "SCORE-%s.ALL" % chromo, "SCORE-%s_%s.ALL" % (chromo,fragmentnumber))
            submit_job(fragmentdirectory + os.sep + jobscript_name)

if __name__ == '__main__' :
    process(os.path.abspath(sys.argv[1]))

