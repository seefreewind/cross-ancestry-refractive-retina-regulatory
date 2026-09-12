#!/usr/bin/env python3
"""Create S-LDXR summary statistics in exact paired-score SNP order."""

from __future__ import annotations

import argparse
import gzip
import hashlib
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_QC = ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv"
FREQ_ROOT = ROOT / "data/interim/sldxr_reference/frequency"
HARMONIZED = ROOT / "data/processed/EUR_EAS_HARMONIZED.parquet"
OUT_DIR = ROOT / "data/interim/sldxr_formal"
UNIVERSE = OUT_DIR / "paired_score_universe_maf_gt_01.parquet"
EAS_OUT = OUT_DIR / "EAS_sumstats_aligned.gz"
EUR_OUT = OUT_DIR / "EUR_sumstats_aligned.gz"
QC_OUT = ROOT / "results/phase1c/SLDXR_FORMAL_SUMSTATS_ALIGNMENT.tsv"


def panel_prefix(chrom: int) -> Path:
    qc = pd.read_csv(REFERENCE_QC, sep="\t")
    row = qc.loc[(qc["population"] == "EUR") & (qc["chromosome"] == chrom)]
    if len(row) != 1:
        raise RuntimeError(f"Missing unique paired-panel prefix for chr{chrom}")
    return Path(row.iloc[0]["bfile_prefix"])


def build_universe() -> int:
    writer: pq.ParquetWriter | None = None
    ordinal = 0
    total = 0
    try:
        for chrom in range(1, 23):
            panel = pd.read_csv(
                Path(f"{panel_prefix(chrom)}.bim"),
                sep=r"\s+",
                header=None,
                names=["CHR", "SNP", "CM", "BP", "A1", "A2"],
                usecols=[0, 1, 3],
                dtype={"CHR": int, "SNP": str, "BP": int},
            )[["CHR", "BP", "SNP"]]
            eas = pd.read_csv(FREQ_ROOT / f"EAS.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
            eur = pd.read_csv(FREQ_ROOT / f"EUR.{chrom}.frq", sep="\t", usecols=["SNP", "MAF"])
            if not panel["SNP"].equals(eas["SNP"]) or not panel["SNP"].equals(eur["SNP"]):
                raise RuntimeError(f"Frequency order differs from paired panel on chr{chrom}")
            keep = (eas["MAF"].to_numpy() > 0.01) & (eur["MAF"].to_numpy() > 0.01)
            part = panel.loc[keep].reset_index(drop=True)
            part["ORD"] = range(ordinal, ordinal + len(part))
            ordinal += len(part)
            total += len(part)
            table = pa.Table.from_pandas(part, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(UNIVERSE, table.schema, compression="zstd")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()
    return total


def ordered_hash(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    rows = 0
    with gzip.open(path, "rt") as handle:
        header = handle.readline().strip().split()
        positions = {name: header.index(name) for name in ("SNP", "CHR", "BP")}
        for line in handle:
            fields = line.split()
            digest.update(
                f"{int(fields[positions['CHR']])}:{int(fields[positions['BP']])}:{fields[positions['SNP']]}\n".encode()
            )
            rows += 1
    return rows, digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if any(path.exists() for path in (UNIVERSE, EAS_OUT, EUR_OUT, QC_OUT)) and not args.force:
        raise FileExistsError("Formal aligned summary-statistic outputs already exist; use --force only before input freeze")

    score_universe_n = build_universe()
    connection = duckdb.connect()
    harm = str(HARMONIZED).replace("'", "''")
    universe = str(UNIVERSE).replace("'", "''")
    eas_out = str(EAS_OUT).replace("'", "''")
    eur_out = str(EUR_OUT).replace("'", "''")
    connection.execute(f"CREATE VIEW h AS SELECT * FROM read_parquet('{harm}')")
    connection.execute(f"CREATE VIEW u AS SELECT * FROM read_parquet('{universe}')")
    harmonized_n = int(connection.execute("SELECT count(*) FROM h").fetchone()[0])
    duplicate_snp_groups = int(
        connection.execute("SELECT count(*) FROM (SELECT SNP_EUR FROM h GROUP BY SNP_EUR HAVING count(*) > 1)").fetchone()[0]
    )
    duplicate_rows_removed = int(
        connection.execute("SELECT coalesce(sum(n), 0) FROM (SELECT count(*) AS n FROM h GROUP BY SNP_EUR HAVING count(*) > 1)").fetchone()[0]
    )
    connection.execute(
        "CREATE VIEW hc AS SELECT * FROM h QUALIFY count(*) OVER (PARTITION BY SNP_EUR) = 1"
    )
    max_n_eas, max_n_eur = connection.execute("SELECT max(N_EAS), max(N_EUR) FROM h").fetchone()
    threshold_eas = max(0.001 * float(max_n_eas), 80.0)
    threshold_eur = max(0.001 * float(max_n_eur), 80.0)
    joined_before = int(connection.execute("SELECT count(*) FROM u JOIN hc h ON u.SNP=h.SNP_EUR").fetchone()[0])
    coord = connection.execute(
        """
        SELECT
          sum(CASE WHEN CAST(h.CHR AS INTEGER) <> u.CHR THEN 1 ELSE 0 END),
          sum(CASE WHEN h.POS <> u.BP THEN 1 ELSE 0 END)
        FROM u JOIN hc h ON u.SNP=h.SNP_EUR
        """
    ).fetchone()
    source_chr_mismatch, source_bp_mismatch = int(coord[0] or 0), int(coord[1] or 0)
    removed_eas = int(
        connection.execute(
            f"SELECT count(*) FROM u JOIN hc h ON u.SNP=h.SNP_EUR WHERE h.z_EAS_aligned_to_EUR*h.z_EAS_aligned_to_EUR > {threshold_eas}"
        ).fetchone()[0]
    )
    removed_eur = int(
        connection.execute(
            f"SELECT count(*) FROM u JOIN hc h ON u.SNP=h.SNP_EUR WHERE h.z_EUR*h.z_EUR > {threshold_eur}"
        ).fetchone()[0]
    )
    condition = (
        f"h.z_EAS_aligned_to_EUR*h.z_EAS_aligned_to_EUR <= {threshold_eas} "
        f"AND h.z_EUR*h.z_EUR <= {threshold_eur} "
        "AND h.N_EAS IS NOT NULL AND h.N_EUR IS NOT NULL "
        "AND h.z_EAS_aligned_to_EUR IS NOT NULL AND h.z_EUR IS NOT NULL"
    )
    base_query = f"FROM u JOIN hc h ON u.SNP=h.SNP_EUR WHERE {condition} ORDER BY u.ORD"
    connection.execute(
        f"COPY (SELECT u.SNP, u.CHR, u.BP, h.A1_EUR AS A1, h.A2_EUR AS A2, h.z_EAS_aligned_to_EUR AS Z, h.N_EAS AS N {base_query}) TO '{eas_out}' (FORMAT CSV, HEADER, DELIMITER ' ', COMPRESSION GZIP)"
    )
    connection.execute(
        f"COPY (SELECT u.SNP, u.CHR, u.BP, h.A1_EUR AS A1, h.A2_EUR AS A2, h.z_EUR AS Z, h.N_EUR AS N {base_query}) TO '{eur_out}' (FORMAT CSV, HEADER, DELIMITER ' ', COMPRESSION GZIP)"
    )
    final_n = int(connection.execute(f"SELECT count(*) {base_query.replace(' ORDER BY u.ORD', '')}").fetchone()[0])
    connection.close()

    eas_rows, eas_hash = ordered_hash(EAS_OUT)
    eur_rows, eur_hash = ordered_hash(EUR_OUT)
    status = "PASS" if (
        source_chr_mismatch == 0
        and source_bp_mismatch == 0
        and eas_rows == eur_rows == final_n
        and eas_hash == eur_hash
        and final_n > 0
    ) else "FAIL"
    row = {
        "score_universe_n_maf_gt_01": score_universe_n,
        "harmonized_input_n": harmonized_n,
        "joined_before_chisq_filter_n": joined_before,
        "duplicate_harmonized_snp_groups": duplicate_snp_groups,
        "duplicate_harmonized_rows_removed": duplicate_rows_removed,
        "eas_chisq_threshold": threshold_eas,
        "eur_chisq_threshold": threshold_eur,
        "eas_high_chisq_rows": removed_eas,
        "eur_high_chisq_rows": removed_eur,
        "source_chr_mismatch": source_chr_mismatch,
        "source_bp_mismatch": source_bp_mismatch,
        "formal_shared_rows": final_n,
        "eas_order_sha256": eas_hash,
        "eur_order_sha256": eur_hash,
        "population_order_match": eas_hash == eur_hash,
        "allele_basis": "EAS_Z_ALIGNED_TO_EUR_A1;EUR_NATIVE_A1",
        "eas_output": str(EAS_OUT),
        "eur_output": str(EUR_OUT),
        "status": status,
    }
    QC_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(QC_OUT, sep="\t", index=False)
    print(f"wrote={QC_OUT} status={status} rows={final_n}")
    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
