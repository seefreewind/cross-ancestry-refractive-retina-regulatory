#!/usr/bin/env bash
set -euo pipefail
workspace_dir="$(cd "$(dirname "$0")/../.." && pwd)"
out="$workspace_dir/data/raw/retina/HRCA_41588_2025_2454_MOESM4_retry1.xlsx"
url="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM4_ESM.xlsx"
echo "DOWNLOAD fresh retry -> $out"
curl --fail --location --retry 3 --retry-delay 2 --silent --show-error --output "$out" "$url"
unzip -t "$out" >/dev/null
echo "ZIP_VALID $out"
