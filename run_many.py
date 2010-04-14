#!/usr/bin/env python
 
import os
import subprocess

DIR_BASE = "_run"
INPUT_PARAMS = "input_params.in"
TEMPLATE_NAME =  "%s.template" % INPUT_PARAMS

def gen_params(buf, N, start, step):
    template = buf.read()
    ret = []
    for i in range(start, start+N*step, step):
        ret.append(template.format(RNG_SEED=i))
    return ret

def initialize(nruns, dir_base, force):
    dirs = []
    for i in range(nruns):
        dir_name = "%s_%02d" % (dir_base, i)
        dirs.append(dir_name)
        try:
            os.mkdir(dir_name)
        except OSError, e:
            if e.errno != 17: # file exists
                raise

    template = open(TEMPLATE_NAME, mode='r')
    params = gen_params(template, nruns, start=51, step=1000)
    template.close()

    for param, dir in zip(params, dirs):
        fname = os.path.join(dir, INPUT_PARAMS)
        if os.path.exists(fname) and not force:
            raise RuntimeException("file %s exists" % fname)
        fh = open(fname, mode='w')
        fh.write(param)
        fh.close()

    return dirs

def run_many(dirs, command):
    basedir = os.path.abspath(os.curdir)
    for dir in dirs:
        os.chdir(dir)
        try:
            subprocess.check_call(command)
        finally:
            os.chdir(basedir)

if __name__ == '__main__':
    from optparse import OptionParser
    usage = "run_many.py [options] -n NRUNS 'command string'"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", type="int", dest="nruns", 
            default=-1, help="number of runs")
    parser.add_option('-f', '--force', dest="force",
            action="store_true", default=False, help="force initialization")

    options, args = parser.parse_args()

    if options.nruns == -1 or not args:
        parser.print_help()
    else:
        dirs = initialize(options.nruns, DIR_BASE, options.force)
        print dirs
