#!/usr/bin/env bash
# Sync remote (marsh@home) to origin/main. Treats remote as a worker:
# - no commits should ever be made on remote
# - if HEAD diverges from origin, the divergent commits get preserved on a
#   timestamped backup branch before hard reset
# - safe to run any time; idempotent if already at origin tip
#
# Usage:
#   bash tools/remote_sync.sh
#
# Why: the remote git tree drifted once (10+ stale commits from older work)
# and blocked future `git pull --ff-only` for two weeks. Always run this
# AFTER pushing a local commit that needs to land on remote runners.

set -euo pipefail
ts=$(date +%Y%m%d_%H%M%S)
ssh -o ConnectTimeout=30 marsh@home "powershell -NoProfile -Command \"\$ErrorActionPreference='SilentlyContinue'; cd C:/dev/hd-instrument; \
    \$local_head = & git.exe rev-parse HEAD; \
    & git.exe fetch origin main 2>&1 | Out-Null; \
    \$origin_head = & git.exe rev-parse origin/main; \
    if (\$local_head -eq \$origin_head) { Write-Output \"[remote_sync] already at origin/main (\$origin_head)\" } \
    else { \
        \$ahead = & git.exe rev-list --count origin/main..HEAD; \
        if (\$ahead -gt 0) { \
            \$backup = 'backup_pre_reset_${ts}'; \
            & git.exe branch \$backup HEAD; \
            Write-Output \"[remote_sync] preserved \$ahead diverged commit(s) on \$backup\"; \
        } \
        & git.exe reset --hard origin/main 2>&1 | Out-Null; \
        Write-Output \"[remote_sync] reset HEAD to \$origin_head\"; \
    }\""
