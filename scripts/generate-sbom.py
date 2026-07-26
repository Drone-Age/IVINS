#!/usr/bin/env python3
"""Generate a minimal CycloneDX SBOM for the exact iVINS Debian delivery."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("artifacts", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))

    entries = list(manifest["components"].values()) + [
        {
            "package": manifest["artifacts"]["meta_package"]["package"],
            "debian_version": manifest["release"]["debian_version"],
            "artifact": manifest["artifacts"]["meta_package"],
        }
    ]
    components = []
    for entry in entries:
        artifact = args.artifacts / entry["artifact"]["filename"]
        components.append(
            {
                "type": "application",
                "name": entry["package"],
                "version": entry["debian_version"],
                "purl": (
                    f"pkg:deb/debian/{entry['package']}@"
                    f"{entry['debian_version']}?arch=arm64"
                ),
                "hashes": [{"alg": "SHA-256", "content": sha256(artifact)}],
            }
        )

    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": manifest["release"]["name"],
                "version": manifest["release"]["version"],
            }
        },
        "components": components,
    }
    args.output.write_text(
        json.dumps(document, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
