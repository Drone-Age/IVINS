#!/usr/bin/env python3
"""Validate an iVINS product release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
DEBIAN_VERSION_RE = re.compile(
    r"^\d+\.\d+\.\d+(?:\.\d+)?(?:-\d+\+deb13)?$"
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def validate(manifest: dict[str, Any], released: bool) -> list[str]:
    errors: list[str] = []
    release = manifest.get("release", {})
    platform = manifest.get("platform", {})
    components = manifest.get("components", {})
    artifacts = manifest.get("artifacts", {})
    gates = manifest.get("gates", {})

    require(errors, manifest.get("schema_version") == 1, "schema_version must be 1")
    version = release.get("version", "")
    require(errors, bool(VERSION_RE.fullmatch(version)), "release.version must have four numeric components")
    require(errors, release.get("name") == "ivins", "release.name must be ivins")
    require(errors, release.get("tag") == f"v{version}", "release.tag must equal v<release.version>")
    require(
        errors,
        release.get("debian_version") == f"{version}-1+deb13",
        "release.debian_version is inconsistent",
    )
    require(errors, release.get("status") in {"draft", "released", "revoked"}, "invalid release.status")

    expected_platform = {
        "distribution": "debian",
        "release": "13",
        "codename": "trixie",
        "architecture": "arm64",
        "native_machine": "aarch64",
        "ros_distribution": "jazzy",
    }
    for key, expected in expected_platform.items():
        require(errors, platform.get(key) == expected, f"platform.{key} must be {expected}")

    expected_components = {
        "iros2": ("https://github.com/Drone-Age/iros2_0.git", "iros2-0"),
        "imavros": (
            "https://github.com/Drone-Age/iMAVROS-release.git",
            "imavros",
        ),
        "vins": ("https://github.com/Drone-Age/VINS-NEO.git", "vins-mono-ros2"),
    }
    require(
        errors,
        set(components) == set(expected_components),
        "components must contain exactly iros2, imavros, and vins",
    )
    for name, (expected_repository, expected_package) in expected_components.items():
        component = components.get(name, {})
        commit = component.get("commit", "")
        artifact = component.get("artifact", {})
        require(
            errors,
            component.get("repository") == expected_repository,
            f"{name}.repository is inconsistent",
        )
        require(errors, component.get("package") == expected_package, f"{name}.package is inconsistent")
        require(errors, bool(SHA_RE.fullmatch(commit)), f"{name}.commit must be a full Git SHA")
        require(
            errors,
            bool(DEBIAN_VERSION_RE.fullmatch(component.get("debian_version", ""))),
            f"{name}.debian_version is invalid",
        )
        require(errors, artifact.get("filename", "").endswith("_arm64.deb"), f"{name} artifact filename is invalid")
        if released:
            require(errors, bool(component.get("tag")), f"released manifest requires {name}.tag")
            require(errors, bool(artifact.get("url")), f"released manifest requires {name} artifact URL")
            require(
                errors,
                "/releases/latest/" not in (artifact.get("url") or ""),
                f"released manifest forbids a latest URL for {name}",
            )
            require(
                errors,
                bool(SHA256_RE.fullmatch(artifact.get("sha256") or "")),
                f"released manifest requires {name} artifact SHA-256",
            )

    meta = artifacts.get("meta_package", {})
    bundle = artifacts.get("offline_bundle", {})
    require(errors, meta.get("package") == "ivins", "meta package name must be ivins")
    require(
        errors,
        meta.get("filename") == f"ivins_{release.get('debian_version', '')}_arm64.deb",
        "meta package filename is inconsistent",
    )
    require(errors, bundle.get("filename", "").endswith("_arm64.tar.zst"), "offline bundle filename is invalid")

    if released:
        require(errors, release.get("status") == "released", "--released requires release.status=released")
        for name, entry in {
            "meta_package": meta,
            "offline_bundle": bundle,
        }.items():
            require(
                errors,
                bool(entry.get("url")),
                f"released manifest requires {name} URL",
            )
            require(
                errors,
                "/releases/latest/" not in (entry.get("url") or ""),
                f"released manifest forbids a latest URL for {name}",
            )
            require(
                errors,
                bool(SHA256_RE.fullmatch(entry.get("sha256") or "")),
                f"released manifest requires {name} SHA-256",
            )
        required_gates = (
            "metadata",
            "package_audit",
            "clean_install",
            "ros_smoke",
            "dataset",
            "post_release",
        )
        for name in required_gates:
            require(errors, bool(gates.get(name)), f"released manifest requires gates.{name}")
        native = gates.get("component_native", {})
        for name in expected_components:
            require(errors, bool(native.get(name)), f"released manifest requires native gate for {name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--released", action="store_true")
    parser.add_argument("--check-artifacts", type=Path)
    args = parser.parse_args()

    path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 2

    errors = validate(manifest, args.released)
    if args.check_artifacts:
        for component in manifest["components"].values():
            artifact = component["artifact"]
            candidate = args.check_artifacts / artifact["filename"]
            if not candidate.is_file():
                errors.append(f"artifact is missing: {candidate}")
            elif artifact.get("sha256") and digest(candidate) != artifact["sha256"]:
                errors.append(f"artifact checksum mismatch: {candidate}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    try:
        display_path = path.relative_to(ROOT)
    except ValueError:
        display_path = path.name
    print(f"{display_path.as_posix()}: valid ({manifest['release']['status']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
