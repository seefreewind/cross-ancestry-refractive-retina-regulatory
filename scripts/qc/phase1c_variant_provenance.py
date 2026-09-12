#!/usr/bin/env python3
"""Phase 1C rsID coverage and empirical dual-assembly audit.

This script deliberately separates:
1. raw-file marker coverage;
2. empirical comparison of released CHR/POS with official dbSNP placements;
3. downstream reference anchoring, which is handled only after the formal LD
   reference has been frozen.

The dbSNP VCFs are official NCBI Human Build 151 common-SNP placements for
GRCh37.p13 and GRCh38.p7. The script never infers a build from coordinates
alone and never edits raw GWAS or Phase 0 outputs.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import heapq
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "phase1c"
INTERIM = ROOT / "data" / "interim" / "phase1c"
DBSNP = ROOT / "data" / "raw" / "dbsnp_b151"

DATASETS = {
    "EUR": ROOT / "data" / "raw" / "gwas" / "EUR_meta_no23andMe.fastGWAz",
    "EAS": ROOT / "data" / "raw" / "gwas" / "EAS_meta.fastGWAz",
    "AFR": ROOT / "data" / "raw" / "gwas" / "AFR_meta.fastGWAz",
    "CROSS": ROOT / "data" / "raw" / "gwas" / "Cross_ancestry_EUR_EAS_AFR_no23andMe",
}

VCFS = {
    "GRCh37": DBSNP / "common_all_GRCh37p13.vcf.gz",
    "GRCh38": DBSNP / "common_all_GRCh38p7.vcf.gz",
}

RS_RE = re.compile(r"^rs[0-9]+$")
DNA = set("ACGT")
COMPLEMENT = str.maketrans("ACGT", "TGCA")


@dataclass(frozen=True)
class Variant:
    dataset: str
    rsid: str
    chr: str
    pos: int
    a1: str
    a2: str
    role: str


def is_valid_rsid(value: str) -> bool:
    return bool(RS_RE.fullmatch(value))


def is_biallelic_snp(a1: str, a2: str) -> bool:
    return len(a1) == 1 and len(a2) == 1 and a1 in DNA and a2 in DNA and a1 != a2


def allele_compatible(raw_a1: str, raw_a2: str, ref: str, alt: str) -> Tuple[bool, bool, bool]:
    """Return compatible, allele_flip, strand_resolved."""
    raw_a1, raw_a2, ref, alt = raw_a1.upper(), raw_a2.upper(), ref.upper(), alt.upper()
    if len(ref) != 1 or len(alt) != 1 or "," in alt:
        return False, False, False
    if {raw_a1, raw_a2} == {ref, alt}:
        return True, raw_a1 == alt and raw_a2 == ref, False
    comp1, comp2 = raw_a1.translate(COMPLEMENT), raw_a2.translate(COMPLEMENT)
    if {comp1, comp2} == {ref, alt}:
        return True, comp1 == alt and comp2 == ref, True
    return False, False, False


def read_hm3_rsids() -> set[str]:
    """Read the rsID universe from the existing generic HapMap3 LDSC files."""
    rsids: set[str] = set()
    paths = sorted((ROOT / "data" / "interim" / "ld_reference" / "generic_ldscore" / "LDscore").glob("LDscore.*.l2.ldscore.gz"))
    if not paths:
        return rsids
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            header = handle.readline()
            for line in handle:
                parts = line.rstrip("\n").split("\t")
                if len(parts) >= 2 and is_valid_rsid(parts[1]):
                    rsids.add(parts[1])
    return rsids


def parse_header(line: str) -> Dict[str, int]:
    fields = line.rstrip("\n").split()
    return {field: i for i, field in enumerate(fields)}


def iter_gwas_rows(path: Path) -> Iterator[Tuple[Dict[str, int], List[str]]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        header_line = handle.readline()
        if not header_line:
            raise ValueError(f"Empty GWAS file: {path}")
        header = parse_header(header_line)
        for line in handle:
            if line.strip():
                yield header, line.rstrip("\n").split()


def raw_fields(dataset: str, header: Dict[str, int], row: Sequence[str]) -> Tuple[str, str, str, str, str, Optional[int]]:
    marker_col = "SNP" if dataset != "CROSS" else "MarkerName"
    a1_col = "A1" if dataset != "CROSS" else "Allele1"
    a2_col = "A2" if dataset != "CROSS" else "Allele2"
    rsid = row[header[marker_col]]
    a1 = row[header[a1_col]].upper()
    a2 = row[header[a2_col]].upper()
    if dataset == "CROSS":
        return rsid, "", a1, a2, "", None
    chr_value = row[header["CHR"]]
    pos = int(float(row[header["POS"]]))
    return rsid, chr_value.removeprefix("chr"), a1, a2, chr_value, pos


def coverage_and_samples() -> Tuple[List[Variant], Dict[str, Dict[str, int]], set[str]]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    hm3 = read_hm3_rsids()
    metrics: Dict[str, Dict[str, int]] = {}
    samples: List[Variant] = []

    # Keep a deterministic hash-selected sample balanced across autosomes. The
    # selection is independent of p values and effect sizes.
    discovery_cap = 6000
    holdout_cap = 1000
    heaps: Dict[Tuple[str, str, str], List[Tuple[int, int, Variant]]] = defaultdict(list)
    counter = 0

    for dataset, path in DATASETS.items():
        counts = Counter()
        rsids: set[str] = set()
        duplicate_rsids: set[str] = set()
        hm3_valid: set[str] = set()
        if not path.exists():
            raise FileNotFoundError(path)
        header_seen = None
        for header, row in iter_gwas_rows(path):
            header_seen = header
            counts["total_variants"] += 1
            rsid, chr_value, a1, a2, _, pos = raw_fields(dataset, header, row)
            present = bool(rsid and rsid not in {".", "NA", "N/A", "nan"})
            valid = is_valid_rsid(rsid)
            if present:
                counts["rsid_present"] += 1
            if valid:
                counts["valid_rsid"] += 1
                if rsid in rsids:
                    duplicate_rsids.add(rsid)
                rsids.add(rsid)
            else:
                counts["non_rsid_marker"] += 1
            snp = is_biallelic_snp(a1, a2)
            if valid and snp:
                counts["biallelic_snp_with_rsid"] += 1
                if hm3 and rsid in hm3:
                    hm3_valid.add(rsid)
            elif valid:
                counts["indel_or_non_snp_with_rsid"] += 1
            if dataset != "CROSS" and valid and snp and pos is not None and chr_value in {str(i) for i in range(1, 23)}:
                counter += 1
                h = int.from_bytes(hashlib.sha256(f"{dataset}|{rsid}|{chr_value}|{pos}".encode()).digest()[:8], "big")
                role = "discovery" if h % 100 < 80 else "holdout"
                cap = discovery_cap if role == "discovery" else holdout_cap
                key = (dataset, role, chr_value)
                heap = heaps[key]
                item = (-h, counter, Variant(dataset, rsid, chr_value, pos, a1, a2, role))
                if len(heap) < cap:
                    heapq.heappush(heap, item)
                elif h < -heap[0][0]:
                    heapq.heapreplace(heap, item)
        counts["unique_valid_rsid"] = len(rsids)
        counts["duplicated_rsid_n"] = len(duplicate_rsids)
        counts["hm3_reference_rsid_n"] = len(hm3)
        counts["hm3_overlap_valid_rsid_n"] = len(hm3_valid)
        counts["hm3_overlap_rsid_coverage"] = 1 if hm3_valid else 0
        metrics[dataset] = dict(counts)

    for key, heap in heaps.items():
        samples.extend(item[2] for item in sorted(heap, key=lambda item: (-item[0], item[1])))

    out = RESULTS / "GWAS_RSID_COVERAGE.tsv"
    columns = [
        "dataset", "total_variants", "rsid_present", "valid_rsid", "unique_valid_rsid",
        "duplicated_rsid_n", "non_rsid_marker", "biallelic_snp_with_rsid",
        "indel_or_non_snp_with_rsid", "hm3_reference_rsid_n", "hm3_overlap_valid_rsid_n",
        "hm3_overlap_rsid_coverage", "rsid_coverage", "biallelic_snp_rsid_coverage",
        "rsid_rescue_status",
    ]
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for dataset, counts in metrics.items():
            denominator = counts.get("total_variants", 0)
            snp_denominator = counts.get("valid_rsid", 0)
            rsid_coverage = counts.get("valid_rsid", 0) / denominator if denominator else 0.0
            coverage = counts.get("biallelic_snp_with_rsid", 0) / snp_denominator if snp_denominator else 0.0
            counts = dict(counts)
            counts["non_rsid_marker"] = counts.get("non_rsid_marker", 0)
            counts["rsid_coverage"] = f"{rsid_coverage:.8f}"
            counts["biallelic_snp_rsid_coverage"] = f"{coverage:.8f}"
            counts["rsid_rescue_status"] = "PASS" if rsid_coverage >= 0.95 else "CONDITIONAL" if rsid_coverage >= 0.90 else "INVESTIGATE"
            writer.writerow({"dataset": dataset, **counts})
    return samples, metrics, hm3


def vcf_contigs(vcf: Path) -> List[str]:
    result = subprocess.run(["bcftools", "view", "-h", str(vcf)], check=True, capture_output=True, text=True)
    contigs = []
    for line in result.stdout.splitlines():
        if line.startswith("##contig=<ID="):
            contigs.append(line.split("##contig=<ID=", 1)[1].split(",", 1)[0].split(">", 1)[0])
    return contigs


def contig_for_chrom(chrom: str, contigs: Sequence[str]) -> str:
    if chrom in contigs:
        return chrom
    for prefix in ("chr",):
        if prefix + chrom in contigs:
            return prefix + chrom
    acc37 = {str(i): f"NC_{i:06d}.{10 if i == 1 else 11 if i <= 22 else 7}" for i in range(1, 23)}
    acc38 = {str(i): f"NC_{i:06d}.{11 if i == 1 else 12 if i <= 22 else 7}" for i in range(1, 23)}
    for accession_map in (acc37, acc38):
        if accession_map.get(chrom) in contigs:
            return accession_map[chrom]
    raise ValueError(f"Cannot map chromosome {chrom} to VCF contigs")


def normalize_chrom(chrom: str) -> str:
    """Normalize numeric, chr-prefixed, and RefSeq chromosome labels."""
    value = chrom.strip()
    if value.startswith("chr"):
        value = value[3:]
    match = re.fullmatch(r"NC_(\d{6})\.\d+", value)
    if match:
        return str(int(match.group(1)))
    return value


def scan_vcf_for_rsids(vcf: Path, target_rsids: set[str]) -> Dict[str, List[Tuple[str, int, str, str]]]:
    """Scan an official VCF once and keep only placements for target rsIDs."""
    placements: Dict[str, List[Tuple[str, int, str, str]]] = defaultdict(list)
    cmd = ["bcftools", "query", "-f", "%CHROM\\t%POS\\t%ID\\t%REF\\t%ALT\\n", str(vcf)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    assert proc.stdout is not None
    for line in proc.stdout:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 5:
            continue
        chrom, pos, ids, ref, alt = parts
        if ids == ".":
            continue
        for rsid in ids.split(";"):
            if rsid in target_rsids:
                placements[rsid].append((chrom, int(pos), ref.upper(), alt.upper()))
    stderr = proc.stderr.read() if proc.stderr is not None else ""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"bcftools query failed for {vcf}: {stderr[-2000:]}")
    return placements


def choose_placement(raw: Variant, records: Sequence[Tuple[str, int, str, str]]) -> Tuple[Optional[Tuple[str, int, str, str]], str, bool, bool]:
    compatible = []
    for record in records:
        chrom, pos, ref, alt = record
        ok, flip, strand = allele_compatible(raw.a1, raw.a2, ref, alt)
        if ok and chrom and not chrom.startswith(("NW_", "NT_", "GL", "KI")):
            compatible.append((record, flip, strand))
    if len(compatible) == 1:
        record, flip, strand = compatible[0]
        return record, "UNIQUE_ALLELE_COMPATIBLE", flip, strand
    if len(compatible) > 1:
        return None, "AMBIGUOUS_MULTIPLE_ALLELE_COMPATIBLE", False, False
    if records:
        return None, "PLACEMENT_ALLELE_MISMATCH", False, False
    return None, "MISSING_PLACEMENT", False, False


def concordance() -> None:
    samples, _, _ = coverage_and_samples()
    target_rsids = {variant.rsid for variant in samples}
    if not target_rsids:
        raise RuntimeError("No sample variants available for empirical audit")
    all_placements: Dict[str, Dict[str, List[Tuple[str, int, str, str]]]] = {}
    for assembly, vcf in VCFS.items():
        if not vcf.exists():
            raise FileNotFoundError(vcf)
        all_placements[assembly] = scan_vcf_for_rsids(vcf, target_rsids)

    rows = []
    by_chr = []
    for dataset in ("EUR", "EAS", "AFR"):
        dataset_samples = [v for v in samples if v.dataset == dataset]
        informative = []
        for variant in dataset_samples:
            rec37, status37, flip37, strand37 = choose_placement(variant, all_placements["GRCh37"].get(variant.rsid, []))
            rec38, status38, flip38, strand38 = choose_placement(variant, all_placements["GRCh38"].get(variant.rsid, []))
            if rec37 is None or rec38 is None:
                continue
            informative.append((variant, rec37, rec38, flip37, strand37, flip38, strand38, status37, status38))
        for assembly, idx in (("GRCh37", 1), ("GRCh38", 2)):
            n = len(informative)
            exact_chr = 0
            exact_pos = 0
            allele_n = 0
            mismatch = 0
            role_counts = Counter()
            for item in informative:
                variant = item[0]
                record = item[idx]
                vcf_chr, vcf_pos, ref, alt = record
                raw_chr = variant.chr
                normalized = normalize_chrom(vcf_chr)
                if normalized.isdigit() and normalized == raw_chr:
                    exact_chr += 1
                    if vcf_pos == variant.pos:
                        exact_pos += 1
                ok, _, _ = allele_compatible(variant.a1, variant.a2, ref, alt)
                if ok:
                    allele_n += 1
                else:
                    mismatch += 1
                role_counts[variant.role] += 1
            holdout = [item for item in informative if item[0].role == "holdout"]
            holdout_exact_pos = sum(
                1 for item in holdout
                if item[idx][1] == item[0].pos and normalize_chrom(item[idx][0]) == item[0].chr
            )
            holdout_allele = sum(
                1 for item in holdout
                if allele_compatible(item[0].a1, item[0].a2, item[idx][2], item[idx][3])[0]
            )
            rows.append({
                "dataset": dataset,
                "assembly": assembly,
                "sample_design": "deterministic_hash_discovery_holdout",
                "n_informative": n,
                "n_discovery": role_counts["discovery"],
                "n_holdout": role_counts["holdout"],
                "exact_chromosome_match": exact_chr,
                "exact_position_match": exact_pos,
                "chr_pos_concordance": exact_pos / n if n else 0.0,
                "allele_compatible_n": allele_n,
                "allele_compatible_concordance": allele_n / n if n else 0.0,
                "mismatch_n": mismatch,
                "missing_placement_n": len(dataset_samples) - n,
                "holdout_n": len(holdout),
                "holdout_chr_pos_concordance": holdout_exact_pos / len(holdout) if holdout else 0.0,
                "holdout_allele_compatible_concordance": holdout_allele / len(holdout) if holdout else 0.0,
            })
            for chrom in [str(i) for i in range(1, 23)]:
                subset = [item for item in informative if item[0].chr == chrom]
                exact_pos_chr = sum(1 for item in subset if item[idx][1] == item[0].pos and normalize_chrom(item[idx][0]) == chrom)
                allele_chr = sum(1 for item in subset if allele_compatible(item[0].a1, item[0].a2, item[idx][2], item[idx][3])[0])
                by_chr.append({
                    "dataset": dataset,
                    "assembly": assembly,
                    "chromosome": chrom,
                    "n_informative": len(subset),
                    "exact_position_match": exact_pos_chr,
                    "chr_pos_concordance": exact_pos_chr / len(subset) if subset else 0.0,
                    "allele_compatible_n": allele_chr,
                    "allele_compatible_concordance": allele_chr / len(subset) if subset else 0.0,
                })

    write_tsv(RESULTS / "EMPIRICAL_BUILD_CONCORDANCE.tsv", rows)
    write_tsv(RESULTS / "EMPIRICAL_BUILD_BY_CHROMOSOME.tsv", by_chr)


def write_tsv(path: Path, rows: Sequence[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["coverage", "empirical"], required=True)
    args = parser.parse_args()
    if args.stage == "coverage":
        coverage_and_samples()
    else:
        concordance()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
