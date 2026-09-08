import polars as pl
import numpy as np
import math
import sys


min_cov = int(sys.argv[1])
min_samples  = float(sys.argv[2] )
parquet_dir = sys.argv[3] 
out_dir = sys.argv[4] 

print("## -- Scanning parquet files before collecting...")

## scan file
lf = pl.scan_parquet(parquet_dir+"chr*_total_matrix.parquet",   include_file_paths="file") #, allow_missing_columns=True


## Fix columns & calculate thresholds
lf = lf.with_columns(
    pl.col("file").str.extract(r"([^/]+)_total_matrix\.parquet$", 1).alias("chrom")
)

## Fix columns & calculate thresholds
sample_cols = [c for c in lf.schema.keys() if c not in ("start", "chrom", "file")]
n_samples = len(sample_cols)
min_required = math.ceil(min_samples * n_samples)  # at least this many samples must be >= MIN_COUNT


# # Ensure not string

lf_num = lf.with_columns(
    pl.all().exclude(["start", "chrom", "file"]).cast(pl.Int64, strict=False)
)

print("## -- Filtering parquet files...")
## Per CPG keep samples with total >= min_cov in at least min_samples% of samples
# (boolean-per-sample list of expressions and sum horizontally (row-wise) )
ge_mask_exprs = [pl.col(c) >= min_cov for c in sample_cols]


# Build row-wise boolean checks on the coerced columns
ge_mask_exprs = [(pl.col(c) >= min_cov) for c in sample_cols]

## Filter
filtered = (
    lf_num
    .with_columns([
        pl.sum_horizontal(ge_mask_exprs).alias("n_ge"),   # number of samples meeting the threshold per CpG
        (pl.col("chrom") + pl.lit(":") + pl.col("start").cast(pl.Utf8)).alias("cpg_id")
    ])
    .filter(pl.col("n_ge") >= min_required)  # keep CpGs passing 70%
    .select(["cpg_id"] + sample_cols)   # keep cpg + original sample columns
)

print("## -- Collecting & saving...")

filtered.sink_parquet(out_dir+"all_total_matrix_filt.parquet")


print("Complete!")
