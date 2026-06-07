#!/usr/bin/env bash
# cell4_config.sh -- per-cell config for CELL-4 (HP-12 V2 100K pseudoinverse).
# CELL-4 is mostly numpy/CPU; H100/GH200 is overkill but uses our existing infra.

# Identity
CELL_NAME="CELL-4"
CLUSTER_PREFIX="cell4hp"

# Paths
YAML_PATH="/root/cell4-ship/skypilot/cell4_hp12_v2_h100.yaml"
BUNDLE_PATH="/root/cell4-ship"
EXPECTED_SCRIPT="exp_substrate_hp12_v2_100k_pseudoinverse_v1.py"

# Capacity polling (cheapest first; CELL-4 is light)
SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_pcie gpu_1x_h100_sxm5"
SKYPILOT_KNOWN_REGIONS="us-east-1 us-east-2 us-east-3 us-west-1 us-west-2 us-west-3 us-south-1 us-south-2 us-south-3 us-midwest-1 us-southeast-1 asia-northeast-1 asia-northeast-2 asia-south-1 australia-east-1 europe-central-1 europe-south-1 me-west-1"

GPU_SPEC="H100:1"
AUTOSTOP_MIN=30
HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"
MAX_ACQUIRE_ATTEMPTS=1

# Outputs (single-quoted REMOTE_OUTPUT_PATH; ~ expands on remote)
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_substrate_hp12_v2_100k_pseudoinverse_v1/'
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cell4_results"

# Logs
LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cell4_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cell4_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cell4_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cell4_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cell4_state.json"

LAUNCHER_LOCK_PATH="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
HOURLY_RATE_USD=3.30
