#!/usr/bin/env bash
# cell_colbert_config.sh -- per-cell config for ColBERT-v2 HotpotQA distractor pre-test.

# Identity
CELL_NAME="CELL-COLBERT"
CLUSTER_PREFIX="cellcb"

# Paths
YAML_PATH="/root/cell_colbert-ship/skypilot/cell_colbert_hotpot_h100.yaml"
BUNDLE_PATH="/root/cell_colbert-ship"
EXPECTED_SCRIPT="exp_colbert_v2_hotpot_distractor_v1.py"

# Capacity polling
SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_sxm5 gpu_1x_h100_pcie"
SKYPILOT_KNOWN_REGIONS="us-east-1 us-east-2 us-east-3 us-west-1 us-west-2 us-west-3 us-south-1 us-south-2 us-south-3 us-midwest-1 us-southeast-1 asia-northeast-1 asia-northeast-2 asia-south-1 australia-east-1 europe-central-1 europe-south-1 me-west-1"

GPU_SPEC="H100:1"
AUTOSTOP_MIN=30
HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"
MAX_ACQUIRE_ATTEMPTS=1

# Output paths (SINGLE-QUOTED so ~ expands on REMOTE side)
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_colbert_v2_hotpot_distractor_v1/'
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cell_colbert_results"

# Logs
LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cell_colbert_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cell_colbert_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cell_colbert_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cell_colbert_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cell_colbert_state.json"

LAUNCHER_LOCK_PATH="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
HOURLY_RATE_USD=3.30
