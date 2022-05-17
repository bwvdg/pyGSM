#!/usr/bin/env bash

OMP_NUM_THREADS=8
MKL_NUM_THREADS=8
BAGEL_NUM_THREADS=8

gsm -xyzfile path_inp.xyz -restart_file path_inp.xyz -mode DE_GSM -package BAGEL \
  -lot_inp_file "$(pwd)/bagel.json" -bagel_runpath "$(pwd)/bagel.sh" \
  -reactant_geom_fixed -product_geom_fixed -mp_cores $OMP_NUM_THREADS -num_nodes 30 -max_opt_steps 3 \
  -CONV_TOL 0.003 -max_gsm_iters 40 
