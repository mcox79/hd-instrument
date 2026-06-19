#!/bin/bash
# Test the fixed capacity-detection logic in isolation
set -e

echo "=== syntax check ==="
bash -n /mnt/d/AI/hd-instrument/skypilot/safety/generic_smart_launch.sh && echo "  OK"

echo ""
echo "=== fetching live Lambda data ==="
LAMBDA_KEY=$(grep -oP 'api_key\s*=\s*\K\S+' /root/.lambda_cloud/lambda_keys | head -1)
TMP=/tmp/test_lambda.json
curl -s -H "User-Agent: curl/7.81.0" -u "${LAMBDA_KEY}:" \
    https://cloud.lambdalabs.com/api/v1/instance-types > "$TMP"
echo "  written $(wc -c < $TMP) bytes"

echo ""
echo "=== test logic with CELL-3 SMOKE config ==="
source /mnt/d/AI/hd-instrument/skypilot/cell3/cell3_smoke_config.sh

AVAIL=$(SKUS_TO_TRY="$SKUS_PRIORITY" REGIONS_TO_TRY="$SKYPILOT_KNOWN_REGIONS" \
        LAMBDA_JSON_FILE="$TMP" python3 - <<'PYEOF' 2>&1
import json, sys, os
with open(os.environ["LAMBDA_JSON_FILE"]) as f:
    d = json.load(f)
SKUS = os.environ.get("SKUS_TO_TRY", "").split()
SK_REGIONS = set(os.environ.get("REGIONS_TO_TRY", "").split())
data = d.get("data", {})
for sku in SKUS:
    regs_all = [r["name"] for r in data.get(sku, {}).get("regions_with_capacity_available", [])]
    regs = [r for r in regs_all if r in SK_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
print("NO_CAPACITY")
sys.exit(1)
PYEOF
)
echo "  detected: $AVAIL"

echo ""
echo "=== test logic with CELL-4 config ==="
source /mnt/d/AI/hd-instrument/skypilot/cell4/cell4_config.sh

AVAIL=$(SKUS_TO_TRY="$SKUS_PRIORITY" REGIONS_TO_TRY="$SKYPILOT_KNOWN_REGIONS" \
        LAMBDA_JSON_FILE="$TMP" python3 - <<'PYEOF' 2>&1
import json, sys, os
with open(os.environ["LAMBDA_JSON_FILE"]) as f:
    d = json.load(f)
SKUS = os.environ.get("SKUS_TO_TRY", "").split()
SK_REGIONS = set(os.environ.get("REGIONS_TO_TRY", "").split())
data = d.get("data", {})
for sku in SKUS:
    regs_all = [r["name"] for r in data.get(sku, {}).get("regions_with_capacity_available", [])]
    regs = [r for r in regs_all if r in SK_REGIONS]
    if regs:
        print(f"{sku} {regs[0]}")
        sys.exit(0)
print("NO_CAPACITY")
sys.exit(1)
PYEOF
)
echo "  detected: $AVAIL"
