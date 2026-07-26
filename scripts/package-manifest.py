#!/usr/bin/env python3
"""Create the deterministic build-input manifest embedded in iVINS artifacts."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


def projection(manifest: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(manifest)
    result["release"]["status"] = "build-input"
    result["artifacts"]["meta_package"]["sha256"] = None
    result["artifacts"]["offline_bundle"]["sha256"] = None
    result["gates"] = {
        "metadata": None,
        "component_native": {
            "iros2": None,
            "imavros": None,
            "vins": None,
        },
        "package_audit": None,
        "clean_install": None,
        "ros_smoke": None,
        "dataset": None,
        "post_release": None,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.source.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(projection(manifest), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
