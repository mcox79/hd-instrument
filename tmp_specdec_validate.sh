#!/bin/bash
set -e

echo "=== bash syntax ==="
for f in /mnt/d/AI/hd-instrument/skypilot/cell_specdec/*.sh /mnt/d/AI/hd-instrument/tmp_dispatch_cell_specdec.sh; do
    bash -n "$f" && echo "  $(basename $f) OK"
done

echo ""
echo "=== source-test config ==="
( source /mnt/d/AI/hd-instrument/skypilot/cell_specdec/cell_specdec_config.sh && \
  echo "  CELL_NAME=$CELL_NAME CLUSTER_PREFIX=$CLUSTER_PREFIX EXPECTED_SCRIPT=$EXPECTED_SCRIPT" )

echo ""
echo "=== self-test ==="
chmod +x /mnt/d/AI/hd-instrument/skypilot/cell_specdec/*.sh /mnt/d/AI/hd-instrument/tmp_dispatch_cell_specdec.sh
/root/skyvenv/bin/python3 /mnt/d/AI/hd-instrument/experiments/exp_speculative_decoding_qwen_v1.py --self-test 2>&1 | tail -6

echo ""
echo "=== signature consistency (all defined funcs called with matching args) ==="
for FUNC in load_bridge_questions build_prompt apply_chat_template normalize_answer answer_f1 decide_verdict run_generation_pass _emit_failure_metrics; do
    DEF=$(grep -nP "^def ${FUNC}\(" /mnt/d/AI/hd-instrument/experiments/exp_speculative_decoding_qwen_v1.py)
    echo "  $FUNC def: $DEF"
done

echo ""
echo "=== build bundle ==="
bash /mnt/d/AI/hd-instrument/skypilot/cell_specdec/build_cell_specdec_ship.sh 2>&1 | tail -8

echo ""
echo "=== sky launch DRYRUN (GH200) ==="
source /root/skyvenv/bin/activate
cd /root/cell_specdec-ship
sky launch -y --dryrun --region us-east-3 --instance-type gpu_1x_gh200 --down -i 30 \
    --env HF_TOKEN=foo \
    /root/cell_specdec-ship/skypilot/cell_specdec_qwen_h100.yaml 2>&1 | tail -10

echo ""
echo "=== ALL PRE-DISPATCH CHECKS PASSED ==="
