# !/usr/bin/env python

# To run, in terminal, use:
# python do_phase.py 1 2
# to run phase 1 for group 2 (i.e. list2.txt)
# or with heavy atom ecp template use
# python do_phase.py 4 Br -heavyatom Br 
# i.e. listBr.txt for phase 4

import subprocess
import argparse

# Run a single phase
def run_phase(compound, phase, replaceheavy):
	heavyflag = replaceheavy ? '-w' : ''

	if phase == 1:
		print("\n Starting Phase 1 Calculations: Optimizing Geometry \n")
		if replaceheavy:
			subprocess.call(['python', 'PythonScripts/xes_i.py', compound, '0'])
		else:
			subprocess.call(['python', 'PythonScripts/xes_i.py', compound, '0', '-w'])


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Script to perform a calculation phase')
	parser.add_argument('structname', action='store', type=str)
	parser.add_argument('phase', action='store', type=int)
	parser.add_argument('-w', action='store_true')
	args = parser.parse_args()
	STRUCT_NAME = args.structname
	PHASE = args.phase
	REPLACE_HEAVY = args.w



	if PHASE == 1:
		print("\n Starting Phase I Calculations: Optimizing Geometry \n")
		try:
			COMPOUND = line.replace('\n','').replace('\r','')
			if HEAVYATOM is None:
				subprocess.call(['python', 'PythonScripts/xes_i.py', COMPOUND, '0'])
			else:
				subprocess.call(['python', 'PythonScripts/xes_i.py', COMPOUND, '0', '-heavyatom', HEAVYATOM])
			print("\n")
		finally:
			file.close()
	elif PHASE == 2:
		print("\n Starting Phase II Calculations: Gnd State and XANES \n")
		try:
			file = open('list{}.txt'.format(GROUP), 'r')
			for line in file:
				COMPOUND = line.replace('\n','').replace('\r','')
				if HEAVYATOM is None:
					subprocess.call(['python', 'PythonScripts/xes_ii.py', COMPOUND, '0'])
					subprocess.call(['python', 'PythonScripts/xanes_ii.py', COMPOUND, '0'])
				else:
					subprocess.call(['python', 'PythonScripts/xes_ii.py', COMPOUND, '0', '-heavyatom', HEAVYATOM])
					subprocess.call(['python', 'PythonScripts/xanes_ii.py', COMPOUND, '0', '-heavyatom', HEAVYATOM])
				print("\n") 
		finally:
			file.close()
	elif PHASE == 3:
		print("\n Starting Phase III Calculations: XES spectra \n")
		try:
			file = open('list{}.txt'.format(GROUP), 'r')
			for line in file:
				COMPOUND = line.replace('\n','').replace('\r','')
				if HEAVYATOM is None:
					subprocess.call(['python', 'PythonScripts/xes_iii.py', COMPOUND, '0'])
				else:
					subprocess.call(['python', 'PythonScripts/xes_iii.py', COMPOUND, '0', '-heavyatom', HEAVYATOM])
				print("\n") 
		finally:
			file.close()
	elif PHASE == 4:
		print("\n Starting Phase IV Calculations: XES and XANES output -> dat")
		try:
			file = open('list{}.txt'.format(GROUP), 'r')
			for line in file:
				COMPOUND = line.replace('\n','').replace('\r','')
				subprocess.call(['python', 'PythonScripts/xes_iv.py', COMPOUND])
				subprocess.call(['python', 'PythonScripts/xanes_iv.py', COMPOUND])
				print("\n") 
		finally:
			file.close()
	elif PHASE == 5:
		file = open('list{}.txt'.format(GROUP), 'r')
		for line in file:
			COMPOUND = line.replace('\n','').replace('\r','')
			subprocess.call(['cp', '{}/xanes/{}.dat'.format(COMPOUND, COMPOUND), '../XANES/'])
			subprocess.call(['cp', '{}/xescalc/{}.dat'.format(COMPOUND, COMPOUND), '../XES/'])

	else:
		print("Incorrect phase number. Must be '1', '2', '3','4', or '5'")
		print("Phase I Calculations: Optimizing Geometry")
		print("Phase II Calculations: Gnd State and XANES spectra")
		print("Phase III Calculations: XES spectra and XANES output -> dat")
		print("Phase IV Calculations: XES output -> dat")
		print("Phase V Calculations: Move dat files")


