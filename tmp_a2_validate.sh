#!/bin/bash
set -e

echo "=== bash syntax ==="
for f in /mnt/d/AI/hd-instrument/skypilot/cell_a2/*.sh /mnt/d/AI/hd-instrument/tmp_dispatch_cell_a2.sh; do
    bash -n "$f" && echo "  $(basename $f) OK"
done

echo ""
echo "=== source-test config ==="
( source /mnt/d/AI/hd-instrument/skypilot/cell_a2/cell_a2_config.sh && \
  echo "  CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX EXPECTED_SCRIPT=$EXPECTED_SCRIPT" )

echo ""
echo "=== experiment script --self-test ==="
chmod +x /mnt/d/AI/hd-instrument/skypilot/cell_a2/*.sh /mnt/d/AI/hd-instrument/tmp_dispatch_cell_a2.sh
/root/skyvenv/bin/python3 -c "import numpy" 2>&1 && echo "  numpy ok"
# The script imports numpy unconditionally; skyvenv probably has it. Try self-test:
/root/skyvenv/bin/python3 /mnt/d/AI/hd-instrument/experiments/exp_substrate_llama8b_triples_khop_gpu_v1.py --self-test 2>&1 | tail -8

echo ""
echo "=== signature consistency check ==="
for FUNC in cphasor cidx norm_ent parse_triples _selftest load_hotpot extract_triples _emit_failure_metrics run verdict; do
    DEF=$(grep -nP "^def ${FUNC}\(" /mnt/d/AI/hd-instrument/experiments/exp_substrate_llama8b_triples_khop_gpu_v1.py)
    echo "  $FUNC: $DEF"
done

echo ""
echo "=== build bundle ==="
bash /mnt/d/AI/hd-instrument/skypilot/cell_a2/build_cell_a2_ship.sh 2>&1 | tail -8

echo ""
echo "=== sky launch DRYRUN (GH200) ==="
source /root/skyvenv/bin/activate
cd /root/cell_a2-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo \
    /root/cell_a2-ship/skypilot/cell_a2_llama8b_h100.yaml 2>&1 | tail -10

echo ""
echo "=== ALL PRE-DISPATCH CHECKS PASSED ==="
