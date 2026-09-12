#!/usr/bin/env python3
"""Count GRCh37-anchored GWAS variants in lifted HRCA intervals."""

from __future__ import annotations

import csv
from bisect import bisect_left, bisect_right
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Tuple

import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "data" / "processed" / "reference_anchored" / "CANONICAL_VARIANT_MAP.parquet"
DAR = ROOT / "data" / "processed" / "reference_anchored" / "HRCA_ANCESTRY_DAR_GRCh37.tsv"
OCR = ROOT / "data" / "processed" / "reference_anchored" / "HRCA_UNION_OCR_GRCh37.tsv"
OUT = ROOT / "results" / "phase1c" / "BUILD_RESOLVED_SNP_COUNTS.tsv"


def load_variants() -> Dict[str, List[int]]:
    positions: DefaultDict[str, List[int]] = defaultdict(list)
    for batch in pq.ParquetFile(MAP).iter_batches(columns=["canonical_chr", "canonical_pos", "mapping_status"], batch_size=200_000):
        data = batch.to_pydict()
        for chrom, pos, status in zip(data["canonical_chr"], data["canonical_pos"], data["mapping_status"]):
            if status == "UNIQUE_RSID_ALLELE_ANCHORED" and chrom and pos is not None:
                label = str(chrom)
                if not label.startswith("chr"):
                    label = f"chr{label}"
                positions[label].append(int(pos))
    for chrom in positions:
        positions[chrom].sort()
    return dict(positions)


def merge_intervals(intervals: Iterable[Tuple[int, int]]) -> List[Tuple[int, int]]:
    ordered = sorted(intervals)
    if not ordered:
        return []
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        old_start, old_end = merged[-1]
        if start <= old_end + 1:
            merged[-1] = (old_start, max(old_end, end))
        else:
            merged.append((start, end))
    return merged


def count_for_intervals(positions: Dict[str, List[int]], intervals: Dict[str, List[Tuple[int, int]]]) -> int:
    total = 0
    for chrom, values in intervals.items():
        pos = positions.get(chrom, [])
        for start, end in merge_intervals(values):
            total += bisect_right(pos, end) - bisect_left(pos, start)
    return total


def read_dar() -> Dict[Tuple[str, str], Dict[str, object]]:
    groups: Dict[Tuple[str, str], Dict[str, object]] = {}
    with DAR.open("r", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (row["cell_class"], row["self_reported_ethnicity"])
            item = groups.setdefault(key, {"input": 0, "mapped": 0, "intervals": defaultdict(list)})
            item["input"] += 1
            if row["liftover_status"].startswith("MAPPED"):
                item["mapped"] += 1
                item["intervals"][row["canonical_seqnames"]].append((int(row["canonical_start"]), int(row["canonical_end"])))
    return groups


def read_ocr() -> Dict[str, object]:
    item: Dict[str, object] = {"input": 0, "mapped": 0, "intervals": defaultdict(list)}
    with OCR.open("r", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            item["input"] += 1
            if row["liftover_status"].startswith("MAPPED"):
                item["mapped"] += 1
                item["intervals"][row["canonical_seqnames"]].append((int(row["canonical_start"]), int(row["canonical_end"])))
    return item


def aggregate_dar(groups: Dict[Tuple[str, str], Dict[str, object]], group: str, ethnicity: str) -> Dict[str, object]:
    item: Dict[str, object] = {"input": 0, "mapped": 0, "intervals": defaultdict(list)}
    for (cell_class, eth), source in groups.items():
        if group != "ALL" and cell_class != group:
            continue
        if ethnicity != "ALL" and eth != ethnicity:
            continue
        item["input"] += source["input"]
        item["mapped"] += source["mapped"]
        for chrom, intervals in source["intervals"].items():
            item["intervals"][chrom].extend(intervals)
    return item


def usable_status(n_overlapping: int) -> str:
    if n_overlapping > 5000:
        return "STRONG"
    if n_overlapping >= 1000:
        return "CONDITIONAL"
    return "SPARSE"


def main() -> int:
    positions = load_variants()
    n_variants = sum(len(v) for v in positions.values())
    rows: List[Dict[str, object]] = []
    dar_groups = read_dar()
    dar_rows = []
    for (cell_class, ethnicity), item in sorted(dar_groups.items()):
        intervals = item["intervals"]
        merged_n = sum(len(merge_intervals(v)) for v in intervals.values())
        overlap = count_for_intervals(positions, intervals)
        dar_rows.append({
            "resource": "HRCA_ANCESTRY_DAR",
            "group": cell_class,
            "ethnicity": ethnicity,
            "n_anchored_gwas_variants": n_variants,
            "n_intervals_input": item["input"],
            "n_intervals_mapped": item["mapped"],
            "n_intervals_merged": merged_n,
            "n_overlapping_variants": overlap,
            "variant_overlap_rate": f"{overlap / n_variants if n_variants else 0.0:.8f}",
            "usable_snp_status": usable_status(overlap),
        })
    for ethnicity in sorted({eth for _, eth in dar_groups} | {"ALL"}):
        item = aggregate_dar(dar_groups, "ALL", ethnicity)
        intervals = item["intervals"]
        merged_n = sum(len(merge_intervals(v)) for v in intervals.values())
        overlap = count_for_intervals(positions, intervals)
        dar_rows.append({
            "resource": "HRCA_ANCESTRY_DAR",
            "group": "ALL",
            "ethnicity": ethnicity,
            "n_anchored_gwas_variants": n_variants,
            "n_intervals_input": item["input"],
            "n_intervals_mapped": item["mapped"],
            "n_intervals_merged": merged_n,
            "n_overlapping_variants": overlap,
            "variant_overlap_rate": f"{overlap / n_variants if n_variants else 0.0:.8f}",
            "usable_snp_status": usable_status(overlap),
        })
    rows.extend(dar_rows)
    item = read_ocr()
    intervals = item["intervals"]
    merged_n = sum(len(merge_intervals(v)) for v in intervals.values())
    overlap = count_for_intervals(positions, intervals)
    rows.append({
        "resource": "HRCA_UNION_OCR",
        "group": "ALL",
        "ethnicity": "ALL",
        "n_anchored_gwas_variants": n_variants,
        "n_intervals_input": item["input"],
        "n_intervals_mapped": item["mapped"],
        "n_intervals_merged": merged_n,
        "n_overlapping_variants": overlap,
        "variant_overlap_rate": f"{overlap / n_variants if n_variants else 0.0:.8f}",
        "usable_snp_status": "NOT_APPLICABLE",
    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
