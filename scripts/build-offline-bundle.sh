#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${1:?Usage: build-offline-bundle.sh MANIFEST ARTIFACTS [OUTPUT_DIR]}"
artifacts="${2:?Usage: build-offline-bundle.sh MANIFEST ARTIFACTS [OUTPUT_DIR]}"
output_dir="${3:-${artifacts}}"
manifest="$(realpath "${manifest}")"
artifacts="$(realpath "${artifacts}")"
mkdir -p "${output_dir}"
output_dir="$(realpath "${output_dir}")"

python3 "${repo_root}/scripts/validate-release.py" "${manifest}"

mapfile -t names < <(python3 - "${manifest}" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
for component in data["components"].values():
    print(component["artifact"]["filename"])
print(data["artifacts"]["meta_package"]["filename"])
print(data["artifacts"]["offline_bundle"]["filename"])
PY
)

bundle="${names[4]}"
stage="$(mktemp -d)"
trap 'rm -rf -- "${stage}"' EXIT

for name in "${names[@]:0:4}"; do
  test -f "${artifacts}/${name}"
  cp -f -- "${artifacts}/${name}" "${stage}/${name}"
done

python3 "${repo_root}/scripts/package-manifest.py" \
  "${manifest}" "${stage}/build-manifest.json"
install -m 0755 "${repo_root}/packaging/install-offline.sh" \
  "${stage}/install.sh"

(
  cd "${stage}"
  sha256sum "${names[@]:0:4}" build-manifest.json install.sh > SHA256SUMS
)

tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  --zstd -cf "${output_dir}/${bundle}" -C "${stage}" .
sha256sum "${output_dir}/${bundle}" > "${output_dir}/${bundle}.sha256"
