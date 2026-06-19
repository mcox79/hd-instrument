#!/bin/bash
# Final pre-dispatch validation for CELL-COLBERT.
set -e

echo "=== bash syntax check ==="
bash -n /mnt/d/AI/hd-instrument/skypilot/cell_colbert/cell_colbert_config.sh && echo "  cell_colbert_config.sh OK"
bash -n /mnt/d/AI/hd-instrument/skypilot/cell_colbert/build_cell_colbert_ship.sh && echo "  build_cell_colbert_ship.sh OK"
bash -n /mnt/d/AI/hd-instrument/tmp_dispatch_cell_colbert.sh && echo "  tmp_dispatch_cell_colbert.sh OK"

echo ""
echo "=== source-test config ==="
( source /mnt/d/AI/hd-instrument/skypilot/cell_colbert/cell_colbert_config.sh && \
  echo "  CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX EXPECTED_SCRIPT=$EXPECTED_SCRIPT" )

echo ""
echo "=== run experiment script --self-test ==="
chmod +x /mnt/d/AI/hd-instrument/skypilot/cell_colbert/*.sh
chmod +x /mnt/d/AI/hd-instrument/tmp_dispatch_cell_colbert.sh
/root/skyvenv/bin/python3 /mnt/d/AI/hd-instrument/experiments/exp_colbert_v2_hotpot_distractor_v1.py --self-test 2>&1 | tail -8

echo ""
echo "=== build bundle ==="
bash /mnt/d/AI/hd-instrument/skypilot/cell_colbert/build_cell_colbert_ship.sh 2>&1 | tail -8

echo ""
echo "=== bundle contents ==="
find /root/cell_colbert-ship -type f -printf '%P  %s bytes\n' | sort

echo ""
echo "=== sky launch DRYRUN (GH200) ==="
source /root/skyvenv/bin/activate
cd /root/cell_colbert-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo \
    /root/cell_colbert-ship/skypilot/cell_colbert_hotpot_h100.yaml 2>&1 | tail -15

echo ""
echo "=== sky launch DRYRUN (H100 SXM5) ==="
sky launch -y --dryrun --region us-south-2 --instance-type gpu_1x_h100_sxm5 --down -i 30 \
    --env HF_TOKEN=foo \
    /root/cell_colbert-ship/skypilot/cell_colbert_hotpot_h100.yaml 2>&1 | tail -15

echo ""
echo "=== ALL PRE-DISPATCH CHECKS PASSED ==="
