#!/bin/bash
scratch=$(grep myscratch .env | cut -d '=' -f2)
work=$(grep work .env | cut -d '=' -f2)
email=$(grep email .env | cut -d '=' -f2)
mpidest=$(grep mpidest .env | cut -d '=' -f2)
echo Working directory: $work
echo Scratch directory: $scratch
echo Out directory: ~/phosphorus/out
echo MPI destination: $mpidest
echo Email: $email
module load contrib/python_3.8/3.8
#python modify_settings.py -e $email -p $mpidest
python nwxpl.py -i 2.list -b basisfiles/Pbasis.bas -w $work -s $scratch -o ~/phosphorus/out
