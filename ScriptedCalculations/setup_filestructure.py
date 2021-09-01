"""
Setup directory in order to run job. Copies and fills out templates
"""

import shutil, os
from pathlib import Path

from nwxutils import *


def setup_job_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, charge=0):
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
    # (values will changed/finalized during job)
    for nwchemstage in ['geometryoptimize', 'gndstate', 'xanes', 'xescalc']:
        set_template_vars(compounddir/nwchemstage/'input.nw',
            [('COMPOUND', compoundname),
            ('SCRATCH_DIR', scratchdir),
            #('PERMANENT_DIR', str(workdir/compoundname)),
            # ('BASIS_DATA', basisdata),
            ('CHARGE', charge),
            ('MULT', mult)])

    print(repr(str(Path(env_config['NWXPL_MPI_PATH'])/'lib')))

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
                            scratchdir, outdir, charge=0):
    """
    Set up esp filestructure in working dir before job is started.

    Paths passed to setup must be absolute.
    """
    # Root dir of pipeline filestructure (should this be passed?)
    PL_ROOT = Path(__file__).parents[1]

    compoundname = structfilename.stem
    structbasename = structfilename.name
    compounddir = workdir/compoundname

    # Make esp dir
    os.mkdirs(compounddir/'esp')
    shutil.copy(PL_ROOT/'template'/'esp'/'input.nw', compounddir/'esp')

    # Set template vars in input file
    set_template_vars(compounddir/'esp'/'input.nw',
                      [('COMPOUND', compoundname),
                       ('SCRATCH_DIR', scratchdir)])
