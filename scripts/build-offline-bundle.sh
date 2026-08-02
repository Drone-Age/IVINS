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
print(data["artifacts"]["offline_bundle"]["filename"])
if data["schema_version"] == 1:
    for component in data["components"].values():
        print(f"artifact:{component['artifact']['filename']}")
else:
    print(f"artifact:{data['components']['iros2']['apt_repository']['filename']}")
    print(f"artifact:{data['components']['iros2']['package_inventory']['filename']}")
    for name in ("imavros", "vins"):
        print(f"artifact:{data['components'][name]['artifact']['filename']}")
for release_note in data["artifacts"].get("release_notes", []):
    print(f"source:{release_note['source']}")
print(f"artifact:{data['artifacts']['meta_package']['filename']}")
PY
)

bundle="${names[0]}"
stage="$(mktemp -d)"
trap 'rm -rf -- "${stage}"' EXIT

bundle_names=()
for item in "${names[@]:1}"; do
  case "${item}" in
    artifact:*)
      name="${item#artifact:}"
      test -f "${artifacts}/${name}"
      cp -f -- "${artifacts}/${name}" "${stage}/${name}"
      bundle_names+=("${name}")
      ;;
    source:*)
      source="${item#source:}"
      test -f "${repo_root}/${source}"
      name="$(basename "${source}")"
      cp -f -- "${repo_root}/${source}" "${stage}/${name}"
      bundle_names+=("${name}")
      ;;
  esac
done

python3 "${repo_root}/scripts/package-manifest.py" \
  "${manifest}" "${stage}/build-manifest.json"
python3 "${repo_root}/scripts/generate-sbom.py" \
  "${manifest}" "${artifacts}" "${stage}/sbom.cdx.json"
install -m 0755 "${repo_root}/packaging/install-offline.sh" \
  "${stage}/install.sh"

(
  cd "${stage}"
  sha256sum "${bundle_names[@]}" build-manifest.json sbom.cdx.json install.sh \
    > SHA256SUMS
)

tar --sort=name --mtime='@0' --owner=0 --group=0 --numeric-owner \
  --zstd -cf "${output_dir}/${bundle}" -C "${stage}" .
sha256sum "${output_dir}/${bundle}" > "${output_dir}/${bundle}.sha256"
