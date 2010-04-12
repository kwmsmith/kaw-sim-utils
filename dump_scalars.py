#!/usr/bin/env python
import tables

INT_FMT, FLT_FMT = "%9d", "%#-13.4g"


def dump_scalars(fname, start=0):
    fields = ('index', 'basic_steps', 'wall_time', 'sim_time', 'be', 've', 'ne', 'msf')

    formats = (INT_FMT + ' ' + INT_FMT + (' ' + FLT_FMT)*6).split()
    dta = tables.openFile(fname)
    scs = dta.getNode('/scalars/scalar_data')
    stop = scs.nrows
    scal_dta = scs.read(start=start, stop=stop)
    dta.close()
    for row in scal_dta:
        etot = row['be'] + row['ve'] + row['ne']
        for (field, fmt) in zip(fields, formats):
            print (fmt+' ') % (row[field]),
        print FLT_FMT % etot,
        print
    return stop
        

if __name__ == '__main__':
    import sys, time
    fname = sys.argv[1]
    start = 0
    while True:
        start = dump_scalars(fname, start)
        time.sleep(10)
