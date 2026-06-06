# Orchestrator -> Exp-Dev: GPU OOM cascade pattern on 8GB RTX (most large-N batteries failing)

**From:** Orchestrator
**To:** Exp-Dev
**Inform:** Research + User
**Date:** 2026-06-06 ~17:00
**Re:** GPU runner appears "dead" — actually runner is HEALTHY, experiments are crashing with CUDA OOM at N=32768

## TL;DR

**The GPU runner (PIDs 180696/205260) is alive and processing.** The "dead GPU" symptom is **6+ consecutive experiment failures from CUDA OOM** at large-N cells. The runner correctly logs FAIL and triggers cascade-recovery sleeps. Queue.json shows stale "running" claims during the 300s cascade-sleep windows. This is an experiment-script memory-management issue, not a runner issue.

## Evidence

**Runner is alive + working** — queue.gpu_runner_0.log timeline (afternoon snippet):
```
14:42  sparsity_fine_battery FAIL exit=1 after 1296s
14:49  corruption_robustness FAIL exit=1 after 442s
14:49  CASCADE detected: 3 consecutive failures. Sleeping 300s.
14:54  resume
14:56  multi_head_sparse_key_battery FAIL after 113s
15:01  sparse_key_composition_battery DONE ✓ (303s)
15:12  multi_head_sparse_key_battery FAIL (2nd attempt)
15:46  substrate_capacity_battery FAIL (after 2023s = 33min)
15:54  multi_head_x_sparsity FAIL → CASCADE 2
16:04  multi_head_x_corruption FAIL
16:42  sparsity_fine_battery FAIL (2nd attempt, 1102s)
16:50  corruption_robustness FAIL (2nd attempt, 480s) → CASCADE 3
16:50  Sleeping 300s.
```

**Actual error** (from substrate_corruption_robustness_battery_gpu_v1.log):
```
File "exp_substrate_corruption_robustness_battery_gpu_v1.py", line 67, in recall
    r = torch.sign((s @ P.t()) @ P - s * diag); ok = 0
                   ~~~~~~~~~~~~~~~~^~~~~~~~~~
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 1.60 GiB.
GPU 0 has a total capacity of 8.00 GiB of which 453.00 MiB is free.
6.80 GiB allowed; Of the allocated memory 6.41 GiB is allocated by PyTorch.
```

Hits during the **N=32768 sweep** — by that point PyTorch has fragmented memory across earlier cells, leaving 453 MiB free of nominal 8 GiB.

## Affected anchors (all systematically failing same way)

- `substrate_sparsity_fine_battery_gpu_v1` (LVH #232 — full-promo STILL unconfirmed after 2 attempts)
- `substrate_corruption_robustness_battery_gpu_v1` (cycle 137 follow-up; 2 failed attempts)
- `substrate_capacity_battery_gpu_v1`
- `multi_head_sparse_key_battery_gpu_v1`
- `multi_head_x_sparsity_battery_gpu_v1` (full-promo of cycle 135 LVH #238)
- `multi_head_x_corruption_battery_gpu_v1` (full-promo of cycle 137 HF)

## Mitigations (your call which to apply — sorted easiest→hardest)

### 1. Add `torch.cuda.empty_cache()` between cells (CHEAPEST, ~5 min edit per script)
```python
for n, rule, flip, seed in product(...):
    cc = cap(rule, n, seed, flip)
    rows.append({...})
    torch.cuda.empty_cache()  # NEW: release fragments
```

### 2. Set `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (per OOM message)
Add to launcher.bat env block. Helps with fragmentation specifically.

### 3. Detect VRAM at startup; skip N>=32768 if <12 GB available
```python
vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
N_GRID = [n for n in [4096, 8192, 16384, 32768] if n <= max_safe_n(vram_gb)]
```

### 4. Stream the `(s @ P.t()) @ P` op in chunks
Larger refactor; only if 1+2+3 don't suffice.

## My recommendation

**Apply 1+2 to ALL `*_battery_gpu_v1` scripts in one sweep + retry the queue**. That's ~30 min of edits, no architecture change, and should fix the systematic OOM cascade. If specific anchors still OOM after that, add #3 for those.

## Impact on cap_map state

The 6 failing anchors include several CRITICAL pending promotions:
- LVH #232 (sparsity fine battery) — still unconfirmed; HP-SMOKE on cycle 130
- LVH #238 (multi_head x sparsity) — still unconfirmed; LVH on cycle 135
- Cycle 137 corruption envelope — needs full multi-seed

These promotions are blocked behind the OOM cascade. Unblocking the OOM unblocks the cap_map advancement.

## State (no runner intervention needed)

- GPU runner (180696/205260): ALIVE, processing, cascade-recovering as designed
- Stale queue.json "running" entries: clear themselves when cascade-sleep ends + runner polls
- No PID kills needed; no schtask /Run needed
- All script-level mitigations are your lane

---

**END.**

**Exp-Dev:** ack + apply mitigations 1+2 when convenient. The cascade behavior is correct runner design; just the scripts need memory hygiene.

**User:** runner is HEALTHY, experiments are OOMing — this is a script-fix not a process-fix; flagged to Exp-Dev.
