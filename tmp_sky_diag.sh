#!/bin/bash
echo "=== sky API server log (recent crashes) ==="
tail -40 ~/.sky/api_server/server.log 2>&1
echo ""
echo "=== ports in use ==="
ss -tlnp 2>&1 | grep -E '46580|50011' | head -5
echo ""
echo "=== any lingering sky procs ==="
ps -ef | grep -iE 'sky|SkyPilot' | grep -v grep | head -10
