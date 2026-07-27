# Repository instructions

## Normative documentation

- Read `docs/README.md`, `docs/COMPONENT_PROCESS_ALIGNMENT.md`,
  `docs/RELEASE_PROCESS.md`, and `docs/PRE_RELEASE_TESTING.md` before changing
  integration, manifests, packaging, installers, tests, or releases.
- English normative documents are canonical for automation and machine-facing
  interpretation. Ukrainian `.uk.md` counterparts are mandatory and must be
  updated in the same commit.
- Follow `docs/DOCUMENTATION_POLICY.md` for documentation changes and
  `docs/VERSIONING.md` for product/process versions and immutable tags.
- Files named `*_UK.md` are legacy records for the iVINS 1.0.0.0 matrix and
  must not be used as the current component contract.

## Work tracking

- Material work requires one linked GitHub Issue and one ClickUp task before
  implementation.
- GitHub is authoritative for source, commits, tags, releases, technical
  acceptance criteria, manifests, checksums, and durable evidence.
- ClickUp is authoritative for planning state, ownership, priority, estimates,
  blockers, and cross-component coordination.
- Do not mark a stage complete without its required check and verified
  chronological evidence.

## Accepted integration constraints

- The supported release target is native Raspberry Pi 5, Debian 13 Trixie,
  `arm64`/`aarch64`, ROS 2 Jazzy.
- The current underlay contract is the signed split-package `iros2j` APT
  snapshot at `/opt/iros2j`; do not recreate `iros2-0` or
  `/opt/iros2_0/jazzy`.
- iMAVROS owns `/opt/imavros`; VINS-NEO owns `/opt/vins`; neither component
  may duplicate ROS packages owned by iROS2j.
- Activate clean-shell environments in the order iROS2j, iMAVROS, VINS.
- Docker, QEMU, emulation, cross-compilation, AMD64, and locally rebuilt
  substitutes are not native release evidence.
- Published component/product tags, manifests, repository snapshots, hashes,
  and evidence are immutable.

## Release safety

- A new iVINS matrix may select only immutable published component releases
  with matching native evidence.
- Every planned test receives an explicit result defined by
  `docs/PRE_RELEASE_TESTING.md`; never report a skipped, blocked, partial, or
  timed-out result as `PASS`.
- Do not create or move a product/process tag until metadata, component,
  package, offline-install, integration, acceptance, publication, and
  post-release requirements applicable to that tag are satisfied.
