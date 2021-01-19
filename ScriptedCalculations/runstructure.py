#!/usr/bin/env python

import subprocess
import pathlib
import shutil
from pathlib import Path
import argparse

from nwxutils import *

# Set up filestructure in working dir before job is started 
# Paths passed to setup must be absolute 
def setup_job_filestructure(structfilename, basisfilename, workdir, scratchdir, outdir, charge=0):
 
		PL_ROOT = Path(__file__).parents[1]	# Root dir of pipeline filestructure (should this be passed?)

		compoundname = structfilename.stem 
		structbasename = structfilename.name 
		compounddir = workdir/compoundname 
 
		# Read basis code 
		with basisfilename.open() as f: 
				basisdata = f.read() 
 
		# Make calculation dir and move files into it
		if compounddir.exists():
				shutil.rmtree(compounddir)	# Remove dir and replace if already exists
		shutil.copytree(PL_ROOT/'template', compounddir) # Copy template dirs 
		shutil.copy(structfilename, compounddir/'geometryoptimize')		# Copy XYZ 
 
		# Get initial multiplicity 
		mult = basic_multiplicity_from_atoms(read_xyz(structfilename)) 
		 
		# Set common template vars in all nwchem input files (values will changed/finalized during job) 
		for nwchemstage in ['geometryoptimize', 'gndstate', 'xanes', 'xescalc']:
				set_template_vars(compounddir/nwchemstage/'input.nw',  
						[('COMPOUND', compoundname), 
						('SCRATCH_DIR', scratchdir), 
						#('PERMANENT_DIR', str(workdir/compoundname)), 
						#('BASIS_DATA', basisdata), 
						('CHARGE', charge), 
						('MULT', mult)]) 
 
		# Set template vars in job file and finalize
		# Note path strings are put through repr to add quotes, guarding spaces
		set_template_vars(compounddir/'job.run', 
				[('JOB_NAME', compoundname), 
				('PIPELINE_SCRIPT', repr(str(Path(__file__).resolve()))), 
				('COMPOUND_NAME', compoundname), 
				('WORK_DIR', repr(str(workdir))), 
				('OUT_DIR', repr(str(outdir)))])
		finalize_template_vars(compounddir/'job.run')

# Run geometry optimize step and return exit code
def run_geometry_optimization(compoundname, compounddir, numcores):
	print("Starting Geometry Optimization for {}".format(compoundname))
	geomdir = compounddir/'geometryoptimize'
	finalize_template_vars(geomdir/'input.nw') 	# No need to change any vals
	replace_text_in_file(geomdir/'input.nw', [('* library 6-311G**', '* library 6-31G*')])
	return run_nwchem_job(geomdir/'input.nw',geomdir/'output.out', numcores)

# Run ground state calculation and return exit code
def run_gnd_state_calculation(compoundname, compounddir, numcores):
	print("Starting Ground State Calculation for {}".format(compoundname))
	gnddir = compounddir/'gndstate'
	geomdir = compounddir/'geometryoptimize'
	# Copy over optimized XYZ and center it
	highestxyznum = find_highest_number_xyz_file(geomdir/'xyzfiles')
	highestxyzpath = geomdir/'xyzfiles/'/'{}-{:03}.xyz'.format(compoundname, highestxyznum)
	optimizedfilepath = gnddir/(compoundname+'_optimized.xyz')
	shutil.copyfile(highestxyzpath, optimizedfilepath)
	centeredfile = center_xyz(optimizedfilepath,0)
	# Set and finalize template vals in input.nw
	set_template_vars(gnddir/'input.nw',
		[('GEOMETRY_FILE', centeredfile.name)])
	finalize_template_vars(gnddir/'input.nw')
	# Call nwchem for gnd state calculation
	return run_nwchem_job(gnddir/'input.nw', gnddir/'output.out',numcores)

# Run XANES calculation and return exit code
def run_xanes_calculation(compoundname, compounddir, numcores):
	print("Starting XANES calculation for {}".format(compoundname))
	xanesdir = compounddir/'xanes'
	# Copy over centered XYZ
	centeredfile = (compounddir/'gndstate').glob('*center*').__next__()	# Slightly hacky
	shutil.copy(centeredfile, xanesdir/centeredfile.name)
	# Find ecut from geometry optimization output
	ecut = find_ecut(compounddir/'geometryoptimize'/'output.out')
	# Set and finalize template vals in input.nw
	set_template_vars(xanesdir/'input.nw',
		[('GEOMETRY_FILE', centeredfile.name),
		('ECUT', ecut)])
	finalize_template_vars(xanesdir/'input.nw')
	# Run nwchem XANES calculation and write output to file
	return run_nwchem_job(xanesdir/'input.nw', xanesdir/'output.out', numcores)

# Run XES calculation and return exit code
def run_xes_calculation(compoundname, compounddir, numcores):
	print("Starting VTC XES calculation for {}".format(compoundname))
	xesdir = compounddir/'xescalc'
	gnddir = compounddir/'gndstate'
	# Copy over centered XYZ and the molecular vectors file
	centeredfile = gnddir.glob('*center*').__next__()	# Slightly hacky
	shutil.copy(centeredfile, xesdir/centeredfile.name)
	shutil.copy(gnddir/(compoundname+'.movecs'), xesdir)
	# Set and finalize template vals in input.nw
	highest_occupied_beta = get_highest_occupied_beta_movec(gnddir/'output.out')
	charge = int(get_template_var(xesdir/'input.nw', 'CHARGE'))+1	# Increase charge by 1
	set_template_vars(xesdir/'input.nw',
		[('GEOMETRY_FILE', centeredfile.name),
		('CHARGE', charge),
		('MULT', '2'),
		('HIGHEST_OCCUPIED_BETA', highest_occupied_beta)])
	finalize_template_vars(xesdir/'input.nw')
	# Run nwchem for xes calc
	return run_nwchem_job(xesdir/'input.nw', xesdir/'output.out', numcores)

def run_structure(compoundname, workdir, outdir, numcores):
	compounddir = workdir/compoundname
	
	## Run geometry optimization	
	exitcode = run_geometry_optimization(compoundname, compounddir, numcores)
	assert exitcode == 0, "NWChem call on geometry optimization step returned exitcode {}!".format(exitcode)

	## Run ground state calculation
	exitcode = run_gnd_state_calculation(compoundname, compounddir, numcores)
	assert exitcode == 0, "NWChem call on gnd state calculation step returned exitcode {}!".format(exitcode)

	## Run XANES calculation
	exitcode = run_xanes_calculation(compoundname, compounddir, numcores)
	assert exitcode == 0, "NWChem call on xanes calculation step returned exitcode {}!".format(exitcode)

	## Run XES calculation
	exitcode = run_xes_calculation(compoundname, compounddir, numcores)
	assert exitcode == 0, "NWChem call on xes calculation step returned exitcode {}!".format(exitcode)
	
	## Extract dat from XANES output
	# TODO: make these function calls within python rather than a shell calls
	print("Extracting spectrum from XANES output for {}".format(compoundname))
	subprocess.run(['python', 'ToolScripts/nw_spectrum_xanes.py', '-x',
		'-i', (compounddir/'xanes'/'output.out').resolve(),
		'-o', (compounddir/'xanes'/'xanes.dat').resolve()])

	## Extract dat from XES output
	print("Extracting spectrum from XES output for {}".format(compoundname))	
	subprocess.run(['python', 'ToolScripts/nw_spectrum_xes.py', '-x',
		'-i', (compounddir/'xescalc'/'output.out').resolve(),
		'-o', (compounddir/'xescalc'/'xes.dat').resolve()])

	## Collect dats
	print("Moving spectrum dat files to output directory")
	shutil.copy(compounddir/'xanes'/'xanes.dat', outdir/'{}_xanes.dat'.format(compoundname))
	shutil.copy(compounddir/'xescalc'/'xes.dat', outdir/'{}_xes.dat'.format(compoundname))
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser( \
		description='Run a single structure through pipeline (Should be run WITHIN JOB')
	parser.add_argument('compoundname', action='store', type=str)
	parser.add_argument('workdir', action='store', type=str)
	parser.add_argument('outdir', action='store', type=str)
	parser.add_argument('cores', action='store', type=int)

	args = parser.parse_args()
	COMPOUND_NAME = args.compoundname
	WORK_DIR = Path(args.workdir).resolve()
	OUT_DIR = Path(args.outdir).resolve()
	CORES = args.cores

	print(CORES)

	run_structure(COMPOUND_NAME, WORK_DIR, OUT_DIR, CORES)
