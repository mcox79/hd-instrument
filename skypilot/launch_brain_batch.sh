#!/usr/bin/env bash
# Launch the brain-inspired multi-channel probe batch on Lambda A100.
# Pre-flight (substrate single-pass economy) + Experiment B (spectral training
# monitor on GPT-2-small) + Experiment C (8-channel orchestration ablation
# on GPT-2-small).
#
# Run from inside WSL Ubuntu (any cwd; this script does the cd).
set -euo pipefail

source /root/skyvenv/bin/activate

cd /root/brain-ship
echo "launching from $(pwd)"
echo "bundle size: $(du -sh /root/brain-ship | awk '{print $1}')"

# --async: kick off launch in background; return immediately
# --retry-until-up: cycle through Lambda regions until A100 capacity found
# --down: terminate (not stop) on autostop -- Lambda doesn't support stop
# -i 30: autodown after 30 min idle
sky launch \
    -c hd-brain \
    -y \
    --async \
    --retry-until-up \
    --down \
    -i 30 \
    skypilot/brain_batch.yaml
