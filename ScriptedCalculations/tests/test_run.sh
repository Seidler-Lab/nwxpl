#!/bin/bash
scratch=$(grep SCRATCH_DIR= test_env.env | cut -d '=' -f2)
work=$(grep WORK_DIR= test_env.env | cut -d '=' -f2)
out=$(grep OUT_DIR= test_env.env | cut -d '=' -f2)
email=$(grep EMAIL= test_env.env | cut -d '=' -f2)
echo Working directory: $work
echo Scratch directory: $scratch
echo Out directory: $out
echo Email: $email
#module load contrib/python_3.8/3.8
python test_nwxpl.py -i 1.list -b ../../basisfiles/basis.bas -w $work -s $scratch -o $out -a Ca
