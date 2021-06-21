#! /usr/bin/env python

""""
Run Structures through pipeline linearly.
Creates one job per structure.
To see more options use '-h' flag.
"""

import argparse
import sys
from pathlib import Path

from nwxutils import start_batch_job
from setup_filestructure import setup_job_filestructure


# Setup and start a job for a structure
# Arguments are Path objects
def run_structure(structfilename, basisfilename, workdir, scratchdir, outdir):
	compoundname = structfilename.stem
	print("\nSetting up for {}".format(compoundname))
	setup_job_filestructure(structfilename, basisfilename, workdir, scratchdir, outdir)
	print("Starting job for {}".format(compoundname))
	start_batch_job(str(workdir/compoundname/'job.run'))  # from nwxutils.py


if __name__ == '__main__':
	parser = argparse.ArgumentParser( \
		description="Script to run structures through XES/XANES calculation linearly")
	parser.add_argument('-i', '--inlist', action='store', dest='listname', type=str, required=True, \
		help="Name of list containing line-separated names of structure files (without extensions")
	parser.add_argument('-b', '--basefile', action='store', dest='basefile', type=str, required=True, \
		help="Specify file with NWChem atom basis specifications")
	parser.add_argument('-w', '--workdir', action='store', dest='workdir', type=str, default='', \
		help="Specify dir to perform calculations in (should persist across jobs)")
	parser.add_argument('-s', '--scratchdir', action='store', dest='scratchdir', type=str, default='', \
		help="Specify scratch dir to be used by NWChem (default: current dir)")
	parser.add_argument('-o', '--outputdir', action='store', dest='outdir', type=str, default='', \
		help="Specify location to output final spectra dat files")

	args = parser.parse_args()
	LIST_FILENAME = Path(args.listname).resolve()
	BASIS_FILENAME = Path(args.basefile).resolve()
	WORK_DIR = Path(args.workdir).resolve()
	SCRATCH_DIR = Path(args.scratchdir).resolve()
	OUT_DIR = Path(args.outdir).resolve()

	# Check basis file exists if specified
	if (BASIS_FILENAME is not None and not BASIS_FILENAME.exists()):
		print("Can't read basis file")
		sys.exit(1)
	
	try:	
		with open(LIST_FILENAME, 'r') as f:
			for line in f:
				structfilename = Path(line.strip())
				run_structure(structfilename, BASIS_FILENAME, WORK_DIR, SCRATCH_DIR, OUT_DIR)
	except:
		print("Unable to open structure list file: {}".format(LIST_FILENAME))
		sys.exit(1)
