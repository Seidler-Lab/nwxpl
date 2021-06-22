"""
Useful functions for use in pipeline scripts.

Written by Vikram Kashyap 2021
"""

import re
import subprocess
from subprocess import run
import warnings


def run_nwchem_job(jobfile, outfile, cores):
    """Run an nwchem job, write output to file, and return errorcode."""
    completedjob = run(['/gscratch/home/stetef/mpich-3.2/bin/mpirun', '-n', str(cores),
                        'nwchem', str(jobfile.name)],
                       cwd=jobfile.parent,
                       capture_output=True)
    with open(outfile, 'wb') as f:
        f.write(completedjob.stdout)
    return completedjob.returncode


def start_batch_job(jobfile='job.run'):
    """Queue a job and return error code of queueing call."""
    return subprocess.call(['sbatch', jobfile])


def replace_text_in_file(infile, pairs):
    """Replace pairs of text in a file."""
    # Read in the file
    with open(infile, 'r') as f:
        filedata = f.read()
    # Replace the target strings
    for pair in pairs:
        filedata = filedata.replace(pair[0], pair[1])
    # Write the file out again
    with open(infile, 'w') as f:
        f.write(filedata)


def get_template_var(tfile, tag):
    """Get the current value set for a template variable. Returns a string."""
    with open(tfile) as f:
        data = f.read()
    match = re.search('\[{}=([^]]*)\]'.format(tag), data)
    if match is not None:
        return match.groups()[0]
    else:
        return None


def set_template_vars(tfile, pairs):
    """
    Set the values for variable in a template.

    Pass var tags and values as list of tuples (tag, val)
    Remember to finalize all values before using file.
    """
    with open(tfile) as f:
        data = f.read()
    for pair in pairs:
        # Search and replace instances of var starting at end of file
        # to avoid index changes
        tvar_instances = list(re.finditer('\[{}=([^]]*)\]'.format(
            pair[0]), data))
        if tvar_instances is None:
            raise Exception("Template Tag Not Found: File {}, Tag {}".format(
                str(tfile), pair[0]))
        for tvar in reversed(tvar_instances):
            data = data[:tvar.start()] + "[{}={}]".format(pair[0], pair[1]) \
                + data[tvar.end():]
    with open(tfile, 'w') as f:
        f.write(data)


def finalize_template_vars(tfile):
    """
    Finalize template values in a file.

    Repalces variable expression with value.
    """
    with open(tfile) as f:
        data = f.read()
    # Search and replace var tags starting at end of file to avoid index errors
    tvars = list(re.finditer('\[([^]]+)=([^]]*)\]', data))
    for tvar in reversed(tvars):
        val = tvar.groups()[1]
        data = data[:tvar.start()] + val + data[tvar.end():]
    with open(tfile, 'w') as f:
        f.write(data)


def basic_multiplicity_from_atoms(atoms):
    """
    Get electron multiplicity from atoms.

    Formatted like output from read_xyz.
    """
    return 1
    try:
        import periodictable
        electrons = 0
        for a in atoms:
            electrons += periodictable.__getattribute__(a).number
        print('{} electrons, which means basic multiplicity {}'.format(
            electrons, electrons % 2 + 1))
        return electrons % 2 + 1
    except ModuleNotFoundError:
        warnings.warn("Can't import 'periodictable'")
    finally:
        print("Returning multiplicity of 1.")
        return 1


def read_xyz(file):
    """Read XYZ and parse data into lists."""
    with open(file, 'r') as f:
        lines = f.readlines()
        atoms = []
        coords = []
        for l in lines[2:]:  # XYZ files must have two header rows
            split = l.split()
            atoms.append(split[0])
            coords.append([float(x) for x in split[1:]])
        assert len(atoms) == len(coords), 'Something went wrong, \
            len of atoms doesnt equal length of coords'
    return atoms, coords


def find_highest_number_xyz_file(directory):
    """Return number of highest xyz file in a directory."""
    maxnum = 0
    for filename in directory.glob('*.xyz'):
        num = int(re.split(r'[-.]', filename.name)[1])
        if num > maxnum:
            maxnum = num
    return maxnum


def center_xyz(infile, n):
    """
    Take the path of an XYZ and center it on the coordinate of the nth atom.

    Returns the new filename.
    """
    with open(infile) as f:
        for i, line in enumerate(f):
            # Targetline is numbered after the first 2 metadata lines
            if i == n + 2:
                centercoords = list(map(float, line.split()[1:4]))
        f.seek(0)

        outfile = infile.parent / (infile.stem + '_centered.xyz')
        with open(outfile, 'w') as nf:
            nf.write(f.readline())
            nf.write(f.readline())
            while True:
                coords = f.readline().split()
                if len(coords) != 4:
                    break
                for c in range(1, 4):
                    coords[c] = float(coords[c]) - centercoords[c - 1]
                nf.write('{}  {:>15.5f}{:>15.5f}{:>15.5f}\n'.format(*coords))
            return outfile


def find_ecut(infile):
    """Find energy cut for XANES calculation."""
    # Read optimized geometry file
    with open(infile) as f:
        for line in f:
            # Find first line the looks something like
            # 'Vector    1  Occ=1.000000D+00  E=-8.888006D+01'
            if 'Vector    1' in line:
                ecut = line.split('E=')[1].replace('\n', '').replace('D', 'E')
                ecut = round(float(ecut), 1) + 1
                # print("Energy cut at {} hartrees".format(ecut))
                return ecut
    # No ecut found. Throw error.
    raise SystemExit('Error: No ecut found. Exiting XANES calculation.')


def get_highest_occupied_beta_movec(infile):
    """Retrieve highest occupied beta movec from groundstate calc output."""
    with open(infile, 'r') as f:
        content = f.read()
        borbitalsindex = content.index('DFT Final Beta Molc Orbital Analysis')
        betaorbitals = content[borbitalsindex:]
        occ0index = betaorbitals.index('Occ=0')
        f.seek(borbitalsindex + occ0index)
        vectorindex = betaorbitals.index('Vector', occ0index - 14, occ0index)
        f.seek(borbitalsindex + vectorindex)
        r = f.readline()
        return int(r.split()[1]) - 1


def check_for_heavy_atoms(infile):
    """Check xyz file for any atoms larger than target atom."""
    heavy_atoms = []
    with open(infile, 'r') as f:
        data = f.read()
    check_these_atoms = ['Br', 'Cl']
    for atom in check_these_atoms:
        if atom in data:
            heavy_atoms.append(atom)
    return heavy_atoms


def ecp_required(heavy_atoms):
    """Determine if ecp required by checking if heavy atom list is empty."""
    isempty = not heavy_atoms
    return not isempty


def add_ecp(infile, heavy_atoms, ecp="Stuttgart RLC ECP"):
    """Add ECP to input file for the specified heavy atoms."""
    # add except for heavy atoms for basis
    ecp_template = "HEAVYATOM library {}".format(ecp)
    ecp_block_template = 'ecp\n  {}\nend\n'.format(ecp_template)
    with open(infile, 'r') as f:
        filedata = f.read()
    filedata = re.sub("except P",
                      "except P HEAVYATOM\n{}".format(ecp_template), filedata)
    filedata = re.sub("charge",
                      '{}\ncharge'.format(ecp_block_template), filedata)
    filedata = re.sub("HEAVYATOM", ' '.join(heavy_atoms), filedata)
    with open(infile, 'w') as f:
        f.write(filedata)
    return
