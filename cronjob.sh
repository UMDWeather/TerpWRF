#!/bin/bash
# cronjob.sh
# test to see if this fixes problem
# C. Martin - 12/13/15
source ~wrf/.bashrc

cd /home/wrf/scripts

module load mpi

python cronjob.py

