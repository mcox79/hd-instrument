#!/usr/bin/env bash
# Launch cornerstone C1+C2+C3 frontier-scale validation on Lambda H100.
# Belt-and-suspenders teardown: autostop -i 30 AND explicit `sky down` once
# the job completes (per SkyPilot autostop reliability issues #1472/#2247/#4103).
#
# Run from WSL Ubuntu (any cwd; this script does the cd):
#   bash /mnt/d/AI/hd-instrument/skypilot/launch_cornerstone.sh
set -euo pipefail

source /root/skyvenv/bin/activate

HF_TOKEN_VAL="$(cat /mnt/d/AI/hd-instrument/.hf_token)"
if [ -z "${HF_TOKEN_VAL}" ]; then
  echo "ERROR: HF token at /mnt/d/AI/hd-instrument/.hf_token is empty"
  exit 1
fi
echo "HF_TOKEN length: ${#HF_TOKEN_VAL} chars; prefix: ${HF_TOKEN_VAL:0:5}..."

cd /root/cornerstone-ship
echo "launching from $(pwd)"
echo "bundle size: $(du -sh /root/cornerstone-ship | awk '{print $1}')"

# Cluster-name suffix avoids stale region metadata from prior failed launches.
CLUSTER_NAME="cornerstone-$(date +%H%M%S 2>/dev/null || echo run)"
echo "cluster name: ${CLUSTER_NAME}"

# No region pin: SkyPilot's --retry-until-up cycles regions on capacity miss.
# Per feedback_cloud_location_doesnt_matter, we trust SkyPilot to find any
# region with stock. YAML setup phase pins torch defensively against
# image-driver mismatches across regions.
sky launch \
    -c "${CLUSTER_NAME}" \
    -y \
    --retry-until-up \
    --down \
    -i 30 \
    --env HF_TOKEN="${HF_TOKEN_VAL}" \
    skypilot/cornerstone.yaml

EXIT_CODE=$?
echo ""
echo "=== sky launch returned exit code ${EXIT_CODE} ==="

# Belt-and-suspenders teardown regardless of exit code. The autostop --down -i 30
# should fire after job completes, but SkyPilot has documented Lambda-path bugs
# in #1472/#2247/#4103 where autostop can leave the cluster in INIT state
# without billing protection. Explicit `sky down` is the spend-protection
# insurance the $9-12 budget requires.
echo ""
echo "=== issuing explicit `sky down ${CLUSTER_NAME} -y` (belt-and-suspenders) ==="
sky down "${CLUSTER_NAME}" -y || echo "  [warn] sky down ${CLUSTER_NAME} returned non-zero; verify cluster state manually"

# Optional: verify no orphan Lambda instances remain (uses existing helper)
echo ""
echo "=== verifying no orphan Lambda instances ==="
bash /mnt/d/AI/hd-instrument/skypilot/verify_no_lambda_instances.sh || \
  echo "  [warn] verify_no_lambda_instances.sh returned non-zero; check Lambda dashboard"

exit ${EXIT_CODE}
