"""Python script that is run on cluster by job or sbatch file."""

#!/usr/bin/env python

import shutil
from pathlib import Path
import argparse
import subprocess

from nwxutils import set_template_vars
from nwxutils import finalize_template_vars
from nwxutils import replace_text_in_file
from nwxutils import run_nwchem_job
from nwxutils import find_highest_number_xyz_file
from nwxutils import center_xyz
from nwxutils import check_for_heavy_atoms
from nwxutils import ecp_required, add_ecp
from nwxutils import find_ecut
from nwxutils import get_highest_occupied_beta_movec
from nwxutils import basic_multiplicity_from_atoms
from nwxutils import get_template_var


def run_geometry_optimization(compoundname, compounddir, numcores, test_phase,
                              mpi_path=None):
    """Run geometry optimize step and return exit code."""
    print("Starting Geometry Optimization for {}".format(compoundname))
    geomdir = compounddir / 'geometryoptimize'
    finalize_template_vars(geomdir / 'input.nw')  # No need to change any vals
    replace_text_in_file(geomdir / 'input.nw', [('* library 6-311G**',
                                                 '* library 6-31G*')])
    if test_phase:
        return 0
    else:
        return run_nwchem_job(geomdir / 'input.nw', geomdir / 'output.out',
                              numcores, mpi_path=mpi_path)


def run_gnd_state_calculation(compoundname, compounddir, numcores, test_phase,
                              atom, mpi_path=None):
    """Run ground state calculation and return exit code."""
    print("Starting Ground State Calculation for {}".format(compoundname))
    gnddir = compounddir / 'gndstate'
    geomdir = compounddir / 'geometryoptimize'
    # Copy over optimized XYZ and center it
    if test_phase:
        highpath = geomdir / '{}.xyz'.format(compoundname)
    else:
        highestxyz = find_highest_number_xyz_file(geomdir / 'xyzfiles')
        if highestxyz == 0:
            highpath = geomdir / '{}.xyz'.format(compoundname)
        else:
            highpath = geomdir / 'xyzfiles' / '{}-{:03}.xyz'.format(compoundname,
                                                                    highestxyz)

    optimizedfilepath = gnddir / (compoundname + '_optimized.xyz')
    shutil.copyfile(highpath, optimizedfilepath)
    centeredfile = center_xyz(optimizedfilepath, 0)
    # check for heavier atoms to replace with ECP
    heavy_atoms = check_for_heavy_atoms(centeredfile, atom)
    if ecp_required(heavy_atoms):
        # replace heavier atoms with ECP
        add_ecp(gnddir / 'input.nw', heavy_atoms)
    # Set and finalize template vals in input.nw
    geometry_file = centeredfile.name
    set_template_vars(gnddir / 'input.nw', [('GEOMETRY_FILE', geometry_file)])
    finalize_template_vars(gnddir / 'input.nw')
    if test_phase:
        return 0
    else:
        # Call nwchem for gnd state calculation
        return run_nwchem_job(gnddir / 'input.nw', gnddir / 'output.out',
                              numcores, mpi_path=mpi_path)


def run_xanes_calculation(compoundname, compounddir, numcores, test_phase,
                          atom, mpi_path=None):
    """Run XANES calculation and return exit code."""
    print("Starting XANES calculation for {}".format(compoundname))
    xanesdir = compounddir / 'xanes'
    # Copy over centered XYZ
    centeredfile = (compounddir / 'gndstate').glob('*center*').__next__()
    shutil.copy(centeredfile, xanesdir / centeredfile.name)
    if test_phase:
        ecut = 42
    else:
        # Find ecut from geometry optimization output
        ecut = find_ecut(compounddir / 'gndstate' / 'output.out')
    # check for heavier atoms to replace with ECP
    heavy_atoms = check_for_heavy_atoms(centeredfile, atom)
    if ecp_required(heavy_atoms):
        # replace heavier atoms with ECP
        add_ecp(xanesdir / 'input.nw', heavy_atoms)
    # Set and finalize template vals in input.nw
    geometry_file = centeredfile.name
    set_template_vars(xanesdir / 'input.nw', [('GEOMETRY_FILE', geometry_file),
                                              ('ECUT', ecut)])
    finalize_template_vars(xanesdir / 'input.nw')
    if test_phase:
        return 0
    else:
        # Run nwchem XANES calculation and write output to file
        return run_nwchem_job(xanesdir / 'input.nw', xanesdir / 'output.out',
                              numcores, mpi_path=mpi_path)


def run_xes_calculation(compoundname, compounddir, numcores, test_phase,
                        atom, mpi_path=None):
    """Run XES calculation and return exit code."""
    print("Starting VtC-XES calculation for {}".format(compoundname))
    xesdir = compounddir / 'xescalc'
    gnddir = compounddir / 'gndstate'
    # Copy over centered XYZ and the molecular vectors file
    centeredfile = gnddir.glob('*center*').__next__()  # Slightly hacky
    shutil.copy(centeredfile, xesdir / centeredfile.name)
    if test_phase:
        high_occ_beta = 42
    else:
        shutil.copy(gnddir / (compoundname + '.movecs'), xesdir)
        # Set and finalize template vals in input.nw
        high_occ_beta = get_highest_occupied_beta_movec(gnddir / 'output.out')
    # check for heavier atoms to replace with ECP
    heavy_atoms = check_for_heavy_atoms(centeredfile, atom)
    if ecp_required(heavy_atoms):
        # replace heavier atoms with ECP
        add_ecp(xesdir / 'input.nw', heavy_atoms)
    # Increase charge by 1
    charge = int(get_template_var(xesdir / 'input.nw', 'CHARGE')) + 1
    mult = basic_multiplicity_from_atoms(xesdir / centeredfile.name)
    geometry_file = centeredfile.name
    set_template_vars(xesdir / 'input.nw', [('GEOMETRY_FILE', geometry_file),
                                            ('CHARGE', charge),
                                            ('MULT', mult),
                                            ('HIGHEST_OCCUPIED_BETA',
                                             high_occ_beta)])
    finalize_template_vars(xesdir / 'input.nw')
    if test_phase:
        return 0
    else:
        # Run nwchem for xes calc
        return run_nwchem_job(xesdir / 'input.nw', xesdir / 'output.out',
                              numcores, mpi_path=mpi_path)


def run_esp_calculation(compoundname, workdir, outdir, numcores, test_phase,
                        atom, mpi_path=None):
    """Run charge calculation."""
    compounddir = workdir / compoundname

    print("Starting ESP Charge Calculation for {}".format(compoundname))

    gnddir = compounddir / 'gndstate'
    espdir = compounddir / 'esp'
    # Copy over optimized and centered XYZ from grnstate calculation
    filename = '{}_optimized_centered.xyz'.format(compoundname)
    shutil.copyfile(gnddir / filename, espdir / filename)
    centeredfile = espdir.glob('*center*').__next__()

    # check for heavier atoms to replace with ECP
    heavy_atoms = check_for_heavy_atoms(centeredfile, atom)
    if ecp_required(heavy_atoms):
        # replace heavier atoms with ECP
        add_ecp(espdir / 'input.nw', heavy_atoms)
    # Set and finalize template vals in input.nw
    set_template_vars(espdir / 'input.nw', [('GEOMETRY_FILE',
                                             centeredfile.name)])
    finalize_template_vars(espdir / 'input.nw')

    if test_phase:
        pass
    else:
        # Call nwchem for gnd state calculation
        exitcode = run_nwchem_job(espdir / 'input.nw', espdir / 'output.out',
                                  numcores, mpi_path=mpi_path)
        assert exitcode == 0, "NWChem call on esp charge calculation " + \
            "step returned exitcode {}!".format(exitcode)

        # Collect esp file
        print("Moving esp file to output directory")
        shutil.copy(compounddir / 'esp' / '{}.esp'.format(compoundname),
                    outdir / '{}.esp'.format(compoundname))


def run_structure_through_pipeline(compoundname, workdir, outdir, numcores,
                                   atom, run_esp=False, test_phase=False,
                                   mpi_path=None):
    """Main calulcuation pipeline."""
    compounddir = workdir / compoundname

    # Run geometry optimization
    
    exitcode = run_geometry_optimization(compoundname, compounddir,
                                         numcores, test_phase,
                                         mpi_path=mpi_path)
    assert exitcode == 0, "NWChem call on geometry optimization step " + \
                          "returned exitcode {}!".format(exitcode)
    
    # Run ground state calculation
    exitcode = run_gnd_state_calculation(compoundname, compounddir,
                                         numcores, test_phase, atom,
                                         mpi_path=mpi_path)
    assert exitcode == 0, "NWChem call on gnd state calculation step " + \
                          "returned exitcode {}!".format(exitcode)

    # Run XANES calculation
    exitcode = run_xanes_calculation(compoundname, compounddir,
                                     numcores, test_phase, atom,
                                     mpi_path=mpi_path)
    assert exitcode == 0, "NWChem call on xanes calculation step " + \
                          "returned exitcode {}!".format(exitcode)

    # Run XES calculation
    """
    exitcode = run_xes_calculation(compoundname, compounddir,
                                   numcores, test_phase, atom,
                                   mpi_path=mpi_path)
    assert exitcode == 0, "NWChem call on xes calculation step " + \
                          "returned exitcode {}!".format(exitcode)
    """
    # Run ESP
    if run_esp:
        run_esp_calculation(compoundname, compounddir, outdir, numcores,
                            test_phase, atom, mpi_path=mpi_path)
    else:
        pass

    if test_phase:
        pass
    else:
        # Extract dat from XANES output
        # TODO: make these function calls within python rather than a shell
        print("Extracting XANES spectrum for {}.".format(compoundname))
        subprocess.run(['python', 'ToolScripts/nw_spectrum_xanes.py', '-x',
                        '-i', (compounddir / 'xanes' / 'output.out').resolve(),
                        '-o', (compounddir / 'xanes' / 'xanes.dat').resolve()])

        # Extract dat from XES output
        print("Extracting XES spectrum for {}.".format(compoundname))
        subprocess.run(['python', 'ToolScripts/nw_spectrum_xes.py', '-x', '-i',
                        (compounddir / 'xescalc' / 'output.out').resolve(),
                        '-o', (compounddir / 'xescalc' / 'xes.dat').resolve()])

        # Collect dats
        print("Moving spectrum dat files to output directory.")
        shutil.copy(compounddir / 'xanes' / 'xanes.dat',
                    outdir / '{}_xanes.dat'.format(compoundname))
        shutil.copy(compounddir / 'xescalc' / 'xes.dat',
                    outdir / '{}_xes.dat'.format(compoundname))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a single structure ' +
                                     'through pipeline (run WITHIN JOB)')
    parser.add_argument('compoundname', action='store', type=str)
    parser.add_argument('workdir', action='store', type=str)
    parser.add_argument('outdir', action='store', type=str)
    parser.add_argument('cores', action='store', type=int)
    parser.add_argument('atom', action='store', type=str)
    parser.add_argument('-t', '--test', action='store', dest='test',
                        type=bool, default=False,
                        help="Specify whether in testing phase or not.")
    parser.add_argument('-mpi', '--mpipath', action='store', dest='mpi_path',
                        type=str, default='',
                        help="Specify mpi path (for use on Hyak)")

    args = parser.parse_args()
    COMPOUND_NAME = args.compoundname
    WORK_DIR = Path(args.workdir).resolve()
    OUT_DIR = Path(args.outdir).resolve()
    MPI_PATH = Path(args.mpi_path).resolve()
    CORES = args.cores
    ATOM = args.atom
    test_phase = args.test

    run_esp = False  # todo -- make this better

    run_structure_through_pipeline(COMPOUND_NAME, WORK_DIR, OUT_DIR, CORES,
                                   ATOM, run_esp=run_esp, mpi_path=MPI_PATH,
                                   test_phase=test_phase)
