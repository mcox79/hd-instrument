#!/bin/bash
# Kill CELL-A2 cleanly: cluster tear-down + local orchestrator kill + verification.
set -uo pipefail

echo "=== STEP 1: tear down Lambda cluster cella2-100520 ==="
source /root/skyvenv/bin/activate
sky down -y cella2-100520 2>&1 | tail -5

echo ""
echo "=== STEP 2: verify Lambda API confirms termination ==="
sleep 3
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/i.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/i.json"))
print(f"Lambda instances: {len(d.get('data',[]))}")
for i in d.get("data", []):
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type',{}).get('name','?')} status={i.get('status','?')}")
PYEOF

echo ""
echo "=== STEP 3: kill local safety stack procs ==="
for pat in safety_launch_all generic_smart_launch generic_kill_switch generic_watchdog generic_progress_rsync; do
    pkill -9 -f "$pat" 2>/dev/null && echo "  killed: $pat" || echo "  (none): $pat"
done

echo ""
echo "=== STEP 4: cleanup lockfiles + state json ==="
rm -f /tmp/cella2_smart_launch.pid 2>/dev/null
echo "  done"

echo ""
echo "=== STEP 5: final verification ==="
echo "remaining sky procs:"
ps -ef | grep -iE 'cella2|safety_launch|generic_' | grep -v grep | head -5 || echo "  (none)"
echo ""
date -u '+%H:%M:%S CELL-A2 killed'
