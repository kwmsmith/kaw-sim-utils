#!/usr/bin/env python
 
import os, time, sys
import re
import subprocess
import glob
from cStringIO import StringIO

DIR_BASE = "_run"
INPUT_PARAMS = "input_params.in"
TEMPLATE_NAME =  "%s.template" % INPUT_PARAMS

matcher = re.compile("^\s*input_params%(\w*)\s*=\s*([^,]*),$").match
def parse_ip(buf):
    parse_dict = {}
    order_dict = {}
    lines = buf.readlines()
    for idx, line in enumerate(lines):
        m = matcher(line)
        if not m: continue
        key, val = m.groups()
        parse_dict[key] = val
        order_dict[idx] = key
    return parse_dict, order_dict

def write_ip(parse_dict, order_dict):
    buf = StringIO()
    buf.write("&params\n")
    for idx in sorted(order_dict):
        key = order_dict[idx]
        val = parse_dict[key]
        buf.write("input_params%%%(pname)s = %(pval)s,\n" % \
                    {'pname':key, 'pval':val})
    buf.write("/\n")
    return buf

def gen_params(buf, N, start, step):
    template = buf.read()
    ret = []
    for i in range(start, start+N*step, step):
        ret.append(template.format(RNG_SEED=i))
    return ret

def find_dirs(dir_base):
    return glob.glob("%s_??" % dir_base)

#def restart_init(dir_base, input_params):
    #for dir in find_dirs(dir_base):
        #ip = open(os.path.join(dir, input_params), mode='r'))
        



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
            raise RuntimeError("file %s exists" % fname)
        fh = open(fname, mode='w')
        fh.write(param)
        fh.close()

    return dirs

def run_many(dirs, command):
    basedir = os.path.abspath(os.curdir)
    for dir in dirs:
        os.chdir(dir)
        print "-"*79
        print "directory: %s" % os.path.abspath(os.curdir)
        print "command: %s" % command
        print "time: %s" % time.ctime()
        print "-"*79
        sys.stdout.flush()
        try:
            subprocess.check_call(command, shell=True)
        finally:
            os.chdir(basedir)

if __name__ == '__main__':
    from optparse import OptionParser
    usage = "run_many.py [options] -n NRUNS -c 'command string'"
    parser = OptionParser(usage=usage)
    parser.add_option("-n", type="int", dest="nruns", 
            default=-1, help="number of runs")
    parser.add_option('-f', '--force', dest="force",
            action="store_true", default=False, help="force initialization")
    parser.add_option('-c', dest="command",
            type="string", default='', help="command string")
    parser.add_option('-r', dest="restart",
            type="int", default=-1, help="restart runs and set new nsteps")

    options, args = parser.parse_args()

    if options.nruns == -1 or not options.command:
        parser.print_help()
    else:
        dirs = initialize(options.nruns, DIR_BASE, options.force)
        run_many(dirs, [options.command])
