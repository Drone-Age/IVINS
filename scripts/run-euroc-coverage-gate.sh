#!/usr/bin/env bash
set -Eeuo pipefail

bag="${1:?Usage: run-euroc-coverage-gate.sh ROS2_BAG OUTPUT_DIR}"
output="${2:?Usage: run-euroc-coverage-gate.sh ROS2_BAG OUTPUT_DIR}"
mkdir -p "$output"
bag="$(realpath "$bag")"
output="$(realpath "$output")"

set +u
source /opt/iros2j/setup.bash
source /opt/imavros/setup.bash
source /opt/vins/setup.bash
set -u
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
command -v setsid >/dev/null

process_groups=()
cleanup() {
  for pgid in "${process_groups[@]}"; do
    kill -INT -- "-$pgid" 2>/dev/null || true
  done
  for _ in $(seq 1 50); do
    remaining=0
    for pgid in "${process_groups[@]}"; do
      kill -0 -- "-$pgid" 2>/dev/null && remaining=1 || true
    done
    (( remaining == 0 )) && break
    sleep 0.1
  done
  for pgid in "${process_groups[@]}"; do
    kill -TERM -- "-$pgid" 2>/dev/null || true
  done
  wait "${process_groups[@]}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

setsid ros2 launch feature_tracker vins_feature_tracker.launch.py \
  >"$output/feature-tracker.log" 2>&1 &
process_groups+=("$!")
setsid ros2 launch vins_estimator euroc.launch.py \
  >"$output/vins-estimator.log" 2>&1 &
process_groups+=("$!")
sleep 8

setsid ros2 bag record --output "$output/coordinates" \
  /vins_estimator/odometry >"$output/record.log" 2>&1 &
record_pid=$!
process_groups+=("$record_pid")
sleep 2

ros2 bag play "$bag" >"$output/play.log" 2>&1
sleep 5
kill -INT -- "-$record_pid" 2>/dev/null || true
wait "$record_pid" || true

ros2 bag info "$output/coordinates" >"$output/coordinates-info.txt"
