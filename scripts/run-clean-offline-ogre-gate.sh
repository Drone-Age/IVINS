#!/usr/bin/env bash
set -Eeuo pipefail

bundle="${1:?Usage: run-clean-offline-ogre-gate.sh BUNDLE EVIDENCE_DIR}"
evidence_dir="${2:?Usage: run-clean-offline-ogre-gate.sh BUNDLE EVIDENCE_DIR}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bundle="$(realpath "${bundle}")"
mkdir -p "${evidence_dir}"
evidence_dir="$(realpath "${evidence_dir}")"

install_dir="$(mktemp -d /home/rpi/ivins-ogre-offline.XXXXXX)"
case "${install_dir}" in
  /home/rpi/ivins-ogre-offline.*) ;;
  *) echo "Unexpected temporary path: ${install_dir}" >&2; exit 2 ;;
esac

tar --zstd -xf "${bundle}" -C "${install_dir}"
(
  cd "${install_dir}"
  sha256sum -c SHA256SUMS
)

mapfile -t installed < <(
  dpkg-query -W -f='${binary:Package}\t${db:Status-Status}\n' \
    | awk '$2 == "installed" && ($1 == "ivins" || $1 == "imavros" ||
      $1 == "vins-mono-ros2" || $1 ~ /^iros2j-/) { print $1 }' \
    | sort -u
)
for package in "${installed[@]}"; do
  [[ "${package}" =~ ^(ivins|imavros|vins-mono-ros2|iros2j-[a-z0-9.+-]+)$ ]]
done
printf '%s\n' "${installed[@]}" > "${evidence_dir}/removed-packages.txt"

if ((${#installed[@]})); then
  sudo -n apt-get remove -y "${installed[@]}" \
    > "${evidence_dir}/package-removal.log" 2>&1
else
  printf 'Product packages were already absent.\n' \
    > "${evidence_dir}/package-removal.log"
fi
for prefix in /opt/iros2j /opt/imavros /opt/vins; do
  resolved="$(realpath -m "${prefix}")"
  [[ "${resolved}" == "${prefix}" ]]
  if [[ -d "${resolved}" ]]; then
    sudo -n find "${resolved}" -mindepth 1 -delete
  fi
  test -z "$(find "${resolved}" -mindepth 1 -print -quit 2>/dev/null)"
done

(
  cd "${install_dir}"
  sudo -n env DEBIAN_FRONTEND=noninteractive bash ./install.sh
) > "${evidence_dir}/clean-offline-reinstall.log" 2>&1

find /opt/iros2j -type f -print0 | sort -z | xargs -0 sha256sum \
  > "${evidence_dir}/iros2j-installed-after-reinstall.sha256"

bash "${repo_root}/scripts/run-ogre-compat-gate.sh" \
  "${evidence_dir}/ogre-gate-after-reinstall"

printf 'Clean offline OGRE gate PASSED; extracted bundle: %s\n' "${install_dir}"
