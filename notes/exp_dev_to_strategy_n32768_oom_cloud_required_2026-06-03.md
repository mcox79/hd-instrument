# Upstream push: Q-A3 N=32768 INFRA_FAIL -- cloud GPU required

**Date:** 2026-06-03
**From:** exp_dev (v362 refill cycle)
**To:** Strategy/Orchestrator

## Problem

q_a3_l20_cross_layer_composition_v1_n32768 and q_a3_l21_cross_layer_composition_v1_n32768
both INFRA_FAIL on the local RTX 4060 Ti:

  CUDA OOM: tried to allocate 4.00 GiB
  GPU total: 8.00 GiB; only 2.80 GiB free
  4.05 GiB already allocated (display adapter VRAM overhead)

Root cause: the W matrix at N=32768 is (32768, 32768) float32 = 4.295 GB.
The display adapter uses ~4 GB VRAM for the Windows desktop.
Available for experiments: ~4.5 GB. Required for W: 4.295 GB. Barely fits in theory
but fragmentation and display overhead make it infeasible in practice.

## Required fix

These anchors need a headless GPU with >= 8 GB free VRAM:
- Lambda Cloud A10 (24 GB VRAM) or A100 (40/80 GB): sufficient.
- Cloud dispatch authorized per project_phase05_combined_auth_2026-06-02.md (limited budget).

## Scripts ready

Experiment scripts are fully written, tested (self-test PASS), and PROT-018/019/021 compliant:
- d:/AI/hd-instrument/experiments/exp_q_a3_l20_cross_layer_composition_v1_n32768.py
- d:/AI/hd-instrument/experiments/exp_q_a3_l21_cross_layer_composition_v1_n32768.py

Scripts already have `torch.cuda.empty_cache()` calls in the W build loop.
Prereqs: d:/AI/hd-instrument/prereqs/2026-06-03_q_a3_l20_n32768.md
         d:/AI/hd-instrument/prereqs/2026-06-03_q_a3_l21_n32768.md

## Estimated cost

2 anchors x ~300s wall each on Lambda A10 at $0.60/h = ~$0.10 total.
Very cheap; worth grouping with other cloud batch if one is authorized.

## Recommended action

1. Include in next Lambda Cloud batch (when PP-56 N=65536 result is in and cloud dispatch is
   authorized).
2. Alternatively: if user has access to a headless GPU machine, route to overnight_queue there.
3. OR: reduce N to 16384 for initial cross-N test (N=16384 already has L=20..L=30 confirmed;
   skip N=32768 ladder and go to cloud for N=65536 instead).
