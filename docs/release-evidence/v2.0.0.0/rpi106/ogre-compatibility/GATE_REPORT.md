# iVINS 2.0.0.0 OGRE loader compatibility gate

Date: 2026-07-28
Target: `rpi@192.168.144.106`
Platform: Raspberry Pi 5 Model B, Debian 13, `aarch64`
Result: **PASS**

## Implementation

The `ivins` package owns `/usr/share/ivins/activate.sh`. From a clean shell,
the versioned hook activates iROS2j, prepends
`/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE` exactly once to
`LD_LIBRARY_PATH`, and then activates iMAVROS and VINS. It does not modify,
patch, replace, or repackage iROS2j.

## Results

| Test | Result | Evidence |
| --- | --- | --- |
| Clean-shell deterministic/idempotent activation | PASS | `native-install/clean-shell-activation.txt` |
| `Plugin_OctreeZone` dependency resolution | PASS | `native-install/octree-ldd.txt` |
| OGRE shared-object loading smoke | PASS | `native-install/ogre-plugin-smoke.txt` |
| Complete installed ELF audit | PASS, 435/435 | `native-install/elf-ldd-audit.txt`, empty `native-install/elf-ldd-failures.txt` |
| Immutable iROS2j installed payload | PASS | Identical `iros2j-installed-before.sha256` and `offline-reinstall-final/iros2j-installed-after-reinstall.sha256`; list SHA-256 `837b603030ff1a5c0d829b371da2214fce8831c69626445a6e42d05a69c6e88d` |
| Immutable iROS2j release inputs | PASS | Identical `iros2j-release-inputs-before.sha256` and `iros2j-release-inputs-after.sha256` |
| Clean signed-bundle reinstall | PASS | `offline-reinstall-final/clean-offline-reinstall.log` |
| ELF/OGRE gate after clean reinstall | PASS, 435/435 | `offline-reinstall-final/ogre-gate-after-reinstall/results.tsv` |

## Product artifacts

- `ivins_2.0.0.0-1+deb13_arm64.deb`:
  `9590c1615ceecd362a034d8e9ea17afe4d246096e490bb6ae828e65bba06ce6f`
- `ivins_2.0.0.0-1+deb13_arm64.tar.zst`:
  `94970a6ab5bdae7f7db7fda5497332fbbab68cd53a877e341447b536bb6d6ca6`

This gate removes only the OGRE loader blocker. The independent calibration
and camera-workspace blockers remain outside this task.
