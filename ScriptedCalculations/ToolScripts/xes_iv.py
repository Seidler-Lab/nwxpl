#!/usr/bin/env python3

import os
import subprocess

from NWChemScripting import *

import argparse
parser = argparse.ArgumentParser(description='Script to convert XANES .out to .dat')
parser.add_argument('compound', action='store')
args = parser.parse_args()
COMPOUND = args.compound

print("{} XES out->dat".format(COMPOUND))

if __name__ == '__main__':
    os.chdir('{}'.format(COMPOUND))
    with open('xescalc/output-vtc.out', 'r') as xesoutput:
        with open('xescalc/{}.dat'.format(COMPOUND), 'w') as xesdat:
            #proc = subprocess.Popen(['../PythonScripts/NWChemScripting/nw_spectrum_vtc_wespecmod.py', '-x'], stdin=xesoutput, stdout=xesdat)
            proc = subprocess.Popen(['../PythonScripts/NWChemScripting/nw_spectrum_xes.py', '-x'], stdin=xesoutput, stdout=xesdat)
