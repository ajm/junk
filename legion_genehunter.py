#!/usr/bin/env python
import re
import os
import sys
import shutil
from glob import glob

# bit of a quick'n'dirty script to preprocess data using mega2
# then generate jobs scripts and submit them using qsub

CONSORTIUM='BioinfCompBio'
PROJECT='UCL_Linkage'
#jobscript_name = 'jobscript'

jobscript = """#!/bin/bash -l
#PBS -l nodes=1:ppn=1
#PBS -l pvmem=2000mb
#PBS -l walltime=00:15:00
#PBS -j oe
#PBS -A ucl/%s/%s

set -v

cd %s
date
ghm < %s
date
"""

def _system(command) :
    print command
    if os.system(command) != 0 :
        print >> sys.stderr, "os.system failure: %s" % command
        sys.exit(-1)

def submit_job(j) :
    #_system("qsub %s" % j)
    pass

def write_job_script(path, setupfile, jobscript_name) :
    global CONSORTIUM, PROJECT
    global jobscript

    tmp = jobscript % (CONSORTIUM, PROJECT, path, setupfile)

    f = open(path + os.sep + jobscript_name, 'w')
    print >> f, tmp
    f.close()

def process(path) :
    global jobscript_name

    dir_re   = re.compile(".*c(\d+)$")
    input_re = re.compile("^setup_(\d+)\..*")

    listing = filter(lambda x : os.path.isdir(x) and dir_re.match(x), glob(path + os.sep + "*"))
    
    for dir in listing :
        chromo = dir_re.match(dir).group(1)
        inputfiles = glob(dir + os.sep + 'setup_*')

        for f in inputfiles :
            dirname,filename = os.path.split(f)
            m = input_re.match(filename)
            if not m :
                continue

            fragmentnumber = m.group(1)

            resultsfile = dirname + os.sep + ("gh_%s.out" % (fragmentnumber))
            if os.path.exists(resultsfile) :
                print "skipping chromosome %s, fragment %s results file present : %s" % (chromo, fragmentnumber, resultsfile)
                continue

            jobscript_name = "jobscript.%s" % fragmentnumber
            write_job_script(dirname, filename, jobscript_name)
            submit_job(dirname + os.sep + jobscript_name)

if __name__ == '__main__' :
    process(os.path.abspath(sys.argv[1]))

