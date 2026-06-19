#!/bin/bash
echo "=== port 50011 holders ==="
ss -tlnp 2>&1 | grep 50011 || echo "  (none — port free)"
lsof -i :50011 2>&1 | head -5 || echo "  (lsof not available)"
echo ""
echo "=== all sky-related procs alive right now ==="
ps -ef | grep -iE 'sky|safety|generic' | grep -v grep | head -20
echo ""
echo "=== anything from our current session orchestrators? ==="
ls -la /tmp/cell3sm_*.pid /tmp/cell4hp_*.pid 2>&1
echo ""
echo "=== check if PowerShell's launching process model is the culprit ==="
echo "WSL distro PID 1:"
ps -p 1 -o cmd=
echo ""
echo "=== current Lambda capacity (sanity) ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instance-types > /tmp/types.json
python3 - <<'PYEOF'
import json
d = json.load(open("/tmp/types.json"))
for sku in ["gpu_1x_gh200", "gpu_1x_h100_sxm5", "gpu_1x_h100_pcie"]:
    regs = [r["name"] for r in d.get("data", {}).get(sku, {}).get("regions_with_capacity_available", [])]
    print(f"  {sku}: {regs if regs else 'NO CAPACITY'}")
PYEOF
