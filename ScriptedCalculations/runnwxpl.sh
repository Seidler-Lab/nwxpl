#!/bin/bash
scratch=$(grep SCRATCH_DIR= .env | cut -d '=' -f2)
work=$(grep WORK_DIR= .env | cut -d '=' -f2)
out=$(grep OUT_DIR= .env | cut -d '=' -f2)
email=$(grep EMAIL= .env | cut -d '=' -f2)
mpidest=$(grep NWXPL_MPI_PATH= .env | cut -d '=' -f2)
echo Working directory: $work
echo Scratch directory: $scratch
echo Out directory: $out
echo MPI destination: $mpidest
echo Email: $email
module load contrib/python_3.8/3.8
python nwxpl.py -i 2.list -b basisfiles/Pbasis.bas -w $work -s $scratch -o $out
