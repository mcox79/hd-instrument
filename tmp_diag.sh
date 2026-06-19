#!/bin/bash
echo "=== ALL processes related to our stack ==="
ps -ef | grep -E 'safety_launch|generic_|sky' | grep -v grep
echo ""
echo "=== CELL-3 SMOKE orchestrator log ==="
cat /mnt/d/AI/hd-instrument/data/cell3_smoke_orchestrator.log 2>&1
echo ""
echo "=== CELL-3 SMOKE smart_launch log (FULL) ==="
cat /mnt/d/AI/hd-instrument/data/cell3_smoke_smart_launch.log 2>&1
echo ""
echo "=== check sky api server log ==="
cat ~/.sky/api_server/server.log 2>&1 | tail -20
echo ""
echo "=== uptime + lockfiles ==="
date -u '+%H:%M:%S now'
ls -la /tmp/cell3sm_smart_launch.pid 2>&1
ls -la /tmp/cell4hp_smart_launch.pid 2>&1
