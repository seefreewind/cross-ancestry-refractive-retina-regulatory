#!/usr/bin/env python3
"""Lift HRCA hg38 intervals to the frozen hg19/GRCh37 analysis build."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from pyliftover import LiftOver


ROOT = Path(__file__).resolve().parents[2]
CHAIN = ROOT / "data" / "raw" / "retina" / "hg38ToHg19.over.chain.gz"
OUT_DIR = ROOT / "data" / "processed" / "reference_anchored"
QC_OUT = ROOT / "results" / "phase1c" / "RETINA_LIFTOVER_QC.tsv"


def normalize_chrom(value: str) -> str:
    value = value.strip()
    return value if value.startswith("chr") else f"chr{value}"


def lift_interval(lo: LiftOver, chrom: str, start_1based: int, end_1based: int) -> Tuple[Optional[str], Optional[int], Optional[int], str]:
    """Return target BED-like 1-based inclusive coordinates and status."""
    source = normalize_chrom(chrom)
    if end_1based < start_1based:
        return None, None, None, "INVALID_INTERVAL"
    start_hits = lo.convert_coordinate(source, start_1based - 1)
    end_hits = lo.convert_coordinate(source, end_1based - 1)
    if not start_hits or not end_hits:
        return None, None, None, "UNMAPPED_BOUNDARY"
    candidates = []
    for start_hit in start_hits:
        for end_hit in end_hits:
            if start_hit[0] != end_hit[0] or start_hit[2] != end_hit[2]:
                continue
            if start_hit[2] == "+":
                target_start0, target_end0 = start_hit[1], end_hit[1]
            else:
                target_start0, target_end0 = end_hit[1], start_hit[1]
            if target_end0 < target_start0:
                continue
            candidates.append((start_hit[0], target_start0 + 1, target_end0 + 1, start_hit[2]))
    unique = sorted(set(candidates))
    if len(unique) != 1:
        return None, None, None, "AMBIGUOUS_MAPPING" if unique else "INCOMPLETE_MAPPING"
    target_chrom, target_start, target_end, strand = unique[0]
    source_width = end_1based - start_1based + 1
    target_width = target_end - target_start + 1
    status = "MAPPED_WIDTH_PRESERVED" if source_width == target_width else "MAPPED_WIDTH_CHANGED"
    return target_chrom, target_start, target_end, status


def process_dar(lo: LiftOver, source: Path, target: Path) -> Dict[str, object]:
    counts = Counter()
    with source.open("r", encoding="utf-8", errors="replace", newline="") as handle, target.open("w", encoding="utf-8", newline="") as out:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or []) + ["canonical_build", "canonical_seqnames", "canonical_start", "canonical_end", "liftover_status"]
        writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            counts["n_input"] += 1
            try:
                chrom, start, end, status = lift_interval(lo, row["seqnames"], int(row["start"]), int(row["end"]))
            except (KeyError, TypeError, ValueError):
                chrom, start, end, status = None, None, None, "INVALID_INTERVAL"
            row.update({
                "canonical_build": "GRCh37.p13",
                "canonical_seqnames": chrom or "",
                "canonical_start": start or "",
                "canonical_end": end or "",
                "liftover_status": status,
            })
            writer.writerow(row)
            counts[status] += 1
    return counts


def process_union_ocr(lo: LiftOver, source: Path, target: Path) -> Dict[str, object]:
    counts = Counter()
    with source.open("r", encoding="utf-8", errors="replace", newline="") as handle, target.open("w", encoding="utf-8", newline="") as out:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or []) + ["canonical_build", "canonical_seqnames", "canonical_start", "canonical_end", "liftover_status"]
        writer = csv.DictWriter(out, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for row in reader:
            counts["n_input"] += 1
            try:
                chrom, start, end, status = lift_interval(lo, row["seqnames"], int(row["start"]), int(row["end"]))
            except (KeyError, TypeError, ValueError):
                chrom, start, end, status = None, None, None, "INVALID_INTERVAL"
            row.update({
                "canonical_build": "GRCh37.p13",
                "canonical_seqnames": chrom or "",
                "canonical_start": start or "",
                "canonical_end": end or "",
                "liftover_status": status,
            })
            writer.writerow(row)
            counts[status] += 1
    return counts


def main() -> int:
    if not CHAIN.exists():
        raise FileNotFoundError(CHAIN)
    dar_source = ROOT / "data" / "processed" / "HRCA_ANCESTRY_DAR.tsv"
    ocr_source = ROOT / "data" / "processed" / "HRCA_UNION_OCR.tsv"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    QC_OUT.parent.mkdir(parents=True, exist_ok=True)
    lo = LiftOver(str(CHAIN))
    dar_counts = process_dar(lo, dar_source, OUT_DIR / "HRCA_ANCESTRY_DAR_GRCh37.tsv")
    ocr_counts = process_union_ocr(lo, ocr_source, OUT_DIR / "HRCA_UNION_OCR_GRCh37.tsv")
    rows = []
    for resource, counts in [("HRCA_ANCESTRY_DAR", dar_counts), ("HRCA_UNION_OCR", ocr_counts)]:
        mapped = sum(counts[k] for k in ("MAPPED_WIDTH_PRESERVED", "MAPPED_WIDTH_CHANGED"))
        preserved = counts["MAPPED_WIDTH_PRESERVED"]
        n = counts["n_input"]
        rows.append({
            "resource": resource,
            "source_build": "hg38",
            "target_build": "GRCh37.p13 (hg19 coordinate convention)",
            "n_input": n,
            "n_mapped": mapped,
            "n_width_preserved": preserved,
            "mapping_rate": f"{mapped / n if n else 0.0:.8f}",
            "width_preservation_rate": f"{preserved / mapped if mapped else 0.0:.8f}",
            "unmapped_or_ambiguous_n": n - mapped,
            "status": "READY" if mapped == n and preserved == mapped else "REVIEW_REQUIRED",
        })
    with QC_OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
