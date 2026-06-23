# Pre-reg: substrate_brain_full_compose_LM_v1 (MAXIMALIST brain-architecture substrate-as-LM)

**Date:** 2026-06-23
**Anchor:** substrate_brain_full_compose_LM_v1
**Cell:** experiments/exp_substrate_brain_full_compose_LM_v1.py
**Queue:** overnight_queue (remote GPU; torch.cuda; N_DIM=8192; 3-layer PC stack across 4 brain-arms; Fix #24)
**Run-mode:** full (smoke for gate)
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** USER strategic principle 2026-06-23 (brain-as-existence-proof reframe)

## Why this cell

USER strategic principle 2026-06-23: **brain is existence proof; substrate-as-LM
needs to match brain's full mechanism stack, NOT rely on rank-1 Hebbian alone.**

Prior substrate-as-LM tests collapsed to unigram (substrate signal weaker than
just guessing the most common word) because they used JUST W matrix + argmax.
Brain uses 7+ mechanisms in concert. This cell composes the validated substrate-
native equivalents.

## Brain mechanisms -> substrate primitives composed

1. **Hierarchical predictive coding** (Friston/Rao-Ballard) ->
   3-layer substrate W stack with local-error Hebbian updates.
2. **Sparse competitive activations** (Tonegawa-CREB excitability trace) ->
   top-K competitive readout (keep top f=0.10 logits, zero rest before softmax).
3. **Recurrent attractor dynamics** ->
   iterative attractor cleanup at each layer (k=2 nearest-prototype steps).
4. **Lock-in attention** ->
   per-hop lock-in cosine positional code at frequency = pos * 31.
5. **Working-memory HRR-slots** ->
   context held as bundle of bind(word_i, slot_i_vec); window=5.
6. **Kinetic proofreading non-linear readout** ->
   2-step agreement gate (predict twice with sigma=0.02 noise; keep positions
   where cos(p1, p2) >= 1.0 - tau with tau=0.20; disagreement -> uniform).
7. **Sparse-bipolar W matrix** ->
   f=0.05 sparse outer products (20-300x bundle capacity per prior drill).

## Six arms (ablation; isolates which mechanisms are load-bearing)

1. **ARM_UNIGRAM** -- analytic floor (BPC=7.738 ref on text8 100k).
2. **ARM_BASELINE_RANK1_HEBBIAN** -- W = sum dense outer products + argmax;
   the rank-1 ceiling (should reproduce ~7.86 BPC ~ unigram).
3. **ARM_PC_HIERARCHY_ONLY** -- 3-layer PC stack + argmax readout
   (tests if hierarchy alone breaks the W-rank cap).
4. **ARM_PC_PLUS_SPARSE_COMPETITIVE** -- 3-layer PC + Tonegawa top-K readout
   (tests hierarchy + non-linear competition).
5. **ARM_PC_PLUS_LOCK_IN_ATTENTION** -- 3-layer PC + per-hop lock-in attention
   over context window (tests hierarchy + attention).
6. **ARM_BRAIN_FULL_COMPOSE** -- ALL primitives: 3-layer PC + sparse-competitive
   + lock-in attention + WM HRR-slots + sparse-bipolar W + kinetic proofreading
   + attractor cleanup.

## Pre-reg HARD bands (CHAIN-GRADE V2 closure eligible)

### HARD_PASS
ALL three must hold:
- `ARM_BRAIN_FULL_COMPOSE bpc_best` < **7.500** (clearly beats unigram by 0.24+ bits)
- AND `ARM_BRAIN_FULL_COMPOSE bpc_best` < `ARM_BASELINE_RANK1_HEBBIAN bpc_best - 1.000`
  (clearly beats rank-1 ceiling by 1+ bit)
- AND at least one ablation arm clearly identifies the load-bearing mechanism
  (lift-over-baseline >= **0.30 bits** on some non-FULL arm)
- bpc cv across 3 seeds <= **0.10**

### HARD_FAIL
ALL arms `bpc_best` >= **7.738** (no composition beats unigram). Substrate-as-LM
is fundamentally W-architecture capped; forces pivot to substrate-as-refuse-
aware-product.

### MIDDLE_BAND
Composition lifts over rank-1 baseline but doesn't beat unigram -> partial
mechanism; characterize what is still missing.

## Sanity gates (HANDOFF self-test; T1-T14, all PASSED locally)

T1. char-trigram encoder produces bipolar vectors
T2. build_E_char_trigram_gpu shape + L2 norm
T3. sparsify_bipolar_gpu correct sparsity (f * N_DIM nonzero, +/-1/0)
T4. hrr_bind_batch correct output shape
T5. sparse_competitive_logits keeps k_frac top
T6. lock-in positional code L2-normed + low-correlation across positions
T7. build_context_keys L2-normed + correct shape
T8. PC stack training + forward correct shape + norm
T9. attractor cleanup non-decreasing similarity to nearest prototype
T10. kinetic proofreading agreement: at sigma=0 all positions agree
T11. BPC sanity: uniform logits -> log2(V) bits per token
T12. log-linear interp endpoints (lam=1 = raw substrate; lam=0 = unigram)
T13. verdict bands HARD_PASS / HARD_FAIL / MIDDLE_BAND
T14. LLM counter clean

## Smoke gate (executed locally 2026-06-23)

```
.venv/Scripts/python.exe experiments/exp_substrate_brain_full_compose_LM_v1.py --smoke
```
- N_DIM=8192 (matches full), N_TRAIN=1500, N_HELD=300, VOCAB_CAP=300, seeds=[0]
- All 6 arms execute end-to-end on CPU in **69s** (under SMOKE_TIMEOUT_S=180)
- All 14 self-tests PASS
- atexit synthesizer wired; per-seed checkpoint via `_seed_checkpoint`
- VERDICT: MIDDLE_BAND (expected at smoke scale; all arms converge to
  log-linear lam=0.0 pure-unigram fallback because V=300 / N=1500 is too
  sparse for substrate signal to dominate; full V=4000 / N=100k is the
  decisive regime).

## GPU dispatch (Fix #24 compliance)

- torch.cuda backend for ALL matmul: PC training + Hebbian writes + sparse-bipolar
  projection + recall
- W = 8192x8192 fp32 per layer = ~256MB; PC arms hold 3 layers concurrently
  during training = ~768MB; cleanup between arms via empty_cache
- INGEST_CHUNK=4096, RECALL_BATCH=256, batched outer-products / recall
- Per-arm `mem_get_info()` heartbeat + wall-time logging
- Compute estimate per arm-seed at full scale:
  - rank-1: ~80s ingest (8192x4096 matmul x 25 chunks)
  - 3-layer PC: ~250s ingest (3 layers x 80s each, includes cumulative-pred update)
  - per arm: ~50s recall
  - FULL = 5 arms x (80-300s + 50s recall) x 3 seeds ~= 60-80min total

## Compute budget

- 6 arms x 3 seeds; per-arm wall mix:
  - rank-1: ~130s
  - PC arms (3-layer): ~300s each x 4 = 1200s
  - per seed: ~1400s; 3 seeds = ~4200s = 70min
- **Timeout: 10800s** (180 min; 2.5x headroom over ~70min estimate; absorbs
  variance from kinetic-proofreading noise + sparse-bipolar sparsification +
  attractor cleanup iterations)

## Pre-flight discipline (this ship)

- **Fix #26 (pre-dispatch verify-the-referent):** ran
  `python tools/predispatch_check.py substrate_brain_full_compose_LM` ->
  0 matching landings, 0 atoms; PROCEED.
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling
  on `data/exp_substrate_brain_full_compose_LM_v1/metrics.json`.
- **Fix #28 (per-arm metrics):** post-landing run
  `python tools/peek_arm_metrics.py exp_substrate_brain_full_compose_LM_v1`
  to read per-arm BPC before propagating cross-arm narratives. Particularly
  critical here: 6 arms; do NOT generalize from FULL_COMPOSE verdict to
  individual mechanism claims without per-arm read.
- **Long-cells discipline:** per-seed checkpoint via `_seed_checkpoint`;
  atexit synthesizer wired; SIGTERM handler installed.
- **ASCII-only:** all print() + verdict_msg.
- **Fair comparison:** same V=4000 / N_TRAIN=100k / N_HELD=20k / N_DIM=8192 /
  seeds=[7,17,23] as fresh_W_bpc_per_encoder_v2; each arm fresh W;
  brain-arm gets NO advantages over rank-1 baseline.
- **Commit prereg + cell before remote dispatch:** USER discipline 2026-06-17.

## Status_log

- `event_kind="experiment_ship"` `importance=HIGH`
- Note: maximalist composition test under USER brain-as-existence-proof reframe;
  load-bearing V2 LM gap test using FULL brain architecture (not just rank-1
  + encoder lift). Decisive HARD_PASS chain-grade-eligible.

## Cites

- preregs/2026-06-23_substrate_brain_full_compose_LM_v1.md (this file)
- experiments/exp_substrate_brain_full_compose_LM_v1.py (this cell)
- experiments/exp_fresh_W_bpc_per_encoder_v2.py (rank-1 baseline pattern)
- experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py (HRR+lock-in pattern)
- USER strategic principle 2026-06-23 (brain-as-existence-proof)
- USER directive 2026-06-22 (Fix #24 GPU dispatch must use GPU)
- Rao + Ballard 1999 (predictive coding)
- Friston 2009 (free energy principle)
- Tonegawa et al. 2015 (excitability-trace allocation)
- Hopfield 1982 (attractor dynamics)
- Plate 1995 (holographic reduced representations)

-- Exp-Dev
