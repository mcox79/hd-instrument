#!/bin/bash
echo "=== CELL-3 SMOKE launcher (last 25 lines) ==="
tail -25 /mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log 2>&1
echo ""
echo "=== CELL-4 launcher (last 25 lines) ==="
tail -25 /mnt/d/AI/hd-instrument/data/cell4_smart_launch.log 2>&1
echo ""
echo "=== Lambda instances ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instances > /tmp/inst.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/inst.json"))
data = d.get("data", [])
print(f"count: {len(data)}")
for i in data:
    print(f"  id={i.get('id','?')[:12]} type={i.get('instance_type', {}).get('name','?')} status={i.get('status','?')} region={i.get('region',{}).get('name','?')} ip={i.get('ip','n/a')}")
PYEOF
echo ""
echo "=== sky status ==="
source /root/skyvenv/bin/activate
sky status 2>&1 | head -10
echo ""
echo "=== state JSONs ==="
echo "CELL-3 SMOKE:"
cat /mnt/d/AI/hd-instrument/data/cell3_smoke_state.json 2>&1
echo ""
echo "CELL-4:"
cat /mnt/d/AI/hd-instrument/data/cell4_state.json 2>&1
