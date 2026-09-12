#!/usr/bin/env bash
set -euo pipefail
workspace_dir="$(cd "$(dirname "$0")/../.." && pwd)"
retina_dir="$workspace_dir/data/raw/retina"
mkdir -p "$retina_dir"
download() {
  local url="$1"; local out="$2"
  echo "DOWNLOAD $url -> $out"
  curl --fail --location --retry 3 --retry-delay 2 --silent --show-error --continue-at - --output "$out" "$url"
}
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM1_ESM.pdf" "$retina_dir/HRCA_41588_2025_2454_MOESM1.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM2_ESM.pdf" "$retina_dir/HRCA_41588_2025_2454_MOESM2.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM3_ESM.pdf" "$retina_dir/HRCA_41588_2025_2454_MOESM3.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM4_ESM.xlsx" "$retina_dir/HRCA_41588_2025_2454_MOESM4.xlsx"
