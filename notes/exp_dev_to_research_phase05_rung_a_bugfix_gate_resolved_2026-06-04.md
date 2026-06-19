# Exp-Dev -> Research/Orchestrator: Phase 0.5 v1 Rung A bug-fix gate RESOLVED

**From:** Exp-Dev  **To:** Research + Orchestrator  **Date:** 2026-06-04
**Re:** routing_phase05_v1_rung_a_reprioritize_parallel_track_2026-06-04.md (the "are the 3 bug fixes ready?" question)

## Answer: all 3 already handled in the current pipeline -> Rung A unblocked
Verified against the Pythia-160M debug pipeline (exp_phase05_v1_algorithm1_debug_pythia160m_v1.py +
exp_phase05_probe_training_v1.py) that the Rung A scaffold reuses:
1. NaN check: float("nan") fallbacks for empty loss lists (debug L310-312) + nan_frac embedding check (L549). HANDLED.
2. BFloat16 torchmetrics unique() crash: residual extraction casts .float() before numpy (debug L347-351) AND
   an explicit catch/recover wrapper for the torchmetrics BFloat16-unique error (probe_training L617-647). HANDLED.
3. CUDA/CPU device mismatch: consistent .to(device) for model+tensors + .cpu().numpy() extraction. HANDLED.
The 3 bugs were specific to the OLD cloud-path code; the new pipeline bypasses them (as the routing suspected).

## Implication for Rung A engineering
No separate bug-fix sub-task needed. The Llama-3.2-1B extension must carry the SAME patterns: (a) .float()
cast on residual extraction (Llama is BF16), (b) the BFloat16-unique recovery wrapper in the probe trainer,
(c) .to(device) discipline. These are already in the reused scaffold; just preserve them at 1B scale.

## Status / next
User authorized "Bundle A now, Rung A next." Bundle A shipped (GPU). Rung A engineering (Algorithm 1 K-means
+ sum-pool over Llama-3.2-1B layers 8-16 + Hyperprobe MLP + 3 audit primitives; ~6-10h) is the next heavy
GPU track -- begins next cycle (multi-cycle build). Pre-reg unchanged (val_sim>=0.80 HP gate).

**END.**
