# !/usr/bin/env python

import os
import shutil
import time
import subprocess


from NWChemScripting import *

import argparse
parser = argparse.ArgumentParser(description='Script to run geometryoptimize with NWChem.')
parser.add_argument('compound', action='store')
parser.add_argument('initialcharge', action='store', type=int)
parser.add_argument('-heavyatom', action='store', dest='heavyatom', type=str)
args = parser.parse_args()
COMPOUND = args.compound
INITIALCHARGE = args.initialcharge
HEAVYATOM = args.heavyatom

print(COMPOUND)

def run_geometry_optimize():
    os.chdir(ROOTDIR + '/geometryoptimize')
    shutil.copyfile('template-input.nw', 'input.nw')
    replace_text_in_file('input.nw', 'COMPOUND', COMPOUND)
    replace_text_in_file('input.nw', 'charge INPUTCHARGE', 'charge {}'.format(INITIALCHARGE))
    replace_text_in_file('input.nw', 'mult INPUTMULT', 'mult {}'.format(INITIALMULT))
    
    if HEAVYATOM is not None:
        replace_text_in_file('input.nw', 'HEAVYATOM', '{}'.format(HEAVYATOM))
   
    shutil.copyfile('../../../job.run', 'job.run')
    replace_text_in_file('job.run', 'output.out', 'output-geometryoptimize.out')
    replace_text_in_file('job.run', 'NAME', COMPOUND)    
    replace_text_in_file('job.run', 'T:00:00', '10:00:00')    
    start_job_mpi() #actual nwchem call


if __name__ == '__main__':
    # # Check for geometry file
    restart = True
    
    if restart:
        subprocess.call(['rm', '-r', COMPOUND])
        #os.chdir('{}'.format(COMPOUND))
        #ROOTDIR = os.getcwd()
        #os.chdir(ROOTDIR + '/geometryoptimize')        
        #lastxyz = find_second_highest_number_xyz_file(ROOTDIR + '/geometryoptimize/xyzfiles/')
        #replace_text_in_file('input.nw', 'load ', 'load xyzfiles/{} #'.format(lastxyz)) 
        #start_job_mpi() #actual nwchem call
    
    #print('input_xyz/{}.mol'.format(COMPOUND))
    molexists = os.path.exists('input_xyz/{}.mol'.format(COMPOUND))
    xyzexists = os.path.exists('input_xyz/{}.xyz'.format(COMPOUND))
    assert molexists or xyzexists, 'Error, specified compound molecular geometry file does not exist'

    # Make directory structure
    assert not os.path.exists(COMPOUND), 'Error, folder already exists'
    os.mkdir(COMPOUND)
        
    #print('Copying template folder to new directory')
    if HEAVYATOM is None:
        shutil.copytree('../template/geometryoptimize', '{}/geometryoptimize'.format(COMPOUND))
        shutil.copytree('../template/gndstate', '{}/gndstate'.format(COMPOUND))
        shutil.copytree('../template/xescalc', '{}/xescalc'.format(COMPOUND))
    else:
        shutil.copytree('../template/ECP/geometryoptimize', '{}/geometryoptimize'.format(COMPOUND))
        shutil.copytree('../template/ECP/gndstate', '{}/gndstate'.format(COMPOUND))
        shutil.copytree('../template/ECP/xescalc', '{}/xescalc'.format(COMPOUND))


    # Convert mol to xyz if needed
    if not xyzexists:
        convert_mol_to_xyz('input_xyz/{}.mol'.format(COMPOUND))

    #print('Copying xyz file to new folder.')
    shutil.copy('input_xyz/{}.xyz'.format(COMPOUND), '{}/geometryoptimize/{}.xyz'.format(COMPOUND, COMPOUND))

    # Set current working directory  and ROOTDIR needed for the 'run' functions to work
    os.chdir('{}'.format(COMPOUND))
    ROOTDIR = os.getcwd()

    #Get initial multiplicity from XYZ file
    INITIALMULT = basic_multiplicity_from_atoms(read_xyz(ROOTDIR + '/geometryoptimize/{}.xyz'.format(COMPOUND))[0])
    #print('Initial multiplicity chosen to be {} based on number of electrons and atomic species in input XYZ file'.format(INITIALMULT))

    print('Beginning calculation sequence...')
    run_geometry_optimize()
    
