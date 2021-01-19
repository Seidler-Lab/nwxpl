# Useful functions for use in pipeline scripts

import os
import sys
from subprocess import run
import pathlib
from pathlib import Path

# Run an nwchem job, write output to file, and return errorcode
def run_nwchem_job(jobfile=Path('input.nw'), outfile=Path('output.out'), cores=16):
        completedjob = run(['mpirun', 'nwchem', '-n {}'.format(cores), str(jobfile)], capture_output=True)
	with open(outfile) as f:
		f.write(completedjob.stdout)
	return completedjob.returncode

# Queue a job and return error code of queueing call
def start_batch_job(jobfile='job.run'):
        return run(['sbatch'], jobfile).returncode

# Replace pairs of text in a file
def replace_text_in_file(infile, pairs):
        # Read in the file
        with open(infile, 'r') as file:
                filedata = file.read()

        # Replace the target strings
        for pair in pairs:
                filedata = filedata.replace(pair[0], pair[1])

        # Write the file out again
        with open(infile, 'w') as file:
                file.write(filedata)


# Get the current value set for a template variable
# Returns a string
def get_template_var(tfile, tag):
	with open(tfile) as f:
		data = f.read()
	match = re.search('\[{}=(\w+|)\]'.format(tag), data)
	if match is not None:
		return match.groups()[0]
	else:
		return None

# Set the values for variable in a template
# Pass var tags and values as list of tuples (tag, val)
# Remember to finalize all values before using file
def set_template_var(tfile, pairs):
	with open(tfile) as f:
		data = f.read()
	for pair in pairs:
		match = re.search('\[{}=(\w+|)\]'.format(pair[0]), data)
		if match is None:
			raise Exception("Template Tag Not Found: File {}, Tag {}".format(str(infile), pair[0]))
		varloc = match.start()
		data = data[:match.start()] + "[{}={}]".format(pair[0], pair[1]) + data[match.end():]
	with open(tfile,'w') as f:
		f.write(data)

# Finalize template values in a file by replace variable expression with value
def finalize_template_vars(tfile):
	with open(tfile) as f:
		data = f.read()
	tvars = re.finditer('\[(\w+)=(\w+|)\]',data)
	for tvar in tvars:
		val = tvar.groups()[1]
		data = data[:tvar.start()] + val + data[tvar.end():]
	with open(tfile,'w') as f:
		f.write(data)

# Returns number of highest xyz file in a directory
def find_highest_number_xyz_file(directory):
        maxnum = 0
        for filename in directory.glob(r'(.*?)(\d*)(.xyz)'):
                num = int(re.split('[-.]',filename)[1])
                if num>maxnum:
                        num = maxnum
        return maxnum


# Take the path of an XYZ, center it on the coordinate of the nth listed atom, and return the new filename
def center_xyz(infile, n):
        with open(infile) as f:
                for i, line in enumerate(f):
                        if i == n+2:	# Targetline is numbered after the first 2 metadata lines
                                centercoords = list(map(float,line.split()[1:4]))
                f.seek(0)

                outfile = infile.parent/(infile.stem+'_centered_xyz')
                with open(outfile, 'w') as nf:
                        nf.write(f.readline())
                        nf.write(f.readline())
                        while True:
                                coords = file.readline().split()
                                if len(coords) != 4: break
                                for c in range(1,4):
                                        coords[c] = float(coords[c])-centercoords[c]
                                nf.write('{}  {:>15.5f}{:>15.5f}{:>15.5f}\n'.format(*coords))
                                nf.write('\n')
                return outfile

def find_ecut(infile):
    # Read optimized geometry file
    with open(infile) as f:
        for line in f:
            # find first line the looks something like 'Vector    1  Occ=1.000000D+00  E=-8.888006D+01'
            if 'Vector    1' in line:
                ecut = line.split('E=')[1].replace('\n','').replace('D','E')
                ecut = round(float(ecut), 1) + 1
                #print("Energy cut at {} hartrees".format(ecut))
                return ecut
    # No ecut found. Throw error.
    raise SystemExit('Error: No ecut found. Exiting XANES calculation.')

