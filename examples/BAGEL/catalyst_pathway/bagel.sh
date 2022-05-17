#!/bin/bash

export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export BAGEL_NUM_THREADS=4

#source /opt/intel/oneapi/setvars.sh

BAGEL bagel.json


