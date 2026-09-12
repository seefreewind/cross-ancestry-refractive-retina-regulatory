#!/usr/bin/env python3
"""Phase 0 GWAS metadata and basic QC for Cheng et al. 2026 RE summary data."""

from __future__ import annotations

import argparse
import hashlib
import math
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATASETS = {
    "EUR": {
        "filename": "EUR_meta_no23andMe.fastGWAz",
        "download_url": "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/EUR_seven_cohorts_myopia_metal_ratio01_adjusted_no23andme.fastGWAz",
        "n_total": 1495159,
        "phenotype": "refractive error / mean spherical equivalent with study-specific definitions as described by Cheng et al. 2026",
    },
    "EAS": {
        "filename": "EAS_meta.fastGWAz",
        "download_url": "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/five_cohort_EAS_metal.fastGWAz",
        "n_total": 121172,
        "phenotype": "refractive error / mean spherical equivalent with study-specific definitions as described by Cheng et al. 2026",
    },
    "AFR": {
        "filename": "AFR_meta.fastGWAz",
        "download_url": "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/two_cohort_AFR_metal.fastGWAz",
        "n_total": 144737,
        "phenotype": "myopia case-control meta-analysis across MVP and All of Us, as described by Cheng et al. 2026",
    },
}

REMOTE_BYTES = {
    "EUR": 546618578,
    "EAS": 458797930,
    "AFR": 906857500,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def is_snp(a: pd.Series, b: pd.Series) -> pd.Series:
    return a.str.fullmatch(r"[ACGT]") & b.str.fullmatch(r"[ACGT]")


def qc_one(path: Path, ancestry: str, results_dir: Path, plots_dir: Path) -> tuple[dict, pd.DataFrame]:
    usecols = ["SNP", "A1", "A2", "freq", "b", "se", "p", "N", "CHR", "POS", "z"]
    dtypes = {"SNP": "string", "A1": "string", "A2": "string", "CHR": "string"}
    counts = {
        "dataset": ancestry,
        "filename": path.name,
        "file_exists": path.exists(),
        "file_size_bytes": path.stat().st_size if path.exists() else 0,
        "expected_remote_bytes": REMOTE_BYTES.get(ancestry, ""),
        "file_complete_by_remote_size": (path.stat().st_size == REMOTE_BYTES[ancestry]) if path.exists() else False,
        "sha256": sha256(path) if path.exists() else "",
        "number_variants": 0,
        "duplicated_variants": 0,
        "duplicated_chr_pos": 0,
        "missing_p": 0,
        "missing_allele": 0,
        "invalid_p": 0,
        "invalid_freq": 0,
        "missing_freq": 0,
        "missing_info": "NA",
        "snp_variants": 0,
        "indel_or_non_snp_variants": 0,
        "ambiguous_snp_variants": 0,
        "multi_allelic_loci": "not inferable from source columns; audited as duplicated chr:pos",
        "genomewide_significant_p_lt_5e-8": 0,
        "rsid_available": 0,
        "chromosome_min": "",
        "chromosome_max": "",
    }
    chrom = {}
    p_bins = np.linspace(0, 20, 101)
    p_hist = np.zeros(len(p_bins) - 1, dtype=np.int64)
    maf_bins = np.linspace(0, 0.5, 101)
    maf_hist = np.zeros(len(maf_bins) - 1, dtype=np.int64)
    info_hist = None
    seen_snp: set[str] = set()
    seen_pos: set[str] = set()
    rows_for_recheck = []
    for chunk in pd.read_csv(path, sep=r"\s+", usecols=usecols, dtype=dtypes, chunksize=250_000, low_memory=False):
        counts["number_variants"] += len(chunk)
        for col in ["p", "freq"]:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")
        for col in ["CHR", "POS"]:
            chunk[col] = chunk[col].astype("string")
        counts["missing_p"] += int(chunk["p"].isna().sum())
        counts["invalid_p"] += int(((chunk["p"].notna()) & ((chunk["p"] < 0) | (chunk["p"] > 1))).sum())
        counts["missing_allele"] += int((chunk["A1"].isna() | chunk["A2"].isna()).sum())
        counts["missing_freq"] += int(chunk["freq"].isna().sum())
        counts["invalid_freq"] += int(((chunk["freq"].notna()) & ((chunk["freq"] < 0) | (chunk["freq"] > 1))).sum())
        snp = is_snp(chunk["A1"].fillna(""), chunk["A2"].fillna(""))
        counts["snp_variants"] += int(snp.sum())
        counts["indel_or_non_snp_variants"] += int((~snp).sum())
        amb = snp & (((chunk["A1"] == "A") & (chunk["A2"] == "T")) | ((chunk["A1"] == "T") & (chunk["A2"] == "A")) | ((chunk["A1"] == "C") & (chunk["A2"] == "G")) | ((chunk["A1"] == "G") & (chunk["A2"] == "C")))
        counts["ambiguous_snp_variants"] += int(amb.sum())
        counts["genomewide_significant_p_lt_5e-8"] += int((chunk["p"] < 5e-8).sum())
        counts["rsid_available"] += int(chunk["SNP"].notna().sum())
        for v in chunk["SNP"].dropna().astype(str):
            if v in seen_snp:
                counts["duplicated_variants"] += 1
            seen_snp.add(v)
        key = chunk["CHR"].fillna("NA") + ":" + chunk["POS"].fillna("NA")
        for v in key:
            if v in seen_pos:
                counts["duplicated_chr_pos"] += 1
            seen_pos.add(v)
        c = chunk["CHR"].fillna("NA").value_counts()
        for k, v in c.items():
            chrom[k] = chrom.get(k, 0) + int(v)
        p = chunk["p"].clip(lower=10 ** -20, upper=1)
        h, _ = np.histogram(-np.log10(p), bins=p_bins)
        p_hist += h
        maf = np.minimum(chunk["freq"], 1 - chunk["freq"])
        h, _ = np.histogram(maf.dropna(), bins=maf_bins)
        maf_hist += h
        rows_for_recheck.append(chunk[["SNP", "A1", "A2", "freq", "p", "N", "CHR", "POS", "z"]])
    counts["chromosome_min"] = min(chrom) if chrom else ""
    counts["chromosome_max"] = max(chrom) if chrom else ""
    counts["chromosome_variant_counts"] = ";".join(f"{k}:{chrom[k]}" for k in sorted(chrom, key=lambda x: (len(x), x)))
    summary = pd.DataFrame([counts])
    summary.to_csv(results_dir / f"{ancestry}_GWAS_QC.tsv", sep="\t", index=False)
    pd.DataFrame({"bin_left": p_bins[:-1], "bin_right": p_bins[1:], "count": p_hist}).to_csv(results_dir / f"{ancestry}_P_HIST.tsv", sep="\t", index=False)
    pd.DataFrame({"bin_left": maf_bins[:-1], "bin_right": maf_bins[1:], "count": maf_hist}).to_csv(results_dir / f"{ancestry}_MAF_HIST.tsv", sep="\t", index=False)
    return counts, pd.concat(rows_for_recheck, ignore_index=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    ws = args.workspace
    results = ws / "results" / "phase0"
    plots = results / "plots"
    results.mkdir(parents=True, exist_ok=True)
    plots.mkdir(parents=True, exist_ok=True)
    summaries = []
    metadata = []
    for ancestry, spec in DATASETS.items():
        path = ws / "data" / "raw" / "gwas" / spec["filename"]
        if not path.exists() or path.stat().st_size != REMOTE_BYTES[ancestry]:
            summaries.append({"dataset": ancestry, "file_exists": path.exists(), "filename": path.name, "file_size_bytes": path.stat().st_size if path.exists() else 0, "expected_remote_bytes": REMOTE_BYTES[ancestry], "file_complete_by_remote_size": False, "status": "BLOCKING_INCOMPLETE_SOURCE"})
            continue
        s, _ = qc_one(path, ancestry, results, plots)
        summaries.append(s)
        metadata.append({
            "dataset": f"{ancestry}_meta_no23andMe" if ancestry == "EUR" else f"{ancestry}_meta",
            "ancestry": ancestry,
            "publication": "Cheng et al. 2026, Nature Genetics",
            "doi": "10.1038/s41588-026-02576-0",
            "download_url": spec["download_url"],
            "filename": path.name,
            "genome_build": "UNRESOLVED: source file and publication audit do not yet provide an explicit build",
            "n_total": spec["n_total"],
            "n_cases": "NA / mixed continuous and case-control cohorts",
            "n_controls": "NA / mixed continuous and case-control cohorts",
            "phenotype": spec["phenotype"],
            "effect_allele_definition": "A1 is coded/effect allele per source header; A2 is other allele; source script confirms ALLELE A1 A2",
            "columns": "SNP A1 A2 freq b se p N CHR POS z",
            "effect_type": "b (beta-like source effect) plus z and se; cross-ancestry meta-analysis described as sample-size-weighted Z; raw beta comparison not assumed valid",
            "has_beta": True,
            "has_se": True,
            "has_z": True,
            "has_p": True,
            "has_af": True,
            "has_n": True,
            "variant_id_format": "rsID in SNP plus CHR/POS",
            "sample_overlap_notes": "Publication reports ancestry-stratified meta-analyses; 23andMe excluded from released EUR/cross-ancestry files; cohort overlap audit remains source-publication dependent",
            "imputation_notes": "Not stated in raw header; retain unresolved until full source audit",
            "sha256": s["sha256"],
        })
    pd.DataFrame(summaries).to_csv(results / "GWAS_QC_SUMMARY.tsv", sep="\t", index=False)
    pd.DataFrame(metadata).to_csv(ws / "metadata" / "GWAS_METADATA.tsv", sep="\t", index=False)

    # Overview plots from histogram sidecars; these are QC-only and not manuscript figures.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for ancestry, ax in zip(DATASETS, axes.flat):
        ph = results / f"{ancestry}_P_HIST.tsv"
        mh = results / f"{ancestry}_MAF_HIST.tsv"
        if not ph.exists():
            ax.axis("off")
            continue
        p = pd.read_csv(ph, sep="\t")
        m = pd.read_csv(mh, sep="\t")
        ax2 = ax.twinx()
        ax.bar(p["bin_left"], p["count"], width=0.18, alpha=0.35, label="-log10(P)")
        ax2.plot(m["bin_left"], m["count"], color="darkorange", label="MAF")
        ax.set_title(ancestry)
        ax.set_xlabel("QC bin")
        ax.set_ylabel("P count")
        ax2.set_ylabel("MAF count")
    fig.suptitle("Phase 0 GWAS QC distributions (QC only)")
    fig.savefig(plots / "GWAS_QC_DISTRIBUTIONS.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
