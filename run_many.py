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
    return sorted(glob.glob("%s_??" % dir_base))

def restart_setup(dir_base, input_params_name, new_nsteps):
    dirs = find_dirs(dir_base)
    for dir in dirs:
        ip_fname = os.path.join(dir, input_params_name)
        ip = open(ip_fname, mode='r')
        parse_dict, order_dict = parse_ip(ip)
        ip.close()
        old_nsteps = int(parse_dict['nsteps'])
        if old_nsteps > int(new_nsteps):
            raise RuntimeError("old nsteps %d > new_nsteps %d" % (old_nsteps, int(new_nsteps)))
        parse_dict['restart'] = str(1)
        parse_dict['nsteps'] = str(new_nsteps)
        ip = open(ip_fname, mode='w')
        ip.write(write_ip(parse_dict, order_dict).getvalue())
        ip.close()
    return dirs

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
            type="int", default=None, help="restart runs and set new nsteps")

    options, args = parser.parse_args()

    if not options.command:
        parser.print_help()
    else:
        if options.restart is not None:
            restart_setup(DIR_BASE, INPUT_PARAMS, options.restart)
        else:
            initialize(options.nruns, DIR_BASE, options.force)
        dirs = find_dirs(DIR_BASE)
        run_many(dirs, [options.command])