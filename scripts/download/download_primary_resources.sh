#!/usr/bin/env bash
set -euo pipefail

workspace_dir="$(cd "$(dirname "$0")/../.." && pwd)"
gwas_dir="$workspace_dir/data/raw/gwas"
retina_dir="$workspace_dir/data/raw/retina"
mkdir -p "$gwas_dir" "$retina_dir"

download() {
  local url="$1"
  local out="$2"
  if [[ -s "$out" ]]; then
    echo "RESUME/check existing: $out"
  fi
  echo "DOWNLOAD $url -> $out"
  curl --fail --location --retry 3 --retry-delay 2 --silent --show-error --continue-at - --output "$out" "$url"
}

download "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/EUR_seven_cohorts_myopia_metal_ratio01_adjusted_no23andme.fastGWAz" \
  "$gwas_dir/EUR_meta_no23andMe.fastGWAz"
download "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/five_cohort_EAS_metal.fastGWAz" \
  "$gwas_dir/EAS_meta.fastGWAz"
download "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/two_cohort_AFR_metal.fastGWAz" \
  "$gwas_dir/AFR_meta.fastGWAz"
download "https://yanglab.westlake.edu.cn/resources/publication_data/Chengfeifei/fixed_effect/Cross_ancest_EUR_EAS_AFR_no23andme1tbl" \
  "$gwas_dir/Cross_ancestry_EUR_EAS_AFR_no23andMe"

# HRCA supplementary sources; these remain raw and are audited before use.
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM1_ESM.pdf" \
  "$retina_dir/HRCA_41588_2025_2454_MOESM1.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM2_ESM.pdf" \
  "$retina_dir/HRCA_41588_2025_2454_MOESM2.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM3_ESM.pdf" \
  "$retina_dir/HRCA_41588_2025_2454_MOESM3.pdf"
download "https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-025-02454-1/MediaObjects/41588_2025_2454_MOESM4_ESM.xlsx" \
  "$retina_dir/HRCA_41588_2025_2454_MOESM4.xlsx"

echo "Primary resource download step complete."
