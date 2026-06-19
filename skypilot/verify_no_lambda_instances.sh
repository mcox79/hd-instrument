#!/usr/bin/env bash
# Verify directly via Lambda Cloud API that no instances are live.
set -e

KEY=$(grep '^api_key' /root/.lambda_cloud/lambda_keys | sed 's/.*= *//' | tr -d '\n\r')
if [ -z "${KEY}" ]; then
  echo "ERROR: no api_key found in /root/.lambda_cloud/lambda_keys"
  exit 1
fi

echo "=== Direct Lambda Cloud API check ==="
RESP=$(curl -s -u "${KEY}:" https://cloud.lambda.ai/api/v1/instances)
echo "${RESP}" | python3 -c "
import json, sys
r = json.loads(sys.stdin.read())
items = r.get('data', [])
print(f'instances: {len(items)}')
for it in items:
    print(f'  id={it.get(\"id\")} type={it.get(\"instance_type\",{}).get(\"name\")} status={it.get(\"status\")} region={it.get(\"region\",{}).get(\"name\")}')"
