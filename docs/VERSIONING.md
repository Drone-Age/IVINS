# iVINS versioning policy

## Product version

`VERSION` uses `PRODUCT.MAJOR.MINOR.PATCH`; the product tag is
`v<PRODUCT>.<MAJOR>.<MINOR>.<PATCH>`.

- **PRODUCT**: a new product generation or compatibility identity;
- **MAJOR**: incompatible end-product behavior or interface;
- **MINOR**: backward-compatible functionality or component-matrix update;
- **PATCH**: backward-compatible correction or repackaging.

An iVINS version identifies one verified matrix of exact component commits,
immutable tags, Debian versions, artifacts, dependency repositories, hashes,
and gate results. It does not copy a component version.

A migration from monolithic `iros2-0` to split-package `iros2j` requires a new
iVINS product version because the install contract and offline delivery format
change. Existing iVINS 1.0.0.0 metadata remains immutable.

## Process version

`PROCESS_VERSION` uses semantic versioning independently:

- **MAJOR**: incompatible manifest schema or mandatory gate change;
- **MINOR**: backward-compatible mandatory capability or automation;
- **PATCH**: compatible correction or clarification.

Process tags use `process-v<MAJOR>.<MINOR>.<PATCH>`. A change affecting both
product and process increments both files and creates both immutable tags
after their applicable gates pass.

## Immutability

Published tags, manifests, checksums, signed repository snapshots, and gate
evidence are immutable. A defective release is revoked but not rewritten or
reused. Its correction receives a new version and repeats every affected gate.
