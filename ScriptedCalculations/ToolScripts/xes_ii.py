#!/usr/bin/env python3

import os
import shutil
import time
import subprocess


from NWChemScripting import *

#import pathlib
import argparse
parser = argparse.ArgumentParser(description='Script to run gndstate for XES with NWChem.')
parser.add_argument('compound', action='store')
parser.add_argument('initialcharge', action='store', type=int)
parser.add_argument('-heavyatom', action='store', dest='heavyatom', type=str)
args = parser.parse_args()
COMPOUND = args.compound
INITIALCHARGE = args.initialcharge
HEAVYATOM = args.heavyatom

print(COMPOUND)

def run_gnd_state():
    os.chdir(ROOTDIR + '/gndstate')

    shutil.copyfile('template-input-gnd.nw', 'input.nw')

    optimizedxyz = find_highest_number_xyz_file(ROOTDIR + '/geometryoptimize/xyzfiles/')
    shutil.copyfile(ROOTDIR + '/geometryoptimize/xyzfiles/{}'.format(optimizedxyz), ROOTDIR + '/gndstate/{}'.format(optimizedxyz))

    centeredfile = center_xyz(optimizedxyz, 3)

    replace_text_in_file('input.nw', 'COMPOUND', COMPOUND)
    replace_text_in_file('input.nw', 'charge INPUTCHARGE', 'charge {}'.format(INITIALCHARGE))
    replace_text_in_file('input.nw', 'mult INPUTMULT', 'mult {}'.format(INITIALMULT))

    if HEAVYATOM is not None:
    	replace_text_in_file('input.nw', 'HEAVYATOM', HEAVYATOM)

    replace_text_in_file('input.nw', 'load GEOMETRYFILE', 'load {}'.format(centeredfile))

    shutil.copyfile('../../../job.run', 'job.run')
    replace_text_in_file('job.run', 'output.out', 'output-gnd.out')
    replace_text_in_file('job.run', 'NAME', COMPOUND)
    replace_text_in_file('job.run', 'T:00:00', '0:30:00')
    start_job_mpi()

if __name__ == '__main__':
    os.chdir('{}'.format(COMPOUND))
    ROOTDIR = os.getcwd()

    #Get initial multiplicity from XYZ file
    INITIALMULT = basic_multiplicity_from_atoms(read_xyz(ROOTDIR + '/geometryoptimize/{}.xyz'.format(COMPOUND))[0])
    #print('Initial multiplicity chosen to be {} based on number of electrons and atomic species in input XYZ file'.format(INITIALMULT))

    print('Beginning Gnd State calculation sequence...')
    run_gnd_state()
