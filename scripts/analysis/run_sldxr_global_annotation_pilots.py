#!/usr/bin/env python3
"""Run the three gate-controlled global retinal S-LDXR estimability pilots."""

from __future__ import annotations

import hashlib
import math
import re
import subprocess
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
S_LDXR = Path("/Users/zy/.codex/tools/s-ldxr/s-ldxr.py")
FREEZE = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
FORMAL = ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv"
BLOCK_QC = ROOT / "results/phase1c/SLDXR_BLOCK_JACKKNIFE.tsv"
LOCO_QC = ROOT / "results/phase1c/SLDXR_LOCO_DIAGNOSTIC.tsv"
OUT = ROOT / "results/phase1c/SLDXR_GLOBAL_ANNOTATION_PILOT.tsv"
POWER_OUT = ROOT / "results/phase1c/SLDXR_DAR_POWER_COUNTS.tsv"
RAW_ROOT = ROOT / "results/phase1c/sldxr_pilot"
SUMSTATS = ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz"

TARGETS = {
    "all_retinal_OCR": {
        "kind": "ocr_union",
        "source_interval_n": 700146,
        "mapped_interval_n": 685987,
    },
    "ancestry_DAR": {
        "kind": "dar_global",
        "source_interval_n": 2227,
        "mapped_interval_n": 2219,
    },
    "matched_non_DAR_retinal_OCR": {
        "kind": "matched_non_dar_ocr",
        "source_interval_n": 697837,
        "mapped_interval_n": 683683,
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def require_baseline_pass() -> None:
    formal = pd.read_csv(FORMAL, sep="\t").set_index("metric_name")
    required = ("HSQ1", "HSQ2", "GCOV", "GCOR", "GCORSQ")
    if any(name not in formal.index for name in required):
        raise RuntimeError("Baseline formal output is incomplete")
    for name in required:
        row = formal.loc[name]
        if row["convergence"] != "PASS" or not math.isfinite(float(row["estimate"])) or not math.isfinite(float(row["SE"])):
            raise RuntimeError(f"Baseline formal gate failed for {name}")
    if float(formal.loc["HSQ1", "estimate"]) <= 0 or float(formal.loc["HSQ2", "estimate"]) <= 0:
        raise RuntimeError("Baseline heritability component is non-positive")
    blocks = pd.read_csv(BLOCK_QC, sep="\t")
    loco = pd.read_csv(LOCO_QC, sep="\t")
    for table, label in ((blocks, "jackknife"), (loco, "chromosome influence")):
        key = table.loc[table["metric_name"] == "GCORSQ"]
        if key.empty or key["catastrophic"].astype(bool).any():
            raise RuntimeError(f"Baseline {label} gate is not PASS")


def verify_target_files(freeze: dict, kind: str) -> None:
    roles = {
        "EAS_sumstats",
        "EUR_sumstats",
        "formal_sumstats_alignment_qc",
        "all_score_universe_qc",
    }
    prefixes = (
        "baseline_score_",
        "baseline_annotation_",
        "weights_",
        "frequency_",
        f"{kind}_score_",
        f"{kind}_annotation_",
    )
    # Freeze roles use readable aliases for the two OCR resources.
    aliases = {
        "ocr_union": ("ocr_union_score_", "ocr_union_annotation_"),
        "dar_global": ("dar_global_score_", "dar_global_annotation_"),
        "matched_non_dar_ocr": ("ocr_matched_non_dar_score_", "ocr_matched_non_dar_annotation_"),
    }
    checked_target = 0
    for item in freeze["files"]:
        role = str(item["role"])
        wanted = role in roles or role.startswith(prefixes[:4]) or role.startswith(aliases[kind])
        if not wanted:
            continue
        path = resolve(str(item["path"]))
        if not path.exists() or path.stat().st_size != int(item["bytes"]) or sha256(path) != item["sha256"]:
            raise RuntimeError(f"Frozen pilot input changed: {path}")
        if role.startswith(aliases[kind]):
            checked_target += 1
    if checked_target != 88:  # 22 annotations + 22 x 3 score files
        raise RuntimeError(f"Frozen {kind} file count is {checked_target}, expected 88")


def score_prefix(kind: str) -> str:
    root = "data/interim/sldxr_scores_aligned" if kind == "baseline" else "data/interim/sldxr_scores"
    return str(ROOT / root / f"{kind}_chr.")


def annotation_prefix(kind: str) -> str:
    directory = "baseline_paired" if kind == "baseline" else kind
    return f"{ROOT / 'data/interim/sldxr_annotations' / directory}/"


def command(kind: str, out: Path, freeze: dict) -> list[str]:
    return [
        "python3", str(S_LDXR), "--gcor",
        str(ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz"),
        str(ROOT / "data/interim/sldxr_formal/EUR_sumstats_aligned.gz"),
        "--ref-ld-chr", score_prefix("baseline"), score_prefix(kind),
        "--w-ld-chr", score_prefix("weights"),
        "--frqfile",
        str(ROOT / "data/interim/sldxr_reference/frequency/EAS."),
        str(ROOT / "data/interim/sldxr_reference/frequency/EUR."),
        "--annot", annotation_prefix("baseline"), annotation_prefix(kind),
        "--fit-intercept", "yes", "yes", "no",
        "--use-intercept", "1.0", "1.0", "0.0",
        "--use-chrom", "1", "22",
        "--n-blocks", str(freeze["jackknife_blocks"]),
        "--min-maf", str(freeze["formal_estimation_min_maf"]),
        "--apply-shrinkage", str(freeze["shrinkage_alpha"]),
        "--save-pseudo-coef", "--out", str(out),
    ]


def warnings_and_n(log: Path) -> tuple[str, int]:
    content = log.read_text(errors="replace")
    match = re.search(r"After intersection, (\d+) SNPs are left for regression", content)
    if not match:
        raise RuntimeError(f"Regression SNP count absent from {log}")
    warnings = [line.strip() for line in content.splitlines() if ("Warning" in line or "WARNING" in line) and "FutureWarning" not in line]
    return (" | ".join(dict.fromkeys(warnings)) if warnings else "NONE", int(match.group(1)))


def annotation_counts(kind: str) -> dict[str, int]:
    formal_snps = set(pd.read_csv(SUMSTATS, sep=r"\s+", compression="gzip", usecols=["SNP"])["SNP"])
    panel_n = maf01_n = maf05_n = shared_n = 0
    for chrom in range(1, 23):
        path = ROOT / f"data/interim/sldxr_annotations/{kind}/{chrom}.annot.gz"
        annot = pd.read_csv(path, sep="\t", compression="gzip", usecols=["SNP", kind])
        eas = pd.read_csv(ROOT / f"data/interim/sldxr_reference/frequency/EAS.{chrom}.frq", sep=r"\s+", usecols=["SNP", "MAF"])
        eur = pd.read_csv(ROOT / f"data/interim/sldxr_reference/frequency/EUR.{chrom}.frq", sep=r"\s+", usecols=["SNP", "MAF"])
        if not annot["SNP"].equals(eas["SNP"]) or not annot["SNP"].equals(eur["SNP"]):
            raise RuntimeError(f"Annotation/frequency order mismatch for {kind} chr{chrom}")
        hit = annot[kind].to_numpy() == 1
        panel_n += int(hit.sum())
        maf01 = hit & (eas["MAF"].to_numpy() > 0.01) & (eur["MAF"].to_numpy() > 0.01)
        maf05 = hit & (eas["MAF"].to_numpy() > 0.05) & (eur["MAF"].to_numpy() > 0.05)
        maf01_n += int(maf01.sum())
        maf05_n += int(maf05.sum())
        shared_n += int((hit & annot["SNP"].isin(formal_snps).to_numpy()).sum())
    return {"panel_SNP_N": panel_n, "shared_usable_SNP_N": shared_n, "MAF_gt_0p01_SNP_N": maf01_n, "MAF_gt_0p05_SNP_N": maf05_n}


def main() -> None:
    require_baseline_pass()
    freeze = yaml.safe_load(FREEZE.read_text())
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    power_rows = []
    for label, spec in TARGETS.items():
        kind = str(spec["kind"])
        verify_target_files(freeze, kind)
        counts = annotation_counts(kind)
        raw = RAW_ROOT / f"SLDXR_PILOT_{kind}_RAW.tsv"
        if not raw.exists():
            runlog = RAW_ROOT / f"SLDXR_PILOT_{kind}_RUNNER.log"
            with runlog.open("w") as handle:
                result = subprocess.run(command(kind, raw, freeze), cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
            if result.returncode != 0 or not raw.exists():
                raise RuntimeError(f"S-LDXR pilot failed for {kind}; inspect {runlog}")
        warning, effective_n = warnings_and_n(Path(f"{raw}.log"))
        table = pd.read_csv(raw, sep="\t")
        selected = table.loc[table["ANNOT"] == kind]
        if len(selected) != 1:
            raise RuntimeError(f"Expected one {kind} result row; found {len(selected)}")
        selected = selected.iloc[0]
        estimate = float(selected["GCORSQ"])
        se = float(selected["GCORSQ_SE"])
        finite = math.isfinite(estimate) and math.isfinite(se) and se >= 0
        stability = "PASS_NUMERICALLY_ESTIMABLE" if finite else "FAIL_NONFINITE"
        rows.append({
            "annotation": label,
            "annotation_internal_name": kind,
            "metric_name": "GCORSQ",
            "interval_N": int(spec["source_interval_n"]),
            "mapped_unique_interval_N": int(spec["mapped_interval_n"]),
            **counts,
            "estimate": estimate,
            "SE": se,
            "CI95_low": estimate - 1.96 * se,
            "CI95_high": estimate + 1.96 * se,
            "effective_regression_SNP_N": effective_n,
            "effective_blocks": int(freeze["jackknife_blocks"]),
            "warning": warning,
            "stability": stability,
            "pilot_scope": "NUMERICAL_ESTIMABILITY_ONLY_NOT_BIOLOGICAL_HYPOTHESIS_TEST",
            "input_freeze_id": freeze["freeze_id"],
        })
        power_rows.append({"annotation": label, "interval_N": int(spec["source_interval_n"]), "mapped_unique_interval_N": int(spec["mapped_interval_n"]), **counts})
    pd.DataFrame(rows).to_csv(OUT, sep="\t", index=False)
    pd.DataFrame(power_rows).to_csv(POWER_OUT, sep="\t", index=False)
    print(f"wrote={OUT}")
    print(f"wrote={POWER_OUT}")


if __name__ == "__main__":
    main()
