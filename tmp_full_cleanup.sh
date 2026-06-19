#!/bin/bash
echo "=== killing EVERYTHING related to our safety stack + sky daemon ==="

# Phase 1: pkill by name pattern
pkill -9 -f safety_launch_all 2>/dev/null
pkill -9 -f generic_smart_launch 2>/dev/null
pkill -9 -f generic_kill_switch 2>/dev/null
pkill -9 -f generic_watchdog 2>/dev/null
pkill -9 -f generic_progress_rsync 2>/dev/null
pkill -9 -f watchdog_cell2 2>/dev/null
pkill -9 -f 'sky.server.server' 2>/dev/null
pkill -9 -f 'sky api' 2>/dev/null
pkill -9 -f 'sky.*launch' 2>/dev/null
pkill -9 -f 'sky status' 2>/dev/null

# Phase 2: kill any "SkyPilot:" workers by exact name (not pkill -f which
# matches command line, but the process's listed name)
pkill -9 -x -f 'SkyPilot:' 2>/dev/null
ps -ef | awk '$NF ~ /SkyPilot:/ {print $2}' | xargs -r kill -9 2>/dev/null

# Phase 3: kill anything holding port 50011 or 46580
for PORT in 50011 46580; do
    HOLDER=$(ss -tlnp 2>&1 | grep ":$PORT" | grep -oP 'pid=\K[0-9]+' | head -1)
    if [ -n "$HOLDER" ]; then
        echo "  port $PORT held by PID $HOLDER, killing"
        kill -9 "$HOLDER" 2>/dev/null
    fi
done

# Phase 4: kill orphaned skyvenv python processes (parents 1 == reparented to init)
ps -ef | grep skyvenv | grep -v grep | awk '$3 == "1" || $3 == "0" {print $2}' | \
    xargs -r kill -9 2>/dev/null

# Phase 5: kill ALL skyvenv python procs (last resort)
pkill -9 -f /root/skyvenv/bin/python 2>/dev/null

sleep 2

# Phase 6: remove lockfiles + state
rm -f /tmp/cell3sm_*.pid /tmp/cell3fd_*.pid /tmp/cell4hp_*.pid 2>/dev/null
rm -f ~/.sky/api_server/server.pid 2>/dev/null

echo ""
echo "=== remaining sky-related procs ==="
ps -ef | grep -iE 'sky|SkyPilot' | grep -v grep | head -10 || echo "  (none)"
echo ""
echo "=== ports 50011 / 46580 ==="
ss -tlnp 2>&1 | grep -E '50011|46580' || echo "  (both free)"

echo ""
echo "=== state JSONs cleanup ==="
rm -f /mnt/d/AI/hd-instrument/data/cell3_smoke_state.json /mnt/d/AI/hd-instrument/data/cell4_state.json 2>/dev/null
echo "  cleaned"
