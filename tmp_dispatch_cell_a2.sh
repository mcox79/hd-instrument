#!/bin/bash
# Dispatch CELL-A2 via safety stack; HOLD WSL alive via wait $ORCH_PID.
set -e

SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== verifying bundle ==="
test -d /root/cell_a2-ship || { echo "ERROR: bundle missing; run build first"; exit 1; }
test -f /root/cell_a2-ship/skypilot/cell_a2_llama8b_h100.yaml || { echo "ERROR: YAML missing"; exit 1; }
test -f /root/cell_a2-ship/experiments/exp_substrate_llama8b_triples_khop_gpu_v1.py || { echo "ERROR: script missing"; exit 1; }
test -f /root/cell_a2-ship/data/datasets/hotpot_qa_distractor_dev_1k.jsonl || { echo "ERROR: HotpotQA data missing"; exit 1; }
echo "  bundle: $(du -sh /root/cell_a2-ship 2>&1 | cut -f1)"

echo ""
echo "=== verifying NO existing Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current: $N_INST"
[ "$N_INST" = "0" ] || { echo "ERROR: pre-existing instances"; exit 1; }

echo ""
echo "=== launch CELL-A2 in background ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell_a2/cell_a2_config.sh \
    > $DATA/cell_a2_orchestrator.log 2>&1 &
ORCH_PID=$!
echo "  orchestrator PID: $ORCH_PID"

echo ""
echo "===== HOLDING WSL ALIVE BY WAITING FOR ORCHESTRATOR (~2-3 hr) ====="
wait $ORCH_PID
RC=$?
echo "===== CELL-A2 orchestrator finished rc=$RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== final state ==="
ls -la $DATA/cell_a2_results/ 2>&1 | head -10
echo ""
echo "  verdict:"
cat $DATA/cell_a2_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -30
