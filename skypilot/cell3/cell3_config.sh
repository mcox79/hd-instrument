#!/usr/bin/env bash
# cell3_config.sh -- per-cell config for CELL-3 (distilled 22M student).
# Sourced by skypilot/safety/safety_launch_all.sh + each generic_*.sh.

# Identity
CELL_NAME="CELL-3"
CLUSTER_PREFIX="cell3fd"

# Paths
YAML_PATH="/root/cell3-ship/skypilot/cell3_distillation_h100.yaml"
BUNDLE_PATH="/root/cell3-ship"
EXPECTED_SCRIPT="exp_substrate_cell3_distilled_22M_student_v1.py"

# Capacity polling (GH200 priority since it's 47pct cheaper and we proved cu128 path)
SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_sxm5 gpu_1x_h100_pcie"
SKYPILOT_KNOWN_REGIONS="us-east-1 us-east-2 us-east-3 us-west-1 us-west-2 us-west-3 us-south-1 us-south-2 us-south-3 us-midwest-1 us-southeast-1 asia-northeast-1 asia-northeast-2 asia-south-1 australia-east-1 europe-central-1 europe-south-1 me-west-1"

# Cloud-launch params
GPU_SPEC="H100:1"   # YAML's any_of covers both GH200 + H100 via SkyPilot accelerators alias
AUTOSTOP_MIN=30
HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"
MAX_ACQUIRE_ATTEMPTS=1   # SAFETY: never auto-restart on cluster death

# Output paths -- IMPORTANT: REMOTE_OUTPUT_PATH single-quoted so ~ expands on
# the REMOTE ubuntu user's home, NOT locally on WSL root (CELL-2 v3 bug)
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_substrate_cell3_distilled_22M_student_v1/'
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cell3_results"

# Log paths
LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cell3_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cell3_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cell3_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cell3_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cell3_state.json"

# State + cost
LAUNCHER_LOCK_PATH="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
# H100 SXM5 = $4.29/h; GH200 = $2.29/h. Set to a middle estimate so watchdog
# cum_cost is roughly right regardless of SKU acquired.
HOURLY_RATE_USD=3.30

# Optional: scope override -- if set, passed to the script via env to limit articles
# Set CELL3_MAX_ARTICLES in env BEFORE invoking safety_launch_all.sh to override.
# Default: full 5.84M (no override).
export CELL3_MAX_ARTICLES="${CELL3_MAX_ARTICLES:-}"
