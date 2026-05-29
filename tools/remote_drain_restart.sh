#!/usr/bin/env bash
# Drain + restart remote runners safely so they pick up new bytecode.
# Used when local commits modify runner_v2_prod.py or other long-running
# python that's been imported into the live runner processes.
#
# Sequence:
#   1. Touch PAUSED in each queue dir (runner honors this between anchors)
#   2. Poll heartbeat until both runners show status="paused" (drained)
#   3. Stop-ScheduledTask + Start-ScheduledTask on both runners
#   4. Remove PAUSED files (runners resume on next poll)
#
# Usage:
#   bash tools/remote_drain_restart.sh         # default 4h max-wait
#   bash tools/remote_drain_restart.sh 7200    # 2h max-wait
#
# NEVER kills running experiments mid-flight. If max-wait elapses without
# drain, exits non-zero and leaves PAUSED in place for user inspection.

set -euo pipefail
max_wait=${1:-14400}
poll_interval=30

echo "[drain_restart] setting PAUSED flags on both queues"
ssh -o ConnectTimeout=15 marsh@home "powershell -NoProfile -Command \"\$ErrorActionPreference='SilentlyContinue'; \
    New-Item -ItemType File -Force -Path C:/dev/hd-instrument/data/overnight_queue/PAUSED | Out-Null; \
    New-Item -ItemType File -Force -Path C:/dev/hd-instrument/data/remote_cpu_queue/PAUSED | Out-Null\""

echo "[drain_restart] waiting up to ${max_wait}s for runners to drain (poll every ${poll_interval}s)"
elapsed=0
while [ "$elapsed" -lt "$max_wait" ]; do
    statuses=$(ssh -o ConnectTimeout=15 marsh@home "powershell -NoProfile -Command \"\$ErrorActionPreference='SilentlyContinue'; \
        \$gpu = (Get-Content C:/dev/hd-instrument/data/overnight_queue/heartbeat.json -Raw | ConvertFrom-Json).status; \
        \$cpu = (Get-Content C:/dev/hd-instrument/data/remote_cpu_queue/heartbeat.json -Raw | ConvertFrom-Json).status; \
        Write-Output \\\"gpu=\$gpu cpu=\$cpu\\\"\"" 2>&1 | grep -E "gpu=.* cpu=.*" | tail -1)
    echo "[drain_restart] elapsed=${elapsed}s status: ${statuses}"
    if echo "$statuses" | grep -qE "gpu=(paused|idle|exited)" && echo "$statuses" | grep -qE "cpu=(paused|idle|exited)"; then
        echo "[drain_restart] both runners drained"
        break
    fi
    sleep "$poll_interval"
    elapsed=$((elapsed + poll_interval))
done

if [ "$elapsed" -ge "$max_wait" ]; then
    echo "[drain_restart] TIMEOUT: runners did not drain within ${max_wait}s; PAUSED left in place" >&2
    exit 1
fi

echo "[drain_restart] restarting schtasks"
ssh -o ConnectTimeout=30 marsh@home "powershell -NoProfile -Command \"\$ErrorActionPreference='SilentlyContinue'; \
    Stop-ScheduledTask -TaskName hd_gpu_runner_0; \
    Stop-ScheduledTask -TaskName hd_cpu_runner_0; \
    Start-Sleep -Seconds 2; \
    Start-ScheduledTask -TaskName hd_gpu_runner_0; \
    Start-ScheduledTask -TaskName hd_cpu_runner_0\""

echo "[drain_restart] removing PAUSED flags"
ssh -o ConnectTimeout=15 marsh@home "powershell -NoProfile -Command \"\$ErrorActionPreference='SilentlyContinue'; \
    Remove-Item -Force C:/dev/hd-instrument/data/overnight_queue/PAUSED; \
    Remove-Item -Force C:/dev/hd-instrument/data/remote_cpu_queue/PAUSED\""

echo "[drain_restart] DONE; new runners will pick up next anchor on poll"
