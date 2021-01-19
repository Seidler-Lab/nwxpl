# Useful functions for use in pipeline scripts
# Written by Vikram Kashyap 2021 adapted from 

import os
import sys
from subprocess import run
import re
import pathlib
from pathlib import Path

# Run an nwchem job, write output to file, and return errorcode
def run_nwchem_job(jobfile, outfile, cores):
	completedjob = run(['/usr/lusers/vkashyap/swtest/usr/lib64/mpich-3.2/bin/mpirun', '-n', str(cores),
		'nwchem', str(jobfile.name)],
		cwd=jobfile.parent,
		capture_output=True)
	with open(outfile,'wb') as f:
		f.write(completedjob.stdout)
	return completedjob.returncode

# Queue a job and return error code of queueing call
def start_batch_job(jobfile='job.run'):
	return run(['sbatch', jobfile]).returncode

# Replace pairs of text in a file
def replace_text_in_file(infile, pairs):
	# Read in the file
	with open(infile, 'r') as f:
		filedata = f.read()
	# Replace the target strings
	for pair in pairs:
		filedata = filedata.replace(pair[0], pair[1])
	# Write the file out again
	with open(infile, 'w') as f:
		f.write(filedata)


# Get the current value set for a template variable
# Returns a string
def get_template_var(tfile, tag):
	with open(tfile) as f:
		data = f.read()
	match = re.search('\[{}=([^]]*)\]'.format(tag), data)
	if match is not None:
		return match.groups()[0]
	else:
		return None

# Set the values for variable in a template
# Pass var tags and values as list of tuples (tag, val)
# Remember to finalize all values before using file
def set_template_vars(tfile, pairs):
	with open(tfile) as f:
		data = f.read()
	for pair in pairs:
		# Search and replace instances of var starting at end of file to avoid index changes
		tvar_instances = list(re.finditer('\[{}=([^]]*)\]'.format(pair[0]), data))
		if tvar_instances is None:
			raise Exception("Template Tag Not Found: File {}, Tag {}".format(str(tfile), pair[0]))
		for tvar in reversed(tvar_instances):
			data = data[:tvar.start()] + "[{}={}]".format(pair[0], pair[1]) + data[tvar.end():]

	with open(tfile,'w') as f:
		f.write(data)

# Finalize template values in a file by replace variable expression with value
def finalize_template_vars(tfile):
	with open(tfile) as f:
		data = f.read()
	# Search and replace var tags starting at end of file to avoid index errors 
	tvars = list(re.finditer('\[([^]]+)=([^]]*)\]',data))
	for tvar in reversed(tvars):
		val = tvar.groups()[1]
		data = data[:tvar.start()] + val + data[tvar.end():]

	with open(tfile,'w') as f:
		f.write(data)

# Get electron multiplicity from atoms formatted like output from read_xyz
def basic_multiplicity_from_atoms(atoms):
        return 1
        import periodictable
        electrons = 0
        for a in atoms:
                electrons += periodictable.__getattribute__(a).number
        print('{} electrons, which means basic multiplicity {}'.format(electrons, electrons % 2 + 1))
        return electrons % 2 + 1

# Read XYZ and parse data into lists
def read_xyz(file):
        with open(file, 'r') as f:
                lines = f.readlines()
                atoms = []
                coords = []
                for l in lines[2:]: #XYZ files must have two header rows
                        split = l.split()
                        atoms.append(split[0])
                        coords.append([float(x) for x in split[1:]])
                assert len(atoms) == len(coords), 'Something went wrong, len of atoms doesnt equal length of coords'
        return atoms, coords


# Returns number of highest xyz file in a directory
def find_highest_number_xyz_file(directory):
	maxnum = 0
	for filename in directory.glob('*.xyz'):
		num = int(re.split(r'[-.]',filename.name)[1])
		if num>maxnum:
			maxnum = num
	return maxnum


# Take the path of an XYZ, center it on the coordinate of the nth listed atom, and return the new filename
def center_xyz(infile, n):
	with open(infile) as f:
		for i, line in enumerate(f):
			if i == n+2:	# Targetline is numbered after the first 2 metadata lines
				centercoords = list(map(float,line.split()[1:4]))
		f.seek(0)

		outfile = infile.parent/(infile.stem+'_centered.xyz')
		with open(outfile, 'w') as nf:
			nf.write(f.readline())
			nf.write(f.readline())
			while True:
				coords = f.readline().split()
				if len(coords) != 4: break
				for c in range(1,4):
					coords[c] = float(coords[c])-centercoords[c-1]	
				nf.write('{}  {:>15.5f}{:>15.5f}{:>15.5f}\n'.format(*coords))
			return outfile

# Find energy cut
def find_ecut(infile):
	# Read optimized geometry file
	with open(infile) as f:
		for line in f:
			# find first line the looks something like 'Vector	1  Occ=1.000000D+00  E=-8.888006D+01'
			if 'Vector    1' in line:
				ecut = line.split('E=')[1].replace('\n','').replace('D','E')
				ecut = round(float(ecut), 1) + 1
				#print("Energy cut at {} hartrees".format(ecut))
				return ecut
	# No ecut found. Throw error.
	raise SystemExit('Error: No ecut found. Exiting XANES calculation.')

# Retrieve highest occupied beta movec from groundstate calc output
def get_highest_occupied_beta_movec(infile):
	with open(infile, 'r') as f:
		content = f.read()
		betaorbitalsindex = content.index('DFT Final Beta Molecular Orbital Analysis')
		betaorbitals = content[betaorbitalsindex:]
		occ0index = betaorbitals.index('Occ=0')
		f.seek(betaorbitalsindex + occ0index)
		vectorindex = betaorbitals.index('Vector', occ0index - 14, occ0index)
		f.seek(betaorbitalsindex + vectorindex)
		r = f.readline()
		return int(r.split()[1]) - 1
