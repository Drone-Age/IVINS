#!/usr/bin/env bash
set -Eeuo pipefail

deb="${1:?Usage: audit-meta-package.sh ivins_VERSION_arm64.deb}"
manifest="${2:?Usage: audit-meta-package.sh PACKAGE MANIFEST}"

python3 "$(dirname "$0")/validate-release.py" "${manifest}"

expected="$(python3 - "${manifest}" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
print(", ".join(
    f"{item['package']} (= {item['debian_version']})"
    for item in data["components"].values()
))
PY
)"

[[ "$(dpkg-deb -f "${deb}" Package)" == ivins ]]
[[ "$(dpkg-deb -f "${deb}" Architecture)" == arm64 ]]
[[ "$(dpkg-deb -f "${deb}" Depends)" == "${expected}" ]]
dpkg-deb --contents "${deb}" | grep -q './usr/share/doc/ivins/release-manifest.json'

payload="$(mktemp -d)"
trap 'rm -rf -- "${payload}"' EXIT
dpkg-deb --extract "${deb}" "${payload}"
python3 "$(dirname "$0")/package-manifest.py" \
  "${manifest}" "${payload}/expected-release-manifest.json"
cmp "${payload}/expected-release-manifest.json" \
  "${payload}/usr/share/doc/ivins/release-manifest.json"
echo "iVINS meta-package audit PASSED."
