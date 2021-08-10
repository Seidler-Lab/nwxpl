#!/usr/bin/env python

import shutil
from pathlib import Path


from nwxutils import *


if __name__ == '__main__':

    workdir = '/gscratch/stf/stetef/work/'
    inputdir = '/usr/lusers/stetef/phosphorus/nwxpl/ScriptedCalculations/input_xyz/'
    listname = '3.list'

    WORK_DIR = Path(workdir).resolve()
    OUT_DIR = Path(outdir).resolve()
    LIST_FILENAME = Path(listname).resolve()

    try:
        with open(LIST_FILENAME, 'r') as f:
            structurelist = [Path(line.strip()) for line in f]
    except:
        print("Unable to open structure list file: {}".format(LIST_FILENAME))
        sys.exit(1)

    for structfilename in structurelist:
        compoundname = structfilename.stem

        compounddir = WORK_DIR/compoundname

        geomdir = compounddir/'geometryoptimize'
        # Copy over optimized XYZ and center it
        highestxyznum = find_highest_number_xyz_file(geomdir/'xyzfiles')
        highestxyzpath = geomdir/'xyzfiles'/'{}-{:03}.xyz'.format(compoundname, highestxyznum - 1)
        inputpath = inputdir/'{}.xyz'.format(compoundname)

        shutil.copyfile(highestxyzpath, inputpath)
