#!/bin/bash
# URGENT: manually rescue CELL-3 SMOKE artifacts before cluster tear-down
set -e
echo "=== STEP 1: manually rsync CELL-3 SMOKE artifacts ==="
date -u '+%H:%M:%S start'
mkdir -p /mnt/d/AI/hd-instrument/data/cell3_smoke_results
source /root/skyvenv/bin/activate
# Use sky's known SSH config (set up when cluster was provisioned)
rsync -av --partial --progress \
    -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR" \
    cell3sm-091508:'~/sky_workdir/data/exp_substrate_cell3_distilled_22M_student_v1/' \
    /mnt/d/AI/hd-instrument/data/cell3_smoke_results/ 2>&1 | tail -20
echo ""

echo "=== STEP 2: verify artifacts present ==="
ls -la /mnt/d/AI/hd-instrument/data/cell3_smoke_results/ 2>&1
echo ""
echo "metrics.json verdict:"
cat /mnt/d/AI/hd-instrument/data/cell3_smoke_results/metrics.json 2>&1 | python3 -m json.tool | head -20

echo ""
echo "=== STEP 3: sky down cell3sm-091508 ==="
date -u '+%H:%M:%S'
sky down -y cell3sm-091508 2>&1 | tail -5

echo ""
echo "=== STEP 4: verify Lambda has terminated cell3sm ==="
sleep 5
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/i.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/i.json"))
print("Lambda instances:", len(d.get("data",[])))
for i in d.get("data",[]):
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type',{}).get('name','?')} status={i.get('status','?')}")
PYEOF

echo ""
date -u '+%H:%M:%S done'
