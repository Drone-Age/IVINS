#!/usr/bin/env bash
set -Eeuo pipefail

evidence_dir="${1:?Usage: run-ogre-compat-gate.sh EVIDENCE_DIR}"
mkdir -p "${evidence_dir}"
evidence_dir="$(realpath "${evidence_dir}")"

ogre_dir="/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE"
octree="${ogre_dir}/Plugin_OctreeZone.so.1.12.10"
dependency="${ogre_dir}/Plugin_PCZSceneManager.so.1.12.10"
activation="/usr/share/ivins/activate.sh"
started_at="$(date --iso-8601=seconds)"

test -f "${activation}"
test -f "${octree}"
test -f "${dependency}"

env -i \
  HOME="${HOME}" \
  USER="${USER}" \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  bash --noprofile --norc -c '
    set -Eeuo pipefail
    source /usr/share/ivins/activate.sh
    source /usr/share/ivins/activate.sh
    ogre="/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE"
    [[ "$(tr ":" "\n" <<<"${LD_LIBRARY_PATH}" | grep -Fxc "${ogre}")" == 1 ]]
    printf "IVINS_PRODUCT_VERSION=%s\nLD_LIBRARY_PATH=%s\n" \
      "${IVINS_PRODUCT_VERSION}" "${LD_LIBRARY_PATH}"
  ' > "${evidence_dir}/clean-shell-activation.txt"

source "${activation}"

ldd "${octree}" \
  > "${evidence_dir}/octree-ldd.txt"
! grep -Fq 'not found' "${evidence_dir}/octree-ldd.txt"
grep -Fq "Plugin_PCZSceneManager.so.1.12.10 => ${dependency}" \
  "${evidence_dir}/octree-ldd.txt"

python3 - "${octree}" \
  > "${evidence_dir}/ogre-plugin-smoke.txt" <<'PY'
import ctypes
import sys

ctypes.CDLL(sys.argv[1], mode=ctypes.RTLD_GLOBAL)
print(f"loaded={sys.argv[1]}")
PY

: > "${evidence_dir}/elf-ldd-audit.txt"
: > "${evidence_dir}/elf-ldd-failures.txt"
elf_count=0
while IFS= read -r -d '' candidate; do
  if [[ "$(head -c 4 "${candidate}" | od -An -tx1 | tr -d ' \n')" != 7f454c46 ]]; then
    continue
  fi
  elf_count=$((elf_count + 1))
  {
    printf 'FILE %s\n' "${candidate}"
    if ! ldd "${candidate}" 2>&1; then
      printf 'ldd command failed\n'
    fi
  } >> "${evidence_dir}/elf-ldd-audit.txt"
done < <(find /opt/iros2j /opt/imavros /opt/vins -type f -print0 | sort -z)

grep -E 'not found|ldd command failed' "${evidence_dir}/elf-ldd-audit.txt" \
  > "${evidence_dir}/elf-ldd-failures.txt" || true
test ! -s "${evidence_dir}/elf-ldd-failures.txt"

finished_at="$(date --iso-8601=seconds)"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  test_id result started_at finished_at host target command evidence reason requirement_effect \
  > "${evidence_dir}/results.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  ogre_loader_compat PASS "${started_at}" "${finished_at}" "$(hostname)" \
  "${octree}" "scripts/run-ogre-compat-gate.sh ${evidence_dir}" \
  "${evidence_dir}/octree-ldd.txt" "" satisfied \
  >> "${evidence_dir}/results.tsv"
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  complete_elf_audit PASS "${started_at}" "${finished_at}" "$(hostname)" \
  "/opt/iros2j /opt/imavros /opt/vins (${elf_count} ELF files)" \
  "scripts/run-ogre-compat-gate.sh ${evidence_dir}" \
  "${evidence_dir}/elf-ldd-audit.txt" "" satisfied \
  >> "${evidence_dir}/results.tsv"

printf 'OGRE compatibility gate PASSED; ELF files audited: %s\n' "${elf_count}"
