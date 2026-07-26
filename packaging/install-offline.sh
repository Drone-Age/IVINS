#!/usr/bin/env bash
set -Eeuo pipefail

bundle_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${bundle_dir}"
sha256sum -c SHA256SUMS

mapfile -t packages < <(find . -maxdepth 1 -type f -name '*.deb' -print | sort)
if (( ${#packages[@]} != 4 )); then
  echo "Expected exactly four Debian packages; found ${#packages[@]}." >&2
  exit 1
fi

if (( EUID == 0 )); then
  apt-get install -y "${packages[@]}"
else
  sudo -n apt-get install -y "${packages[@]}"
fi
