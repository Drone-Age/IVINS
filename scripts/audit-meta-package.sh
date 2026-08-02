#!/usr/bin/env bash
set -Eeuo pipefail

deb="${1:?Usage: audit-meta-package.sh ivins_VERSION_arm64.deb}"
manifest="${2:?Usage: audit-meta-package.sh PACKAGE MANIFEST}"

python3 "$(dirname "$0")/validate-release.py" "${manifest}"

expected="$(python3 - "${manifest}" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
if data["schema_version"] == 1:
    dependencies = [
        {
            "name": item["package"],
            "version": item["debian_version"],
        }
        for item in data["components"].values()
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
    f"{item['name']} (= {item['version']})"
    for item in dependencies
))
PY
)"

[[ "$(dpkg-deb -f "${deb}" Package)" == ivins ]]
[[ "$(dpkg-deb -f "${deb}" Architecture)" == arm64 ]]
[[ "$(dpkg-deb -f "${deb}" Depends)" == "${expected}" ]]
contents="$(dpkg-deb --contents "${deb}")"
grep -q './usr/share/doc/ivins/release-manifest.json' <<<"${contents}"
grep -q './usr/share/ivins/activate.sh' <<<"${contents}"
if grep -Eq '\./opt/(iros2j|imavros|vins)(/|$)' <<<"${contents}"; then
  echo "iVINS meta-package must not contain component payload." >&2
  exit 1
fi
if grep -Eq 'iros2-0|/opt/iros2_0' <<<"${contents}"; then
  echo "iVINS meta-package contains a forbidden historical contract." >&2
  exit 1
fi

payload="$(mktemp -d)"
trap 'rm -rf -- "${payload}"' EXIT
dpkg-deb --extract "${deb}" "${payload}"
python3 "$(dirname "$0")/package-manifest.py" \
  "${manifest}" "${payload}/expected-release-manifest.json"
cmp "${payload}/expected-release-manifest.json" \
  "${payload}/usr/share/doc/ivins/release-manifest.json"
bash -n "${payload}/usr/share/ivins/activate.sh"
grep -qF '/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE' \
  "${payload}/usr/share/ivins/activate.sh"
echo "iVINS meta-package audit PASSED."
