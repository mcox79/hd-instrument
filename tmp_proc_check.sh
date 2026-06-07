#!/bin/bash
echo "=== current safety stack procs ==="
ps -ef | grep -E 'safety_launch_all|generic_smart_launch|generic_kill_switch|generic_watchdog|generic_progress_rsync' | grep -v grep
echo ""
echo "=== sky-related procs ==="
ps -ef | grep -E 'sky|skypilot' | grep -v grep | head -10
echo ""
echo "=== Lambda instances right now ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/inst.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/inst.json"))
for i in d.get("data", []):
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type', {}).get('name','?')} status={i.get('status','?')} region={i.get('region',{}).get('name','?')}")
if not d.get("data"):
    print("  (none)")
PYEOF
echo ""
echo "=== Lambda capacity check ==="
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instance-types > /tmp/types.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/types.json"))
for sku in ["gpu_1x_gh200", "gpu_1x_h100_sxm5", "gpu_1x_h100_pcie"]:
    regs = [r["name"] for r in d.get("data", {}).get(sku, {}).get("regions_with_capacity_available", [])]
    print(f"  {sku}: {regs}")
PYEOF
echo ""
echo "=== ALL recent activity ==="
echo "CELL-3 SMOKE launcher full log:"
tail -50 /mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log 2>&1
echo ""
echo "CELL-3 SMOKE state JSON:"
cat /mnt/d/AI/hd-instrument/data/cell3_smoke_state.json 2>&1
