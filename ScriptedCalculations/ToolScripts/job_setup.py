#!/usr/bin/env python

# Setup directory structure before starting phases

import os
import subprocess
import shutil
from pathlib import Path

from ToolScripts import nwxutils	# Utility functions used within pipeline

# Set up filestructure in working dir before job is started
# Paths passed to setup must be absolute
def setup_job_filestructure(structfilename, basisfilename, workdir, scratchdir, outdir, restart=True, inputcharge=0):
	
	# Job resource estimates
	jobhours = 24	
	jobmemgigs = 50

	compoundname = structfilename.stem
	structbasename = structfile.name
	compounddir = workdir/compoundname

	# Read basis code
	with basisfilename.open() as f:
		basisdata = f.read()

	# if restarting (usual case), remove existing calculation dir
	if restart and compounddir.exists():
		shutil.rmtree(compounddir)
		compounddir.mkdir()

	# Make new dir and populate with customized template filestructure
	shutil.copytree(PLROOT/'template', compounddir)	# Copy template dirs including .nw files
	shutil.copy(structfilename, compounddir)	# Copy XYZ

	# Get initial multiplicity
	initialmult = basic_multiplicity_from_atoms(read_xyz(structbasename))
	
	# Set common template vars in all nwchem input files (values will be modified and finalized during job)
	for nwchemstage in ['geometryoptimize', 'gndstate', 'xanes', 'xescalc']:
		set_template_vars(compoundir/nwchemstage/'input.nw', 
			[('COMPOUND', compoundname),
			('SCRATCH_DIR', scratchdir),
			('PERMANENT_DIR', str(workdir/compoundname)),
			('BASIS_DATA', basisdata),
			('INPUT_CHARGE', inputcharge),
			('INPUT_MULT', inputmult)])

	# Set template vars in job file
	set_template_vars(compounddir/'job.run',
		[('JOB_NAME', compoundname),
		('PIPELINE_SCRIPT', str(PLROOT/'ScriptedCalculations'/'run_structure.py')),
		('COMPOUND_NAME', compoundname),
		('WORK_DIR', str(workdir)),
		('OUT_DIR', str(outdir))])


