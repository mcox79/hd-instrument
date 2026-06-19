#!/bin/bash
# Direct Lambda capacity sanity check
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
TMP=/tmp/lambda_types.json
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instance-types > "$TMP"
echo "=== HTTP response size: $(wc -c < $TMP) bytes ==="
head -c 200 "$TMP"
echo ""
echo ""
python3 - "$TMP" <<'PYEOF'
import sys, json
with open(sys.argv[1]) as f:
    d = json.load(f)
data = d.get("data", {})
print(f"=== ALL SKUs with capacity available right now ===")
any_avail = False
for sku, info in sorted(data.items()):
    regs = info.get("regions_with_capacity_available", [])
    if regs:
        any_avail = True
        price = info.get("instance_type", {}).get("price_cents_per_hour", "?")
        print(f"  {sku:30s} | price=${int(price)/100:5.2f}/h | regions: {[r['name'] for r in regs]}")
if not any_avail:
    print("  (NONE -- all SKUs at zero capacity right now)")
print()
print(f"=== SKUs our launchers are polling for ===")
for sku in ["gpu_1x_gh200", "gpu_1x_h100_sxm5", "gpu_1x_h100_pcie"]:
    info = data.get(sku, {})
    regs = info.get("regions_with_capacity_available", [])
    price = info.get("instance_type", {}).get("price_cents_per_hour", "?")
    if regs:
        print(f"  {sku:25s} AVAILABLE in: {[r['name'] for r in regs]} (${int(price)/100:.2f}/h)")
    else:
        print(f"  {sku:25s} NO CAPACITY (${int(price)/100:.2f}/h)")
print()
print(f"=== Total SKUs in catalog: {len(data)} ===")
PYEOF
