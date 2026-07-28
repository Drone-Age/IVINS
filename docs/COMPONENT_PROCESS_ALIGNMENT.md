# iVINS component compatibility contract

This policy defines the integration boundary between iVINS, iROS2j, iMAVROS,
and VINS-NEO. Component rules may be stricter but may not weaken this contract.

## Supported target and component matrix

The target is native Raspberry Pi 5, Debian 13 Trixie, `arm64`/`aarch64`,
ROS 2 Jazzy. Release evidence from Docker, QEMU, emulation,
cross-compilation, AMD64, or another host is not native product evidence.

The next matrix must select immutable releases satisfying:

| Component | Required contract |
|---|---|
| iROS2j | released signed APT snapshot; split `iros2j-*` packages; `/opt/iros2j`; currently compatible baseline 1.0.3 / `v2.1.0.3` |
| iMAVROS | released ARM64 `.deb` built against the same exact iROS2j snapshot; `/opt/imavros`; currently compatible baseline 1.0.0.2 |
| VINS-NEO | new released ARM64 `.deb` built against the same exact iROS2j snapshot; `/opt/vins`; no private ROS dependency copies |
| iVINS | meta-package plus product-owned integration hook, manifest, installer, evidence, and offline bundle |

VINS-NEO 1.0.2.0 is historical and incompatible with this matrix because it
depends on `iros2-0`, sources `/opt/iros2_0/jazzy`, and embeds a private
`cv_bridge`. Until a replacement VINS release passes its own gates, the new
iVINS product matrix is `BLOCKED`, not released.

## Ownership and dependency rules

- iROS2j owns ROS underlay packages, including `cv_bridge`,
  `image_transport`, messages, TF2, RMW implementations, and RViz.
- iMAVROS owns only its `/opt/imavros` overlay and declares exact required
  `iros2j-*` Debian dependencies.
- VINS-NEO owns only its `/opt/vins` overlay and consumes ROS dependencies
  from iROS2j. It must not build or ship a second `cv_bridge`.
- iVINS does not duplicate component payload. Its Debian dependencies and
  embedded manifest identify the exact installable matrix. It may own
  product-level integration files under `/usr/share/ivins`.

The root manifest records the iROS2j release tag/commit, signed APT asset URL
and SHA-256, repository metadata/key identity, exact package set and Debian
versions; iMAVROS and VINS release commits/tags, `.deb` URLs and SHA-256; and
all component gate evidence.

## Environment activation

The normative clean-shell product activation is:

```bash
source /usr/share/ivins/activate.sh
```

The versioned hook sources `/opt/iros2j/setup.bash`, prepends
`/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE` to
`LD_LIBRARY_PATH` exactly once, then sources `/opt/imavros/setup.bash` and
`/opt/vins/setup.bash`. This compatibility belongs to iVINS and does not
modify the immutable iROS2j installation.

All processes use the selected `RMW_IMPLEMENTATION` (Fast DDS for the current
baseline), the same `ROS_DOMAIN_ID`, and compatible DDS discovery settings.
The integration gate verifies package resolution, topics, QoS, timestamps,
frames, TF, and ELF library resolution after this activation.

## Offline delivery

The bundle contains the signed iROS2j APT repository snapshot and keyring,
iMAVROS/VINS/iVINS `.deb` files, root manifest, installer, `SHA256SUMS`, SBOM,
release notes, and gate evidence. The installer configures only the bundled
APT snapshot, verifies all hashes and signatures, and installs through APT.
It must not fabricate legacy packages or compatibility prefixes.
