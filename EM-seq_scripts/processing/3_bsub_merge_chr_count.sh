#!/bin/bash
# -*- coding: utf-8 -*-
# BSUB -o /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/output_logs/bsub_mergeCHR-%J 
# BSUB -e /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/error_logs/bsub_mergeCHR-%J 
# BSUB -n 1
# BSUB -M 150000
# BSUB -R 'select[mem>150000] rusage[mem=150000]'
# BSUB -q yesterday


## -- Set up
## Parquet dir should contain `all_total_matrix_filt.parquet` which will determine which CpGs to keep
SCRIPT_PATH=/nfs/users/nfs_h/hw12/METHYL/0_pipeline/0_processing/merge_across_chr_count.py

PARQUET_DIR=/lustre/scratch125/cellgen/behjati/project_folders/wilms_EMSeq/data/per_chr/
OUT_DIR=/lustre/scratch125/cellgen/behjati/project_folders/wilms_EMSeq/data/


## -- Conda env
source /software/cellgen/team274/miniconda3/etc/profile.d/conda.sh
conda activate meth_pipe_v2

## -- Run for single chromosome
python $SCRIPT_PATH $PARQUET_DIR $OUT_DIR


# to run:
# # # bsub -G team274 < ./3_bsub_merge_chr_count.sh

