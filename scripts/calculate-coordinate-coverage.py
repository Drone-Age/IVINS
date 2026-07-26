#!/usr/bin/env python3
"""Calculate one-second coordinate coverage for a recorded ROS 2 topic."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from rosbags.highlevel import AnyReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    parser.add_argument("--topic", default="/vins_estimator/odometry")
    parser.add_argument("--playback-start-ns", type=int, required=True)
    parser.add_argument("--playback-duration-seconds", type=float, required=True)
    parser.add_argument("--threshold-percent", type=float, default=90.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    total_intervals = math.ceil(args.playback_duration_seconds)
    covered: set[int] = set()
    messages = 0
    with AnyReader([args.bag]) as reader:
        connections = [item for item in reader.connections if item.topic == args.topic]
        for _, timestamp, _ in reader.messages(connections=connections):
            interval = (timestamp - args.playback_start_ns) // 1_000_000_000
            if 0 <= interval < total_intervals:
                covered.add(int(interval))
                messages += 1

    coverage = len(covered) / total_intervals * 100 if total_intervals else 0.0
    result = {
        "test_id": "euroc_coordinate_coverage",
        "result": "PASS" if coverage >= args.threshold_percent else "FAIL",
        "topic": args.topic,
        "playback_start_ns": args.playback_start_ns,
        "playback_duration_seconds": args.playback_duration_seconds,
        "interval_seconds": 1,
        "total_intervals": total_intervals,
        "covered_intervals": len(covered),
        "coordinate_messages_in_window": messages,
        "coverage_percent": round(coverage, 6),
        "threshold_percent": args.threshold_percent,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
