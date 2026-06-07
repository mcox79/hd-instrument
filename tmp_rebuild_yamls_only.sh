#!/bin/bash
# Re-copy only the YAML files to the bundles (avoid the slow 21 GB shard recopy).
set -e
echo "=== copy fixed CELL-3 YAML into bundle ==="
cp /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_distillation_h100.yaml \
   /root/cell3-ship/skypilot/cell3_distillation_h100.yaml
echo "  OK"

echo "=== copy fixed CELL-4 YAML into bundle ==="
cp /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_hp12_v2_h100.yaml \
   /root/cell4-ship/skypilot/cell4_hp12_v2_h100.yaml
echo "  OK"

echo "=== verify the top-level accelerators is GONE ==="
echo "CELL-3:"
grep -E '^  accelerators' /root/cell3-ship/skypilot/cell3_distillation_h100.yaml && echo "  STILL THERE - bad" || echo "  not present - good"
echo "CELL-4:"
grep -E '^  accelerators' /root/cell4-ship/skypilot/cell4_hp12_v2_h100.yaml && echo "  STILL THERE - bad" || echo "  not present - good"

echo ""
echo "=== test sky launch dry-run with the new YAML ==="
source /root/skyvenv/bin/activate
cd /root/cell3-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo --env CELL3_MAX_ARTICLES=1000000 \
    /root/cell3-ship/skypilot/cell3_distillation_h100.yaml 2>&1 | tail -30
