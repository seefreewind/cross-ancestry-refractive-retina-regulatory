#!/usr/bin/env python3
"""Create the immutable Phase 1C.2 formal S-LDXR input freeze."""

from __future__ import annotations

import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
S_LDXR_REPO = Path(os.environ.get("S_LDXR_REPO", "s-ldxr"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def entry(role: str, path: Path) -> dict[str, object]:
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(path)
    return {"role": role, "path": relative(path), "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_gate(path: Path, expected_rows: int) -> pd.DataFrame:
    table = pd.read_csv(path, sep="\t")
    if len(table) != expected_rows or not (table["status"] == "PASS").all():
        raise RuntimeError(f"Formal gate not PASS: {path} rows={len(table)}")
    return table


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"Input freeze already exists and will not be overwritten: {OUT}")

    require_gate(ROOT / "results/phase1c/SLDXR_BASELINE_ROW_IDENTITY.tsv", 22)
    require_gate(ROOT / "results/phase1c/SLDXR_ALIGNED_BASELINE_NUMERICAL_QC.tsv", 66)
    require_gate(ROOT / "results/phase1c/SLDXR_FORMAL_SUMSTATS_ALIGNMENT.tsv", 1)
    universe = require_gate(ROOT / "results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv", 330)
    if not universe["EXACT_PANEL_MATCH"].astype(bool).all():
        raise RuntimeError("At least one score file fails EXACT_PANEL_MATCH")

    files: list[dict[str, object]] = []
    files.extend(
        [
            entry("EAS_sumstats", ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz"),
            entry("EUR_sumstats", ROOT / "data/interim/sldxr_formal/EUR_sumstats_aligned.gz"),
            entry("formal_score_universe", ROOT / "data/interim/sldxr_formal/paired_score_universe_maf_gt_01.parquet"),
            entry("formal_sumstats_alignment_qc", ROOT / "results/phase1c/SLDXR_FORMAL_SUMSTATS_ALIGNMENT.tsv"),
            entry("score_print_snps", ROOT / "data/interim/sldxr_reference/print_snps_maf_gt_01.txt"),
            entry("paired_panel_qc", ROOT / "results/phase1c/SLDXR_PANEL_PAIRING.tsv"),
            entry("reference_qc", ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv"),
            entry("baseline_row_identity_qc", ROOT / "results/phase1c/SLDXR_BASELINE_ROW_IDENTITY.tsv"),
            entry("baseline_numerical_qc", ROOT / "results/phase1c/SLDXR_ALIGNED_BASELINE_NUMERICAL_QC.tsv"),
            entry("all_score_universe_qc", ROOT / "results/phase1c/SLDXR_ALL_SCORE_UNIVERSE_ALIGNMENT.tsv"),
        ]
    )

    reference_qc = pd.read_csv(ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv", sep="\t")
    for chrom in range(1, 23):
        for population in ("EAS", "EUR"):
            row = reference_qc.loc[
                (reference_qc["population"] == population) & (reference_qc["chromosome"] == chrom)
            ]
            if len(row) != 1:
                raise RuntimeError(f"Missing paired panel for {population} chr{chrom}")
            prefix = Path(row.iloc[0]["bfile_prefix"])
            for extension in (".bed", ".bim", ".fam"):
                files.append(entry(f"paired_panel_{population}_chr{chrom}{extension}", Path(f"{prefix}{extension}")))
            files.append(entry(f"frequency_{population}_chr{chrom}", ROOT / f"data/interim/sldxr_reference/frequency/{population}.{chrom}.frq"))

        files.append(entry(f"baseline_annotation_chr{chrom}", ROOT / f"data/interim/sldxr_annotations/baseline_paired/{chrom}.annot.gz"))
        files.append(entry(f"dar_global_annotation_chr{chrom}", ROOT / f"data/interim/sldxr_annotations/dar_global/{chrom}.annot.gz"))
        files.append(entry(f"ocr_union_annotation_chr{chrom}", ROOT / f"data/interim/sldxr_annotations/ocr_union/{chrom}.annot.gz"))
        files.append(entry(f"ocr_matched_non_dar_annotation_chr{chrom}", ROOT / f"data/interim/sldxr_annotations/matched_non_dar_ocr/{chrom}.annot.gz"))
        for suffix in ("pop1", "pop2", "te"):
            files.append(entry(f"baseline_score_chr{chrom}_{suffix}", ROOT / f"data/interim/sldxr_scores_aligned/baseline_chr.{chrom}_{suffix}.gz"))
            files.append(entry(f"weights_chr{chrom}_{suffix}", ROOT / f"data/interim/sldxr_scores/weights_chr.{chrom}_{suffix}.gz"))
            files.append(entry(f"dar_global_score_chr{chrom}_{suffix}", ROOT / f"data/interim/sldxr_scores/dar_global_chr.{chrom}_{suffix}.gz"))
            files.append(entry(f"ocr_union_score_chr{chrom}_{suffix}", ROOT / f"data/interim/sldxr_scores/ocr_union_chr.{chrom}_{suffix}.gz"))
            files.append(entry(f"ocr_matched_non_dar_score_chr{chrom}_{suffix}", ROOT / f"data/interim/sldxr_scores/matched_non_dar_ocr_chr.{chrom}_{suffix}.gz"))

    software_commit = subprocess.check_output(["git", "-C", str(S_LDXR_REPO), "rev-parse", "HEAD"], text=True).strip()
    digest = hashlib.sha256()
    for item in files:
        digest.update(f"{item['role']}\t{item['path']}\t{item['sha256']}\n".encode())
    freeze_id = f"SLDXR_FORMAL_INPUT_FREEZE_v1:{digest.hexdigest()}"

    manifest = {
        "freeze_id": freeze_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "formal_ready": True,
        "analysis_build": "GRCh37.p13_reference_anchored",
        "population_order": ["EAS", "EUR"],
        "score_filter": "MAF_EAS>0.01 and MAF_EUR>0.01",
        "formal_estimation_min_maf": 0.01,
        "jackknife_blocks": 200,
        "intercepts": {"fit": ["yes", "yes", "no"], "fixed": [1.0, 1.0, 0.0]},
        "shrinkage_alpha": 0.5,
        "reference_source": {
            "paired_panel": "1000 Genomes Phase 3 EUR/EAS PLINK bundles; derived exact shared-SNP paired panels",
            "baseline_ld": "1000G Phase3 baselineLD v2.2 annotations aligned to the paired panel",
            "dbsnp_anchor": "NCBI dbSNP Build 151 GRCh37.p13",
        },
        "software": {"name": "S-LDXR", "repository": str(S_LDXR_REPO), "git_commit": software_commit},
        "formal_command_inputs": {
            "gcor": [
                "data/interim/sldxr_formal/EAS_sumstats_aligned.gz",
                "data/interim/sldxr_formal/EUR_sumstats_aligned.gz",
            ],
            "ref_ld_chr": ["data/interim/sldxr_scores_aligned/baseline_chr."],
            "w_ld_chr": ["data/interim/sldxr_scores/weights_chr."],
            "frqfile": ["data/interim/sldxr_reference/frequency/EAS.", "data/interim/sldxr_reference/frequency/EUR."],
            "annot": ["data/interim/sldxr_annotations/baseline_paired/"],
        },
        "invalid_inputs_excluded": {
            "status": "INVALID_FOR_FORMAL_ANALYSIS_ROWSET_MISMATCH",
            "baseline_score_prefix": "data/interim/sldxr_scores/baseline_chr.",
            "provenance_report": "reports/SLDXR_INVALID_BASELINE_PROVENANCE.md",
        },
        "files": files,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"wrote={OUT}")
    print(f"freeze_id={freeze_id}")


if __name__ == "__main__":
    main()
