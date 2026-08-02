#!/usr/bin/env python3
"""Validate an iVINS product release manifest."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
DEBIAN_VERSION_RE = re.compile(
    r"^\d+\.\d+\.\d+(?:\.\d+)?(?:-\d+\+deb13)?$"
)
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FINGERPRINT_RE = re.compile(r"^[0-9A-F]{40}$")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def openpgp_v4_fingerprint(armored_key: bytes) -> str:
    text = armored_key.decode("ascii")
    begin = "-----BEGIN PGP PUBLIC KEY BLOCK-----"
    end = "-----END PGP PUBLIC KEY BLOCK-----"
    if begin not in text or end not in text:
        raise ValueError("armored public key block is missing")
    body = text.split(begin, 1)[1].split(end, 1)[0]
    payload_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip()
        and ":" not in line
        and not line.lstrip().startswith("=")
    ]
    if not payload_lines:
        raise ValueError("armored public key payload is missing")
    packets = base64.b64decode("".join(payload_lines), validate=True)
    position = 0
    while position < len(packets):
        header = packets[position]
        position += 1
        if not header & 0x80:
            raise ValueError("invalid OpenPGP packet header")
        if header & 0x40:
            tag = header & 0x3F
            first = packets[position]
            position += 1
            if first < 192:
                length = first
            elif first < 224:
                second = packets[position]
                position += 1
                length = ((first - 192) << 8) + second + 192
            elif first == 255:
                length = int.from_bytes(packets[position : position + 4], "big")
                position += 4
            else:
                raise ValueError("partial OpenPGP packet lengths are unsupported")
        else:
            tag = (header >> 2) & 0x0F
            length_type = header & 0x03
            if length_type == 0:
                length = packets[position]
                position += 1
            elif length_type == 1:
                length = int.from_bytes(packets[position : position + 2], "big")
                position += 2
            elif length_type == 2:
                length = int.from_bytes(packets[position : position + 4], "big")
                position += 4
            else:
                length = len(packets) - position
        body = packets[position : position + length]
        position += length
        if tag == 6:
            if not body or body[0] != 4:
                raise ValueError("only OpenPGP v4 public keys are supported")
            prefix = b"\x99" + len(body).to_bytes(2, "big")
            return hashlib.sha1(prefix + body).hexdigest().upper()
    raise ValueError("OpenPGP public-key packet is missing")


def audit_iros2j_snapshot(
    manifest: dict[str, Any], artifact_dir: Path, errors: list[str]
) -> None:
    iros2 = manifest["components"]["iros2"]
    apt_repository = iros2["apt_repository"]
    archive = artifact_dir / apt_repository["filename"]
    inventory_path = artifact_dir / iros2["package_inventory"]["filename"]
    if not archive.is_file() or not inventory_path.is_file():
        return

    try:
        with tarfile.open(archive, "r:gz") as snapshot:
            members = {member.name: member for member in snapshot.getmembers()}
            unsafe = [
                name
                for name in members
                if name.startswith(("/", "\\")) or ".." in Path(name).parts
            ]
            require(errors, not unsafe, "iros2 APT snapshot contains unsafe paths")

            root = "apt-repository/"
            signing_key = apt_repository["signing_key"]
            expected_files = {
                root + signing_key["filename"]: signing_key["sha256"],
                **{
                    root + entry["path"]: entry["sha256"]
                    for entry in apt_repository["signed_metadata"].values()
                },
            }
            extracted: dict[str, bytes] = {}
            for name, expected_hash in expected_files.items():
                require(errors, name in members, f"iros2 APT snapshot is missing {name}")
                if name not in members:
                    continue
                stream = snapshot.extractfile(members[name])
                require(errors, stream is not None, f"iros2 APT snapshot cannot read {name}")
                if stream is None:
                    continue
                content = stream.read()
                extracted[name] = content
                require(
                    errors,
                    hashlib.sha256(content).hexdigest() == expected_hash,
                    f"iros2 APT snapshot hash mismatch for {name}",
                )

            key_name = root + signing_key["filename"]
            if key_name in extracted:
                try:
                    fingerprint = openpgp_v4_fingerprint(extracted[key_name])
                except (UnicodeDecodeError, ValueError) as error:
                    errors.append(f"iros2 signing key cannot be parsed: {error}")
                else:
                    require(
                        errors,
                        fingerprint == signing_key["fingerprint"],
                        "iros2 signing-key fingerprint mismatch",
                    )

            for package in iros2["packages"]:
                prefix = (
                    f"{root}pool/main/i/iros2j/{package['name']}_"
                    f"{package['version']}_"
                )
                candidates = [
                    name
                    for name in members
                    if name.startswith(prefix)
                    and name.endswith(("_arm64.deb", "_all.deb"))
                ]
                require(
                    errors,
                    len(candidates) == 1,
                    f"iros2 APT snapshot must contain exactly one {package['name']} package",
                )
    except (OSError, tarfile.TarError) as error:
        errors.append(f"iros2 APT snapshot cannot be audited: {error}")

    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"iros2 package inventory cannot be read: {error}")
        return
    require(
        errors,
        inventory.get("install_prefix") == iros2["install_prefix"],
        "iros2 package inventory install prefix is inconsistent",
    )
    require(
        errors,
        inventory.get("package_version") == iros2["debian_version"],
        "iros2 package inventory version is inconsistent",
    )
    inventory_names = {
        package.get("debian_name")
        for package in inventory.get("packages", [])
        if isinstance(package, dict)
    }
    for package in iros2["packages"]:
        require(
            errors,
            package["name"] in inventory_names,
            f"iros2 package inventory is missing {package['name']}",
        )


def validate_schema_v2(manifest: dict[str, Any], released: bool) -> list[str]:
    errors: list[str] = []
    release = manifest.get("release", {})
    platform = manifest.get("platform", {})
    components = manifest.get("components", {})
    artifacts = manifest.get("artifacts", {})
    runtime = manifest.get("runtime", {})
    gates = manifest.get("gates", {})

    version = release.get("version", "")
    require(errors, bool(VERSION_RE.fullmatch(version)), "release.version must have four numeric components")
    require(errors, release.get("name") == "ivins", "release.name must be ivins")
    require(errors, release.get("tag") == f"v{version}", "release.tag must equal v<release.version>")
    require(
        errors,
        release.get("debian_version") == f"{version}-1+deb13",
        "release.debian_version is inconsistent",
    )
    require(
        errors,
        bool(SEMVER_RE.fullmatch(release.get("process_version", ""))),
        "release.process_version must use semantic versioning",
    )
    require(
        errors,
        release.get("version") == (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "release.version must match VERSION",
    )
    require(
        errors,
        release.get("process_version")
        == (ROOT / "PROCESS_VERSION").read_text(encoding="utf-8").strip(),
        "release.process_version must match PROCESS_VERSION",
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

    require(
        errors,
        set(components) == {"iros2", "imavros", "vins"},
        "components must contain exactly iros2, imavros, and vins",
    )

    iros2 = components.get("iros2", {})
    require(
        errors,
        iros2.get("repository") == "https://github.com/Drone-Age/iros2_0.git",
        "iros2.repository is inconsistent",
    )
    require(errors, bool(SHA_RE.fullmatch(iros2.get("commit", ""))), "iros2.commit must be a full Git SHA")
    require(errors, bool(iros2.get("tag")), "iros2.tag is required")
    require(errors, iros2.get("package_namespace") == "iros2j", "iros2.package_namespace must be iros2j")
    require(errors, iros2.get("install_prefix") == "/opt/iros2j", "iros2.install_prefix must be /opt/iros2j")
    require(
        errors,
        bool(DEBIAN_VERSION_RE.fullmatch(iros2.get("debian_version", ""))),
        "iros2.debian_version is invalid",
    )

    apt_repository = iros2.get("apt_repository", {})
    apt_filename = apt_repository.get("filename", "")
    apt_url = apt_repository.get("url", "")
    require(errors, apt_filename.endswith(".tar.gz"), "iros2 APT repository filename is invalid")
    require(errors, bool(apt_url), "iros2 APT repository URL is required")
    require(errors, "/releases/latest/" not in apt_url, "iros2 APT repository forbids a latest URL")
    require(
        errors,
        bool(SHA256_RE.fullmatch(apt_repository.get("sha256", ""))),
        "iros2 APT repository SHA-256 is required",
    )

    signing_key = apt_repository.get("signing_key", {})
    require(
        errors,
        signing_key.get("filename") == "iros2j-archive-keyring.asc",
        "iros2 signing key filename is invalid",
    )
    require(
        errors,
        bool(SHA256_RE.fullmatch(signing_key.get("sha256", ""))),
        "iros2 signing key SHA-256 is required",
    )
    require(
        errors,
        bool(FINGERPRINT_RE.fullmatch(signing_key.get("fingerprint", ""))),
        "iros2 signing key fingerprint must be 40 uppercase hexadecimal characters",
    )

    signed_metadata = apt_repository.get("signed_metadata", {})
    expected_metadata = {
        "inrelease": "dists/trixie/InRelease",
        "release": "dists/trixie/Release",
        "release_signature": "dists/trixie/Release.gpg",
    }
    for name, expected_path in expected_metadata.items():
        entry = signed_metadata.get(name, {})
        require(errors, entry.get("path") == expected_path, f"iros2 signed metadata {name} path is invalid")
        require(
            errors,
            bool(SHA256_RE.fullmatch(entry.get("sha256", ""))),
            f"iros2 signed metadata {name} SHA-256 is required",
        )

    inventory = iros2.get("package_inventory", {})
    require(
        errors,
        inventory.get("filename") == "package-inventory.json",
        "iros2 package inventory filename is invalid",
    )
    require(errors, bool(inventory.get("url")), "iros2 package inventory URL is required")
    require(errors, "/releases/latest/" not in (inventory.get("url") or ""), "iros2 package inventory forbids a latest URL")
    require(
        errors,
        bool(SHA256_RE.fullmatch(inventory.get("sha256", ""))),
        "iros2 package inventory SHA-256 is required",
    )

    packages = iros2.get("packages", [])
    require(errors, isinstance(packages, list) and bool(packages), "iros2.packages must be a non-empty list")
    package_names: list[str] = []
    if isinstance(packages, list):
        for index, package in enumerate(packages):
            if not isinstance(package, dict):
                errors.append(f"iros2.packages[{index}] must be an object")
                continue
            name = package.get("name", "")
            package_names.append(name)
            require(errors, name.startswith("iros2j-"), f"iros2.packages[{index}].name must use the iros2j namespace")
            require(
                errors,
                package.get("version") == iros2.get("debian_version"),
                f"iros2.packages[{index}].version must equal iros2.debian_version",
            )
    require(errors, len(package_names) == len(set(package_names)), "iros2.packages must not contain duplicates")
    required_metapackages = {
        "iros2j-ros-core",
        "iros2j-ros-base",
        "iros2j-common-interfaces",
        "iros2j-vision-opencv",
        "iros2j-rviz2",
    }
    require(
        errors,
        required_metapackages.issubset(package_names),
        "iros2.packages must include the required released metapackages",
    )

    expected_binary_components = {
        "imavros": (
            "https://github.com/Drone-Age/iMAVROS-release.git",
            "imavros",
            "/opt/imavros",
        ),
        "vins": (
            "https://github.com/Drone-Age/VINS-NEO.git",
            "vins-mono-ros2",
            "/opt/vins",
        ),
    }
    for name, (expected_repository, expected_package, expected_prefix) in expected_binary_components.items():
        component = components.get(name, {})
        artifact = component.get("artifact", {})
        require(errors, component.get("repository") == expected_repository, f"{name}.repository is inconsistent")
        require(errors, component.get("package") == expected_package, f"{name}.package is inconsistent")
        require(errors, component.get("install_prefix") == expected_prefix, f"{name}.install_prefix is inconsistent")
        require(errors, bool(SHA_RE.fullmatch(component.get("commit", ""))), f"{name}.commit must be a full Git SHA")
        require(errors, bool(component.get("tag")), f"{name}.tag is required")
        require(
            errors,
            bool(DEBIAN_VERSION_RE.fullmatch(component.get("debian_version", ""))),
            f"{name}.debian_version is invalid",
        )
        require(errors, artifact.get("filename", "").endswith("_arm64.deb"), f"{name} artifact filename is invalid")
        require(errors, bool(artifact.get("url")), f"{name} artifact URL is required")
        require(errors, "/releases/latest/" not in (artifact.get("url") or ""), f"{name} artifact forbids a latest URL")
        require(
            errors,
            bool(SHA256_RE.fullmatch(artifact.get("sha256", ""))),
            f"{name} artifact SHA-256 is required",
        )

    expected_activation = ["/opt/iros2j", "/opt/imavros", "/opt/vins"]
    require(
        errors,
        runtime.get("activation_order") == expected_activation,
        "runtime.activation_order must be /opt/iros2j, /opt/imavros, /opt/vins",
    )
    require(
        errors,
        runtime.get("rmw_implementation") == "rmw_fastrtps_cpp",
        "runtime.rmw_implementation must be rmw_fastrtps_cpp",
    )
    require(
        errors,
        runtime.get("product_activation") == "/usr/share/ivins/activate.sh",
        "runtime.product_activation must be /usr/share/ivins/activate.sh",
    )
    require(
        errors,
        runtime.get("ogre_library_path")
        == "/opt/iros2j/rviz_ogre_vendor/opt/rviz_ogre_vendor/lib/OGRE",
        "runtime.ogre_library_path is inconsistent",
    )
    require(errors, "iros2-0" in runtime.get("forbidden_packages", []), "runtime must forbid iros2-0")
    require(errors, "/opt/iros2_0/jazzy" in runtime.get("forbidden_prefixes", []), "runtime must forbid /opt/iros2_0/jazzy")

    meta = artifacts.get("meta_package", {})
    bundle = artifacts.get("offline_bundle", {})
    release_notes = artifacts.get("release_notes", [])
    require(errors, meta.get("package") == "ivins", "meta package name must be ivins")
    require(
        errors,
        meta.get("filename") == f"ivins_{release.get('debian_version', '')}_arm64.deb",
        "meta package filename is inconsistent",
    )
    require(errors, bundle.get("filename", "").endswith("_arm64.tar.zst"), "offline bundle filename is invalid")
    require(
        errors,
        isinstance(release_notes, list)
        and {entry.get("language") for entry in release_notes if isinstance(entry, dict)}
        == {"en", "uk"},
        "artifacts.release_notes must contain English and Ukrainian documents",
    )
    if isinstance(release_notes, list):
        for index, entry in enumerate(release_notes):
            if not isinstance(entry, dict):
                continue
            source = entry.get("source", "")
            require(
                errors,
                entry.get("filename") == Path(source).name,
                f"artifacts.release_notes[{index}].filename is inconsistent",
            )
            require(
                errors,
                bool(source)
                and not Path(source).is_absolute()
                and ".." not in Path(source).parts
                and (ROOT / source).is_file(),
                f"artifacts.release_notes[{index}].source is invalid",
            )

    if released:
        require(errors, release.get("status") == "released", "--released requires release.status=released")
        for name, entry in {"meta_package": meta, "offline_bundle": bundle}.items():
            require(errors, bool(entry.get("url")), f"released manifest requires {name} URL")
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
            "hardware",
            "publication",
            "post_release",
        )
        for name in required_gates:
            require(errors, bool(gates.get(name)), f"released manifest requires gates.{name}")
        native = gates.get("component_native", {})
        for name in components:
            require(errors, bool(native.get(name)), f"released manifest requires native gate for {name}")

    return errors


def validate(manifest: dict[str, Any], released: bool) -> list[str]:
    if manifest.get("schema_version") == 2:
        return validate_schema_v2(manifest, released)

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
        if manifest["schema_version"] == 1:
            artifact_entries = [
                component["artifact"]
                for component in manifest["components"].values()
            ]
        else:
            artifact_entries = [
                manifest["components"]["iros2"]["apt_repository"],
                manifest["components"]["iros2"]["package_inventory"],
                manifest["components"]["imavros"]["artifact"],
                manifest["components"]["vins"]["artifact"],
            ]
        for artifact in artifact_entries:
            candidate = args.check_artifacts / artifact["filename"]
            if not candidate.is_file():
                errors.append(f"artifact is missing: {candidate}")
            elif artifact.get("sha256") and digest(candidate) != artifact["sha256"]:
                errors.append(f"artifact checksum mismatch: {candidate}")
        if manifest["schema_version"] == 2:
            audit_iros2j_snapshot(manifest, args.check_artifacts, errors)

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
