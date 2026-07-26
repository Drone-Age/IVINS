# iVINS v1.0.0.0 gate exceptions

## VINS-NEO v1_00_02_00 component evidence

- Decision date: 2026-07-27
- Decision source: owner instruction in the delegated ClickUp execution chat
- Component commit: `69a1a747db5a88b8db2b348d90ca3051b35fdeb2`
- Component tag: `v1_00_02_00`
- Package: `vins-mono-ros2_1.0.2.0_arm64.deb`
- Package SHA-256:
  `757d043393cdd956a4ecc9c2a2945a3415449ee3fcac2ee6c8f59b57c41d7bd6`

The owner explicitly permits this immutable package to be used as the VINS
component of iVINS v1.0.0.0 despite the component release recording its
automated, install/smoke, and dataset tests as `SKIPPED`.

This exception authorizes component selection only. It does not reclassify a
skipped test as `PASS`, and it does not waive the separate iVINS product-level
clean-install, runtime, integration, hardware, dataset, or post-release gates.

## Product dataset runner

- Decision date: 2026-07-27
- Decision source: owner instruction in the delegated ClickUp execution chat
- Input retained unchanged: `/home/rpi/bag/data.bag`
- Input SHA-256:
  `b7cb3039287a10a2148b49d9bc41d8e51da77f2d0286b5dad99c51bb4e8a63e4`
- Selected configuration: pinned VINS EuRoC configuration

The owner explicitly removed the `vins_test.py` parameter-tuning runner from
the current release scope. The runner will not be installed or executed.
Instead, the product dataset gate uses the pinned EuRoC configuration and the
following owner-approved acceptance criterion:

- divide dataset playback time into one-second intervals;
- an interval is covered when VINS publishes at least one coordinate message;
- coordinate coverage is
  `covered intervals / total playback intervals * 100%`;
- the gate passes when coordinate coverage is at least 90%.

The ROS 1 input remains immutable. Its reproducible ROS 2 conversion, input
and output checksums, commands, logs, coordinate topic, interval counts, and
calculated coverage must be recorded as evidence.
