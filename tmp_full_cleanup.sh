#!/bin/bash
echo "=== killing EVERYTHING related to our safety stack + sky daemon + yesterday's watchdog ==="
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
sleep 2
rm -f /tmp/cell3sm_*.pid /tmp/cell3fd_*.pid /tmp/cell4hp_*.pid 2>/dev/null
echo ""
echo "=== remaining sky-related procs ==="
ps -ef | grep -E 'sky|safety|generic' | grep -v grep | head -20
echo ""
echo "=== state JSONs cleanup ==="
rm -f /mnt/d/AI/hd-instrument/data/cell3_smoke_state.json /mnt/d/AI/hd-instrument/data/cell4_state.json 2>/dev/null
echo "  cleaned"
