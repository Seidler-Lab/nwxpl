# Written by Chat-GPT

import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# find paths to input files in current directory
nw_path = None
for file in os.listdir(script_dir):
    if file.endswith(".nw"):
        nw_path = os.path.abspath(file)

if nw_path is None:
    print("Error: Could not find input files in current directory.")
    os._exit(1)

with open(nw_path, "r") as f:
    nw_contents = f.readlines()

for line in nw_contents:
    if "load" in line:
        xyz_path = line.split()[1]
        break 

# read in atom positions from xyz file
with open(xyz_path, 'r') as xyz_file:
    atom_lines = xyz_file.readlines()[2:]  # skip first two lines
    atom_positions = []
    for line in atom_lines:
        symbol, x, y, z = line.split()
        atom_positions.append(f"{symbol} {x} {y} {z}\n")

# edit nw file to replace geometry section with atom positions
with open(nw_path, 'r') as nw_file:
    nw_lines = nw_file.readlines()
    geometry_start = None
    geometry_end = None
    for i, line in enumerate(nw_lines):
        if line.startswith("geometry"):
            geometry_start = i + 1  # skip over "geometry" line
        elif line.startswith("end"):
            geometry_end = i
            break
    if geometry_start is not None and geometry_end is not None:
        new_nw_lines = nw_lines[:geometry_start] + atom_positions + nw_lines[geometry_end:]
    else:
        print("Error: Could not find 'geometry' and 'end' lines in input file.")
        os._exit(1)

# overwrite original nw file with updated version
with open(nw_path, 'w') as nw_file:
    nw_file.writelines(new_nw_lines)
