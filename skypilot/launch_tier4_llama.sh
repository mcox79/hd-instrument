#!/usr/bin/env bash
# Launch Tier-4-Llama substrate-attention substitution on Lambda H100.
#
# Carries every defense from launch_llama_1b.sh (which HARD_PASS'd):
#   - Cluster name HHMMSS suffix (Bug 7)
#   - --retry-until-up cycles regions on capacity miss (Bug 1-4)
#   - --down -i 30 PLUS explicit `sky down` (Bug 13)
#   - 60s watcher started BEFORE launch (Bug 14 first defense)
#   - Foreground sky launch + final rsync BEFORE sky down (Bug 14 second defense)
#   - verify_no_lambda_instances helper after teardown (Bug 7 second defense)
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/launch_tier4_llama.sh
set -euo pipefail

source /root/skyvenv/bin/activate

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token at /mnt/d/AI/hd-instrument/.hf_token is empty"
  exit 1
fi
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..."

cd /root/tier4-llama-ship
echo "launching from $(pwd)"
echo "bundle size: $(du -sh /root/tier4-llama-ship | awk '{print $1}')"

CLUSTER_NAME="tier4llama-$(date +%H%M%S 2>/dev/null || echo run)"
echo "cluster name: ${CLUSTER_NAME}"

echo "starting tier4llama watcher (60s interval) in background ..."
INTERVAL=60 nohup bash /mnt/d/AI/hd-instrument/skypilot/watch_tier4_llama_rsync.sh >/dev/null 2>&1 &
WATCHER_PID=$!
echo "watcher pid: ${WATCHER_PID}"

sky launch \
    -c "${CLUSTER_NAME}" \
    -y \
    --retry-until-up \
    --down \
    -i 30 \
    --env HF_TOKEN="${HF_TOKEN_VAL}" \
    skypilot/tier4_llama.yaml

EXIT_CODE=$?
echo ""
echo "=== sky launch returned exit code ${EXIT_CODE} ==="

if [ "${EXIT_CODE}" -eq 0 ]; then
  echo ""
  echo "=== SCPing results back via SkyPilot SSH alias (cluster -> laptop) ==="
  LOCAL_DIR=/mnt/d/AI/hd-instrument/data/tier4_llama_results
  mkdir -p "${LOCAL_DIR}"
  rsync -av --partial \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
    "${CLUSTER_NAME}:~/sky_workdir/data/exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1/" \
    "${LOCAL_DIR}/" || \
    echo "  [warn] final rsync returned non-zero; will retry via watcher"

  echo ""
  echo "=== NEXT STEP (run from Windows PowerShell): laptop -> marsh@home ==="
  cat <<MARSHEOF
ssh marsh@home "if not exist C:\dev\hd-instrument\data\exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1 mkdir C:\dev\hd-instrument\data\exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1"
scp D:\AI\hd-instrument\data\tier4_llama_results\metrics.json \
    "marsh@home:C:/dev/hd-instrument/data/exp_substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1/"
MARSHEOF
fi

echo ""
echo "=== issuing explicit sky down ${CLUSTER_NAME} -y (belt-and-suspenders) ==="
sky down "${CLUSTER_NAME}" -y || \
  echo "  [warn] sky down ${CLUSTER_NAME} returned non-zero; verify cluster state manually"

echo ""
echo "=== verifying no orphan Lambda instances ==="
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh || \
  echo "  [warn] verify_no_lambda_instances.sh returned non-zero; check Lambda dashboard"

exit ${EXIT_CODE}
