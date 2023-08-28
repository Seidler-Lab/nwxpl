#!/bin/bash
scratch=$(grep SCRATCH_DIR= .env | cut -d '=' -f2)
work=$(grep WORK_DIR= .env | cut -d '=' -f2)
out=$(grep OUT_DIR= .env | cut -d '=' -f2)
email=$(grep EMAIL= .env | cut -d '=' -f2)
echo Working directory: $work
echo Scratch directory: $scratch
echo Out directory: $out
echo Email: $email

python -c 'import sys; print(f"Using python version {sys.version_info[:]}")'
#python nwxpl.py --inlist 1.list --basefile ../basisfiles/sapporo-qzp-2012.1.nw \
#--workdir $work --scratchdir $scratch --outputdir $out --atom O --charge 0
python nwxpl.py --inlist 3.list --basefile ../basisfiles/sapporo-qzp-2012.2.nw \
--workdir $work --scratchdir $scratch --outputdir $out --atom S --charge 0
