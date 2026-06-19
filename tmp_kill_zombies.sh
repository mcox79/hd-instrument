#!/bin/bash
echo "=== before kill ==="
ps -ef | grep -E 'safety_launch_all|generic_smart_launch|generic_kill_switch|generic_watchdog|generic_progress_rsync' | grep -v grep | awk '{print $2}' | tee /tmp/zombie_pids.txt
echo ""
echo "=== killing ==="
while read pid; do
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null && echo "killed: $pid" || echo "notthere: $pid"
    fi
done < /tmp/zombie_pids.txt
sleep 2
echo ""
echo "=== after kill ==="
ps -ef | grep -E 'safety_launch_all|generic_smart_launch|generic_kill_switch|generic_watchdog|generic_progress_rsync' | grep -v grep | wc -l
echo "procs remaining"
rm -f /tmp/cell3sm_*.pid /tmp/cell3fd_*.pid /tmp/cell4hp_*.pid
echo "lockfiles cleared"
