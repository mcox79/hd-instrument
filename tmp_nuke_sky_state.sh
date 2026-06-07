#!/bin/bash
echo "=== before nuke ==="
ps -ef | grep -iE 'sky|SkyPilot' | grep -v grep | wc -l
echo "  sky procs"
ss -tlnp 2>&1 | grep 50011 | head -3

echo ""
echo "=== killing ALL SkyPilot executor workers + multiprocessing helpers ==="
pkill -9 -f 'SkyPilot:executor' 2>/dev/null
pkill -9 -f 'SkyPilot:' 2>/dev/null
pkill -9 -f 'sky.server.server' 2>/dev/null
pkill -9 -f 'multiprocessing.spawn' 2>/dev/null
pkill -9 -f 'multiprocessing.resource_tracker' 2>/dev/null

# Kill anything holding port 50011 directly
PORT_HOLDER=$(ss -tlnp 2>&1 | grep 50011 | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$PORT_HOLDER" ]; then
    echo "  port 50011 held by PID $PORT_HOLDER, killing"
    kill -9 "$PORT_HOLDER" 2>/dev/null
fi

# Also clear ~/.sky/api_server state if needed
rm -rf ~/.sky/api_server/server.pid 2>/dev/null

sleep 2

echo ""
echo "=== after nuke ==="
ps -ef | grep -iE 'sky|SkyPilot' | grep -v grep | wc -l
echo "  sky procs (should be 0 except maybe parent shell)"
ss -tlnp 2>&1 | grep 50011 | head -3 || echo "  port 50011 free"

echo ""
echo "=== sanity: launch a fresh sky API server to confirm port is usable ==="
source /root/skyvenv/bin/activate
timeout 30 sky api status 2>&1 | head -10
