#!/bin/bash
module load contrib/python_3.8/3.8
python nwxpl.py -i $1 -b basisfiles/Pbasis.bas -w ~/phosforus/work/ -s /gscratch/stf/vkashyap -o ~/phosforus/out
