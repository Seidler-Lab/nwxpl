#! /usr/bin/env python

""""
Run Structures through pipeline linearly.
Creates one job per structure.
To see more options use '-h' flag.
"""

import argparse
from pathlib import Path
import sys
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from nwxutils import parse_env
from setup_filestructure import setup_job_filestructure


def test_job(jobfile):
    with open(jobfile, 'r') as file:
        for line in file:
            if line.startswith('python'):
                print(line)
                break
    file.close()


def test_run_calculation(structfilename, env_config, basisfilename, workdir,
                         scratchdir, outdir, atom, charge, run_esp=False):
    """Setup and start a job for a structure. Arguments are Path objects."""
    compoundname = structfilename.stem
    print("\nSetting up for {}".format(compoundname))
    setup_job_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, atom, charge=charge,
                            run_esp=run_esp)
    print("Starting job for {}".format(compoundname))
    # from nwxutils.py
    test_job(jobfile=str(workdir/compoundname/'tahoma.sbatch'))


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
                        type=float, default=0,
                        help="Specify charge of compound (default 0)")

    args = parser.parse_args()
    LIST_FILENAME = Path(args.listname).resolve()
    BASIS_FILENAME = Path(args.basefile).resolve()
    WORK_DIR = Path(args.workdir).resolve()
    SCRATCH_DIR = Path(args.scratchdir).resolve()
    OUT_DIR = Path(args.outdir).resolve()
    ATOM = args.atom
    CHARGE = args.charge

    run_esp = False

    # Check basis file exists if specified
    if (BASIS_FILENAME is not None and not BASIS_FILENAME.exists()):
        print("Can't read basis file")
        sys.exit(1)

    # Load environment vars
    ENV_CONFIG = parse_env("test_env.env")  # from nwxutils.py

    structurelist = None
    # Run each structure in list
    try:
        with open(LIST_FILENAME, 'r') as f:
            structurelist = [Path(line.strip()) for line in f]
    except:
        print("Unable to open structure list file: {}".format(LIST_FILENAME))
        sys.exit(1)

    for structfilename in structurelist:
        test_run_calculation(structfilename, ENV_CONFIG, BASIS_FILENAME, WORK_DIR,
                             SCRATCH_DIR, OUT_DIR, ATOM, CHARGE, run_esp=run_esp)
