#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="${1:-${repo_root}/manifests/ivins-$(tr -d '\r\n' < "${repo_root}/VERSION").json}"
output_dir="${2:-${repo_root}/artifacts}"

python3 "${repo_root}/scripts/validate-release.py" "${manifest}"

readarray -t values < <(python3 - "${manifest}" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(data["release"]["debian_version"])
print(data["components"]["iros2"]["debian_version"])
print(data["components"]["imavros"]["debian_version"])
print(data["components"]["vins"]["debian_version"])
print(data["artifacts"]["meta_package"]["filename"])
PY
)

version="${values[0]}"
iros2_version="${values[1]}"
imavros_version="${values[2]}"
vins_version="${values[3]}"
filename="${values[4]}"
package_root="$(mktemp -d "/tmp/ivins_${version}_arm64.XXXXXX")"
trap 'rm -rf -- "${package_root}"' EXIT

mkdir -p "${package_root}/DEBIAN" "${package_root}/usr/share/doc/ivins" "${output_dir}"
sed \
  -e "s/@VERSION@/${version}/g" \
  -e "s/@IROS2_VERSION@/${iros2_version}/g" \
  -e "s/@IMAVROS_VERSION@/${imavros_version}/g" \
  -e "s/@VINS_VERSION@/${vins_version}/g" \
  "${repo_root}/packaging/control.in" > "${package_root}/DEBIAN/control"
install -m 0644 "${manifest}" "${package_root}/usr/share/doc/ivins/release-manifest.json"
printf 'Installed-Size: %s\n' "$(du -sk "${package_root}" | cut -f1)" \
  >> "${package_root}/DEBIAN/control"

dpkg-deb --root-owner-group --build "${package_root}" "${output_dir}/${filename}"
sha256sum "${output_dir}/${filename}" > "${output_dir}/${filename}.sha256"
