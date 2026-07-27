# Documentation policy

This policy is normative for iVINS documentation.

## Language contract

English is canonical for automation, machine-facing interpretation, schemas,
commands, identifiers, and international integration. Ukrainian is a
mandatory maintained localization of every human-facing normative document.
The canonical file is `NAME.md`; its Ukrainian counterpart is `NAME.uk.md`.
Commands, paths, package names, versions, fields, hashes, and tags are not
translated.

A normative change is complete only when both language files express
equivalent requirements, are updated in the same commit, navigation remains
valid, `PROCESS_VERSION` is incremented according to `VERSIONING.md`, and the
change is recorded in `CHANGELOG.md`.

If translations conflict, English controls execution. The mismatch remains a
documentation defect and blocks a process or product release.

## Historical documents

Published release notes, manifests, evidence, checksums, and instructions
bound to an immutable product tag are historical records. They must not be
silently rewritten to describe a newer component matrix. Superseded active
instructions receive a visible legacy notice and link to the current policy.

The existing `*_UK.md` process documents are retained for the iVINS 1.0.0.0
matrix. New work follows the canonical documents listed in `docs/README.md`.

## Requirement language

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` have their usual normative meanings.
Documents must distinguish released behavior from a proposed or blocked
target. A component version is eligible for an iVINS matrix only after its
immutable release and required evidence are available.
