#!/usr/bin/env bash
# Copy the licensed .hf_token from this testbed control machine to the runner
# at marsh@home:C:/dev/hd-instrument/.hf_token so the Phase 0.5 v1 Llama-3.2-1B
# residual-extract script picks it up at runtime via _load_hf_token().
#
# Run from WSL Ubuntu:
#   bash /mnt/d/AI/hd-instrument/tools/copy_hf_token_to_runner.sh
set -euo pipefail

SRC=/mnt/d/AI/hd-instrument/.hf_token
SSH_TARGET=marsh@home
DST_PATH='C:/dev/hd-instrument/.hf_token'

echo "=== [1/4] local token present? ==="
if [ ! -f "${SRC}" ]; then
  echo "ERROR: no token at ${SRC}"
  exit 1
fi
SRC_LEN=$(wc -c <"${SRC}" | tr -d '[:space:]')
SRC_PREFIX=$(head -c 5 "${SRC}")
echo "  src: ${SRC}"
echo "  len: ${SRC_LEN} bytes; prefix: ${SRC_PREFIX}..."

echo ""
echo "=== [2/4] SSH connectivity to ${SSH_TARGET} ==="
ssh -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new \
    "${SSH_TARGET}" 'echo ssh-ok' || {
  echo "ERROR: SSH to ${SSH_TARGET} failed"
  exit 2
}

echo ""
echo "=== [3/4] check existing token on runner (will be overwritten) ==="
ssh "${SSH_TARGET}" "if exist \"${DST_PATH//\//\\}\" (for /f %A in ('powershell -NoProfile -Command \"(Get-Item -Path 'C:\\dev\\hd-instrument\\.hf_token').Length\"') do echo existing_size=%A) else (echo no_existing_token)" || true

echo ""
echo "=== [4/4] copy local -> runner ==="
scp "${SRC}" "${SSH_TARGET}:${DST_PATH}"

echo ""
echo "=== verify ==="
ssh "${SSH_TARGET}" "powershell -NoProfile -Command \"\$f='C:\\dev\\hd-instrument\\.hf_token'; if (Test-Path \$f) { \$b=[IO.File]::ReadAllBytes(\$f); Write-Host \"  remote_size=\$(\$b.Length); remote_prefix=$([System.Text.Encoding]::ASCII.GetString(\$b[0..4]))...\" } else { Write-Host '  MISSING' }\""

echo ""
echo "=== done ==="
