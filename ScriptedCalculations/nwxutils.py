"""Useful functions for use in pipeline scripts."""

import re
import subprocess
from subprocess import run
import warnings
from pathlib import Path


PERIODIC_TABLE = \
    ['H',  'He', 'Li', 'Be', 'B',  'C',  'N',  'O',  'F',  'Ne',
     'Na', 'Mg', 'Al', 'Si', 'P',  'S',  'Cl', 'Ar', 'K',  'Ca', 'Sc', 'Ti',
     'V',  'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se',
     'Br', 'Kr', 'Rb', 'Sr', 'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
     'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',  'Xe', 'Cs', 'Ba', 'La', 'Ce',
     'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
     'Lu', 'Hf', 'Ta', 'W',  'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb',
     'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',  'Np', 'Pu',
     'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg',
     'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']


def parse_env(envpath):
    """Parse personal env file."""
    with Path(envpath).open() as f:
        data = f.readlines()
    env = dict()
    for line in data:
        if line.startswith('#') or not line.strip():
            continue  # Ignore comments & blanks
        pair = line.split('=')
        env[pair[0].strip()] = pair[1].strip()
    return env


def run_nwchem_job(jobfile, outfile, cores, mpi_path=None):
    """Run an nwchem job, write output to file, and return errorcode."""
    # Run on Hyak using:
    # completedjob = run([str( (mpi_path/'bin'/'mpirun').resolve() ),
    #                    '-n', str(cores),
    #                    'nwchem', str(jobfile.name)],
    #                   cwd=jobfile.parent,
    #                   capture_output=True)

    # Run on Tahoma using:
    completedjob = run(['mpirun', '-h'])

    """
    completedjob = run(['mpirun', '-n', str(cores), '-ppn', str(cores),
                        '/tahoma/emsls51190/nwchem-exec/nwchem-master',
                        str(jobfile.name)],
                       cwd=jobfile.parent,
                       capture_output=True)
    """
    with open(outfile, 'wb') as f:
        #f.write(completedjob.stdout)
        f.close()
    return 0 #completedjob.returncode


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


def basic_multiplicity_from_atoms(geometryfile):
    """
    Get electron multiplicity from atoms.

    Atoms formatted like output from read_xyz.
    """
    atoms, coords = read_xyz(geometryfile)
    electrons = 0
    for a in atoms:
        electrons += PERIODIC_TABLE.index(a) + 1
    print('{} electrons, which means basic multiplicity {}'.format(
          electrons, electrons % 2 + 1))
    return electrons % 2 + 1


def read_xyz(file):
    """Read XYZ and parse data into lists."""
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        atoms = []
        coords = []
        for l in lines[2:]:  # XYZ files must have two header rows
            split = l.split()
            atoms.append(split[0])
            coords.append([float(x) for x in split[1:]])
        assert len(atoms) == len(coords), 'Something went wrong, \
            len of atoms doesnt equal length of coords'
        f.close()
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
        borbitalsindex = content.index('DFT Final Beta Molec Orbital Analysis')
        betaorbitals = content[borbitalsindex:]
        occ0index = betaorbitals.index('Occ=0')
        f.seek(borbitalsindex + occ0index)
        vectorindex = betaorbitals.index('Vector', occ0index - 14, occ0index)
        f.seek(borbitalsindex + vectorindex)
        r = f.readline()
        return int(r.split()[1]) - 1


def check_for_heavy_atoms(infile, atom):
    """Check xyz file for any atoms larger than target atom."""
    heavy_atoms = []
    with open(infile, 'r') as f:
        data = f.read()
    check_these_atoms = [a for i, a in enumerate(PERIODIC_TABLE)
                         if i > PERIODIC_TABLE.index(atom)]
    for atom in check_these_atoms:
        if atom in data:
            heavy_atoms.append(atom)
    return heavy_atoms


def ecp_required(heavy_atoms):
    """Determine if ecp required by checking if heavy atom list is empty."""
    isempty = not heavy_atoms
    return not isempty


def add_ecp(infile, heavy_atoms, ecp='"Stuttgart RLC ECP"'):
    """Add ECP to input file for the specified heavy atoms."""
    # add except for heavy atoms for basis
    # ecp_template = "HEAVYATOM library {}".format(ecp)

    with open(infile, 'r') as f:
        filedata = f.read()

    # add exception line
    filedata = re.sub("except [COMPOUND=]",
                      "except [COMPOUND=] {}".format(' '.join(heavy_atoms)),
                      filedata)

    # add basis library substitution
    for atom in heavy_atoms:
        filedata = re.sub("# Sapporo", "{} library {}\n# Sapporo".format(atom,
                                                                         ecp),
                          filedata)

    # add ecp block
    ecp_block_template = 'ecp\nend\n'
    filedata = re.sub("task dft",
                      '{}\ntask dft'.format(ecp_block_template), filedata)

    # make ECP block sub here
    for atom in heavy_atoms:
        filedata = re.sub("ecp", "ecp\n  {} library {}".format(atom, ecp),
                          filedata)

    with open(infile, 'w') as f:
        f.write(filedata)
    f.close()
