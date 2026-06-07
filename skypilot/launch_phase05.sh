#!/usr/bin/env bash
# Launch Phase 0.5 v1 (6-anchor pipeline) on Lambda H100 via SkyPilot.
# Run from inside WSL Ubuntu (any cwd; this script does the cd).
set -euo pipefail

source /root/skyvenv/bin/activate

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token at /mnt/d/AI/hd-instrument/.hf_token is empty"
  exit 1
fi
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars"

cd /root/hd-ship
echo "launching from $(pwd)"
echo "bundle size: $(du -sh /root/hd-ship | awk '{print $1}')"

# --async: kick off launch in background; return immediately
# --retry-until-up: cycle through Lambda regions until capacity found
# -i 10: autostop after 10 min idle (terminate cluster automatically)
sky launch \
    -c hd-phase05 \
    -y \
    --async \
    --retry-until-up \
    -i 10 \
    --env HF_TOKEN="${HF_TOKEN_VAL}" \
    skypilot/phase05.yaml
