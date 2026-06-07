#!/bin/bash
# Dispatch CELL-SPECDEC via safety stack; HOLD WSL alive via wait $ORCH_PID.
set -e

SAFETY=/mnt/d/AI/hd-instrument/skypilot/safety/safety_launch_all.sh
DATA=/mnt/d/AI/hd-instrument/data
mkdir -p "$DATA"

echo "=== verifying bundle ==="
test -d /root/cell_specdec-ship || { echo "ERROR: bundle missing; run build first"; exit 1; }
test -f /root/cell_specdec-ship/skypilot/cell_specdec_qwen_h100.yaml || { echo "ERROR: YAML missing"; exit 1; }
test -f /root/cell_specdec-ship/experiments/exp_speculative_decoding_qwen_v1.py || { echo "ERROR: script missing"; exit 1; }
echo "  bundle: $(du -sh /root/cell_specdec-ship 2>&1 | cut -f1)"

echo ""
echo "=== verifying NO existing Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
N_INST=$(curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances | \
    python3 -c "import sys,json;print(len(json.load(sys.stdin).get('data',[])))")
echo "  current: $N_INST"
[ "$N_INST" = "0" ] || { echo "ERROR: pre-existing instances"; exit 1; }

echo ""
echo "=== launch CELL-SPECDEC in background ==="
date -u '+%H:%M:%S'
nohup bash $SAFETY /mnt/d/AI/hd-instrument/skypilot/cell_specdec/cell_specdec_config.sh \
    > $DATA/cell_specdec_orchestrator.log 2>&1 &
ORCH_PID=$!
echo "  orchestrator PID: $ORCH_PID"

echo ""
echo "===== HOLDING WSL ALIVE BY WAITING FOR ORCHESTRATOR (~30-60 min) ====="
wait $ORCH_PID
RC=$?
echo "===== CELL-SPECDEC orchestrator finished rc=$RC at $(date -u '+%H:%M:%S') ====="

echo ""
echo "=== final state ==="
ls -la $DATA/cell_specdec_results/ 2>&1 | head -10
echo ""
echo "  verdict:"
cat $DATA/cell_specdec_results/metrics.json 2>&1 | python3 -m json.tool 2>&1 | head -25
