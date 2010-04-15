template = '''
&params
input_params%restart = 0,
input_params%tstep = 8.0e-2,
input_params%dtfac = 10.0e0,
input_params%nsteps = 5000,
input_params%nout_arrs = 25,
input_params%nout_scals = 1,
input_params%lx = 1.0e0,
input_params%ly = 1.0e0,
input_params%rho_s2 = 1.0e-4,
input_params%viscos = 0.0e0,
input_params%h_viscos = 3.0e-8,
input_params%resis = 0.0e0,
input_params%h_resis = 3.0e-8,
input_params%diffus = 0.0e0,
input_params%h_diffus = 1.0e-8,
input_params%Eb = 0.25e-2,
input_params%Ev = 0.25e-2,
input_params%En = 0.25e-3,
input_params%spectrum_slope = 3.0e0,
input_params%spectrum_peak = 2.0e0,
input_params%rng_seed = {RNG_SEED},
/
'''

import run_many
from cStringIO import StringIO

from nose.tools import set_trace, eq_
 
def test_params_output():
    buf = StringIO(template)
    N, start, step = 10, 51, 100
    params = run_many.gen_params(buf, N=10, start=51, step=100)
    eq_(len(params), 10)
    for idx, param in enumerate(params):
        rng_seed = 51 + idx * step
        eq_(param, template.format(RNG_SEED=rng_seed))

def test_parse_write_ip():
    buf = StringIO(example_ip)
    parse_dict, order_dict = run_many.parse_ip(buf)
    parse_dict['restart'] = str(1)
    parse_dict['nsteps'] = str(6000)
    out_buf = run_many.write_ip(parse_dict, order_dict)
    eq_(example_ip_out, out_buf.getvalue())

example_ip = '''\
&params
input_params%restart = 0,
input_params%tstep = 8.0e-2,
input_params%dtfac = 10.0e0,
input_params%nsteps = 5000,
input_params%nout_arrs = 25,
input_params%nout_scals = 1,
input_params%lx = 1.0e0,
input_params%ly = 1.0e0,
input_params%rho_s2 = 1.0e-4,
input_params%viscos = 0.0e0,
input_params%h_viscos = 3.0e-8,
input_params%resis = 0.0e0,
input_params%h_resis = 3.0e-8,
input_params%diffus = 0.0e0,
input_params%h_diffus = 1.0e-8,
input_params%Eb = 0.25e-2,
input_params%Ev = 0.25e-2,
input_params%En = 0.25e-3,
input_params%spectrum_slope = 3.0e0,
input_params%spectrum_peak = 2.0e0,
input_params%rng_seed = 1789,
/
'''
example_ip_out = '''\
&params
input_params%restart = 1,
input_params%tstep = 8.0e-2,
input_params%dtfac = 10.0e0,
input_params%nsteps = 6000,
input_params%nout_arrs = 25,
input_params%nout_scals = 1,
input_params%lx = 1.0e0,
input_params%ly = 1.0e0,
input_params%rho_s2 = 1.0e-4,
input_params%viscos = 0.0e0,
input_params%h_viscos = 3.0e-8,
input_params%resis = 0.0e0,
input_params%h_resis = 3.0e-8,
input_params%diffus = 0.0e0,
input_params%h_diffus = 1.0e-8,
input_params%Eb = 0.25e-2,
input_params%Ev = 0.25e-2,
input_params%En = 0.25e-3,
input_params%spectrum_slope = 3.0e0,
input_params%spectrum_peak = 2.0e0,
input_params%rng_seed = 1789,
/
'''
