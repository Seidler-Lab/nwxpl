#! /usr/bin/env python

"""
Run Structures through pipeline linearly.

Creates one job per structure.
To see more options use '-h' flag.
"""

import argparse
from pathlib import Path
import sys
import os
import subprocess

from nwxutils import parse_env, start_batch_job
from setup_filestructure import setup_job_filestructure


def test_job(jobfile):
    """When testing pipeline, don't submit job to the cluster."""
    with open(jobfile, 'r') as file:
        for line in file:
            if line.startswith('python'):
                line = line.replace('P ML', 'P_ML').replace("\\\\", '/')
                line = line.replace("\n", "").replace("'", "")
                line = line.split(" ")
                command = [ele.replace('P_ML', 'P ML') for ele in line]
                command.insert(2, '-t')
                command.insert(3, 'True')
                subprocess.call(command)
                break
    file.close()


def run_calculation(structfilename, env_config, basisfilename, workdir,
                    scratchdir, outdir, atom, charge, run_esp=False,
                    test_phase=False):
    """Setup and start a job for a structure. Arguments are Path objects."""
    compoundname = structfilename.stem
    print("\nSetting up for {}".format(compoundname))
    setup_job_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, atom, charge=charge,
                            run_esp=run_esp)
    print("Starting job for {}".format(compoundname))
    if test_phase:
        print("in test phase")
        test_job(jobfile=str(workdir / compoundname / 'tahoma.sbatch'))
    else:
        #start_batch_job(jobfile=str(workdir / compoundname / 'tahoma.sbatch'))
        print("in nwxpl.py, trying to run run.sh")
        start_batch_job(jobfile=str(workdir / compoundname / 'run.sh'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Script to run through entire NWChem pipeline.")
    parser.add_argument('-i', '--inlist', action='store', dest='listname',
                        type=str, required=True,
                        help="Name of list containing line-separated names " +
                             "of structure files (without extensions")
    parser.add_argument('-b', '--basefile', action='store', dest='basefile',
                        type=str, required=True,
                        help="Specify file with NWChem atom basis.")
    parser.add_argument('-w', '--workdir', action='store', dest='workdir',
                        type=str, default='',
                        help="Specify dir to perform calculations in " +
                             "(should persist across jobs)")
    parser.add_argument('-s', '--scratchdir', action='store',
                        dest='scratchdir', type=str, default='',
                        help="Specify scratch dir to be used by NWChem " +
                             "(default: current dir)")
    parser.add_argument('-o', '--outputdir', action='store', dest='outdir',
                        type=str, default='',
                        help="Specify location to move final dat files")
    parser.add_argument('-a', '--atom', action='store', dest='atom', type=str,
                        default='Ca',
                        help="Specify element, or atom, of which to perform " +
                             "calculations")
    parser.add_argument('-c', '--charge', action='store', dest='charge',
                        type=int, default=0,
                        help="Specify charge of compound (default 0)")
    parser.add_argument('-t', '--test', action='store', dest='test',
                        type=int, default=0,
                        help="Specify whether in testing phase or not.")


    args = parser.parse_args()
    LIST_FILENAME = Path(args.listname).resolve()
    BASIS_FILENAME = Path(args.basefile).resolve()
    WORK_DIR = Path(args.workdir).resolve()
    SCRATCH_DIR = Path(args.scratchdir).resolve()
    OUT_DIR = Path(args.outdir).resolve()
    ATOM = args.atom
    CHARGE = args.charge
    test_phase = args.test

    if test_phase == 0:
        test_phase = False
    else:
        test_phase = True
    
    run_esp = False

    # Check basis file exists if specified
    if (BASIS_FILENAME is not None and not BASIS_FILENAME.exists()):
        print("Can't read basis file")
        sys.exit(1)

    # Load environment vars
    if test_phase:
        ENV_CONFIG = parse_env("test_env.env")
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.append(parent_dir)
    else:
        ENV_CONFIG = parse_env(".env")

    structurelist = None
    # Run each structure in list
    try:
        with open(LIST_FILENAME, 'r') as f:
            structurelist = [Path(line.strip()) for line in f]
    except:
        print("Unable to open structure list file: {}".format(LIST_FILENAME))
        sys.exit(1)

    for structfilename in structurelist:
        run_calculation(structfilename, ENV_CONFIG, BASIS_FILENAME, WORK_DIR,
                        SCRATCH_DIR, OUT_DIR, ATOM, CHARGE, run_esp=run_esp,
                        test_phase=test_phase)
