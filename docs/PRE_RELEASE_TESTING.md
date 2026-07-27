# iVINS pre-release testing standard

Every planned test has exactly one result:

- `PASS`;
- `FAIL`;
- `BLOCKED`;
- `SKIPPED_NOT_CONFIGURED`;
- `SKIPPED_NOT_APPLICABLE`;
- `NOT_RUN`.

Partial, interrupted, timed-out, skipped, or blocked work is never `PASS`.
Each result records test ID, timestamps, host, target, exact command, root and
component commits, manifest/artifact hashes, evidence location, reason for
non-`PASS`, and requirement effect.

## 1. Metadata and compatibility gate

1. Product/process versions, tags, manifest name, schema, and changelog agree.
2. Every component has an immutable repository, commit, tag, version, asset
   URL, SHA-256, and gate-evidence link.
3. The iROS2j APT snapshot is signed, hash-pinned, Debian 13 ARM64, and records
   exact package versions.
4. iMAVROS and VINS select the same iROS2j release, prefix, RMW baseline, and
   compatible system ABI.
5. VINS contains no private ROS underlay package, especially `cv_bridge`.
6. Historical manifests and tags are unchanged.
7. Static validators, unit tests, documentation pairing, and
   `git diff --check` pass.

## 2. Component evidence gate

Accept each component gate only when evidence matches the selected commit,
manifest hash, artifact hash, native Raspberry Pi 5 identity, Debian 13,
`aarch64`, commands, timestamps, and final result.

- iROS2j: signed APT repository audit, install, clean-shell ROS/RMW smoke, and
  downstream CMake consumer.
- iMAVROS: metadata, native build, package/ELF, clean install, MAVROS node, and
  configured FCU hardware gate.
- VINS-NEO: metadata, native build, tests, package/ELF, clean install, runtime,
  and controlled dataset gate.

## 3. Product package and bundle gate

1. Build `ivins` from the committed root manifest.
2. Verify package metadata and exact dependencies on required `iros2j-*`,
   `imavros`, and `vins-mono-ros2` versions.
3. Confirm the meta-package has no `/opt/iros2j`, `/opt/imavros`, or
   `/opt/vins` payload.
4. Verify the embedded manifest, SBOM, package hash, bundle inventory, and
   every bundle-file hash.
5. Confirm the bundle contains the signed APT repository/keyring and has no
   unpinned network dependency or legacy `iros2-0` compatibility payload.

## 4. Clean offline install gate

On a clean supported Raspberry Pi 5:

1. clear inherited ROS/colcon/CMake/library environment variables;
2. verify bundle hashes, APT key identity, and signed repository metadata;
3. install with networking disabled or otherwise prove no network fallback;
4. verify exact installed package versions and Debian ownership;
5. prove `iros2-0` and `/opt/iros2_0/jazzy` are absent;
6. prove `cv_bridge` resolves only to `/opt/iros2j`;
7. activate `/opt/iros2j`, `/opt/imavros`, then `/opt/vins`;
8. run `ros2 doctor --report`, package-prefix checks, version commands, and a
   complete ELF `ldd` audit.

## 5. Integration and acceptance gate

1. Use the selected Fast DDS RMW, identical `ROS_DOMAIN_ID`, and compatible
   DDS discovery configuration for every process.
2. Start iMAVROS with the configured flight controller.
3. Start the configured camera path and VINS.
4. Verify IMU/image topics, types, rates, QoS compatibility, timestamps,
   clock domain, frames, TF tree, and absence of duplicate publishers.
5. Verify VINS reaches the required operating state and publishes valid
   odometry.
6. Run the pinned dataset acceptance test and record thresholds/results.
7. Run configured-hardware smoke and reboot/login-shell persistence tests.

Hardware absent from the authoritative configuration may be
`SKIPPED_NOT_CONFIGURED`; configured hardware that is unexpectedly unavailable
is `BLOCKED` or `FAIL`. A mandatory skip does not satisfy the release gate.

## 6. Release and post-release criterion

A `FAIL` fails the gate. Otherwise any mandatory `BLOCKED`, `NOT_RUN`, or
unaccepted skip blocks it. Plain `PASS` requires every applicable mandatory
test to pass.

After publication, download public assets, repeat signature/hash verification,
clean offline install, activation, ROS/RMW smoke, component version checks,
and representative integration smoke. Only verified public artifacts may
close the release gate.
