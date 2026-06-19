#!/bin/bash
echo "=== /root/skyvenv/bin/ contents ==="
ls /root/skyvenv/bin/ | head -20
echo "---"
if [ -f /root/skyvenv/bin/activate ]; then
    echo "activate: FOUND"
else
    echo "activate: NOT FOUND"
fi
echo "---"
/root/skyvenv/bin/python --version 2>&1
echo "---"
/root/skyvenv/bin/python -c 'import sky; print("sky version:", sky.__version__)' 2>&1
echo "---"
echo "CELL-2 smart launcher venv activation line:"
grep -E 'source.*venv|skyvenv' /mnt/d/AI/hd-instrument/skypilot/smart_launch_cell2.sh 2>&1 | head -3
