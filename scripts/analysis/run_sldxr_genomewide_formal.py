#!/usr/bin/env python3
"""Run and summarize the frozen genome-wide EUR-EAS S-LDXR baseline."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import subprocess
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
S_LDXR = Path("/Users/zy/.codex/tools/s-ldxr/s-ldxr.py")
RAW_OUT = ROOT / "results/phase1c/sldxr_formal/SLDXR_GENOMEWIDE_EUR_EAS_RAW.tsv"
FORMAL_OUT = ROOT / "results/phase1c/SLDXR_GENOMEWIDE_EUR_EAS_FORMAL.tsv"
RUNNER_LOG = ROOT / "results/phase1c/sldxr_formal/SLDXR_GENOMEWIDE_EUR_EAS_RUNNER.log"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(path: str) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def resolve_prefix(path: str) -> str:
    resolved = str(resolve(path))
    return f"{resolved}/" if path.endswith("/") else resolved


def verify_frozen_inputs(freeze: dict) -> None:
    roles = {
        "EAS_sumstats",
        "EUR_sumstats",
        "score_print_snps",
        "paired_panel_qc",
        "reference_qc",
        "baseline_row_identity_qc",
        "baseline_numerical_qc",
        "all_score_universe_qc",
        "formal_score_universe",
        "formal_sumstats_alignment_qc",
    }
    prefixes = ("paired_panel_", "frequency_", "baseline_annotation_", "baseline_score_", "weights_")
    checked = 0
    for item in freeze["files"]:
        role = str(item["role"])
        if role not in roles and not role.startswith(prefixes):
            continue
        path = resolve(str(item["path"]))
        if not path.exists() or path.stat().st_size != int(item["bytes"]):
            raise RuntimeError(f"Frozen input missing or size changed: {path}")
        if sha256(path) != item["sha256"]:
            raise RuntimeError(f"Frozen input SHA256 changed: {path}")
        checked += 1
    if checked == 0:
        raise RuntimeError("No formal baseline inputs were verified")


def command(freeze: dict) -> list[str]:
    inputs = freeze["formal_command_inputs"]
    fit = freeze["intercepts"]["fit"]
    fixed = freeze["intercepts"]["fixed"]
    return [
        "python3",
        str(S_LDXR),
        "--gcor",
        *(str(resolve(p)) for p in inputs["gcor"]),
        "--ref-ld-chr",
        *(resolve_prefix(p) for p in inputs["ref_ld_chr"]),
        "--w-ld-chr",
        *(resolve_prefix(p) for p in inputs["w_ld_chr"]),
        "--frqfile",
        *(resolve_prefix(p) for p in inputs["frqfile"]),
        "--annot",
        *(resolve_prefix(p) for p in inputs["annot"]),
        "--fit-intercept",
        *(str(x) for x in fit),
        "--use-intercept",
        *(str(x) for x in fixed),
        "--use-chrom",
        "1",
        "22",
        "--n-blocks",
        str(freeze["jackknife_blocks"]),
        "--min-maf",
        str(freeze["formal_estimation_min_maf"]),
        "--apply-shrinkage",
        str(freeze["shrinkage_alpha"]),
        "--save-pseudo-coef",
        "--out",
        str(RAW_OUT),
    ]


def parse_effective_n(log_text: str) -> int:
    match = re.search(r"After intersection, (\d+) SNPs are left for regression", log_text)
    if not match:
        raise RuntimeError("Effective regression SNP count absent from S-LDXR log")
    return int(match.group(1))


def summarize(freeze: dict) -> None:
    raw = pd.read_csv(RAW_OUT, sep="\t")
    base = raw.loc[raw["ANNOT"] == "base"]
    if len(base) != 1:
        raise RuntimeError(f"Expected one genome-wide base row; found {len(base)}")
    base = base.iloc[0]
    sldxr_log = Path(f"{RAW_OUT}.log")
    log_text = sldxr_log.read_text(errors="replace")
    effective_n = parse_effective_n(log_text)
    warning_lines = []
    for line in RUNNER_LOG.read_text(errors="replace").splitlines() + log_text.splitlines():
        if "FutureWarning" in line:
            continue
        if "Warning" in line or "WARNING" in line or "LinAlg" in line:
            warning_lines.append(line.strip())
    warnings = " | ".join(dict.fromkeys(warning_lines)) if warning_lines else "NONE"

    metrics = [
        ("TAU1", "EAS heritability annotation coefficient"),
        ("TAU2", "EUR heritability annotation coefficient"),
        ("THETA", "trans-ancestry genetic covariance annotation coefficient"),
        ("HSQ1", "EAS stratified heritability"),
        ("HSQ2", "EUR stratified heritability"),
        ("GCOV", "stratified trans-ancestry genetic covariance"),
        ("GCOR", "stratified trans-ancestry genetic correlation"),
        ("GCORSQ", "stratified squared trans-ancestry genetic correlation"),
        ("HSQ1_ENRICHMENT", "EAS heritability enrichment"),
        ("HSQ2_ENRICHMENT", "EUR heritability enrichment"),
        ("GCOV_ENRICHMENT", "genetic covariance enrichment"),
        ("GCORSQ_ENRICHMENT", "squared genetic-correlation enrichment"),
        ("GCOVSQ_DIFF", "difference in squared genetic covariance"),
    ]
    key_metrics = ("HSQ1", "HSQ2", "GCOV", "GCOR", "GCORSQ")
    convergence = "PASS"
    for metric in key_metrics:
        if not math.isfinite(float(base[metric])) or not math.isfinite(float(base[f"{metric}_SE"])):
            convergence = "FAIL_NONFINITE"

    rows = []
    for metric, definition in metrics:
        se_col = f"{metric}_SE"
        estimate = float(base[metric])
        se = float(base[se_col])
        statistic = estimate / se if math.isfinite(se) and se > 0 else math.nan
        rows.append(
            {
                "metric_name": metric,
                "official_definition": definition,
                "estimate": estimate,
                "SE": se,
                "Z_or_test_statistic": statistic,
                "test_statistic_definition": "estimate/SE" if math.isfinite(statistic) else "UNDEFINED",
                "CI95_low": estimate - 1.96 * se if math.isfinite(se) else math.nan,
                "CI95_high": estimate + 1.96 * se if math.isfinite(se) else math.nan,
                "effective_SNP_N": effective_n,
                "number_blocks": int(freeze["jackknife_blocks"]),
                "convergence": convergence,
                "warnings": warnings,
                "software_version": freeze["software"]["git_commit"],
                "input_freeze_id": freeze["freeze_id"],
                "population_1": "EAS",
                "population_2": "EUR",
            }
        )
    FORMAL_OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(FORMAL_OUT, sep="\t", index=False)
    print(f"wrote={FORMAL_OUT}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summarize-existing", action="store_true")
    args = parser.parse_args()
    freeze = yaml.safe_load(FREEZE.read_text())
    if freeze.get("formal_ready") is not True:
        raise RuntimeError("Formal input freeze is not marked formal_ready")
    verify_frozen_inputs(freeze)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    if not args.summarize_existing:
        if RAW_OUT.exists():
            raise FileExistsError(f"Formal raw output already exists: {RAW_OUT}")
        with RUNNER_LOG.open("w") as handle:
            result = subprocess.run(command(freeze), cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
        if result.returncode != 0 or not RAW_OUT.exists() or RAW_OUT.stat().st_size == 0:
            raise RuntimeError(f"Formal S-LDXR failed; inspect {RUNNER_LOG} and {RAW_OUT}.log")
    summarize(freeze)


if __name__ == "__main__":
    main()
