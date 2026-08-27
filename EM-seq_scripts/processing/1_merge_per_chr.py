import sys
import polars as pl
import pandas as pd
import time
import os
#from concurrent.futures import ProcessPoolExecutor, as_completed

##### ----- SET UP ------
if len(sys.argv) < 6:
    print("Usage: python script.py <CHR> <VALUE> <COV_DIR> <TMP_DIR> <OUT_DIR>")
    sys.exit(1)

CHR = str(sys.argv[1]) ## fix for fetal data
#CHR = sys.argv[1]
VAL = sys.argv[2]
COV_DIR = sys.argv[3]
TMP_DIR = sys.argv[4]
OUT_DIR = sys.argv[5]

# if CHR.isnumeric():
#    print("Please ensure CHR is of format: 'chr11' ")
#    sys.exit(1)

if VAL not in ["total", "meth_count", "meth_percent"]:
    print("Please ensure VAL is one of: total, meth_count, or meth_percent ")
    sys.exit(1)    

print(f".Cov file dir: {COV_DIR}")
print(f"Tmp dir: {TMP_DIR}")
print(f"Output dir: {OUT_DIR}")


schema = {
    "chrom": pl.Utf8,
    "start": pl.Int64,
    "end": pl.Int64,
    "meth_percent": pl.Float64,
    "meth_count": pl.Int64,
    "unmeth_count": pl.Int64,
}

print("## -- Set up complete....")

##### ----- FUNCTION ------
def shard_cov_total_only(sample_id, chr_x, val_x, cov_dir, tmp_dir):
    path = os.path.join(cov_dir, sample_id, f"{sample_id}.bismark_methylation.cov.gz")

    try:
        scan = pl.scan_csv(
            path,
            separator="\t",
            has_header=False,
            new_columns=["chrom", "start", "end", "meth_percent", "meth_count", "unmeth_count"],
            schema_overrides=schema,
            quote_char=None,
        )

        (
            scan
            .filter(pl.col("chrom") == chr_x)
            .with_columns([
                (pl.col("meth_count") + pl.col("unmeth_count")).alias("total"),
                pl.lit(sample_id).alias("sample_id")
            ])
            .select(["start", val_x, "sample_id"])
            .sink_parquet(f"{tmp_dir}/{sample_id}.{chr_x}.{val_x}.parquet")
        )

    except pl.exceptions.NoDataError:
        print(f"[skip empty file] {sample_id}")
        return

def shard_cov_total_only_old(sample_id: str, chr_x: str, val_x: str, cov_dir: str, tmp_dir: str):
    scan = pl.scan_csv(
        cov_dir+sample_id+"/"+sample_id+".bismark_methylation.cov.gz",
        separator="\t",
        has_header=False,
        new_columns=["chrom", "start", "end", "meth_percent", "meth_count", "unmeth_count"],
        dtypes={
            "chrom": pl.Utf8,
            "start": pl.Int64,
            "end": pl.Int64,
            "meth_percent": pl.Float64,
            "meth_count": pl.Int64,
            "unmeth_count": pl.Int64,
        },
        quote_char=None,
    )

    (
        scan
        .filter(pl.col("chrom") == chr_x)
        .with_columns([
            (pl.col("meth_count") + pl.col("unmeth_count")).alias("total"),
            pl.lit(sample_id).alias("sample_id")
        ])
        .select(["start", val_x, "sample_id"])   
        .sink_parquet(f"{tmp_dir}/{sample_id}.{chr_x}.{val_x}.parquet")
    )


##### ----- RUN PER CHR ------
#files = [i for i in os.listdir(COV_DIR) if i in i+".bismark_methylation.cov.gz" in os.listdir(COV_DIR+i+"/")]
files = [
    i for i in os.listdir(COV_DIR)
    if os.path.isfile(os.path.join(COV_DIR, i, f"{i}.bismark_methylation.cov.gz"))
    and os.path.getsize(os.path.join(COV_DIR, i, f"{i}.bismark_methylation.cov.gz")) > 0
]
print("## -- Loading .cov files....")  


start = time.time()
for i_pd in files:
    path = os.path.join(COV_DIR, i_pd, f"{i_pd}.bismark_methylation.cov.gz")
    print("..."+i_pd)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        print(f"[skip empty] {i_pd}")
        continue

    shard_cov_total_only(i_pd, CHR, VAL, COV_DIR, TMP_DIR)

end = time.time()

print("## -- Finished loading .cov files, time: "+str(end - start))  

##### ----- MERGE ACROSS SAMPLES ------
print("## -- Merging across samples....") 
start = time.time()
lf = pl.scan_parquet(TMP_DIR+"*."+CHR+"."+VAL+".parquet")

df = (
    lf.select(["start", "sample_id", VAL])
      .group_by(["start", "sample_id"])
      .agg(pl.sum(VAL).alias(VAL))
      .collect()        
)

## creating cpg by sample matrix
matrix = (
    df.pivot(values=VAL, index="start", columns="sample_id")
      .sort("start")
      .fill_null(0)
)

end = time.time()

print("## -- Finished loading temporary .parquet files, time: "+str(end - start))  

##### ----- SAVE FILE -----
matrix.write_parquet(OUT_DIR+CHR+"_"+VAL+"_matrix.parquet")


print("## -- Complete!")
