#!/usr/bin/env python3

import os
import shutil
import time
import subprocess


from NWChemScripting import *

import argparse
parser = argparse.ArgumentParser(description='Script to run VTC XES with NWChem.')
parser.add_argument('compound', action='store')
parser.add_argument('initialcharge', action='store', type=int)
parser.add_argument('-heavyatom', action='store', dest='heavyatom', type=str)
args = parser.parse_args()
COMPOUND = args.compound
INITIALCHARGE = args.initialcharge
HEAVYATOM = args.heavyatom

INITIALTMULT = 1

print(COMPOUND)

def run_xes_calc():

    os.chdir(ROOTDIR + '/xescalc')

    shutil.copyfile('template-input-vtc.nw', 'input.nw')

    replace_text_in_file('input.nw', 'COMPOUND', COMPOUND)
    replace_text_in_file('input.nw', 'charge INPUTCHARGE', 'charge {}'.format(INITIALCHARGE + 1))
    replace_text_in_file('input.nw', 'mult INPUTMULT', 'mult {}'.format(1 + 1))
    if HEAVYATOM is not None:
        replace_text_in_file('input.nw', 'HEAVYATOM', HEAVYATOM)

    centeredfile = find_highest_number_xyz_file(ROOTDIR + '/geometryoptimize/xyzfiles/').split('.xyz')[0] + '_centered.xyz'

    shutil.copyfile(ROOTDIR + '/gndstate/{}'.format(centeredfile), ROOTDIR + '/xescalc/{}'.format(centeredfile))

    shutil.copyfile(ROOTDIR + '/gndstate/{}.movecs'.format(COMPOUND), ROOTDIR + '/xescalc/{}.movecs'.format(COMPOUND))

    replace_text_in_file('input.nw', 'load GEOMETRYFILE', 'load {}'.format(centeredfile))

    replace_text_in_file('input.nw', 'HIGHESTOCCUPIEDBETA', str(get_highest_occupied_beta_movec(ROOTDIR + '/gndstate/output-gnd.out')))

#    assert start_job() == 0, 'Run did NOT start succesfully.'
    shutil.copyfile('../../../job.run', 'job.run')
    replace_text_in_file('job.run', 'output.out', 'output-vtc.out')
    replace_text_in_file('job.run', 'NAME', COMPOUND)
    replace_text_in_file('job.run', 'T:00:00', '9:00:00')
    start_job_mpi() 


if __name__ == '__main__':    
    os.chdir('{}'.format(COMPOUND))
    ROOTDIR = os.getcwd()
    os.chdir(ROOTDIR + '/xescalc')
    print('Beginning XES calculation sequence...')
    run_xes_calc()
