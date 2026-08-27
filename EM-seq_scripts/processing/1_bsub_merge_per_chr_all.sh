#!/bin/bash
# -*- coding: utf-8 -*-

## -- Set up
SCRIPT_PATH=/nfs/users/nfs_h/hw12/METHYL/0_pipeline/0_processing/merge_per_chr.py
VAL="total" 
CHR_TO_MERGE=(chr1 chr2 chr3 chr4 chr5 chr6 chr7 chr8 chr9 chr10 chr11 chr12 chr13 chr14 chr15 chr16 chr17 chr18 chr19 chr20 chr21 chr22) ## 160000 GB

COV_DIR=/lustre/scratch124/casm/pipelines/nst_links/live/3874/
#COV_DIR=/lustre/scratch124/casm/pipelines/nst_links/live/3889/
TMP_DIR=/lustre/scratch125/cellgen/behjati/hw12/wilms_EMseq/0_merging_tmp/
OUT_DIR=/lustre/scratch125/cellgen/behjati/project_folders/wilms_EMSeq/data/per_chr/


for CHR in "${CHR_TO_MERGE[@]}"; do

  job_id=$(bsub -G team274 <<EOF | grep -oE "[0-9]+"
#!/bin/bash
#BSUB -J "mergeCOV_${CHR}"
#BSUB -o /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/output_logs/bsub_mergeCOV_${CHR}-%J 
#BSUB -e /lustre/scratch125/cellgen/behjati/hw12/bsub_logs/error_logs/bsub_mergeCOV_${CHR}-%J 
#BSUB -n 1
#BSUB -M 400000
#BSUB -R 'select[mem>400000] rusage[mem=400000]'
#BSUB -q yesterday



## -- Conda env
source /software/cellgen/team274/miniconda3/etc/profile.d/conda.sh
conda activate meth_pipe

## -- Run for single chromosome
python $SCRIPT_PATH ${CHR} $VAL $COV_DIR $TMP_DIR $OUT_DIR 
echo "Finished"
EOF
  )

  if [[ -z "${job_id}" ]]; then
    echo "Failed to submit tar job for ${CHR}." >&2
  else
    echo ".Cov merge job ${job_id} for ${CHR} submitted."
  fi

done

