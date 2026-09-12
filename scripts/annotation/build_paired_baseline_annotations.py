#!/usr/bin/env python3
"""Align baseline-LD annotations to the derived paired S-LDXR panel order."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/interim/ld_reference/eur_baseline"
PANEL = ROOT / "data/interim/sldxr_annotations/base"
OUT = ROOT / "data/interim/sldxr_annotations/baseline_paired"
QC = ROOT / "results/phase1c/SLDXR_BASELINE_ANNOTATION_ALIGNMENT.tsv"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for chrom in range(1, 23):
        source_path = SOURCE / f"baselineLD.{chrom}.annot.gz"
        panel_path = PANEL / f"{chrom}.annot.gz"
        output_path = OUT / f"{chrom}.annot.gz"

        source = pd.read_csv(source_path, sep="\t", compression="gzip")
        panel = pd.read_csv(panel_path, sep="\t", compression="gzip")
        if source["SNP"].duplicated().any():
            raise RuntimeError(f"Duplicate baseline SNP IDs on chr{chrom}")
        if panel["SNP"].duplicated().any():
            raise RuntimeError(f"Duplicate paired-panel SNP IDs on chr{chrom}")

        annotation_columns = [col for col in source.columns if col not in {"CHR", "BP", "SNP", "CM"}]
        merged = panel[["CHR", "BP", "SNP", "CM"]].merge(
            source[["SNP", "CHR", "BP", "CM", *annotation_columns]],
            on="SNP",
            how="left",
            sort=False,
            suffixes=("_panel", "_source"),
            indicator=True,
            validate="one_to_one",
        )
        missing = int((merged["_merge"] != "both").sum())
        if missing:
            raise RuntimeError(f"Baseline annotation is missing {missing} paired SNPs on chr{chrom}")
        chr_mismatch = int((merged["CHR_panel"].astype(str) != merged["CHR_source"].astype(str)).sum())
        bp_mismatch = int((merged["BP_panel"] != merged["BP_source"]).sum())
        if chr_mismatch or bp_mismatch:
            raise RuntimeError(
                f"Baseline coordinate mismatch on chr{chrom}: chr={chr_mismatch}, bp={bp_mismatch}"
            )

        aligned = merged[["CHR_panel", "BP_panel", "SNP", "CM_panel", *annotation_columns]].copy()
        aligned.columns = ["CHR", "BP", "SNP", "CM", *annotation_columns]
        aligned.to_csv(output_path, sep="\t", index=False, compression="gzip", float_format="%.10g")
        rows.append(
            {
                "chromosome": chrom,
                "source_rows": len(source),
                "paired_panel_rows": len(panel),
                "aligned_rows": len(aligned),
                "annotation_columns": len(annotation_columns),
                "missing_paired_snps": missing,
                "chr_mismatch": chr_mismatch,
                "bp_mismatch": bp_mismatch,
                "status": "PASS",
            }
        )

    QC.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(QC, sep="\t", index=False)
    print(f"wrote={QC} rows={len(rows)}")


if __name__ == "__main__":
    main()
