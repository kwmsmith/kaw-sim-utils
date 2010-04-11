#!/usr/bin/env python
import tables

def dump_scalars(fname, start=0):
    fields = ('index', 'basic_steps', 'wall_time', 'sim_time', 'be', 've', 'ne', 'msf')
    formats = ('%-d %-d' + ' %-10.4g'*6).split()
    dta = tables.openFile(fname)
    scs = dta.getNode('/scalars/scalar_data')
    stop = scs.nrows
    scal_dta = scs.read(start=start, stop=stop)
    dta.close()
    for row in scal_dta:
        for (field, fmt) in zip(fields, formats):
            print (fmt+' ') % (row[field]),
        print
    return stop
        

if __name__ == '__main__':
    import sys, time
    fname = sys.argv[1]
    start = 0
    while True:
        start = dump_scalars(fname, start)
        time.sleep(10)
