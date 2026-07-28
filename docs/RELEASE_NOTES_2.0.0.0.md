# iVINS 2.0.0.0 release notes

Status: draft.

## Component matrix

| Component | Immutable release |
|---|---|
| iROS2j | 1.0.3, tag `v2.1.0.3`, commit `4e4f9e159365e8d14da185655a706ed1125dea39` |
| iMAVROS | 1.0.0.2, tag `v1.0.0.2`, commit `10634b225fd540ab3c7ad1b87a768b215e229361` |
| VINS-NEO | 1.0.3.0, tag `v1_00_03_00`, commit `34b2805099c77d35f5489007da9a7fe66b04b6d8` |

This release replaces the historical monolithic `iros2-0` installation
contract with the signed split-package iROS2j APT snapshot at `/opt/iros2j`.
The supported activation order is `/opt/iros2j`, `/opt/imavros`, then
`/opt/vins`, using `rmw_fastrtps_cpp`.

## Offline delivery

The autonomous bundle contains the signed iROS2j APT snapshot and key,
the exact iMAVROS and VINS-NEO packages, the payload-free iVINS meta-package,
the build-input manifest, package inventory, SBOM, installer, release notes,
and `SHA256SUMS`. The installer configures only the bundled repository and
rejects the historical package and prefix.

## Release status

The meta-package, signed offline bundle, clean offline reinstall, controlled
dataset, configured FCU, and OV5647 gates passed on the authorized Raspberry
Pi 5. Publication remains blocked by the iROS2j 1.0.3 OGRE ELF dependency
failure, the absence of a hardware-specific OV5647/FCU VINS calibration, and
the available camera workspace's legacy `/opt/iros2_0/jazzy` underlay
reference. See the [versioned native gate report](release-evidence/v2.0.0.0/rpi106/GATE_REPORT.md).
This draft must not be published until every mandatory result is `PASS`.
