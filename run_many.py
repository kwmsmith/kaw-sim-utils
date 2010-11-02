#!/usr/bin/env python

import os, time, sys
import re
import subprocess
import glob
from cStringIO import StringIO

DIR_BASE = "_run"
INPUT_PARAMS = "input_params.in"
PARAM_VALS_NAME = "param_vals"

matcher = re.compile("^\s*input_params%(\w*)\s*=\s*([^,]*),$").match
def parse_ip(buf):
    if isinstance(buf, basestring):
        lines = buf.splitlines()
    else:
        lines = buf.readlines()
    parse_dict = {}
    order_dict = {}
    for idx, line in enumerate(lines):
        m = matcher(line)
        if not m: continue
        key, val = m.groups()
        parse_dict[key] = val
        order_dict[idx] = key
    return parse_dict, order_dict

def gen_ip(parse_dict, order_dict):
    buf = []
    buf += ["&params"]
    for idx in sorted(order_dict):
        key = order_dict[idx]
        val = parse_dict[key]
        buf += ["input_params%%%(pname)s = %(pval)s," % \
                    {'pname':key, 'pval':val}]
    buf += ["/", ""]
    return '\n'.join(buf)

def gen_param_dicts(param_vals, param_dicts):
    '''
    param_vals is a dict, entries are either
        'param-name' : [list-of-values]
    or
        ('param-name-1', 'param-name-2', ...) : [list-of-values]
    or
        ('param-name-1', 'param-name-2', ...) : [[list-of-values],[list-of-values],...]
    In the first instance, a new param_dict will be generated with param-name
    set to one of the values specified.
    In the second instance, the parameters both vary but take on the exact same
    values.
    In the third instance, the parameters both vary together, taking on values
    from their resp. lists.
    '''

    if not param_vals:
        return param_dicts

    pnames, vals = param_vals.popitem()

    if isinstance(pnames, basestring):
        pnames = (pnames,)

    if not isinstance(vals[0], (tuple, list)):
        vals = [vals]*len(pnames)

    assert len(vals) == len(pnames)

    pdicts_out = []

    N = len(vals[0])
    for pdict in param_dicts:
        for idx in range(N):
            new_pdict = pdict.copy()
            for pname, val in zip(pnames, vals):
                new_pdict[pname] = str(val[idx])
            pdicts_out.append(new_pdict)

    return gen_param_dicts(param_vals, pdicts_out)

def gen_params(template, param_vals):
    parse_dict, odict = parse_ip(template)
    ret = []

    param_dicts = gen_param_dicts(param_vals.copy(), [parse_dict.copy()])

    for pdict in param_dicts:
        ret.append(gen_ip(pdict, odict))

    return ret

def find_dirs(dir_base):
    return sorted(glob.glob("%s*" % dir_base))

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

def initialize(dir_base, force, template_name):

    template_mod = __import__(template_name)
    params = gen_params(template_mod.template, template_mod.param_vals)

    from hashlib import md5

    dirs = ["%s_%s" % (dir_base, md5(param).hexdigest()) for param in params]

    for dir in dirs:
        try:
            os.mkdir(dir)
        except OSError, e:
            if e.errno != 17: # file exists
                raise

    for param, dir in zip(params, dirs):
        fname = os.path.join(dir, INPUT_PARAMS)
        if os.path.exists(fname) and not force:
            raise RuntimeError("file %s exists" % fname)
        fh = open(fname, mode='w')
        fh.write(param)
        fh.close()

def timestamp(indicator, command, fhandle=sys.stdout):
    divider = '-'*79
    fhandle.write(divider)
    fhandle.write(indicator)
    fhandle.write("directory: %s" % os.getcwd())
    fhandle.write("command: %s" % command)
    fhandle.write("time: %s" % time.ctime())
    fhandle.write(divider)
    fhandle.flush()

def run_many(dirs, command):
    basedir = os.getcwd()
    for dir in dirs:
        os.chdir(dir)
        timestamp('START', command)
        try:
            subprocess.check_call(command, shell=True)
        finally:
            timestamp('STOP', command)
            os.chdir(basedir)

if __name__ == '__main__':
    from optparse import OptionParser
    usage = """\
run_many.py [options] -c 'command string'

example:
    run_many.py -c 'mpiexec -np 4 ../three_fields.x </dev/null'  >run_many.out &
to restart:
    run_many.py -r 3000 -c 'mpiexec -np 4 ../three_fields.x </dev/null' >>run_many.out &\
"""

    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--force', dest="force",
            action="store_true", default=False, help="force initialization")
    parser.add_option('-c', dest="command",
            type="string", default='', help="command string")
    parser.add_option('-r', dest="restart",
            type="int", default=None, help="restart runs and set new nsteps")
    parser.add_option('-t', dest='template_name',
            type='string', default=PARAM_VALS_NAME,
            help="name of template file [default: %default]")

    options, args = parser.parse_args()

    if '&' in options.command:
        parser.error("'&' in command string -- not meant to be run in background.")

    if not options.command:
        parser.print_help()
    else:
        if options.restart is not None:
            restart_setup(DIR_BASE, INPUT_PARAMS, options.restart)
        else:
            initialize(DIR_BASE, options.force, options.template_name)
        dirs = find_dirs(DIR_BASE)
        run_many(dirs, [options.command])
