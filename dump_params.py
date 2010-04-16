#!/usr/bin/env python
import tables

COMPILED_PARAMS = """NP NX NY INTEGRATOR MODEL 
            MAJOR_VERSION MINOR_VERSION REVISION""".split()

PARAMS = """tstep dtfac nsteps max_wall_mins nout_arrs nout_scals lx ly rho_s2
            viscos h_viscos resis h_resis diffus h_diffus eb ev en spectrum_slope 
            spectrum_peak rng_seed""".upper().split()

def dump_params(fname):
    dta = tables.openFile(fname)
    sim_params = dta.getNode("/sim_params")
    print "\nCOMPILED PARAMS:\n"
    for cp in COMPILED_PARAMS:
        print "    %15s: %-s" % (cp, sim_params._v_attrs[cp])
    print "\nRUNTIME PARAMS:\n"
    for pm in PARAMS:
        print "    %15s: %-s" % (pm, sim_params._v_attrs[pm])
    dta.close()

if __name__ == '__main__':
    import sys, time
    fname = sys.argv[1]
    dump_params(fname)
