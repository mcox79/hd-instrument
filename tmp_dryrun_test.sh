#!/bin/bash
echo "=== copy fixed YAMLs into bundles ==="
cp /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_distillation_h100.yaml \
   /root/cell3-ship/skypilot/cell3_distillation_h100.yaml
cp /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_hp12_v2_h100.yaml \
   /root/cell4-ship/skypilot/cell4_hp12_v2_h100.yaml
echo "  OK"

echo ""
echo "=== CELL-3 dryrun: gh200 (us-east-3) ==="
source /root/skyvenv/bin/activate
cd /root/cell3-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo --env CELL3_MAX_ARTICLES=1000000 \
    /root/cell3-ship/skypilot/cell3_distillation_h100.yaml 2>&1 | tail -15

echo ""
echo "=== CELL-3 dryrun: h100_sxm5 (us-south-2) ==="
sky launch -y --dryrun --region us-south-2 --instance-type gpu_1x_h100_sxm5 --down -i 30 \
    --env HF_TOKEN=foo --env CELL3_MAX_ARTICLES=1000000 \
    /root/cell3-ship/skypilot/cell3_distillation_h100.yaml 2>&1 | tail -15

echo ""
echo "=== CELL-4 dryrun: gh200 (us-east-3) ==="
cd /root/cell4-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo \
    /root/cell4-ship/skypilot/cell4_hp12_v2_h100.yaml 2>&1 | tail -15
