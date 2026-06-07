#!/usr/bin/env bash
# Pre-flight gate for ANY cloud dispatch.
#
# Per [[cloud-dispatch-pre-flight-checklist]] (2026-06-06 lesson from CLOUD-1b
# zombie-process incident): catches the two bug classes that have burned money:
#   A. YAML setup-block + run-block reference DIFFERENT scripts (silent mismatch)
#   B. Orphan watcher / launcher / SkyPilot processes that can spawn unauthorized
#      EXPENSIVE cloud instances when capacity returns.
#
# Usage:
#   bash preflight_cloud_dispatch.sh <yaml_path> <expected_script_name> [bundle_path]
#
# Exits 0 if safe to dispatch; non-zero with a specific failure message otherwise.
# Designed to be called by smart_launch_*.sh as the FIRST step.

set -u
RED=$'\e[31m'; GREEN=$'\e[32m'; YELLOW=$'\e[33m'; RESET=$'\e[0m'

YAML="${1:-}"
EXPECTED_SCRIPT="${2:-}"
BUNDLE_PATH="${3:-/root/cloud-1-ship}"

if [ -z "$YAML" ] || [ -z "$EXPECTED_SCRIPT" ]; then
  echo "${RED}FAIL${RESET}: usage: $0 <yaml_path> <expected_script_name> [bundle_path]"
  exit 1
fi

fail() {
  echo "${RED}PREFLIGHT FAIL${RESET}: $1"
  exit 2
}

ok() {
  echo "  ${GREEN}OK${RESET}: $1"
}

warn() {
  echo "  ${YELLOW}WARN${RESET}: $1"
}

echo "=== preflight check for cloud dispatch ==="
echo "  yaml:            $YAML"
echo "  expected script: $EXPECTED_SCRIPT"
echo "  bundle path:     $BUNDLE_PATH"
echo ""

# ============================================================================
# CHECK 1: YAML script reference consistency (Bug A)
# ============================================================================
echo "[check 1/6] YAML script-reference consistency"
if [ ! -f "$YAML" ]; then
  fail "YAML file not found: $YAML"
fi
# Find ALL script invocations in YAML; check all reference EXPECTED_SCRIPT
SCRIPT_HITS=$(grep -oE 'experiments/[^[:space:]]+\.py' "$YAML" | sort -u)
echo "  script references in YAML:"
echo "$SCRIPT_HITS" | sed 's/^/    /'
MISMATCH=$(echo "$SCRIPT_HITS" | grep -v "$EXPECTED_SCRIPT" || true)
if [ -n "$MISMATCH" ]; then
  fail "YAML references scripts OTHER than $EXPECTED_SCRIPT:
$MISMATCH

This is the 2026-06-06 v1-vs-v2 mismatch bug. Setup-block and run-block
must reference the SAME script. Fix YAML and rebuild bundle before dispatch."
fi
ok "all YAML references point to $EXPECTED_SCRIPT"

# ============================================================================
# CHECK 2: Bundle contains the expected script
# ============================================================================
echo "[check 2/6] bundle contents"
BUNDLED_SCRIPT="$BUNDLE_PATH/experiments/$EXPECTED_SCRIPT"
if [ ! -f "$BUNDLED_SCRIPT" ]; then
  fail "bundled script missing: $BUNDLED_SCRIPT
Run build_*_ship.sh again."
fi
SIZE=$(stat -c '%s' "$BUNDLED_SCRIPT")
ok "$EXPECTED_SCRIPT present in bundle ($SIZE bytes)"

# ============================================================================
# CHECK 3: Zero orphan launcher / watcher / monitor processes (Bug B)
# ============================================================================
# The smart launcher INVOKES this preflight, so preflight's own ancestor chain
# (PPID, PPPID, ...) MAY contain a legitimately-running launcher we should not
# flag. Walk the ancestor chain and collect those PIDs to ignore.
echo "[check 3/6] orphan launcher / watcher / monitor processes"
ALLOWED_PIDS="$$ $PPID"
P=$PPID
while [ -n "$P" ] && [ "$P" != "1" ] && [ "$P" != "0" ]; do
  P=$(ps -o ppid= -p "$P" 2>/dev/null | tr -d ' ' || echo "")
  if [ -n "$P" ] && [ "$P" != "0" ] && [ "$P" != "1" ]; then
    ALLOWED_PIDS="$ALLOWED_PIDS $P"
  fi
done
# Build awk-ready skip list: PIDs in column 2 of ps output to ignore
ALLOWED_REGEX=$(echo "$ALLOWED_PIDS" | tr ' ' '|')
ORPHANS=$(ps auxf 2>/dev/null \
  | grep -iE 'watch_cloud_|launch_cloud_|smart_launch_cloud_|monitor_cloud_' \
  | grep -v grep \
  | awk -v sk="^($ALLOWED_REGEX)$" '$2 !~ sk' \
  || true)
if [ -n "$ORPHANS" ]; then
  echo "  orphan processes found (excluding current ancestor chain: $ALLOWED_PIDS):"
  echo "$ORPHANS" | sed 's/^/    /'
  fail "orphan launcher / watcher / monitor processes are running.
Kill them first:
  pkill -9 -f watch_cloud_
  pkill -9 -f launch_cloud_
  pkill -9 -f smart_launch_cloud_
  pkill -9 -f monitor_cloud_"
fi
ok "no orphan watcher / launcher / monitor processes (excl. current chain: $ALLOWED_PIDS)"

# ============================================================================
# CHECK 4: Lambda API direct probe -- ZERO running instances
# ============================================================================
echo "[check 4/6] Lambda API direct probe"
API_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys 2>/dev/null | head -1)
if [ -z "$API_KEY" ]; then
  warn "could not parse Lambda API key; skipping direct probe"
else
  INSTANCES_JSON=$(curl -s -u "${API_KEY}:" https://cloud.lambdalabs.com/api/v1/instances 2>/dev/null)
  N_INSTANCES=$(python3 -c "
import json, sys
try:
    d = json.loads('''$INSTANCES_JSON''')
    data = d.get('data', [])
    # Allow instances in 'terminating' state (they're going away soon)
    active = [i for i in data if i.get('status') not in ('terminating', 'terminated')]
    print(len(active))
    for i in active:
        print(f'  {i[\"id\"]} status={i.get(\"status\")} type={i.get(\"instance_type\",{}).get(\"name\")} region={i.get(\"region\",{}).get(\"name\")}', file=sys.stderr)
except Exception as e:
    print('ERR')
" 2>&1)
  N_ACTIVE=$(echo "$N_INSTANCES" | head -1)
  DETAILS=$(echo "$N_INSTANCES" | tail -n +2)
  if [ "$N_ACTIVE" = "ERR" ]; then
    warn "could not parse Lambda API response; skipping check"
  elif [ "$N_ACTIVE" -gt 0 ]; then
    echo "$DETAILS"
    fail "Lambda has $N_ACTIVE non-terminating instance(s) running.
Terminate them first via Lambda API direct (sky down alone may not propagate).
This is the 2026-06-06 zombie-cluster bug class."
  else
    ok "Lambda reports 0 non-terminating instances"
  fi
fi

# ============================================================================
# CHECK 5: sky status shows ZERO INIT/UP clusters WITH OUR PREFIX
# ============================================================================
# 2026-06-07: previously failed on ANY INIT/UP cluster. But when launching
# CELL-4 in parallel with CELL-3 SMOKE, CELL-4's preflight saw cell3sm-XXXXXX
# as INIT and falsely flagged it as an orphan. Now: filter by our own
# CLUSTER_PREFIX (env var) so only OUR cell's stale clusters block dispatch.
echo "[check 5/6] sky status"
CHECK_PREFIX="${CLUSTER_PREFIX:-}"
if [ -n "$CHECK_PREFIX" ]; then
  # Only flag clusters whose name starts with $CHECK_PREFIX-
  SKY_CLUSTERS=$(sky status 2>/dev/null | grep -E "^${CHECK_PREFIX}-[0-9]+" | grep -E 'INIT|UP' || true)
  OTHER_CLUSTERS=$(sky status 2>/dev/null | grep -E '^[a-z0-9-]+\s+Lambda' | grep -E 'INIT|UP' | grep -vE "^${CHECK_PREFIX}-" || true)
  if [ -n "$OTHER_CLUSTERS" ]; then
    echo "  other-cell clusters in INIT/UP (allowed, not ours):"
    echo "$OTHER_CLUSTERS" | sed 's/^/    /'
  fi
else
  # Fallback: no prefix supplied -> conservative; flag ANY INIT/UP
  SKY_CLUSTERS=$(sky status 2>/dev/null | grep -E '^[a-z0-9-]+\s+Lambda' | grep -E 'INIT|UP' || true)
fi
if [ -n "$SKY_CLUSTERS" ]; then
  echo "  OUR sky-tracked clusters in INIT/UP state (orphan?):"
  echo "$SKY_CLUSTERS" | sed 's/^/    /'
  fail "sky has clusters in INIT/UP state with our prefix '$CHECK_PREFIX'.
Run: sky status 2>/dev/null | grep -oE '${CHECK_PREFIX}-[0-9]+' | sort -u | xargs -r sky down -y"
fi
ok "sky status clean (no INIT/UP clusters with prefix '${CHECK_PREFIX:-<any>}')"

# ============================================================================
# CHECK 6: HF token file present
# ============================================================================
echo "[check 6/6] HF token availability"
HF_TOKEN_FILE=/mnt/d/AI/hd-instrument/.hf_token
if [ ! -f "$HF_TOKEN_FILE" ]; then
  fail ".hf_token missing at $HF_TOKEN_FILE"
fi
HF_TOKEN_LEN=$(wc -c < "$HF_TOKEN_FILE" | tr -d ' ')
if [ "$HF_TOKEN_LEN" -lt 30 ]; then
  fail ".hf_token suspiciously short ($HF_TOKEN_LEN bytes)"
fi
ok ".hf_token present ($HF_TOKEN_LEN bytes)"

echo ""
echo "${GREEN}=== PREFLIGHT PASS ===${RESET}"
echo "Safe to dispatch cloud run."
exit 0
