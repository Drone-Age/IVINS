# iVINS release process

## 1. Planning and eligibility

Create a linked GitHub Issue and ClickUp task with version, scope, component
matrix, acceptance criteria, estimates, and ordered gates. Select only
published immutable component releases with complete required evidence.

For the next iROS2j-based matrix:

- iROS2j must provide a signed, versioned Debian 13 ARM64 APT snapshot;
- iMAVROS must be released against that exact snapshot;
- VINS-NEO must be released against that exact snapshot without a private
  `cv_bridge`;
- all three component gates must identify their exact release commits and
  artifacts.

If the required VINS release is not yet published, preparation may continue
but the product release remains `BLOCKED`.

## 2. Root manifest

Create a new `manifests/ivins-<version>.json`; do not modify the published
1.0.0.0 manifest. The next matrix uses `schema_version: 2`; schema version 1
remains valid only for historical 1.0.0.0 validation. The new schema must
distinguish:

- the iROS2j APT repository artifact, its SHA-256, signing-key identity,
  Release/InRelease metadata, package inventory, and exact Debian versions;
- iMAVROS and VINS `.deb` artifacts with package metadata and SHA-256;
- the iVINS meta-package and offline bundle;
- component, integration, dataset, hardware, publication, and post-release
  evidence.

The manifest is `draft` until every mandatory gate passes. `latest` URLs,
floating branches, mutable package feeds, inferred versions, and locally
rebuilt substitutes are forbidden.

## 3. Metadata and tooling gate

Before commit and again from the committed snapshot:

```bash
python3 scripts/validate-release.py manifests/ivins-<version>.json
python3 -m unittest discover -s tests -v
git diff --check
```

The validator, schema/tests, `packaging/control.in`, meta-package builder,
offline installer, bundle builder, audit scripts, and SBOM generation must
support the signed APT snapshot plus split-package dependency model before the
new manifest is eligible.

## 4. Dependency-ordered component gates

Run the tracked native release workflow for each component:

1. iROS2j signed APT snapshot and downstream-consumer gate;
2. iMAVROS build/package/hardware gate against the selected snapshot;
3. VINS-NEO build/package/dataset gate against the selected snapshot;
4. iVINS meta-package, offline bundle, and integration gate.

A component `PASS` is accepted only for the exact commit, manifest, artifact,
and hash selected by the root manifest.

## 5. Product assembly

The `ivins` meta-package contains no component payload. It declares exact
dependencies on the required `iros2j-*` packages, exact iMAVROS, and exact
VINS Debian versions. The bundle contains the signed APT snapshot and keyring,
component/meta `.deb` files, root manifest, installer, `SHA256SUMS`, SBOM,
release notes, and evidence.

The offline installer must:

1. verify bundle and individual-file hashes;
2. validate the bundled APT signing key and signed repository metadata;
3. configure only the bundled repository;
4. install through APT without network fallback;
5. verify exact installed package versions and prefixes;
6. remove temporary repository configuration without deleting installed
   package state.

## 6. Product acceptance

Execute `PRE_RELEASE_TESTING.md` on the authorized Raspberry Pi 5. Every
planned test receives an explicit result. A mandatory `FAIL`, `BLOCKED`,
`NOT_RUN`, or unaccepted skip prevents release.

Before publication, set the root manifest to `released`, add final artifact
hashes and evidence URLs, and run the released-mode validator. Merge the
reviewed commit, then create immutable product and process tags. Publish only
artifacts produced by the verified workflow.

## 7. Post-release

On a clean supported target, download the public release assets, verify
signatures and hashes, install only from the published bundle, and repeat the
required clean-install/runtime/integration smoke gate. Record durable evidence.

If verification fails, mark the release defective or revoked. Do not delete,
move, or reuse its tag or version; fix forward with a new release.
