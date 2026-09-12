#!/usr/bin/env python3
"""Register the released METAL cross-ancestry summary file in the audit metadata."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
META = ROOT / "metadata/GWAS_METADATA.tsv"
RAW = ROOT / "data/raw/gwas/Cross_ancestry_EUR_EAS_AFR_no23andMe"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    meta = pd.read_csv(META, sep="\t", dtype=str)
    dataset = "Cross_ancestry_EUR_EAS_AFR_no23andMe"
    meta = meta[meta["dataset"] != dataset]
    if RAW.exists():
        meta = pd.concat(
            [
                meta,
                pd.DataFrame(
                    [
                        {
                            "dataset": dataset,
                            "ancestry": "EUR+EAS+AFR",
                            "publication": "Cheng et al. 2026, Nature Genetics",
                            "doi": "10.1038/s41588-026-02576-0",
                            "download_url": "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/Cross_ancest_EUR_EAS_AFR_no23andme1tbl",
                            "filename": RAW.name,
                            "genome_build": "UNRESOLVED: source file and publication audit do not yet provide an explicit build",
                            "n_total": "1761068 (sum of reported EUR/EAS/AFR discovery totals; not encoded in file)",
                            "n_cases": "NA",
                            "n_controls": "NA",
                            "phenotype": "cross-ancestry refractive error/myopia meta-analysis",
                            "effect_allele_definition": "Allele1 is the METAL reference/effect allele; Allele2 is the alternate allele",
                            "columns": "MarkerName Allele1 Allele2 Freq1 FreqSE MinFreq MaxFreq Weight Zscore P-value Direction HetISq HetChiSq HetDf HetPVal",
                            "effect_type": "sample-size-weighted fixed-effect Z meta-analysis; no beta or standard error in released file",
                            "has_beta": "False",
                            "has_se": "False",
                            "has_z": "True",
                            "has_p": "True",
                            "has_af": "True",
                            "has_n": "False",
                            "variant_id_format": "rsID in MarkerName; alleles may include indels",
                            "sample_overlap_notes": "Cross-ancestry released file; source publication reports ancestry-stratified analyses and excludes 23andMe from released EUR/cross-ancestry data",
                            "imputation_notes": "Not stated in raw header; retain unresolved",
                            "sha256": sha256(RAW),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    meta.to_csv(META, sep="\t", index=False)


if __name__ == "__main__":
    main()
