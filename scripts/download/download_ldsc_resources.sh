#!/usr/bin/env bash
set -euo pipefail
workspace_dir="$(cd "$(dirname "$0")/../.." && pwd)"
ld_dir="$workspace_dir/data/raw/ld_reference"
mkdir -p "$ld_dir"
base="https://zenodo.org/records/10515792/files"
download() {
  local file="$1"
  local url="$base/$file?download=1"
  local out="$ld_dir/$file"
  echo "DOWNLOAD $file"
  curl --fail --location --retry 3 --retry-delay 2 --silent --show-error --continue-at - --output "$out" "$url"
}
download "1000G_Phase3_baselineLD_v2.2_ldscores.tgz"
download "1000G_Phase3_EAS_baselineLD_v2.2_ldscores.tgz"
download "1000G_Phase3_weights_hm3_no_MHC.tgz"
download "1000G_Phase3_EAS_weights_hm3_no_MHC.tgz"
download "1000G_Phase3_plinkfiles.tgz"
download "1000G_Phase3_EAS_plinkfiles.tgz"
