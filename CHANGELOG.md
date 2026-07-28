# Changelog

All notable product-level changes to iVINS are documented in this file.

## Process [2.1.0] - Unreleased

### Added

- Added a versioned iVINS product activation hook that supplies immutable
  iROS2j 1.0.3 OGRE loader compatibility before activating iMAVROS and VINS.

## [2.0.0.0] - Unreleased

### Added

- Added a draft schema-v2 product manifest for the immutable iROS2j 1.0.3,
  iMAVROS 1.0.0.2, and VINS-NEO 1.0.3.0 component matrix.
- Recorded the signed iROS2j APT snapshot, signing-key fingerprint, signed
  repository metadata, exact package selection, component artifacts, hashes,
  activation order, and release-gate placeholders.

### Changed

- Bumped the process version to 2.0.0 for the incompatible root-manifest
  schema change. Schema v1 remains supported exclusively for historical
  iVINS 1.0.0.0 validation.

### Release status

- Draft and blocked. The meta-package, signed offline bundle, clean offline
  reinstall, controlled dataset, configured FCU, and OV5647 gates passed on
  `rpi@192.168.144.106`.
- The iVINS-owned activation hook resolves the iROS2j 1.0.3 OGRE dependency;
  publication remains blocked by the missing OV5647/FCU-specific VINS
  calibration and the available `camera_ros` workspace's legacy
  `/opt/iros2_0/jazzy` underlay reference.

## Process [1.1.0] - 2026-07-28

### Changed

- Replaced the obsolete monolithic `iros2-0` integration contract with the
  signed split-package `iros2j` APT repository contract.
- Aligned the next iVINS product matrix with iROS2j 1.0.3, iMAVROS 1.0.0.2,
  and a new VINS-NEO release that consumes ROS dependencies from
  `/opt/iros2j`.
- Defined exact component compatibility, activation order, evidence states,
  native/integration gates, offline delivery contents, and post-release
  verification.
- Established canonical English normative documents with mandatory Ukrainian
  `.uk.md` counterparts. Existing `*_UK.md` files are retained as legacy
  documents for the 1.0.0.0 product history.

## [1.0.0.0] - 2026-07-27

### Added

- Initial Raspberry Pi 5 / Debian 13 ARM64 product matrix.
- Exact Debian dependencies on `iros2-0`, `imavros`, and `vins-mono-ros2`.
- Product meta-package and versioned offline-bundle workflow.
- Release manifest validation, package audit, clean-install, runtime, dataset,
  and post-release gates.

### Release status

- IROS2_0 `v0.1.2`, iMAVROS `v1.0.0.1`, and VINS-NEO `v1_00_02_00`
  artifacts are pinned by immutable versioned URLs and independently verified
  SHA-256 values.
- iMAVROS `v1.0.0.1` includes the clean-install dataset fix and recorded
  native hardware-gate evidence.
- The release remains a draft until every required component, package,
  integration, dataset, hardware, and post-release gate has recorded `PASS`
  evidence.
