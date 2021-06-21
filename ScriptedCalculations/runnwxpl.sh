#!/bin/bash
myPATH=$(grep myPATH .env | cut -d '=' -f2)
email=$(grep email .env | cut -d '=' -f2)
mpidest=$(grep mpidest .env | cut -d '=' -f2)
echo Working directory: $myPATH/
echo Scratch directory: $myPATH/scratch/
echo Out directory: ~/phosphorus/out
echo MPI destination: $mpidest
echo Email: $email
module load contrib/python_3.8/3.8
#python modify_settings.py -e $email -p $mpidest
python nwxpl.py -i 1.list -b basisfiles/Pbasis.bas -w $myPATH/ -s $myPATH/scratch/ -o ~/phosphorus/out
