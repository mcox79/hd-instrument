#!/bin/bash
echo "=== CELL-3 SMOKE last 50 lines ==="
tail -50 /mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log 2>&1
echo ""
echo "=== CELL-3 SMOKE orchestrator log last 15 lines ==="
tail -15 /mnt/d/AI/hd-instrument/data/cell3_smoke_orchestrator.log 2>&1
echo ""
echo "=== CELL-4 launcher log last 30 lines ==="
tail -30 /mnt/d/AI/hd-instrument/data/cell4_smart_launch.log 2>&1
echo ""
echo "=== Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/i.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/i.json"))
data = d.get("data", [])
print(f"count: {len(data)}")
for i in data:
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type', {}).get('name','?')} status={i.get('status','?')} region={i.get('region',{}).get('name','?')} ip={i.get('ip','n/a')}")
PYEOF
echo ""
echo "=== sky status ==="
source /root/skyvenv/bin/activate
sky status 2>&1 | head -15
echo ""
echo "=== screens ==="
screen -ls 2>&1
echo ""
echo "=== process tree ==="
ps -ef | grep -E 'safety_launch|generic_' | grep -v grep | head -15
