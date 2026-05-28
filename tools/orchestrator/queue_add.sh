#!/usr/bin/env bash
# tools/orchestrator/queue_add.sh
#
# Multi-queue dispatcher.  Routes an experiment to the correct runner queue.
#
# Usage:
#   bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout_s> [extra_flags...]
#
# Args (positional; first 5 required):
#   queue       overnight_queue | remote_cpu_queue | local_cpu_queue
#   name        queue entry name (also HDLAB_EXP_NAME on the runner)
#   script      script path relative to repo root (e.g. experiments/exp_X.py)
#   prereg      prereg path relative to repo root (e.g. preregs/2026-05-23_X.md)
#   timeout_s   per-run timeout in seconds (e.g. 3600)
#
# Optional extra flags (passed through verbatim to queue_add.py):
#   --rerun-as <new_name>   Queue clone under new_name; original entry untouched.
#   --allow-duplicate       Reset a terminal (done/failed/completed/canceled/killed) entry to pending.
#   --skip-smoke            Skip the smoke run.
#
# Queue routing:
#   overnight_queue   -> SCP + SSH to marsh@home; runs queue_add.py there targeting overnight_queue
#   remote_cpu_queue  -> SCP + SSH to marsh@home; runs queue_add.py there targeting remote_cpu_queue
#   local_cpu_queue   -> direct local queue_add.py call (no SCP; script already in local repo)
#
# Exits 0 on success, non-zero on failure.  All output goes to stdout/stderr.

set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "usage: $0 <queue> <name> <script_rel_path> <prereg_rel_path> <timeout_s> [extra_flags...]" >&2
  exit 2
fi

QUEUE="$1"
NAME="$2"
SCRIPT_REL="$3"
PREREG_REL="$4"
TIMEOUT_S="$5"
shift 5
# Any remaining args are passed through to queue_add.py (e.g. --rerun-as, --allow-duplicate).
EXTRA_FLAGS=("$@")

REPO_LOCAL="$(cd "$(dirname "$0")/../.." && pwd)"
REPO_REMOTE="C:/dev/hd-instrument"
SSH_TARGET="marsh@home"

echo "[queue-add] queue=${QUEUE} name=${NAME}"

# Ship-attempt sentinel (audit rec #2 / Condition 2). Heartbeat watchdog reads
# this to detect ships that "succeeded locally" but never landed in remote
# queue.json (silent SSH/SCP failures). Written ON SUCCESSFUL EXIT below.
SHIP_SENTINEL="${REPO_LOCAL}/data/recent_ship_attempts.jsonl"
record_ship_attempt() {
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  mkdir -p "$(dirname "${SHIP_SENTINEL}")"
  # JSONL line; single-line, no embedded newlines. Atomic append is fine on
  # local FS; torn writes are tolerated by the watchdog parser.
  printf '{"ts":"%s","queue":"%s","name":"%s","attempted_at":"%s"}\n' \
    "${now}" "${QUEUE}" "${NAME}" "${now}" >> "${SHIP_SENTINEL}"
}

if [[ "${QUEUE}" == "local_cpu_queue" ]]; then
  # ── Local CPU path ──────────────────────────────────────────────────────────
  # Script and prereg are already in the local repo; no SCP needed.
  SCRIPT_LOCAL="${REPO_LOCAL}/${SCRIPT_REL}"
  PREREG_LOCAL="${REPO_LOCAL}/${PREREG_REL}"

  if [[ ! -f "${SCRIPT_LOCAL}" ]]; then
    echo "FAIL: script not found at ${SCRIPT_LOCAL}" >&2
    exit 3
  fi
  if [[ ! -f "${PREREG_LOCAL}" ]]; then
    echo "FAIL: prereg not found at ${PREREG_LOCAL}" >&2
    exit 3
  fi

  echo "[queue-add] local path: ${SCRIPT_LOCAL}"
  echo "[queue-add] running local queue_add.py for local_cpu_queue"
  QUEUE_ADD_OUTPUT=$(python "${REPO_LOCAL}/tools/queue_add.py" \
    local_cpu_queue \
    "${NAME}" \
    "${SCRIPT_REL}" \
    --prereg "${PREREG_REL}" \
    --timeout "${TIMEOUT_S}" \
    --skip-smoke \
    "${EXTRA_FLAGS[@]}" 2>&1)
  echo "${QUEUE_ADD_OUTPUT}"

  # Only record ship attempt if queue_add.py actually added the entry (not a dedup reject).
  # A dedup-rejected ship prints "WARN: ... already in queue" and exits 0 but does NOT
  # add the entry. Recording it as a ship_attempt would cause watchdog ship_unconfirmed
  # false positives (the entry is "completed" in queue.json, not newly pending).
  if echo "${QUEUE_ADD_OUTPUT}" | grep -qF "already in queue"; then
    echo "[queue-add] SKIP ship_attempt sentinel: duplicate rejected by queue_add.py"
  else
    record_ship_attempt
  fi
  echo "[queue-add] OK: ${NAME} queued to local_cpu_queue"

elif [[ "${QUEUE}" == "overnight_queue" || "${QUEUE}" == "remote_cpu_queue" ]]; then
  # ── Remote path (GPU or remote-CPU runner on marsh@home) ────────────────────
  SCRIPT_LOCAL="${REPO_LOCAL}/${SCRIPT_REL}"
  PREREG_LOCAL="${REPO_LOCAL}/${PREREG_REL}"

  if [[ ! -f "${SCRIPT_LOCAL}" ]]; then
    echo "FAIL: script not found at ${SCRIPT_LOCAL}" >&2
    exit 3
  fi
  if [[ ! -f "${PREREG_LOCAL}" ]]; then
    echo "FAIL: prereg not found at ${PREREG_LOCAL}" >&2
    exit 3
  fi

  SCRIPT_REMOTE_DIR="${REPO_REMOTE}/$(dirname "${SCRIPT_REL}")"
  PREREG_REMOTE_DIR="${REPO_REMOTE}/$(dirname "${PREREG_REL}")"

  echo "[queue-add] SCP script -> ${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
  scp -o ConnectTimeout=10 "${SCRIPT_LOCAL}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
  echo "[queue-add] SCP prereg -> ${SSH_TARGET}:${PREREG_REMOTE_DIR}/"
  scp -o ConnectTimeout=10 "${PREREG_LOCAL}" "${SSH_TARGET}:${PREREG_REMOTE_DIR}/"

  # SSH+PowerShell payload. Single-quote bash outer per [[feedback-ssh-powershell-quoting]].
  # Extra flags (e.g. --rerun-as, --allow-duplicate) are appended verbatim.
  # HDLAB_QUEUE_ADD_ON_REMOTE=1 satisfies the host-guard in queue_add.py that
  # refuses direct local writes to remote-queue queue.json files.
  EXTRA_FLAGS_STR="${EXTRA_FLAGS[*]:-}"
  PS_PAYLOAD="cd ${REPO_REMOTE}; \$env:HDLAB_QUEUE_ADD_ON_REMOTE='1'; .\\.venv\\Scripts\\python.exe tools/queue_add.py ${QUEUE} ${NAME} ${SCRIPT_REL} --prereg ${PREREG_REL} --timeout ${TIMEOUT_S} --skip-smoke ${EXTRA_FLAGS_STR}"

  echo "[queue-add] SSH queue_add -> ${SSH_TARGET} (${QUEUE})"
  echo "[queue-add] payload: ${PS_PAYLOAD}"
  ssh -o ConnectTimeout=10 "${SSH_TARGET}" "powershell -Command \"${PS_PAYLOAD}\""

  # Post-ship verification: confirm entry actually landed in REMOTE queue.json.
  # Catches scp/ssh silent failures and proves the entry is reachable by the runner.
  VERIFY_PS="Get-Content ${REPO_REMOTE}/data/${QUEUE}/queue.json | ConvertFrom-Json | Select-Object -ExpandProperty experiments | Where-Object { \$_.name -eq '${NAME}' } | Select-Object -ExpandProperty name"
  REMOTE_HIT=$(ssh -o ConnectTimeout=10 "${SSH_TARGET}" "powershell -Command \"${VERIFY_PS}\"" 2>/dev/null | tr -d '\r' | grep -F "${NAME}" || true)
  if [[ -z "${REMOTE_HIT}" ]]; then
    echo "FAIL: post-ship verification — ${NAME} NOT found in remote ${QUEUE}/queue.json" >&2
    exit 5
  fi
  echo "[queue-add] VERIFIED: ${NAME} present in remote ${QUEUE}/queue.json"
  record_ship_attempt
  echo "[queue-add] OK: ${NAME} queued to ${QUEUE}"

else
  echo "FAIL: unknown queue '${QUEUE}'. Must be one of: overnight_queue, remote_cpu_queue, local_cpu_queue" >&2
  exit 4
fi
