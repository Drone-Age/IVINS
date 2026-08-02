#!/usr/bin/env bash

# This file is sourced by users and launchers; do not enable shell options here.
if [[ "${IVINS_PRODUCT_VERSION:-}" == "2.0.0.0" ]]; then
  return 0 2>/dev/null || exit 0
fi

_ivins_ogre_dir="/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE"
_ivins_restore_nounset=0
case "$-" in
  *u*)
    set +u
    _ivins_restore_nounset=1
    ;;
esac

source /opt/iros2j/setup.bash

case ":${LD_LIBRARY_PATH:-}:" in
  *":${_ivins_ogre_dir}:"*) ;;
  *)
    export LD_LIBRARY_PATH="${_ivins_ogre_dir}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
    ;;
esac

source /opt/imavros/setup.bash
source /opt/vins/setup.bash

export IVINS_PRODUCT_VERSION="2.0.0.0"
unset _ivins_ogre_dir
if (( _ivins_restore_nounset )); then
  set -u
fi
unset _ivins_restore_nounset
