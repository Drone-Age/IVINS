#!/usr/bin/env bash
set -Eeuo pipefail

bundle_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${bundle_dir}"
sha256sum -c SHA256SUMS

as_root() {
  if (( EUID == 0 )); then
    "$@"
  else
    sudo -n "$@"
  fi
}

schema_version="$(
  python3 -c 'import json; print(json.load(open("build-manifest.json", encoding="utf-8"))["schema_version"])'
)"

if [[ "${schema_version}" == 1 ]]; then
  mapfile -t packages < <(find . -maxdepth 1 -type f -name '*.deb' -print | sort)
  if (( ${#packages[@]} != 4 )); then
    echo "Expected exactly four Debian packages; found ${#packages[@]}." >&2
    exit 1
  fi
  as_root apt-get install -y "${packages[@]}"
  exit 0
fi

if [[ "${schema_version}" != 2 ]]; then
  echo "Unsupported build manifest schema: ${schema_version}" >&2
  exit 1
fi

for command in apt-get dpkg-query gpg gpgv python3 sha256sum tar; do
  command -v "${command}" >/dev/null
done

mapfile -t manifest_values < <(python3 - <<'PY'
import json

data = json.load(open("build-manifest.json", encoding="utf-8"))
iros2 = data["components"]["iros2"]
apt = iros2["apt_repository"]
print(apt["filename"])
print(apt["sha256"])
print(apt["signing_key"]["filename"])
print(apt["signing_key"]["sha256"])
print(apt["signing_key"]["fingerprint"])
for key in ("inrelease", "release", "release_signature"):
    print(apt["signed_metadata"][key]["path"])
    print(apt["signed_metadata"][key]["sha256"])
print(iros2["package_inventory"]["filename"])
print(iros2["package_inventory"]["sha256"])
for package in iros2["packages"]:
    print(f"package:{package['name']}={package['version']}")
for name in ("imavros", "vins"):
    component = data["components"][name]
    print(
        "deb:"
        f"{component['artifact']['filename']}:"
        f"{component['package']}={component['debian_version']}:"
        f"{component['artifact']['sha256']}"
    )
meta = data["artifacts"]["meta_package"]
print(
    "deb:"
    f"{meta['filename']}:"
    f"{meta['package']}={data['release']['debian_version']}:"
    f"{meta.get('sha256') or ''}"
)
PY
)

apt_archive="${manifest_values[0]}"
apt_sha256="${manifest_values[1]}"
key_filename="${manifest_values[2]}"
key_sha256="${manifest_values[3]}"
key_fingerprint="${manifest_values[4]}"
inrelease_path="${manifest_values[5]}"
inrelease_sha256="${manifest_values[6]}"
release_path="${manifest_values[7]}"
release_sha256="${manifest_values[8]}"
release_signature_path="${manifest_values[9]}"
release_signature_sha256="${manifest_values[10]}"
inventory_filename="${manifest_values[11]}"
inventory_sha256="${manifest_values[12]}"

temporary="$(mktemp -d)"
trap 'rm -rf -- "${temporary}"' EXIT
printf '%s  %s\n' "${apt_sha256}" "${apt_archive}" | sha256sum -c -
tar -xzf "${apt_archive}" -C "${temporary}"
apt_root="${temporary}/apt-repository"
key_path="${apt_root}/${key_filename}"
inrelease="${apt_root}/${inrelease_path}"
release="${apt_root}/${release_path}"
release_signature="${apt_root}/${release_signature_path}"

printf '%s  %s\n' "${key_sha256}" "${key_path}" | sha256sum -c -
printf '%s  %s\n' "${inrelease_sha256}" "${inrelease}" | sha256sum -c -
printf '%s  %s\n' "${release_sha256}" "${release}" | sha256sum -c -
printf '%s  %s\n' "${release_signature_sha256}" "${release_signature}" \
  | sha256sum -c -
printf '%s  %s\n' "${inventory_sha256}" "${inventory_filename}" \
  | sha256sum -c -

actual_fingerprint="$(
  gpg --batch --show-keys --with-colons "${key_path}" \
    | awk -F: '$1 == "fpr" { print $10; exit }'
)"
if [[ "${actual_fingerprint}" != "${key_fingerprint}" ]]; then
  echo "APT signing-key fingerprint mismatch." >&2
  exit 1
fi

keyring="${temporary}/iros2j-archive-keyring.gpg"
gpg --batch --yes --dearmor --output "${keyring}" "${key_path}"
gpgv --keyring "${keyring}" "${inrelease}"
gpgv --keyring "${keyring}" "${release_signature}" "${release}"

source_list="${temporary}/iros2j.list"
lists_dir="${temporary}/apt-lists"
mkdir -p "${lists_dir}/partial"
printf 'deb [arch=arm64 signed-by=%s] file:%s trixie main\n' \
  "${keyring}" "${apt_root}" > "${source_list}"
apt_options=(
  -o "Dir::Etc::sourcelist=${source_list}"
  -o "Dir::Etc::sourceparts=-"
  -o "Dir::State::lists=${lists_dir}"
  -o "Acquire::Languages=none"
  -o "Acquire::AllowInsecureRepositories=false"
  -o "Acquire::AllowDowngradeToInsecureRepositories=false"
)

iros2_packages=()
deb_files=()
expected_versions=()
for value in "${manifest_values[@]:13}"; do
  case "${value}" in
    package:*)
      specification="${value#package:}"
      iros2_packages+=("${specification}")
      expected_versions+=("${specification}")
      ;;
    deb:*)
      specification="${value#deb:}"
      filename="${specification%%:*}"
      remainder="${specification#*:}"
      package_version="${remainder%%:*}"
      expected_sha256="${remainder#*:}"
      if [[ -n "${expected_sha256}" ]]; then
        printf '%s  %s\n' "${expected_sha256}" "${bundle_dir}/${filename}" \
          | sha256sum -c -
      fi
      deb_files+=("${bundle_dir}/${filename}")
      expected_versions+=("${package_version}")
      ;;
  esac
done

as_root apt-get "${apt_options[@]}" update
as_root apt-get "${apt_options[@]}" install -y --no-install-recommends \
  "${iros2_packages[@]}" "${deb_files[@]}"

for specification in "${expected_versions[@]}"; do
  package="${specification%%=*}"
  expected="${specification#*=}"
  actual="$(dpkg-query -W -f='${Version}' "${package}")"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "${package}: expected ${expected}, found ${actual}" >&2
    exit 1
  fi
done

if dpkg-query -W -f='${db:Status-Status}' iros2-0 2>/dev/null \
  | grep -qx installed; then
  echo "Forbidden package iros2-0 is installed." >&2
  exit 1
fi
test ! -e /opt/iros2_0/jazzy
test -f /opt/iros2j/setup.bash
test -f /opt/imavros/setup.bash
test -f /opt/vins/setup.bash
test -f /usr/share/ivins/activate.sh
