#!/usr/bin/env bash
set -euo pipefail

workspace_dir="$(cd "$(dirname "$0")/../.." && pwd)"
raw_dir="$workspace_dir/data/raw/ld_reference"
mkdir -p "$raw_dir"

record="https://zenodo.org/records/8292725/files"

download_checked() {
  local file="$1"
  local md5_expected="$2"
  local url="$record/$file?download=1"
  local out="$raw_dir/$file"

  if [[ -f "$out" ]] && [[ "$(md5 -q "$out")" == "$md5_expected" ]]; then
    echo "VALID $file"
    return
  fi

  echo "DOWNLOAD $file"
  aria2c \
    --continue=true \
    --allow-overwrite=true \
    --auto-file-renaming=false \
    --file-allocation=none \
    --check-integrity=true \
    --checksum="md5=$md5_expected" \
    --max-tries=20 \
    --retry-wait=15 \
    --connect-timeout=30 \
    --timeout=60 \
    -x 8 -s 8 -k 8M \
    --dir="$raw_dir" \
    --out="$file" \
    "$url"
  [[ "$(md5 -q "$out")" == "$md5_expected" ]]
}

download_checked "1000G_Phase3_plinkfiles.tgz" "a7773ab485827b533cb300c76356d76b"
download_checked "1000G_Phase3_EAS_plinkfiles.tgz" "abf52fba6416622ea0757ca9aca51a87"
download_checked "hm3_no_MHC.list.txt" "65a34c68833eb4a764d0707b5505b508"

echo "S-LDXR public reference inputs are complete and MD5-verified."
