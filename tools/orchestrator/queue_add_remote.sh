#!/usr/bin/env bash
# tools/orchestrator/queue_add_remote.sh
#
# Backward-compat wrapper: delegates to queue_add.sh with queue=overnight_queue.
# Kept so any callers that hard-code this path continue working.
#
# Usage:
#   bash tools/orchestrator/queue_add_remote.sh <name> <script_rel_path> <prereg_rel_path> <timeout_s>

set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "usage: $0 <name> <script_rel_path> <prereg_rel_path> <timeout_s>" >&2
  exit 2
fi

NAME="$1"
SCRIPT_REL="$2"
PREREG_REL="$3"
TIMEOUT_S="$4"

DISPATCHER="$(dirname "$0")/queue_add.sh"
echo "[remote-queue-add] delegating to queue_add.sh (queue=overnight_queue)"
bash "${DISPATCHER}" overnight_queue "${NAME}" "${SCRIPT_REL}" "${PREREG_REL}" "${TIMEOUT_S}"
