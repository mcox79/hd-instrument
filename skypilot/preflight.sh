#!/usr/bin/env bash
# Pre-launch sanity check for Phase 0.5 SkyPilot dispatch
set +e

echo "=== HF token ==="
if [ -f /mnt/d/AI/hd-instrument/.hf_token ]; then
  tok=$(cat /mnt/d/AI/hd-instrument/.hf_token)
  echo "exists; size=$(stat -c%s /mnt/d/AI/hd-instrument/.hf_token) bytes"
  echo "length=${#tok} chars"
  echo "prefix=${tok:0:5}..."
else
  echo "MISSING"
fi
echo ""

echo "=== Lambda creds ==="
if [ -f /root/.lambda_cloud/lambda_keys ]; then
  echo "exists; size=$(stat -c%s /root/.lambda_cloud/lambda_keys) bytes"
  head -c 50 /root/.lambda_cloud/lambda_keys | od -c | head -3
else
  echo "MISSING"
fi
echo ""

echo "=== sky check lambda ==="
source /root/skyvenv/bin/activate
sky check lambda 2>&1 | tail -15
echo ""

echo "=== sky status (existing clusters) ==="
sky status 2>&1 | tail -10
echo ""

echo "=== bundle present ==="
ls -la /root/hd-ship/ 2>&1
