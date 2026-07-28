# iVINS 2.0.0.0 native gate report

Date: 2026-07-28
Target: `rpi@192.168.144.106`
Hardware: Raspberry Pi 5 Model B
Platform: Debian 13 Trixie, `aarch64`

## Selected matrix

| Component | Version | Commit |
| --- | --- | --- |
| iROS2j | 1.0.3 / `v2.1.0.3` | `4e4f9e159365e8d14da185655a706ed1125dea39` |
| iMAVROS | 1.0.0.2 / `v1.0.0.2` | `10634b225fd540ab3c7ad1b87a768b215e229361` |
| VINS-NEO | 1.0.3.0 / `v1_00_03_00` | `34b2805099c77d35f5489007da9a7fe66b04b6d8` |
| iVINS | 2.0.0.0 draft | working tree for Issue #7 |

## Artifact identities

- `ivins_2.0.0.0-1+deb13_arm64.deb`:
  `b8795aff2b9c6a141466647740ebad6afe1c62eeb058ad9e3f39f0a892bc497b`
- `ivins_2.0.0.0-1+deb13_arm64.tar.zst`:
  `dee1f7d365cae716b63290507969187b1c5bb8c287c36fa692ea891d75eef98d`

These are pre-release artifacts. They are not public release assets and must
not be published while a mandatory gate is `FAIL`, `BLOCKED`, or `NOT_RUN`.

## Results

| Gate | Result | Evidence |
| --- | --- | --- |
| Historical manifest validation | PASS | `native-product-build.log` |
| Schema 2 manifest and artifact validation | PASS | `native-product-build.log` |
| Unit tests | PASS (18 tests) | `native-product-build.log` |
| Shell syntax | PASS | `native-product-build.log` |
| Meta-package build and payload/dependency audit | PASS | `native-product-build.log` |
| Bundle inventory, checksums, SBOM, key and signed APT metadata | PASS | `native-product-build.log`, `clean-offline-install.log` |
| Clean product-package removal and file-only offline reinstall | PASS | `clean-offline-install.log` |
| Exact installed versions and activation order | PASS | `evidence/runtime/` |
| `cv_bridge` ownership under `/opt/iros2j` | PASS | `evidence/runtime/python-prefixes.txt` |
| Fast DDS selection and `ros2 doctor --report` | PASS | `evidence/runtime/` |
| Complete ELF `ldd` audit | PASS (435 of 435 ELF files) | `ogre-compatibility/native-install/results.tsv` |
| Controlled ROS 2 dataset | PASS | `evidence/dataset/` |
| FCU raw MAVLink/MAVROS/IMU telemetry | PASS | `evidence/imavros-hardware/` |
| OV5647 still capture | PASS | `evidence/vins-hardware/` |
| OV5647 ROS image topic | PASS (28.8 Hz) | `evidence/camera-ros/` |
| Calibrated live camera + FCU + VINS integration | BLOCKED | See blockers below |
| Reboot persistence | NOT_RUN | Blocked release was not reboot-qualified |
| Publication and public-asset verification | NOT_RUN | Release is not eligible for publication |

## Mandatory blockers

1. The configured OV5647/FCU installation has no active
   `/etc/vins-neo/iVIN.yaml` or equivalent hardware-specific camera
   intrinsics, distortion, camera-to-IMU extrinsics, time offset, and rolling
   shutter configuration. The packaged VINS configurations are dataset or
   unrelated-device profiles and cannot be represented as valid live
   OV5647/FCU calibration.
2. The available `camera_ros` workspace was built with a legacy
   `/opt/iros2_0/jazzy` underlay reference. The camera publishes successfully
   when iROS2j is sourced first, but its setup emits the forbidden legacy
   underlay lookup and is not an eligible release input.

## Release decision

Overall result: **BLOCKED**. The draft tooling, package, signed offline bundle,
clean reinstall, complete ELF audit, controlled dataset, FCU, and camera gates
are reproducible, but the calibrated live integration criteria are not
satisfied. Do not set the manifest to `released`, merge as a release, create
immutable tags, or publish assets until the three blockers are fixed and all
affected native and post-release gates are repeated.
