import polars as pl
import numpy as np
import math
import sys
import os



parquet_dir = sys.argv[1] 
out_dir = sys.argv[2] 

print("## -- Scanning parquet files before collecting...")


# -- Build key set lazily (no need to collect to Python list)
keys_lf = (
    pl.scan_parquet(os.path.join(out_dir, "all_total_matrix_filt.parquet"))
      .select("cpg_id")
      .unique()
)

# -- Scan all chr parquet files
pattern = os.path.join(parquet_dir, "chr*_meth_count_matrix.parquet")
lf = pl.scan_parquet(pattern, include_file_paths="file")

# STEP 1: create 'chrom'
lf = lf.with_columns(
    pl.col("file").str.extract(r"([^/]+)_meth_count_matrix\.parquet$", 1).alias("chrom")
)

# STEP 2: now 'chrom' exists; create 'cpg_id'
lf = lf.with_columns(
    (pl.col("chrom") + pl.lit(":") + pl.col("start").cast(pl.Utf8)).alias("cpg_id")
)

# Determine sample columns AFTER adding metadata cols
schema = lf.collect_schema()
sample_cols = [c for c in schema if c not in ("start", "chrom", "file", "cpg_id")]

# Ensure numeric
lf_num = lf.with_columns(
    pl.all().exclude(["start", "chrom", "file", "cpg_id"]).cast(pl.Int64, strict=False)
)

# Filter to key CpGs via semi-join (efficient, no Python list)
filtered = (
    lf_num
    .join(keys_lf, on="cpg_id", how="semi")
    .select(["cpg_id"] + sample_cols)
)

print("## -- Collecting & saving...")
filtered.sink_parquet(os.path.join(out_dir, "all_meth_count_matrix_filt.parquet"))
print("Complete!")

