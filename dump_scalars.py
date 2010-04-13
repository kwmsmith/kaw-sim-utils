#!/usr/bin/env python
import tables

INT_FMT, FLT_FMT = ("%8d ",), ("% #-9.3e",)


def dump_scalars(fname, start=0):
    fields = ('index', 'basic_steps', 'wall_time', 'sim_time', 'be', 've', 'ne', 'msf')

    formats = INT_FMT*2 + FLT_FMT*6
    dta = tables.openFile(fname)
    scs = dta.getNode('/scalars/scalar_data')
    stop = scs.nrows
    scal_dta = scs.read(start=start, stop=stop)
    dta.close()
    for row in scal_dta:
        etot = row['be'] + row['ve'] + row['ne']
        for (field, fmt) in zip(fields, formats):
            print (fmt+' ') % (row[field]),
        print FLT_FMT[0] % etot,
        print
    return stop

def dump_stats(fname, field):
    fields = ('index', 'ave', 'std_dev', 'skew', 'kurt')
    formats = INT_FMT + FLT_FMT*4
    dta = tables.openFile(fname)
    stats = dta.getNode('/stats/%s' % field).read()
    dta.close()
    for row in stats:
        for (field,fmt) in zip(fields, formats):
            print (fmt+' ') % (row[field]),
        print
        

if __name__ == '__main__':
    import time
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-f", action="store_true", dest="follow",
                      default=False, help="follow, like 'tail -f'")
    parser.add_option('-s', dest="stats", help="output statistics for field")

    options, args = parser.parse_args()

    fname = args[0]

    if options.stats:
        dump_stats(fname, options.stats)

    else:
        start = dump_scalars(fname)

        if options.follow:
            while True:
                try:
                    start = dump_scalars(fname, start)
                    time.sleep(10)
                except KeyboardInterrupt:
                    import sys; sys.exit(0)
