#!/usr/bin/env python3
"""Run ancestry-matched LDSC h2 when validated reference bundles are available."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_REF = ROOT / "data/raw/ld_reference"
REF_ROOT = ROOT / "data/interim/ld_reference"
OUT = ROOT / "results/phase1/LDSC_H2_SUMMARY.tsv"
LDSC = "/Users/zy/.local/bin/ldsc.py"


def archive_complete(path: Path, expected_bytes: int) -> bool:
    return (
        path.exists()
        and not path.name.startswith("._")
        and not path.name.endswith(".aria2")
        and path.stat().st_size == expected_bytes
    )


def archive_valid(path: Path, expected_bytes: int) -> bool:
    """Reject size-matching but truncated/corrupt gzip archives before extraction."""
    if not archive_complete(path, expected_bytes):
        return False
    check = subprocess.run(
        ["gzip", "-t", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return check.returncode == 0


def find_prefix(directory: Path, pattern: str) -> str | None:
    hits = sorted(p for p in directory.rglob(pattern) if not p.name.startswith("._"))
    if not hits:
        return None
    # LDSC expects the prefix before the chromosome number.
    hit = hits[0]
    m = re.match(r"(.+)\.([0-9]+)\.l2\.ldscore\.gz$", str(hit))
    return m.group(1) + "." if m else None


def real_chr_file_count(directory: Path, pattern: str) -> int:
    return len({
        int(match.group(1))
        for path in directory.rglob(pattern)
        if not path.name.startswith("._")
        for match in [re.search(r"\.([0-9]+)\.l2\.ldscore\.gz$", path.name)]
        if match
    })


def parse_h2(log: Path) -> tuple[str, str, str]:
    text = log.read_text(errors="replace") if log.exists() else ""
    m = re.search(r"Total Observed scale h2:\s+([-+0-9.eE]+)\s*\(\s*([-+0-9.eE]+)\s*\)", text)
    if not m:
        return "", "", ""
    h2, se = float(m.group(1)), float(m.group(2))
    return str(h2), str(se), str(h2 / se if se else float("nan"))


def main() -> None:
    REF_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    specs = {
        "EUR": (ROOT / "data/interim/ldsc/EUR.sumstats.gz", RAW_REF / "1000G_Phase3_baselineLD_v2.2_ldscores.tgz", 675845447, RAW_REF / "1000G_Phase3_weights_hm3_no_MHC.tgz", 12757654, "eur"),
        "EAS": (ROOT / "data/interim/ldsc/EAS.sumstats.gz", RAW_REF / "1000G_Phase3_EAS_baselineLD_v2.2_ldscores.tgz", 568735046, RAW_REF / "1000G_Phase3_EAS_weights_hm3_no_MHC.tgz", 11470436, "eas"),
    }
    for ancestry, (sumstats, baseline_tar, baseline_bytes, weights_tar, weights_bytes, tag) in specs.items():
        row = {"ancestry": ancestry, "sumstats": str(sumstats), "status": "PENDING_REFERENCE_DOWNLOAD", "h2": "", "h2_se": "", "h2_z": "", "log": "", "error": ""}
        if not sumstats.exists():
            row["status"] = "MISSING_MUNGED_SUMSTATS"
            rows.append(row)
            continue
        baseline_ok = archive_valid(baseline_tar, baseline_bytes)
        weights_ok = archive_valid(weights_tar, weights_bytes)
        if not baseline_ok or not weights_ok:
            row["status"] = "REFERENCE_ARCHIVE_INVALID"
            row["error"] = f"baseline_valid={baseline_ok};weights_valid={weights_ok}"
            rows.append(row)
            continue
        base_dir = REF_ROOT / f"{tag}_baseline"
        weight_dir = REF_ROOT / f"{tag}_weights"
        base_dir.mkdir(exist_ok=True)
        weight_dir.mkdir(exist_ok=True)
        if real_chr_file_count(base_dir, "*.l2.ldscore.gz") < 22:
            subprocess.run(["tar", "-xzf", str(baseline_tar), "-C", str(base_dir)], check=True)
        if real_chr_file_count(weight_dir, "*.l2.ldscore.gz") < 22:
            subprocess.run(["tar", "-xzf", str(weights_tar), "-C", str(weight_dir)], check=True)
        ref = find_prefix(base_dir, "*.l2.ldscore.gz")
        weight = find_prefix(weight_dir, "*.l2.ldscore.gz")
        if not ref or not weight:
            row["status"] = "REFERENCE_PREFIX_NOT_FOUND"
            rows.append(row)
            continue
        out_prefix = ROOT / f"results/phase1/ldsc_{tag}_h2"
        cmd = [LDSC, "--h2", str(sumstats), "--ref-ld-chr", ref, "--w-ld-chr", weight, "--out", str(out_prefix)]
        log = Path(str(out_prefix) + ".log")
        row["log"] = str(log)
        try:
            proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=3600)
            row["status"] = "RUN_AND_BUILD_RESOLVED" if proc.returncode == 0 else "LDSC_FAILED"
            row["error"] = "" if proc.returncode == 0 else (proc.stderr or proc.stdout)[-2000:]
            row["h2"], row["h2_se"], row["h2_z"] = parse_h2(log)
        except Exception as exc:
            row["status"] = "LDSC_EXCEPTION"
            row["error"] = repr(exc)
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT, sep="\t", index=False)


if __name__ == "__main__":
    main()
