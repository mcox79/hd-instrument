#!/bin/bash
echo "=== progress_rsync log (last 30 lines) ==="
tail -30 /mnt/d/AI/hd-instrument/data/cell3_smoke_progress_rsync.log 2>&1
echo ""
echo "=== smart_launch log post-verdict (last 25 lines) ==="
tail -25 /mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log 2>&1
echo ""
echo "=== orchestrator log tail ==="
tail -15 /mnt/d/AI/hd-instrument/data/cell3_smoke_orchestrator.log 2>&1
echo ""
echo "=== Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/i.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/i.json"))
print("count:", len(d.get("data",[])))
for i in d.get("data",[]):
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type',{}).get('name','?')} status={i.get('status','?')} region={i.get('region',{}).get('name','?')} ip={i.get('ip','n/a')}")
PYEOF
echo ""
echo "=== sky status ==="
source /root/skyvenv/bin/activate
sky status 2>&1 | head -10
echo ""
echo "=== local results dir ==="
ls -la /mnt/d/AI/hd-instrument/data/cell3_smoke_results/ 2>&1
echo ""
echo "=== local CELL-4 results ==="
ls -la /mnt/d/AI/hd-instrument/data/cell4_results/ 2>&1
