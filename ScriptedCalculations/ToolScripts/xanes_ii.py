#!/usr/bin/env python3

import os
import shutil
import time
import subprocess


from NWChemScripting import *

import argparse
parser = argparse.ArgumentParser(description='Script to run xanes from an optimized geometry with NWChem.')
parser.add_argument('compound', action='store')
parser.add_argument('initialcharge', action='store', type=int)
parser.add_argument('-heavyatom', action='store', dest='heavyatom', type=str)
args = parser.parse_args()
COMPOUND = args.compound
INITIALCHARGE = args.initialcharge
HEAVYATOM = args.heavyatom

print(COMPOUND)

def find_ecut(infile):
    # Read optimized geometry file
    with open(infile, 'r') as file:
        for line in file:
            # find first line the looks something like 'Vector    1  Occ=1.000000D+00  E=-8.888006D+01'
            if 'Vector    1' in line:
                ecut = line.split('E=')[1].replace('\n','').replace('D','E')
                ecut = round(float(ecut), 1) + 1
                #print("Energy cut at {} hartrees".format(ecut))
                return ecut
    # No ecut found. Throw error.
    raise SystemExit('Error: No ecut found. Exiting XANES calculation.')


def run_xanes_calc():

    os.chdir(ROOTDIR + '/xanes')

    shutil.copyfile('template-input-xanes.nw', 'input.nw')

    optimizedxyz = find_highest_number_xyz_file(ROOTDIR + '/geometryoptimize/xyzfiles/')
    shutil.copyfile(ROOTDIR + '/geometryoptimize/xyzfiles/{}'.format(optimizedxyz), ROOTDIR + '/xanes/{}'.format(optimizedxyz))

    centeredfile = center_xyz(optimizedxyz, 3)

    replace_text_in_file('input.nw', 'COMPOUND', COMPOUND)
    replace_text_in_file('input.nw', 'charge INPUTCHARGE', 'charge {}'.format(INITIALCHARGE))

    replace_text_in_file('input.nw', 'load GEOMETRYFILE', 'load {}'.format(centeredfile))

    ecut = find_ecut(ROOTDIR + '/geometryoptimize/output-geometryoptimize.out')
    replace_text_in_file('input.nw', 'ecut ECUT', 'ecut {}'.format(ecut))

    if HEAVYATOM is not None:
        replace_text_in_file('input.nw', 'HEAVYATOM', HEAVYATOM)

    shutil.copyfile('../../../job.run', 'job.run')
    replace_text_in_file('job.run', 'output.out', 'output-xanes.out')
    replace_text_in_file('job.run', 'NAME', COMPOUND)
    replace_text_in_file('job.run', 'T:00:00', '7:00:00')
    start_job_mpi()

if __name__ == '__main__':
    # Make directory structure
    #print('Copying template folder to new directory')  
    #subprocess.call(['rm', '-r', '{}/xanes'.format(COMPOUND)])
    
    if HEAVYATOM is None:
        shutil.copytree('../template/xanes', '{}/xanes'.format(COMPOUND)) 
    else:
        shutil.copytree('../template/ECP/xanes', '{}/xanes'.format(COMPOUND)) 

    # Set current working directory  and ROOTDIR needed for the 'run' functions to work
    os.chdir('{}'.format(COMPOUND))
    ROOTDIR = os.getcwd()

    print('Beginning XANES calculation...')
    run_xanes_calc()

