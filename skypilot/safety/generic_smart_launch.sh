#!/usr/bin/env bash
# generic_smart_launch.sh -- SSH-disconnect-aware smart launcher for ANY cell.
#
# REQUIRES: $1 = path to a config file (e.g. cell3_config.sh) that exports
#   CELL_NAME, CLUSTER_PREFIX, YAML_PATH, BUNDLE_PATH, EXPECTED_SCRIPT,
#   SKUS_PRIORITY (space-separated), SKYPILOT_KNOWN_REGIONS (space-separated),
#   REMOTE_OUTPUT_PATH, LOCAL_RESULTS_DIR, LAUNCHER_LOG, HF_TOKEN_FILE,
#   GPU_SPEC, AUTOSTOP_MIN (optional default 30), POLL_INTERVAL_SEC (optional 15).
#
# HARDENING from CELL-2 v3:
# - On sky launch exit != 0: check sky status; if cluster UP -> reattach via
#   sky logs (up to 200 retries) instead of teardown + retry-from-scratch.
# - Single-shot mode by default (MAX_ACQUIRE_ATTEMPTS=1) for safety;
#   set MAX_ACQUIRE_ATTEMPTS>1 in config only when retries are wanted.
# - PID lock file prevents duplicate launchers.
# - TRAP cleanup removes lock + child procs on exit.
# - Preflight gate via preflight_cloud_dispatch.sh.
# - sky api stop flushes catalog cache before launch (SkyPilot daemon bug).
# - Post-acquisition: explicit rsync (in case progress_rsync watcher missed
#   final batch) + sky down -y + verify_no_lambda_instances.

set -uo pipefail

if [ -z "${1:-}" ]; then
    echo "ERROR: usage: $0 <path-to-cell-config.sh>" >&2
    exit 2
fi
CONFIG_FILE="$1"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: config file not found: $CONFIG_FILE" >&2
    exit 2
fi
# shellcheck disable=SC1090
source "$CONFIG_FILE"

# Validate required vars
for required_var in CELL_NAME CLUSTER_PREFIX YAML_PATH BUNDLE_PATH EXPECTED_SCRIPT \
                   SKUS_PRIORITY SKYPILOT_KNOWN_REGIONS REMOTE_OUTPUT_PATH \
                   LOCAL_RESULTS_DIR LAUNCHER_LOG HF_TOKEN_FILE GPU_SPEC; do
    if [ -z "${!required_var:-}" ]; then
        echo "ERROR: config $CONFIG_FILE missing required var: $required_var" >&2
        exit 2
    fi
done

AUTOSTOP_MIN="${AUTOSTOP_MIN:-30}"
POLL_INTERVAL_SEC="${POLL_INTERVAL_SEC:-15}"
MAX_ACQUIRE_ATTEMPTS="${MAX_ACQUIRE_ATTEMPTS:-1}"   # SAFETY: default single-shot
SKY_LOGS_REATTACH_RETRIES="${SKY_LOGS_REATTACH_RETRIES:-200}"

source /root/skyvenv/bin/activate

LOCKFILE="/tmp/${CLUSTER_PREFIX}_smart_launch.pid"
if [ -f "$LOCKFILE" ]; then
    OLD_PID=$(cat "$LOCKFILE" 2>/dev/null || echo "")
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "ERROR: another launcher already running for ${CLUSTER_PREFIX} (PID=$OLD_PID)" >&2
        exit 1
    fi
fi
echo $$ > "$LOCKFILE"
cleanup_on_exit() {
    rm -f "$LOCKFILE"
    pkill -P $$ 2>/dev/null || true
}
trap cleanup_on_exit EXIT INT TERM

mkdir -p "$(dirname "$LAUNCHER_LOG")"

# CRITICAL FIX 2026-06-07: TRUNCATE launcher log on each new run start.
# Without this, the kill_switch's `tail -F $LAUNCHER_LOG` reads stale
# "launch genuinely failed" / "2nd cluster" messages from PREVIOUS failed
# runs and immediately kills the new launcher. This is a silent-kill that
# took several debugging cycles to find.
# We rotate the prior log to .prev to preserve evidence.
if [ -f "$LAUNCHER_LOG" ]; then
    mv "$LAUNCHER_LOG" "${LAUNCHER_LOG}.prev"
fi
: > "$LAUNCHER_LOG"

echo "===== [${CELL_NAME}] smart launch start $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LAUNCHER_LOG"

# Preflight gate
PREFLIGHT_SCRIPT="/mnt/d/AI/hd-instrument/skypilot/preflight_cloud_dispatch.sh"
echo "[${CELL_NAME}] running preflight gate..." | tee -a "$LAUNCHER_LOG"
# YAML_PATH is already the full bundled path; CLUSTER_PREFIX passed via env so
# preflight check 5 only flags clusters that are OURS (not other concurrent cells).
if ! CLUSTER_PREFIX="$CLUSTER_PREFIX" bash "$PREFLIGHT_SCRIPT" "$YAML_PATH" "$EXPECTED_SCRIPT" "$BUNDLE_PATH" >> "$LAUNCHER_LOG" 2>&1; then
    echo "ERROR: preflight FAILED for ${CELL_NAME}; aborting dispatch" | tee -a "$LAUNCHER_LOG"
    exit 1
fi
echo "[${CELL_NAME}] preflight PASS" | tee -a "$LAUNCHER_LOG"

# Optional pre-launch hook from config
if declare -f pre_launch_hook >/dev/null; then
    echo "[${CELL_NAME}] running pre_launch_hook..." | tee -a "$LAUNCHER_LOG"
    pre_launch_hook >> "$LAUNCHER_LOG" 2>&1 || {
        echo "ERROR: pre_launch_hook failed; aborting" | tee -a "$LAUNCHER_LOG"
        exit 1
    }
fi

# NOTE 2026-06-07: REMOVED `sky api stop` from here. Was added originally as a
# workaround for SkyPilot's in-memory catalog DataFrame cache (stale region
# data after editing ~/.sky/catalogs/<v>/vms.csv on disk). But it now causes
# the API server to die mid-flow, and orphan multiprocessing helpers hold
# port 50011, preventing the new sky server from starting. sky launch then
# fails with "SkyPilot API server process exited unexpectedly."
# We don't patch the catalog at runtime, so cached state is fine.
# If catalog patching is needed in the future, do it BEFORE dispatch and
# restart the server explicitly, not in the middle of the launcher flow.
echo "[${CELL_NAME}] using existing SkyPilot API server (no flush)..." | tee -a "$LAUNCHER_LOG"

HF_TOKEN_VAL="$(cat "$HF_TOKEN_FILE")"
if [ -z "${HF_TOKEN_VAL}" ]; then
    echo "ERROR: HF token empty at $HF_TOKEN_FILE" | tee -a "$LAUNCHER_LOG"
    exit 1
fi
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..." | tee -a "$LAUNCHER_LOG"

API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
    echo "ERROR: could not parse Lambda API key" | tee -a "$LAUNCHER_LOG"
    exit 1
fi
echo "api key parsed (len=${#API_KEY})" | tee -a "$LAUNCHER_LOG"

# Poll Lambda API for first available SKU in priority order
query_first_available() {
    local api_json
    api_json=$(curl -s -H "User-Agent: curl/7.81.0" -u "${API_KEY}:" \
        https://cloud.lambdalabs.com/api/v1/instance-types 2>/dev/null)
    SKUS_TO_TRY="$SKUS_PRIORITY" REGIONS_TO_TRY="$SKYPILOT_KNOWN_REGIONS" \
    python3 - <<'PYEOF'
import json, sys, os
api_json = sys.stdin.read()
try:
    d = json.loads(api_json) if api_json else None
except Exception:
    sys.exit(1)
if not d:
    api_json = os.environ.get("_API_JSON_FALLBACK", "")
    try:
        d = json.loads(api_json) if api_json else None
    except Exception:
        sys.exit(1)
if not d:
    sys.exit(1)
SKUS = os.environ.get("SKUS_TO_TRY", "").split()
SK_REGIONS = set(os.environ.get("REGIONS_TO_TRY", "").split())
data = d.get("data", {})
for sku in SKUS:
    regs_all = [r["name"] for r in data.get(sku, {}).get("regions_with_capacity_available", [])]
    regs = [r for r in regs_all if r in SK_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
sys.exit(1)
PYEOF
    # Note: we pass api_json via stdin OR via env fallback. Stdin is preferred.
}

attempt=0
CLUSTER_NAME=""

cd "$BUNDLE_PATH"

while [ "$attempt" -lt "$MAX_ACQUIRE_ATTEMPTS" ]; do
    attempt=$((attempt + 1))
    ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')

    # Capacity wait loop (no MAX -- we'll wait as long as needed).
    # BUG FIX 2026-06-07: previously used `echo "$api_json" | python3 - <<EOF`
    # which is broken in bash because the heredoc redirect WINS over the pipe
    # for stdin -- python would read the script text as JSON and fail.
    # Now: write api_json to a temp file, python reads the file path.
    AVAIL=""
    inner=0
    LAMBDA_JSON_TMP="/tmp/${CLUSTER_PREFIX}_lambda_types.json"
    while [ -z "$AVAIL" ]; do
        inner=$((inner + 1))
        curl -s -H "User-Agent: curl/7.81.0" -u "${API_KEY}:" \
            https://cloud.lambdalabs.com/api/v1/instance-types > "$LAMBDA_JSON_TMP" 2>/dev/null
        AVAIL=$(SKUS_TO_TRY="$SKUS_PRIORITY" REGIONS_TO_TRY="$SKYPILOT_KNOWN_REGIONS" \
                LAMBDA_JSON_FILE="$LAMBDA_JSON_TMP" python3 - <<'PYEOF2' 2>/dev/null
import json, sys, os
try:
    with open(os.environ["LAMBDA_JSON_FILE"]) as f:
        d = json.load(f)
except Exception:
    sys.exit(1)
SKUS = os.environ.get("SKUS_TO_TRY", "").split()
SK_REGIONS = set(os.environ.get("REGIONS_TO_TRY", "").split())
data = d.get("data", {})
for sku in SKUS:
    regs_all = [r["name"] for r in data.get(sku, {}).get("regions_with_capacity_available", [])]
    regs = [r for r in regs_all if r in SK_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
sys.exit(1)
PYEOF2
)
        if [ -z "$AVAIL" ]; then
            if [ $((inner % 20)) -eq 1 ]; then
                echo "[${ts}] attempt=${attempt} inner=${inner}: no capacity in $SKUS_PRIORITY; polling every ${POLL_INTERVAL_SEC}s" | tee -a "$LAUNCHER_LOG"
            fi
            sleep "$POLL_INTERVAL_SEC"
            ts=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
        fi
    done

    SKU=$(echo "$AVAIL" | awk '{print $1}')
    REGION=$(echo "$AVAIL" | awk '{print $2}')
    CLUSTER_NAME="${CLUSTER_PREFIX}-$(date +%H%M%S)"

    echo "[${ts}] attempt=${attempt} CAPACITY DETECTED: sku=${SKU} region=${REGION}" | tee -a "$LAUNCHER_LOG"
    echo "[${ts}] launching cluster=${CLUSTER_NAME}" | tee -a "$LAUNCHER_LOG"

    # Tear down any pre-existing clusters with our prefix (cluster-name collision)
    EXISTING=$(sky status 2>/dev/null | grep -oE "${CLUSTER_PREFIX}-[0-9]+" | sort -u || true)
    if [ -n "$EXISTING" ]; then
        echo "[${ts}] WARN: existing ${CLUSTER_PREFIX} clusters; tearing down" | tee -a "$LAUNCHER_LOG"
        echo "$EXISTING" | xargs -r sky down -y 2>&1 | tail -5 | tee -a "$LAUNCHER_LOG"
    fi

    # Build EXTRA env args from optional config-supplied EXTRA_SKY_ENVS_STR
    # Format: space-separated "NAME=VALUE" pairs (e.g., "CELL3_MAX_ARTICLES=1000000 FOO=bar")
    EXTRA_ENV_ARGS=""
    if [ -n "${EXTRA_SKY_ENVS_STR:-}" ]; then
        for kv in ${EXTRA_SKY_ENVS_STR}; do
            EXTRA_ENV_ARGS="${EXTRA_ENV_ARGS} --env ${kv}"
        done
        echo "[${ts}] extra env args: ${EXTRA_ENV_ARGS}" | tee -a "$LAUNCHER_LOG"
    fi

    # NOTE 2026-06-07: do NOT pass --gpus when --instance-type is set; SkyPilot
    # rejects this combo as inconsistent ("Accelerators for gpu_1x_gh200: {GH200},
    # Accelerators requested: {H100}"). The --instance-type already specifies
    # the GPU type implicitly. GPU_SPEC in config is now informational only.
    sky launch \
        -c "$CLUSTER_NAME" \
        -y \
        --region "$REGION" \
        --instance-type "$SKU" \
        --down \
        -i "$AUTOSTOP_MIN" \
        --env HF_TOKEN="${HF_TOKEN_VAL}" \
        ${EXTRA_ENV_ARGS} \
        "$YAML_PATH" 2>&1 | tee -a "$LAUNCHER_LOG"

    LAUNCH_RC=${PIPESTATUS[0]}
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit code: ${LAUNCH_RC}" | tee -a "$LAUNCHER_LOG"

    # HARDENING: SSH-disconnect-aware retry. If sky launch exits non-zero but
    # the cluster is still UP, the workload kept running -- reattach via sky logs.
    if [ "${LAUNCH_RC}" -ne 0 ]; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky launch exit non-zero; checking cluster + job state before any teardown" | tee -a "$LAUNCHER_LOG"
        REATTACH=0
        while [ "$REATTACH" -lt "$SKY_LOGS_REATTACH_RETRIES" ]; do
            if sky status "$CLUSTER_NAME" 2>/dev/null | grep -qE "UP|INIT"; then
                echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] cluster ${CLUSTER_NAME} still UP -- reattaching (try ${REATTACH})" | tee -a "$LAUNCHER_LOG"
                sky logs "$CLUSTER_NAME" 2>&1 | tee -a "$LAUNCHER_LOG"
                if sky queue "$CLUSTER_NAME" --skip-finished 2>/dev/null | grep -qE "RUNNING|PENDING"; then
                    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] job still RUNNING/PENDING; sky logs SSH dropped; retrying" | tee -a "$LAUNCHER_LOG"
                    REATTACH=$((REATTACH + 1))
                    sleep 15
                    continue
                fi
                LAUNCH_RC=0
                echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] job done on ${CLUSTER_NAME} after ${REATTACH} reattach(es)" | tee -a "$LAUNCHER_LOG"
                break
            else
                echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] cluster ${CLUSTER_NAME} no longer UP -- genuine failure" | tee -a "$LAUNCHER_LOG"
                break
            fi
        done
    fi

    if [ "${LAUNCH_RC}" -eq 0 ]; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ${CELL_NAME} ACQUIRED + RAN on ${SKU} in ${REGION}" | tee -a "$LAUNCHER_LOG"
        break
    fi

    # SAFETY: with MAX_ACQUIRE_ATTEMPTS=1 default, never reach a second attempt.
    # Only triggered if user explicitly opts in to retries via config.
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] launch genuinely failed (cluster dead)" | tee -a "$LAUNCHER_LOG"
    if [ "$attempt" -ge "$MAX_ACQUIRE_ATTEMPTS" ]; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] no more attempts (MAX_ACQUIRE_ATTEMPTS=${MAX_ACQUIRE_ATTEMPTS}); exiting" | tee -a "$LAUNCHER_LOG"
        sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LAUNCHER_LOG" || true
        exit 1
    fi
    sky down -y "$CLUSTER_NAME" 2>&1 | tee -a "$LAUNCHER_LOG" || true
    CLUSTER_NAME=""
    sleep "$POLL_INTERVAL_SEC"
done

if [ -z "$CLUSTER_NAME" ]; then
    echo "===== [${CELL_NAME}] smart launch FAILED $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LAUNCHER_LOG"
    exit 1
fi

# Post-acquisition: final rsync + sky down + verify
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] rsync ${CELL_NAME} outputs back from ${CLUSTER_NAME}" | tee -a "$LAUNCHER_LOG"
mkdir -p "$LOCAL_RESULTS_DIR"
rsync -av --partial --progress \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
    "${CLUSTER_NAME}:${REMOTE_OUTPUT_PATH}" \
    "${LOCAL_RESULTS_DIR}/" 2>&1 | tee -a "$LAUNCHER_LOG" || true

echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] sky down ${CLUSTER_NAME}" | tee -a "$LAUNCHER_LOG"
sky down -y "${CLUSTER_NAME}" 2>&1 | tee -a "$LAUNCHER_LOG" || true

if [ -f "/mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh" ]; then
    bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh 2>&1 | tee -a "$LAUNCHER_LOG" || true
fi

echo "===== [${CELL_NAME}] smart launch end $(date -u '+%Y-%m-%dT%H:%M:%SZ') =====" | tee -a "$LAUNCHER_LOG"
exit 0
