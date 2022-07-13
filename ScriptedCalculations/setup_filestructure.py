"""Setup directory in order to run job. Copies and fills out templates."""

import shutil, os, sys
from pathlib import Path

from nwxutils import *


def setup_job_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, atom, charge=0):
    """
    Set up filestructure in working dir before job is started.

    Paths passed to setup must be absolute.
    """
    # Root dir of pipeline filestructure (should this be passed?)
    PL_ROOT = Path(__file__).parents[1]

    compoundname = structfilename.stem
    structbasename = structfilename.name
    compounddir = workdir/compoundname

    # Read basis code
    with basisfilename.open() as f:
        basisdata = f.read()

    # Make calculation dir and move files into it
    if compounddir.exists():
        print("Found existing directory. Deleting.")
        shutil.rmtree(compounddir)  # Remove dir and replace if already exists
    shutil.copytree(PL_ROOT/'template', compounddir)  # Copy template dirs
    shutil.copy(structfilename, compounddir/'geometryoptimize/')    # Copy XYZ

    # Get initial multiplicity
    mult = basic_multiplicity_from_atoms(read_xyz(structfilename))

    # Set common template vars in all nwchem input files
    # (values will be changed/finalized during the job)
    for nwchemstage in ['geometryoptimize', 'gndstate', 'xanes', 'xescalc']:
        set_template_vars(compounddir/nwchemstage/'input.nw',
            [('COMPOUND', compoundname),
            ('SCRATCH_DIR', scratchdir),
            #('PERMANENT_DIR', str(workdir/compoundname)),
            # ('BASIS_DATA', basisdata),
            ('CHARGE', charge),
            ('MULT', mult)
            ('ATOM', atom)])

    # print(repr(str(Path(env_config['NWXPL_MPI_PATH'])/'lib')))

    # Set template vars in job file and finalize
    # Note path strings are put through repr to add quotes, guarding spaces
    current_file_path = str(Path(__file__).resolve())
    pipeline_Script = current_file_path.replace('setup_filestructure.py', 'runstructure.py')
    set_template_vars(compounddir/'job.run',
        [('JOB_NAME', compoundname),
        ('PIPELINE_SCRIPT', repr(pipeline_Script)),
        ('COMPOUND_NAME', compoundname),
        ('WORK_DIR', repr(str(workdir))),
        ('OUT_DIR', repr(str(outdir))),
        ('MPI_PATH', repr(str(Path(env_config['NWXPL_MPI_PATH'])/'lib'))),
        ('EMAIL', env_config['NWXPL_EMAIL'])])
    finalize_template_vars(compounddir/'job.run')

    # print("Filesctructure setup for {}".format(compoundname))


def setup_esp_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, atom, charge=0):
    """
    Set up esp filestructure in working dir before job is started.

    Paths passed to setup must be absolute.
    """
    # Root dir of pipeline filestructure (should this be passed?)
    PL_ROOT = Path(__file__).parents[1]

    compoundname = structfilename.stem
    structbasename = structfilename.name
    compounddir = workdir/compoundname
    espdir = compounddir/'esp'

    # Check for calculation dir in working directory
    existing_directory = False
    if compounddir.exists():
        print("Found existing working directory.")
        xanesdir = compounddir/'xanes'
        if xanesdir.exists():
            existing_directory = True
        else:
            print("Deleting exisiting directory because it's incomplete.")
            shutil.rmtree(compounddir)  # Remove dir and replace if already exists

    if not existing_directory:
        # If directory does not exist, make it
        os.mkdir(compounddir)
        os.mkdir(compounddir/'gndstate')
        # copy and set template vars of job.run file
        shutil.copy(PL_ROOT/'template'/'job.run', compounddir)
        # Set template vars in job file and finalize
        # Note path strings are put through repr to add quotes, guarding spaces
        current_file_path = str(Path(__file__).resolve())
        pipeline_Script = current_file_path.replace('setup_filestructure.py', 'runstructure.py')
        set_template_vars(compounddir/'job.run',
            [('JOB_NAME', compoundname),
            ('PIPELINE_SCRIPT', repr(pipeline_Script)),
            ('COMPOUND_NAME', compoundname),
            ('WORK_DIR', repr(str(workdir))),
            ('OUT_DIR', repr(str(outdir))),
            ('MPI_PATH', repr(str(Path(env_config['NWXPL_MPI_PATH'])/'lib'))),
            ('EMAIL', env_config['NWXPL_EMAIL'])])
        finalize_template_vars(compounddir/'job.run')

    # If optimized and centered xyz file in input_xyz directory
    optimized_xyz = 'input_xyz/{}_optimized_centered.xyz'.format(compoundname)
    if os.path.exists(optimized_xyz) and not existing_directory:
        print("Found optimized gemoetry file.")
        shutil.copy(optimized_xyz, compounddir/'gndstate')
    else:
        print("Can't find working dir or optimized xyz file for {}".format(compoundname))
        sys.exit(1)

    # Make calculation dir and move files into it
    if espdir.exists():
        print("Found existing esp directory. Deleting.") 
        shutil.rmtree(espdir)  # Remove dir and replace if already exists
    # Make esp dir
    os.mkdir(compounddir/'esp')
    shutil.copy(PL_ROOT/'template'/'esp'/'input.nw', compounddir/'esp')

    # Set template vars in input file
    set_template_vars(compounddir/'esp'/'input.nw',
                      [('COMPOUND', compoundname),
                       ('SCRATCH_DIR', scratchdir)])
