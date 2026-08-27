#!/bin/bash
# -*- coding: utf-8 -*-
# BSUB -o /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/output_logs/bsub_mergeCHR-%J 
# BSUB -e /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/error_logs/bsub_mergeCHR-%J 
# BSUB -n 1
# BSUB -M 600000
# BSUB -R 'select[mem>600000] rusage[mem=600000]'
# BSUB -q yesterday


## -- Set up
SCRIPT_PATH=/nfs/users/nfs_h/hw12/METHYL/0_pipeline/0_processing/merge_across_chr_total.py

PARQUET_DIR=/lustre/scratch125/cellgen/behjati/project_folders/wilms_EMSeq/data/per_chr/
OUT_DIR=/lustre/scratch125/cellgen/behjati/project_folders/wilms_EMSeq/data/
MIN_COUNT=1 # min coverage - 5
MIN_SAMPLE="0.01" # in at least x% samples - 0.7 (70%)


## -- Conda env
source /software/cellgen/team274/miniconda3/etc/profile.d/conda.sh
conda activate meth_pipe_v2

## -- Run for single chromosome
python $SCRIPT_PATH $MIN_COUNT $MIN_SAMPLE $PARQUET_DIR $OUT_DIR


