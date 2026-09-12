#!/usr/bin/env python3
"""Build the Phase 1C GRCh37 reference-anchored variant map.

The raw GWAS coordinates are used only to create indexed candidate regions after
the empirical GRCh37 adjudication has passed. Variant identity is resolved by
rsID and allele compatibility against the frozen NCBI dbSNP Build 151 VCF.
"""

from __future__ import annotations

import csv
import gzip
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
HARMONIZED = ROOT / "data" / "processed" / "EUR_EAS_HARMONIZED.parquet"
DBSNP = ROOT / "data" / "raw" / "dbsnp_b151" / "common_all_GRCh37p13.vcf.gz"
LD_DIR = ROOT / "data" / "interim" / "ld_reference" / "generic_ldscore" / "LDscore"
OUT_MAP = ROOT / "data" / "processed" / "reference_anchored" / "CANONICAL_VARIANT_MAP.parquet"
OUT_LD = ROOT / "results" / "phase1c" / "LD_REFERENCE_VARIANT_ANCHORING.tsv"

DNA = set("ACGT")
COMPLEMENT = str.maketrans("ACGT", "TGCA")
RS_RE = re.compile(r"^rs[0-9]+$")


def normalize_chrom(value: str) -> str:
    value = value.strip()
    if value.startswith("chr"):
        value = value[3:]
    match = re.fullmatch(r"NC_(\d{6})\.\d+", value)
    if match:
        return str(int(match.group(1)))
    return value


def allele_matches(raw_a1: str, raw_a2: str, ref: str, alt: str) -> Tuple[bool, bool, bool]:
    raw_a1, raw_a2 = raw_a1.upper(), raw_a2.upper()
    ref, alt = ref.upper(), alt.upper()
    if len(ref) != 1 or len(alt) != 1 or ref not in DNA or alt not in DNA:
        return False, False, False
    if {raw_a1, raw_a2} == {ref, alt}:
        return True, raw_a1 == alt and raw_a2 == ref, False
    comp1 = raw_a1.translate(COMPLEMENT)
    comp2 = raw_a2.translate(COMPLEMENT)
    if {comp1, comp2} == {ref, alt}:
        return True, comp1 == alt and comp2 == ref, True
    return False, False, False


def iter_harmonized() -> Iterator[Dict[str, object]]:
    parquet = pq.ParquetFile(HARMONIZED)
    columns = ["variant_key", "CHR", "POS", "SNP_EUR", "A1_EUR", "A2_EUR"]
    for batch in parquet.iter_batches(batch_size=100_000, columns=columns):
        data = batch.to_pydict()
        for values in zip(*(data[column] for column in columns)):
            variant_key, chrom, pos, rsid, a1, a2 = values
            if not isinstance(rsid, str) or not RS_RE.fullmatch(rsid):
                continue
            yield {
                "variant_key": str(variant_key),
                "chrom": normalize_chrom(str(chrom)),
                "pos": int(pos),
                "rsid": rsid,
                "a1": str(a1).upper(),
                "a2": str(a2).upper(),
            }


def iter_hm3() -> Iterator[Dict[str, object]]:
    paths = sorted(LD_DIR.glob("LDscore.*.l2.ldscore.gz"))
    if not paths:
        raise FileNotFoundError(f"No generic LDscore files in {LD_DIR}")
    for path in paths:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                rsid = row.get("SNP", "")
                if not RS_RE.fullmatch(rsid):
                    continue
                yield {
                    "variant_key": f"LD|{row['CHR']}:{row['BP']}|{rsid}",
                    "chrom": normalize_chrom(row["CHR"]),
                    "pos": int(row["BP"]),
                    "rsid": rsid,
                    "a1": ".",
                    "a2": ".",
                }


def write_targets(path: Path) -> Tuple[int, int]:
    n_gwas = 0
    n_ld = 0
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        for row in iter_harmonized():
            writer.writerow([row["chrom"], row["pos"], row["rsid"], "GWAS", row["variant_key"], row["a1"], row["a2"]])
            n_gwas += 1
        for row in iter_hm3():
            writer.writerow([row["chrom"], row["pos"], row["rsid"], "LD", row["variant_key"], ".", "."])
            n_ld += 1
    return n_gwas, n_ld


def sort_targets(raw: Path, sorted_path: Path, bed_path: Path) -> None:
    subprocess.run(
        ["sort", "-t", "\t", "-k1,1n", "-k2,2n", "-k3,3", str(raw)],
        check=True,
        stdout=sorted_path.open("w", encoding="utf-8"),
    )
    subprocess.run(
        ["awk", "-F\\t", "BEGIN{OFS=\"\\t\"}{print $1,$2-1,$2}", str(sorted_path)],
        check=True,
        stdout=bed_path.open("w", encoding="utf-8"),
    )
    unique_bed = bed_path.with_suffix(".unique.bed")
    subprocess.run(["sort", "-t", "\t", "-k1,1n", "-k2,2n", "-k3,3n", "-u", str(bed_path)], check=True, stdout=unique_bed.open("w", encoding="utf-8"))
    unique_bed.replace(bed_path)


def parse_vcf_line(line: str) -> Tuple[str, int, str, List[str], str]:
    chrom, pos, ids, ref, alt = line.rstrip("\n").split("\t")
    return normalize_chrom(chrom), int(pos), ids, alt.split(","), ref.upper()


def vcf_records(vcf: Path, bed: Path) -> Iterator[Tuple[str, int, str, List[str], str]]:
    cmd = ["bcftools", "query", "-R", str(bed), "-f", "%CHROM\\t%POS\\t%ID\\t%ALT\\t%REF\\n", str(vcf)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    assert proc.stdout is not None
    for line in proc.stdout:
        if line.strip():
            yield parse_vcf_line(line)
    stderr = proc.stderr.read() if proc.stderr is not None else ""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"bcftools query failed: {stderr[-2000:]}")


def choose_gwas(row: Dict[str, str], records: Sequence[Tuple[str, int, str, List[str], str]]) -> Dict[str, object]:
    candidates = []
    for chrom, pos, ids, alts, ref in records:
        if row["rsid"] not in ids.split(";"):
            continue
        for alt in alts:
            ok, flip, strand = allele_matches(row["a1"], row["a2"], ref, alt)
            if ok:
                candidate = (chrom, pos, ref, alt, flip, strand)
                if candidate not in candidates:
                    candidates.append(candidate)
    if len(candidates) == 1:
        chrom, pos, ref, alt, flip, strand = candidates[0]
        return {
            "canonical_chr": chrom,
            "canonical_pos": pos,
            "canonical_ref": ref,
            "canonical_alt": alt,
            "allele_compatible": True,
            "allele_flip": flip,
            "strand_resolved": strand,
            "mapping_status": "UNIQUE_RSID_ALLELE_ANCHORED",
        }
    status = "MISSING_RSID_PLACEMENT" if not candidates else "AMBIGUOUS_RSID_ALLELE_PLACEMENT"
    return {
        "canonical_chr": "",
        "canonical_pos": None,
        "canonical_ref": "",
        "canonical_alt": "",
        "allele_compatible": False,
        "allele_flip": False,
        "strand_resolved": False,
        "mapping_status": status,
    }


def choose_ld(row: Dict[str, str], records: Sequence[Tuple[str, int, str, List[str], str]]) -> bool:
    return sum(1 for record in records if row["rsid"] in record[2].split(";")) == 1


def target_key(row: Dict[str, str]) -> Tuple[int, int]:
    return int(row["chrom"]), int(row["pos"])


def write_map_and_summary(sorted_targets: Path, bed: Path, workdir: Path, n_gwas: int, n_ld: int) -> None:
    map_tmp = workdir / "CANONICAL_VARIANT_MAP.tmp.parquet"
    schema = pa.schema([
        ("variant_key", pa.string()), ("raw_chr", pa.string()), ("raw_pos", pa.int64()),
        ("rsid", pa.string()), ("raw_a1", pa.string()), ("raw_a2", pa.string()),
        ("canonical_build", pa.string()), ("canonical_chr", pa.string()), ("canonical_pos", pa.int64()),
        ("canonical_ref", pa.string()), ("canonical_alt", pa.string()),
        ("allele_compatible", pa.bool_()), ("allele_flip", pa.bool_()),
        ("strand_resolved", pa.bool_()), ("mapping_status", pa.string()),
        ("source_reference", pa.string()),
    ])
    writer = pq.ParquetWriter(map_tmp, schema, compression="zstd")
    map_rows: List[Dict[str, object]] = []
    gwas_total = gwas_anchored = 0
    ld_total = ld_anchored = 0
    with sorted_targets.open("r", encoding="utf-8") as targets:
        target_iter = csv.reader(targets, delimiter="\t")
        current_target = next(target_iter, None)
        records = vcf_records(DBSNP, bed)
        current_record = next(records, None)

        def record_key(record: Tuple[str, int, str, List[str], str]) -> Tuple[int, int]:
            return int(record[0]), int(record[1])

        while current_target is not None:
            row = {
                "chrom": current_target[0], "pos": current_target[1], "rsid": current_target[2],
                "kind": current_target[3], "variant_key": current_target[4],
                "a1": current_target[5], "a2": current_target[6],
            }
            key = target_key(row)
            while current_record is not None and record_key(current_record) < key:
                current_record = next(records, None)
            at_position = []
            while current_record is not None and record_key(current_record) == key:
                at_position.append(current_record)
                current_record = next(records, None)
            if row["kind"] == "GWAS":
                result = choose_gwas(row, at_position)
                gwas_total += 1
                if result["mapping_status"] == "UNIQUE_RSID_ALLELE_ANCHORED":
                    gwas_anchored += 1
                map_rows.append({
                    "variant_key": row["variant_key"], "raw_chr": row["chrom"], "raw_pos": int(row["pos"]),
                    "rsid": row["rsid"], "raw_a1": row["a1"], "raw_a2": row["a2"],
                    "canonical_build": "GRCh37.p13", **result,
                    "source_reference": "NCBI dbSNP Build 151 common_all GRCh37.p13",
                })
                if len(map_rows) >= 100_000:
                    writer.write_table(pa.Table.from_pylist(map_rows, schema=schema))
                    map_rows.clear()
            else:
                ld_total += 1
                if choose_ld(row, at_position):
                    ld_anchored += 1
            current_target = next(target_iter, None)
    if map_rows:
        writer.write_table(pa.Table.from_pylist(map_rows, schema=schema))
    writer.close()
    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    map_tmp.replace(OUT_MAP)

    rate = ld_anchored / ld_total if ld_total else 0.0
    status = "STRONG" if rate >= 0.98 else "CONDITIONAL" if rate >= 0.95 else "FAIL"
    OUT_LD.parent.mkdir(parents=True, exist_ok=True)
    with OUT_LD.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["reference", "n_total", "n_anchored", "anchoring_rate", "threshold", "status"], delimiter="\t")
        writer.writeheader()
        writer.writerow({"reference": "EUR_EAS_HARMONIZED_GWAS", "n_total": gwas_total, "n_anchored": gwas_anchored, "anchoring_rate": f"{gwas_anchored / gwas_total if gwas_total else 0.0:.8f}", "threshold": ">=98% STRONG; 95-98% CONDITIONAL; <95% FAIL", "status": "STRONG" if gwas_anchored / gwas_total >= 0.98 else "CONDITIONAL" if gwas_anchored / gwas_total >= 0.95 else "FAIL"})
        writer.writerow({"reference": "GENERIC_LDSC_HM3", "n_total": ld_total, "n_anchored": ld_anchored, "anchoring_rate": f"{rate:.8f}", "threshold": ">=98% STRONG; 95-98% CONDITIONAL; <95% FAIL", "status": status})


def sort_by_rsid(raw: Path, sorted_path: Path) -> None:
    with sorted_path.open("w", encoding="utf-8") as handle:
        subprocess.run(
            ["sort", "-t", "\t", "-k3,3", "-k4,4", "-k1,1n", "-k2,2n", str(raw)],
            check=True,
            stdout=handle,
        )


def load_target_sets(raw: Path) -> Tuple[set[str], set[str], Dict[str, Tuple[str, str]]]:
    gwas_rsids: set[str] = set()
    ld_rsids: set[str] = set()
    gwas_alleles: Dict[str, Tuple[str, str]] = {}
    with raw.open("r", encoding="utf-8") as handle:
        for fields in csv.reader(handle, delimiter="\t"):
            if not fields:
                continue
            rsid, kind, a1, a2 = fields[2], fields[3], fields[5], fields[6]
            if kind == "GWAS":
                gwas_rsids.add(rsid)
                pair = (a1, a2)
                if rsid in gwas_alleles and gwas_alleles[rsid] != pair:
                    gwas_alleles[rsid] = ("", "")
                else:
                    gwas_alleles.setdefault(rsid, pair)
            else:
                ld_rsids.add(rsid)
    return gwas_rsids, ld_rsids, gwas_alleles


def scan_vcf_sequential(vcf: Path, gwas_rsids: set[str], ld_rsids: set[str], gwas_alleles: Dict[str, Tuple[str, str]], workdir: Path) -> Tuple[Path, Path]:
    candidate_hits = workdir / "gwas_candidate_hits.tsv"
    ld_hits = workdir / "ld_hits.tsv"
    cmd = ["bcftools", "query", "-f", "%CHROM\\t%POS\\t%ID\\t%ALT\\t%REF\\n", str(vcf)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    assert proc.stdout is not None
    with candidate_hits.open("w", encoding="utf-8", newline="") as gwas_out, ld_hits.open("w", encoding="utf-8", newline="") as ld_out:
        gwas_writer = csv.writer(gwas_out, delimiter="\t", lineterminator="\n")
        ld_writer = csv.writer(ld_out, delimiter="\t", lineterminator="\n")
        for line in proc.stdout:
            if not line.strip():
                continue
            chrom, pos, ids, alt_field, ref = line.rstrip("\n").split("\t")
            chrom = normalize_chrom(chrom)
            pos = int(pos)
            ref = ref.upper()
            ids_set = set(ids.split(";"))
            for rsid in ids_set.intersection(gwas_rsids):
                a1, a2 = gwas_alleles.get(rsid, ("", ""))
                for alt in alt_field.upper().split(","):
                    ok, flip, strand = allele_matches(a1, a2, ref, alt)
                    if ok:
                        gwas_writer.writerow([rsid, chrom, pos, ref, alt, int(flip), int(strand)])
            for rsid in ids_set.intersection(ld_rsids):
                ld_writer.writerow([rsid, chrom, pos])
    stderr = proc.stderr.read() if proc.stderr is not None else ""
    code = proc.wait()
    if code != 0:
        raise RuntimeError(f"bcftools query failed: {stderr[-2000:]}")
    return candidate_hits, ld_hits


def collapse_candidates(hits: Path, workdir: Path) -> Path:
    sorted_hits = workdir / "gwas_candidate_hits.sorted.tsv"
    with sorted_hits.open("w", encoding="utf-8") as handle:
        subprocess.run(["sort", "-t", "\t", "-k1,1", "-k2,2n", "-k3,3n", "-k4,4", "-k5,5", "-k6,6", "-k7,7", "-u", str(hits)], check=True, stdout=handle)
    chosen = workdir / "gwas_chosen.tsv"
    with sorted_hits.open("r", encoding="utf-8") as source, chosen.open("w", encoding="utf-8", newline="") as out:
        reader = csv.reader(source, delimiter="\t")
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        current_rsid = None
        candidates: List[List[str]] = []
        for row in reader:
            if current_rsid is not None and row[0] != current_rsid:
                writer.writerow([current_rsid, "UNIQUE_RSID_ALLELE_ANCHORED", *candidates[0]] if len(candidates) == 1 else [current_rsid, "AMBIGUOUS_RSID_ALLELE_PLACEMENT"])
                candidates = []
            current_rsid = row[0]
            candidates.append(row[1:])
        if current_rsid is not None:
            writer.writerow([current_rsid, "UNIQUE_RSID_ALLELE_ANCHORED", *candidates[0]] if len(candidates) == 1 else [current_rsid, "AMBIGUOUS_RSID_ALLELE_PLACEMENT"])
    return chosen


def collapse_ld_hits(hits: Path, workdir: Path) -> Path:
    sorted_hits = workdir / "ld_hits.sorted.tsv"
    with sorted_hits.open("w", encoding="utf-8") as handle:
        subprocess.run(["sort", "-t", "\t", "-k1,1", "-k2,2n", "-k3,3n", "-u", str(hits)], check=True, stdout=handle)
    chosen = workdir / "ld_chosen.tsv"
    with sorted_hits.open("r", encoding="utf-8") as source, chosen.open("w", encoding="utf-8", newline="") as out:
        reader = csv.reader(source, delimiter="\t")
        writer = csv.writer(out, delimiter="\t", lineterminator="\n")
        current_rsid = None
        n = 0
        for row in reader:
            if current_rsid is not None and row[0] != current_rsid:
                writer.writerow([current_rsid, n])
                n = 0
            current_rsid = row[0]
            n += 1
        if current_rsid is not None:
            writer.writerow([current_rsid, n])
    return chosen


def iter_lookup(path: Path) -> Iterator[List[str]]:
    with path.open("r", encoding="utf-8") as handle:
        for row in csv.reader(handle, delimiter="\t"):
            if row:
                yield row


def write_sequential_map_and_summary(sorted_targets: Path, workdir: Path, n_gwas: int, n_ld: int, chosen_gwas: Path, chosen_ld: Path) -> None:
    map_tmp = workdir / "CANONICAL_VARIANT_MAP.tmp.parquet"
    schema = pa.schema([
        ("variant_key", pa.string()), ("raw_chr", pa.string()), ("raw_pos", pa.int64()),
        ("rsid", pa.string()), ("raw_a1", pa.string()), ("raw_a2", pa.string()),
        ("canonical_build", pa.string()), ("canonical_chr", pa.string()), ("canonical_pos", pa.int64()),
        ("canonical_ref", pa.string()), ("canonical_alt", pa.string()),
        ("allele_compatible", pa.bool_()), ("allele_flip", pa.bool_()),
        ("strand_resolved", pa.bool_()), ("mapping_status", pa.string()),
        ("source_reference", pa.string()),
    ])
    parquet_writer = pq.ParquetWriter(map_tmp, schema, compression="zstd")
    map_rows: List[Dict[str, object]] = []
    gwas_anchored = 0
    ld_anchored = 0
    ld_lookup = iter_lookup(chosen_ld)
    current_ld = next(ld_lookup, None)
    gwas_lookup = iter_lookup(chosen_gwas)
    current_gwas = next(gwas_lookup, None)

    def write_gwas_row(row: List[str], chosen: Optional[List[str]]) -> None:
        nonlocal gwas_anchored
        if chosen is not None and chosen[1] == "UNIQUE_RSID_ALLELE_ANCHORED":
            gwas_anchored += 1
            result = {
                "canonical_chr": chosen[2], "canonical_pos": int(chosen[3]),
                "canonical_ref": chosen[4], "canonical_alt": chosen[5],
                "allele_compatible": True, "allele_flip": bool(int(chosen[6])),
                "strand_resolved": bool(int(chosen[7])), "mapping_status": chosen[1],
            }
        else:
            status = "MISSING_RSID_PLACEMENT" if chosen is None else chosen[1]
            result = {
                "canonical_chr": "", "canonical_pos": None, "canonical_ref": "", "canonical_alt": "",
                "allele_compatible": False, "allele_flip": False, "strand_resolved": False,
                "mapping_status": status,
            }
        map_rows.append({
            "variant_key": row[4], "raw_chr": row[0], "raw_pos": int(row[1]), "rsid": row[2],
            "raw_a1": row[5], "raw_a2": row[6], "canonical_build": "GRCh37.p13", **result,
            "source_reference": "NCBI dbSNP Build 151 common_all GRCh37.p13",
        })

    with sorted_targets.open("r", encoding="utf-8") as source:
        reader = csv.reader(source, delimiter="\t")
        current_target = next(reader, None)
        while current_target is not None:
            rsid = current_target[2]
            group = []
            while current_target is not None and current_target[2] == rsid:
                group.append(current_target)
                current_target = next(reader, None)
            while current_gwas is not None and current_gwas[0] < rsid:
                current_gwas = next(gwas_lookup, None)
            chosen = current_gwas if current_gwas is not None and current_gwas[0] == rsid else None
            while current_ld is not None and current_ld[0] < rsid:
                current_ld = next(ld_lookup, None)
            ld_count = int(current_ld[1]) if current_ld is not None and current_ld[0] == rsid else 0
            for row in group:
                if row[3] == "GWAS":
                    write_gwas_row(row, chosen)
                elif ld_count == 1:
                    ld_anchored += 1
                if len(map_rows) >= 100_000:
                    parquet_writer.write_table(pa.Table.from_pylist(map_rows, schema=schema))
                    map_rows.clear()
    if map_rows:
        parquet_writer.write_table(pa.Table.from_pylist(map_rows, schema=schema))
    parquet_writer.close()
    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    map_tmp.replace(OUT_MAP)

    gwas_rate = gwas_anchored / n_gwas if n_gwas else 0.0
    ld_rate = ld_anchored / n_ld if n_ld else 0.0
    status = "STRONG" if ld_rate >= 0.98 else "CONDITIONAL" if ld_rate >= 0.95 else "FAIL"
    with OUT_LD.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["reference", "n_total", "n_anchored", "anchoring_rate", "threshold", "status"], delimiter="\t")
        writer.writeheader()
        writer.writerow({"reference": "EUR_EAS_HARMONIZED_GWAS", "n_total": n_gwas, "n_anchored": gwas_anchored, "anchoring_rate": f"{gwas_rate:.8f}", "threshold": ">=98% STRONG; 95-98% CONDITIONAL; <95% FAIL", "status": "STRONG" if gwas_rate >= 0.98 else "CONDITIONAL" if gwas_rate >= 0.95 else "FAIL"})
        writer.writerow({"reference": "GENERIC_LDSC_HM3", "n_total": n_ld, "n_anchored": ld_anchored, "anchoring_rate": f"{ld_rate:.8f}", "threshold": ">=98% STRONG; 95-98% CONDITIONAL; <95% FAIL", "status": status})


def main() -> int:
    if not HARMONIZED.exists():
        raise FileNotFoundError(HARMONIZED)
    if not DBSNP.exists():
        raise FileNotFoundError(DBSNP)
    workdir = ROOT / "data" / "interim" / "phase1c"
    workdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="reference_anchor_", dir=workdir) as tmp:
        tmpdir = Path(tmp)
        raw = tmpdir / "targets.tsv"
        sorted_targets = tmpdir / "targets.sorted.tsv"
        n_gwas, n_ld = write_targets(raw)
        sort_by_rsid(raw, sorted_targets)
        gwas_rsids, ld_rsids, gwas_alleles = load_target_sets(raw)
        candidate_hits, ld_hits = scan_vcf_sequential(DBSNP, gwas_rsids, ld_rsids, gwas_alleles, tmpdir)
        chosen_gwas = collapse_candidates(candidate_hits, tmpdir)
        chosen_ld = collapse_ld_hits(ld_hits, tmpdir)
        write_sequential_map_and_summary(sorted_targets, tmpdir, n_gwas, n_ld, chosen_gwas, chosen_ld)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
