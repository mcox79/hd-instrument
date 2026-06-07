#!/usr/bin/env bash
# cell3_smoke_config.sh -- CELL-3 SMOKE variant (1M articles instead of 5.84M).
#
# Identical to cell3_config.sh EXCEPT:
#  - EXTRA_SKY_ENVS_STR forces --max-articles 1000000 via env override
#  - separate log paths so smoke + full can run concurrently without log races
#  - separate cluster prefix so kill switches don't cross-fire
#  - separate local results dir so smoke artifacts don't clobber full
#
# Purpose: catch real-Wikipedia distribution bugs (article-length distribution,
# tokenization wall-clock at scale, DataLoader speed at 4 GB cache, GPU memory
# headroom, step-loss convergence shape, cluster setup time) BEFORE full run.

# Identity
CELL_NAME="CELL-3-SMOKE"
CLUSTER_PREFIX="cell3sm"

# Paths (same script + YAML; different bundle to avoid race with full build)
YAML_PATH="/root/cell3-ship/skypilot/cell3_distillation_h100.yaml"
BUNDLE_PATH="/root/cell3-ship"
EXPECTED_SCRIPT="exp_substrate_cell3_distilled_22M_student_v1.py"

# Capacity polling
SKUS_PRIORITY="gpu_1x_gh200 gpu_1x_h100_sxm5 gpu_1x_h100_pcie"
SKYPILOT_KNOWN_REGIONS="us-east-1 us-east-2 us-east-3 us-west-1 us-west-2 us-west-3 us-south-1 us-south-2 us-south-3 us-midwest-1 us-southeast-1 asia-northeast-1 asia-northeast-2 asia-south-1 australia-east-1 europe-central-1 europe-south-1 me-west-1"

GPU_SPEC="H100:1"
AUTOSTOP_MIN=30
HF_TOKEN_FILE="/mnt/d/AI/hd-instrument/.hf_token"
MAX_ACQUIRE_ATTEMPTS=1

# The SMOKE-specific override: 1M articles instead of 5.84M
EXTRA_SKY_ENVS_STR="CELL3_MAX_ARTICLES=1000000"

# Separate output paths so smoke doesn't clobber full
REMOTE_OUTPUT_PATH='~/sky_workdir/data/exp_substrate_cell3_distilled_22M_student_v1/'
LOCAL_RESULTS_DIR="/mnt/d/AI/hd-instrument/data/cell3_smoke_results"

# Separate logs so concurrent smoke + full don't cross-write
LAUNCHER_LOG="/mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log"
KILL_SWITCH_LOG="/mnt/d/AI/hd-instrument/data/cell3_smoke_kill_switch.log"
PROGRESS_RSYNC_LOG="/mnt/d/AI/hd-instrument/data/cell3_smoke_progress_rsync.log"
WATCHDOG_LOG="/mnt/d/AI/hd-instrument/data/cell3_smoke_watchdog.log"
WATCHDOG_STATE_JSON="/mnt/d/AI/hd-instrument/data/cell3_smoke_state.json"

LAUNCHER_LOCK_PATH="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
HOURLY_RATE_USD=3.30
