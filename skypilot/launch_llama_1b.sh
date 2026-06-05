#!/usr/bin/env bash
# Launch Llama-3.2-1B per-token residual extraction on Lambda H100.
#
# Defenses against prior cloud bugs (cornerstone session):
#   - Cluster name HHMMSS suffix (Bug 7: ghost clusters / stale region metadata)
#   - --retry-until-up cycles regions on capacity miss (Bug 1-4)
#   - --down -i 30 PLUS explicit `sky down` after run (Bug 13: SkyPilot autostop
#     bugs #1472/#2247/#4103 on Lambda)
#   - Foreground sky launch: blocks until job complete so the explicit `sky down`
#     runs as the very next line
#   - SCP the residuals npz back BEFORE sky down (avoids Bug 14 rsync race)
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/skypilot/launch_llama_1b.sh
set -euo pipefail

source /root/skyvenv/bin/activate

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token at /mnt/d/AI/hd-instrument/.hf_token is empty"
  exit 1
fi
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..."

cd /root/llama-1b-ship
echo "launching from $(pwd)"
echo "bundle size: $(du -sh /root/llama-1b-ship | awk '{print $1}')"

# Bug 7 defense: cluster name suffix avoids stale region metadata from prior failed launches.
CLUSTER_NAME="llama1b-$(date +%H%M%S 2>/dev/null || echo run)"
echo "cluster name: ${CLUSTER_NAME}"

# Bug 14 defense layer 0: spawn watcher in background BEFORE launch so per-doc
# partials are pulled to laptop every 60s during the run; mid-run cluster death
# loses <= 1 min of work. PID captured so we can clean up if launcher exits early.
echo "starting llama1b watcher (60s interval) in background ..."
INTERVAL=60 nohup bash /mnt/d/AI/hd-instrument/skypilot/watch_llama_1b_rsync.sh >/dev/null 2>&1 &
WATCHER_PID=$!
echo "watcher pid: ${WATCHER_PID}"

# Bug 1-4 defense: --retry-until-up + accelerators:H100:1 (in YAML) lets SkyPilot
# cycle regions + SKUs. Bug 13 defense: --down -i 30 autostop primary backstop.
sky launch \
    -c "${CLUSTER_NAME}" \
    -y \
    --retry-until-up \
    --down \
    -i 30 \
    --env HF_TOKEN="${HF_TOKEN_VAL}" \
    skypilot/llama_1b.yaml

EXIT_CODE=$?
echo ""
echo "=== sky launch returned exit code ${EXIT_CODE} ==="

# Bug 14 defense: SCP the residuals npz back BEFORE sky down. The watcher would
# eventually pull it but a final-rsync-vs-teardown race lost cornerstone artifacts;
# this is the deterministic path.
if [ "${EXIT_CODE}" -eq 0 ]; then
  echo ""
  echo "=== SCPing residuals back via SkyPilot SSH alias (cluster -> laptop) ==="
  LOCAL_DIR=/mnt/d/AI/hd-instrument/data/llama_1b_results
  mkdir -p "${LOCAL_DIR}"
  rsync -av --partial \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
    "${CLUSTER_NAME}:~/sky_workdir/data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/" \
    "${LOCAL_DIR}/" || \
    echo "  [warn] final rsync returned non-zero; will retry via watcher"

  # User Option A: final destination is C:\dev\hd-instrument\data\ on marsh@home.
  # The second-hop SCP from laptop -> marsh@home is done from Windows PowerShell
  # AFTER this script returns (Windows-side OpenSSH has the marsh@home key;
  # WSL invocation of /mnt/c/Windows/System32/OpenSSH/scp.exe is brittle on path/auth).
  # Print the PowerShell command for visibility; caller / Testbed runs it.
  echo ""
  echo "=== NEXT STEP (run from Windows PowerShell): laptop -> marsh@home ==="
  cat <<MARSHEOF
ssh marsh@home "if not exist C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_per_token_residual_extract_v1 mkdir C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_per_token_residual_extract_v1"
scp D:\AI\hd-instrument\data\llama_1b_results\residuals_per_token.npz \
    D:\AI\hd-instrument\data\llama_1b_results\residuals_per_token_meta.json \
    D:\AI\hd-instrument\data\llama_1b_results\metrics.json \
    "marsh@home:C:/dev/hd-instrument/data/exp_phase05_v1_llama32_1b_per_token_residual_extract_v1/"
MARSHEOF
fi

# Bug 13 defense (belt-and-suspenders): explicit sky down regardless of exit code.
echo ""
echo "=== issuing explicit sky down ${CLUSTER_NAME} -y (belt-and-suspenders) ==="
sky down "${CLUSTER_NAME}" -y || \
  echo "  [warn] sky down ${CLUSTER_NAME} returned non-zero; verify cluster state manually"

# Bug 7 defense (verify no orphan): use the existing helper
echo ""
echo "=== verifying no orphan Lambda instances ==="
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh || \
  echo "  [warn] verify_no_lambda_instances.sh returned non-zero; check Lambda dashboard"

exit ${EXIT_CODE}
