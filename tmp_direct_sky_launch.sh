#!/bin/bash
# Bare-minimum sky launch test (no safety stack) to verify YAML + capacity work.
echo "=== bare sky launch attempt ==="
source /root/skyvenv/bin/activate
cd /root/cell3-ship
HF_TOKEN=$(cat /mnt/d/AI/hd-instrument/.hf_token)
echo "HF token len: ${#HF_TOKEN}"

CLUSTER_NAME="cell3sm-bare-$(date +%H%M%S)"
echo "Launching as $CLUSTER_NAME (smoke variant; CELL3_MAX_ARTICLES=1000000)..."

# Pass --no-confirm + --detach-setup to skip prompts
exec sky launch \
    -c "$CLUSTER_NAME" \
    -y \
    --region us-east-3 \
    --instance-type gpu_1x_gh200 \
    --down \
    -i 30 \
    --env HF_TOKEN="$HF_TOKEN" \
    --env CELL3_MAX_ARTICLES=1000000 \
    /root/cell3-ship/skypilot/cell3_distillation_h100.yaml 2>&1
