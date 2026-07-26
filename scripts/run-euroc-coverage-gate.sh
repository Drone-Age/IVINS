#!/usr/bin/env bash
set -Eeuo pipefail

bag="${1:?Usage: run-euroc-coverage-gate.sh ROS2_BAG OUTPUT_DIR}"
output="${2:?Usage: run-euroc-coverage-gate.sh ROS2_BAG OUTPUT_DIR}"
mkdir -p "$output"
bag="$(realpath "$bag")"
output="$(realpath "$output")"

set +u
source /opt/iros2_0/jazzy/setup.bash
source /opt/vins/setup.bash
set -u

pids=()
cleanup() {
  for pid in "${pids[@]}"; do
    kill -INT "$pid" 2>/dev/null || true
  done
  wait "${pids[@]}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ros2 launch feature_tracker vins_feature_tracker.launch.py \
  >"$output/feature-tracker.log" 2>&1 &
pids+=("$!")
ros2 launch vins_estimator euroc.launch.py \
  >"$output/vins-estimator.log" 2>&1 &
pids+=("$!")
sleep 8

ros2 bag record --output "$output/coordinates" \
  /vins_estimator/odometry >"$output/record.log" 2>&1 &
record_pid=$!
pids+=("$record_pid")
sleep 2

ros2 bag play "$bag" >"$output/play.log" 2>&1
sleep 5
kill -INT "$record_pid" 2>/dev/null || true
wait "$record_pid" || true

ros2 bag info "$output/coordinates" >"$output/coordinates-info.txt"
