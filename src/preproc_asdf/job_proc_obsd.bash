#!/bin/bash

#PBS -A GEO111
#PBS -N Proc_obsd
#PBS -j oe
#PBS -o proc_obsd.$PBS_JOBID.o

#PBS -l walltime=10:00:00
#PBS -l nodes=1

cd $PBS_O_WORKDIR

python process_observed.py
