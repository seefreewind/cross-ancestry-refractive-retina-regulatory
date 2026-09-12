#!/usr/bin/env python3
"""Run reproducible formal S-LDXR GCOR² estimations.

The score and annotation prefixes are deliberately assembled here rather than
typed ad hoc at the shell.  The first prefix is the baseline-LD model; a
second prefix adds one retinal annotation while preserving the same paired
SNP order.  S-LDXR then reports the genome-wide row and the conditional
annotation row in one regression.
"""

from __future__ import annotations

import argparse
import re
import shlex
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
S_LDXR = Path(os.environ.get("S_LDXR", "s-ldxr.py"))
SUMSTATS = [
    ROOT / "data/interim/sldxr_formal/EAS_sumstats_aligned.gz",
    ROOT / "data/interim/sldxr_formal/EUR_sumstats_aligned.gz",
]
SCORE_ROOT = ROOT / "data/interim/sldxr_scores"
ALIGNED_SCORE_ROOT = ROOT / "data/interim/sldxr_scores_aligned"
ANNOT_ROOT = ROOT / "data/interim/sldxr_annotations"
BASELINE_ANNOT = ANNOT_ROOT / "baseline_paired" / ""
FREQ_PREFIXES = [
    ROOT / "data/interim/sldxr_reference/frequency/EAS.",
    ROOT / "data/interim/sldxr_reference/frequency/EUR.",
]
OUT_ROOT = ROOT / "results/phase1c/sldxr_formal"


TARGETS = {
    "baseline": {"score": [], "annot": [], "label": "baseline"},
    "dar_global": {"score": ["dar_global"], "annot": ["dar_global"], "label": "dar_global"},
    "ocr_union": {"score": ["ocr_union"], "annot": ["ocr_union"], "label": "ocr_union"},
    "matched_non_dar_ocr": {
        "score": ["matched_non_dar_ocr"],
        "annot": ["matched_non_dar_ocr"],
        "label": "matched_non_dar_ocr",
    },
}


def score_prefix(kind: str) -> Path:
    root = ALIGNED_SCORE_ROOT if kind == "baseline" else SCORE_ROOT
    return root / f"{kind}_chr."


def annot_prefix(kind: str) -> str:
    if kind == "baseline":
        return f"{BASELINE_ANNOT}/"
    return f"{ANNOT_ROOT / kind}/"


def output_path(target: str, n_blocks: int, min_maf: float, jk_bias_adj: bool) -> Path:
    maf_tag = str(min_maf).replace(".", "p")
    adj_tag = "jkadj" if jk_bias_adj else "analytic"
    return OUT_ROOT / f"GCOR_{target}_blocks{n_blocks}_maf{maf_tag}_{adj_tag}.txt"


def build_command(target: str, n_blocks: int, min_maf: float, jk_bias_adj: bool, out: Path) -> list[str]:
    spec = TARGETS[target]
    score_prefixes = [score_prefix("baseline")] + [score_prefix(k) for k in spec["score"]]
    annot_prefixes = [annot_prefix("baseline")] + [annot_prefix(k) for k in spec["annot"]]
    cmd = [
        "python3",
        str(S_LDXR),
        "--gcor",
        *(str(p) for p in SUMSTATS),
        "--ref-ld-chr",
        *(str(p) for p in score_prefixes),
        "--w-ld-chr",
        str(score_prefix("weights")),
        "--frqfile",
        *(str(p) for p in FREQ_PREFIXES),
        "--annot",
        *(str(p) for p in annot_prefixes),
        "--fit-intercept",
        "yes",
        "yes",
        "no",
        "--use-intercept",
        "1.0",
        "1.0",
        "0.0",
        "--use-chrom",
        "1",
        "22",
        "--n-blocks",
        str(n_blocks),
        "--min-maf",
        str(min_maf),
        "--apply-shrinkage",
        "0.5",
        "--save-pseudo-coef",
        "--out",
        str(out.with_suffix("")),
    ]
    if jk_bias_adj:
        cmd.append("--use-jackknife-bias-adj")
    return cmd


def parse_log(log_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not log_path.exists():
        return values
    text = log_path.read_text(errors="replace")
    patterns = {
        "summary_n_loaded": r"Loaded \d+ SNPs from the GWAS summary data file",
        "score_n": r"Loaded LD scores for (\d+) SNPs (\d+) annotations",
        "annotation_n": r"Loaded annotations: (\d+) SNPs, (\d+) annotations",
        "regression_n": r"After intersection, (\d+) SNPs are left for regression",
        "gcor": r"\[INFO\] gcor: ([^\s]+) ([^\s]+)",
        "gcorsq": r"\[INFO\] gcorsq: ([^\s]+) ([^\s]+)",
    }
    for key, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            values[key] = "|".join(" ".join(m) if isinstance(m, tuple) else m for m in matches)
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", nargs="+", choices=sorted(TARGETS), default=["baseline", "dar_global"])
    parser.add_argument("--n-blocks", type=int, default=200)
    parser.add_argument("--min-maf", type=float, default=0.01)
    parser.add_argument("--use-jackknife-bias-adj", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    freeze = ROOT / "config/SLDXR_FORMAL_INPUT_FREEZE_v1.yaml"
    if not freeze.exists():
        raise SystemExit("Formal input freeze is absent; regression is forbidden before all Phase 1C.2 gates pass")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for target in args.targets:
        out = output_path(target, args.n_blocks, args.min_maf, args.use_jackknife_bias_adj)
        stem = out.with_suffix("")
        log = Path(f"{stem}.log")
        runner_log = Path(f"{out}.runner.log")
        if stem.exists() and stem.stat().st_size > 0 and not args.force:
            print(f"SKIP existing={out}")
            continue
        cmd = build_command(target, args.n_blocks, args.min_maf, args.use_jackknife_bias_adj, out)
        print(f"RUN target={target} n_blocks={args.n_blocks} min_maf={args.min_maf}")
        print(f"COMMAND {shlex.join(cmd)}")
        with runner_log.open("w") as handle:
            result = subprocess.run(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=False)
        parsed = parse_log(log)
        print(f"RETURN target={target} code={result.returncode} output={out} log={log}")
        print(f"QC {parsed}")
        if result.returncode != 0 or not stem.exists() or stem.stat().st_size == 0:
            raise SystemExit(f"S-LDXR failed for target={target}; inspect {log}")


if __name__ == "__main__":
    main()
