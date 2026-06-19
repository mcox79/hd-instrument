#!/bin/bash
echo "=== process tree (interesting procs only) ==="
ps auxf 2>/dev/null | grep -E 'pip|setup|flash|python|colbert|conda|nvcc|ninja' | grep -v grep | head -20
echo ""
echo "=== top CPU consumers ==="
ps aux --sort=-%cpu 2>/dev/null | head -10
echo ""
echo "=== disk usage ==="
df -h | head -8
echo ""
echo "=== HF cache size + top entries ==="
du -sh ~/.cache/huggingface 2>/dev/null
ls -la ~/.cache/huggingface/hub/ 2>/dev/null | head -15
echo ""
echo "=== sky_workdir contents ==="
ls -la ~/sky_workdir/ 2>/dev/null | head -10
ls -la ~/sky_workdir/data/exp_substrate_llama8b_triples_khop_gpu_v1/ 2>/dev/null | head -8
echo ""
echo "=== uptime + GPU ==="
uptime
nvidia-smi --query-gpu=name,memory.used,memory.free,utilization.gpu --format=csv 2>/dev/null
