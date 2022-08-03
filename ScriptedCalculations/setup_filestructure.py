"""Setup directory in order to run job. Copies and fills out templates."""

import shutil
from pathlib import Path

from nwxutils import *


def setup_job_filestructure(structfilename, env_config, basisfilename, workdir,
                            scratchdir, outdir, atom, charge=0, run_esp=False):
    """
    Set up filestructure in working dir before job is started.

    Paths passed to setup must be absolute.
    """
    # Root dir of pipeline filestructure (should this be passed?)
    PL_ROOT = Path(__file__).parents[1]

    compoundname = structfilename.stem
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
    mult = basic_multiplicity_from_atoms(structfilename)

    # Set common template vars in all nwchem input files
    # (values will be changed/finalized during the job)
    for nwchemstage in ['geometryoptimize', 'gndstate', 'xanes', 'xescalc']:
        set_template_vars(compounddir/nwchemstage/'input.nw',
                          [('COMPOUND', compoundname),
                           ('SCRATCH_DIR', scratchdir),
                           # ('PERMANENT_DIR', str(workdir/compoundname)),
                           # ('BASIS_DATA', basisdata),
                           ('CHARGE', charge),
                           ('MULT', mult),
                           ('ATOM', atom)])

    # Set template vars in job file and finalize
    # Note path strings are put through repr to add quotes, guarding spaces
    current_file_path = str(Path(__file__).resolve())
    pipeline_script = current_file_path.replace('setup_filestructure.py',
                                                'runstructure.py')
    #mpi_path = str(Path(env_config['NWXPL_MPI_PATH'])/'lib')
    set_template_vars(compounddir/'tahoma.sbatch',
                      [('JOB_NAME', compoundname),
                       ('PIPELINE_SCRIPT', repr(pipeline_script)),
                       ('COMPOUND_NAME', compoundname),
                       ('WORK_DIR', repr(str(workdir))),
                       ('OUT_DIR', repr(str(outdir))),
                       #('MPI_PATH', repr(mpi_path)),
                       ('EMAIL', env_config['EMAIL'])])
    #finalize_template_vars(compounddir/'job.run')
    finalize_template_vars(compounddir/'tahoma.sbatch')

    if run_esp:
        espdir = compounddir/'esp'
        set_template_vars(espdir/'input.nw',
                          [('COMPOUND', compoundname),
                           ('SCRATCH_DIR', scratchdir)])

    # print("Filesctructure setup for {}".format(compoundname))
