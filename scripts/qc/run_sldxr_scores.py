#!/usr/bin/env python3
"""Generate paired S-LDXR LD scores from auditable EUR/EAS PLINK panels."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
S_LDXR = Path("/Users/zy/.codex/tools/s-ldxr/s-ldxr.py")
QC = ROOT / "results/phase1c/SLDXR_REFERENCE_QC.tsv"
ANNOT_ROOT = ROOT / "data/interim/sldxr_annotations"
SCORE_ROOT = ROOT / "data/interim/sldxr_scores"
PRINT_SNPS = ROOT / "data/interim/sldxr_reference/print_snps_maf_gt_01.txt"
QC_OUT = ROOT / "results/phase1c/SLDXR_SCORE_QC.tsv"


def prefix(population: str, chrom: int) -> Path:
    table = pd.read_csv(QC, sep="\t")
    row = table.loc[(table["population"] == population) & (table["chromosome"] == chrom)]
    if len(row) != 1:
        raise RuntimeError(f"Missing S-LDXR bfile for {population} chr{chrom}")
    return Path(row.iloc[0]["bfile_prefix"])


def annotation_path(kind: str, chrom: int, baseline_prefix: Path) -> Path:
    if kind == "baseline":
        if baseline_prefix.is_dir():
            return baseline_prefix / f"{chrom}.annot.gz"
        return Path(f"{baseline_prefix}{chrom}.annot.gz")
    return ANNOT_ROOT / kind / f"{chrom}.annot.gz"


def output_prefix(kind: str, chrom: int, score_root: Path) -> Path:
    score_root.mkdir(parents=True, exist_ok=True)
    return score_root / f"{kind}_chr.{chrom}"


def output_complete(prefix: Path) -> bool:
    outputs = [prefix.with_name(prefix.name + f"_{suffix}.gz") for suffix in ("pop1", "pop2", "te")]
    return all(path.exists() and path.stat().st_size > 0 for path in outputs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kinds", nargs="+", default=["baseline", "weights", "dar_global"])
    parser.add_argument("--chromosomes", nargs="+", type=int, default=list(range(1, 23)))
    parser.add_argument("--score-root", type=Path, default=SCORE_ROOT)
    parser.add_argument("--qc-out", type=Path, default=QC_OUT)
    parser.add_argument(
        "--baseline-annotation-prefix",
        type=Path,
        default=ROOT / "data/interim/ld_reference/eur_baseline/baselineLD.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not QC.exists() or not PRINT_SNPS.exists():
        raise FileNotFoundError("Run prepare_sldxr_reference.py before generating S-LDXR scores.")
    rows = []
    for kind in args.kinds:
        annot_kind = "base" if kind == "weights" else kind
        for chrom in args.chromosomes:
            annot = annotation_path(annot_kind, chrom, args.baseline_annotation_prefix)
            out = output_prefix(kind, chrom, args.score_root)
            cmd = [
                "python3", str(S_LDXR), "--score", "allelic", "--ld-wind-cm", "1.0",
                "--print-snps", str(PRINT_SNPS), "--bfile", str(prefix("EAS", chrom)),
                str(prefix("EUR", chrom)), "--annot", str(annot), "--out", str(out),
            ]
            row = {"kind": kind, "chromosome": chrom, "annotation": str(annot), "output_prefix": str(out), "status": "DRY_RUN" if args.dry_run else "PENDING", "error": ""}
            if not args.dry_run and output_complete(out):
                row["status"] = "PASS"
            elif not args.dry_run:
                try:
                    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=False)
                    row["status"] = "PASS" if result.returncode == 0 and output_complete(out) else "FAIL"
                    row["error"] = (result.stderr or result.stdout)[-2000:]
                except Exception as exc:
                    row["status"] = "EXCEPTION"
                    row["error"] = repr(exc)
            rows.append(row)
            # Persist progress after every annotation/chromosome pair so an
            # interrupted long run can resume without losing the completed QC.
            args.qc_out.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(rows).to_csv(args.qc_out, sep="\t", index=False)
            if row["status"] not in {"PASS", "DRY_RUN"}:
                raise RuntimeError(f"S-LDXR score generation failed: {row}")
    pd.DataFrame(rows).to_csv(args.qc_out, sep="\t", index=False)
    print(f"wrote={args.qc_out} rows={len(rows)}")


if __name__ == "__main__":
    main()
