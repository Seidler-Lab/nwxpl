#!/usr/bin/env python3

import os
import subprocess

from NWChemScripting import *

import argparse
parser = argparse.ArgumentParser(description='Script to convert XANES .out to .dat')
parser.add_argument('compound', action='store')
args = parser.parse_args()
COMPOUND = args.compound

print("{} XANES out->dat".format(COMPOUND))

if __name__ == '__main__':

    os.chdir('{}'.format(COMPOUND))
    with open('xanes/output-xanes.out', 'r') as xanesoutput:
        with open('xanes/{}.dat'.format(COMPOUND), 'w') as xanesdat:
            #proc = subprocess.Popen(['../PythonScripts/NWChemScripting/nw_spectrum_vtc_wespecmod.py', '-x'], stdin=xesoutput, stdout=xesdat)
            #subprocess.run(['../PythonScripts/NWChemScripting/nw_spectrum_total.py', '-x', 'stdin=xanesoutput', 'stdout=xanesdat'])
            #proc = subprocess.Popen(['../PythonScripts/NWChemScripting/nw_spectrum_total.py', '-x'], stdin=xanesoutput, stdout=xanesdat)
            proc = subprocess.Popen(['../PythonScripts/NWChemScripting/nw_spectrum.py', '-x'], stdin=xanesoutput, stdout=xanesdat)
