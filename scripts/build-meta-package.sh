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
if data["schema_version"] == 1:
    dependencies = [
        {
            "name": component["package"],
            "version": component["debian_version"],
        }
        for component in data["components"].values()
    ]
else:
    dependencies = data["components"]["iros2"]["packages"] + [
        {
            "name": data["components"][name]["package"],
            "version": data["components"][name]["debian_version"],
        }
        for name in ("imavros", "vins")
    ]
print(", ".join(
    f"{dependency['name']} (= {dependency['version']})"
    for dependency in dependencies
))
print(data["artifacts"]["meta_package"]["filename"])
PY
)

version="${values[0]}"
component_depends="${values[1]}"
filename="${values[2]}"
package_root="$(mktemp -d "/tmp/ivins_${version}_arm64.XXXXXX")"
trap 'rm -rf -- "${package_root}"' EXIT

mkdir -p \
  "${package_root}/DEBIAN" \
  "${package_root}/usr/share/doc/ivins" \
  "${package_root}/usr/share/ivins" \
  "${output_dir}"
sed \
  -e "s/@VERSION@/${version}/g" \
  -e "s/@COMPONENT_DEPENDS@/${component_depends}/g" \
  "${repo_root}/packaging/control.in" > "${package_root}/DEBIAN/control"
python3 "${repo_root}/scripts/package-manifest.py" \
  "${manifest}" "${package_root}/usr/share/doc/ivins/release-manifest.json"
install -m 0644 "${repo_root}/packaging/activate.sh" \
  "${package_root}/usr/share/ivins/activate.sh"
printf 'Installed-Size: %s\n' "$(du -sk "${package_root}" | cut -f1)" \
  >> "${package_root}/DEBIAN/control"

find "${package_root}" -exec touch -h -d '@0' {} +
SOURCE_DATE_EPOCH=0 dpkg-deb --root-owner-group --build \
  "${package_root}" "${output_dir}/${filename}"
sha256sum "${output_dir}/${filename}" > "${output_dir}/${filename}.sha256"
