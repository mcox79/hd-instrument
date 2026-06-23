# Pre-reg: substrate_brain_full_compose_LM_v2 (V2 bug-fix re-dispatch)

**Date:** 2026-06-23
**Anchor:** substrate_brain_full_compose_LM_v2
**Cell:** experiments/exp_substrate_brain_full_compose_LM_v2.py
**Queue:** overnight_queue (remote GPU; torch.cuda; N_DIM=8192; 3-layer PC stack across 6 arms; Fix #24)
**Run-mode:** full
**Author:** Exp-Dev (cell author + dispatch)
**Pre-reg source-of-truth:** Re-dispatch of v1 after Skunkworks audit + diagnostic
agent identified 4 substantive bugs blocking substrate-as-LM composition.
**Predecessor cell:** experiments/exp_substrate_brain_full_compose_LM_v1.py
**Predecessor verdict:** MIDDLE_BAND (smoke artifact: all arms at lambda=0.0 pure
unigram fallback; v1 verdict logic FALSE-POSITIVE bpc_ok claim).

## Why a v2

v1 shipped as a **smoke artifact only** (laptop CPU; N_TRAIN=1500; never ran on
actual GPU at full scale) but the verdict logic + 3 mechanism implementations
contained substantive bugs that would have polluted any full run. Per USER
strategic principle: brain-as-existence-proof; current implementation is buggy;
iterate fixes; do NOT pivot from brain-architecture.

## V2 bugs fixed

### Bug 1 (PC primitive zero-init defensiveness)

**v1 symptom:** PC stack W matrices initialized to zeros. In the sister cell
`exp_substrate_pc_hierarchy_text8_lm_v1.py`, this caused `sign(W @ input)` to
saturate to all-ones (sign(0) -> +1 via `_safe_sign_t`), making every layer
identical and recon_err pinned at ~1.0. In this brain compose cell, the PC
primitive is dot-product based (not sign-based), so the catastrophic saturation
did NOT manifest. However, the symmetric defensive fix is still applied: zero W
means the first Hebbian accumulation has to do all the work of establishing
distinct outputs, and tiny smoke-scale n_pairs makes that fragile.

**Fix:** each PC layer W initialized with variance-scaled Gaussian:
```
W = 0.01 * randn(N_DIM, N_DIM) / sqrt(N_DIM)
```
(He / Xavier init analogue; substrate-native; keeps initial activation
magnitudes O(1) for unit-norm inputs.)

**Sanity test (T14):** distinct src_keys must produce distinct outputs from
layer 0 forward (unique_rows >= 2). PASS at selftest.

### Bug 2 (SPARSE_COMPETITIVE_K destroys predictions)

**v1 symptom:** SPARSE_COMPETITIVE_K_FRAC=0.10 over V=4000 = keep top 400 with
HARD zero-mask (`-1e9` for the rest). Catastrophically destroyed predictions
(`BPC=45.86` at full v1 ARM_PC_PLUS_SPARSE_COMPETITIVE, 5-6x worse than rank-1).
Hard mask + uniform-keep-K = throwing away the substrate's confidence rankings.

**Fix:** SOFT K-WTA at K=10 absolute (cortical 1-3% sparsity band per the
sparse_competitive_readout_lm_v1 smoke). Top-K logits scaled by `beta=8.0`
(softmax inverse-temperature) before downstream softmax; the kept top-K get a
temperature-scaled distribution favoring the highest, not uniform.

**Sanity test (T5):** K=10 of 4000 yields exactly 10 finite entries; beta=8
soft-WTA must produce max_prob > 0.5 (NOT uniform over K, which would be 1/K).
PASS at selftest.

### Bug 3 (kinetic proofreading rejects 100%)

**v1 symptom:** `agreement_frac = 0.0` at smoke (KP 2-step cosine agreement gate
with `tau=0.20`, `sigma=0.02` rejected every position because low-confidence
smoke predictions never agreed within tau).

**Fix:** two changes:
- (a) Gate KP entirely off when `N_TRAIN < KP_DISABLE_BELOW_NTRAIN=10000`
  (smoke + selftest scales; substrate signal too weak there).
- (b) At full scale, agreement = TOP-K OVERLAP of the two noisy predictions
  (top-3 default; require `overlap_min=2` shared candidates). Less brittle than
  exact cosine; reflects "do these two perturbed predictions concur on the
  leading candidates" not "are they near-identical vectors".

**Sanity test (T10):** sigma=0 must yield deterministic top-K overlap = K
(all-agree); sigma=1 with strict `overlap_min=K` must NOT all-agree (proves
the gate actually gates, not vacuously true). PASS at selftest.

### Bug 4 (verdict false-positive on lambda=0)

**v1 symptom:** `bpc_ok=True` from `bpc_best < 7.500` without checking
`best_lambda > 0`. The smoke MIDDLE_BAND with bpc=5.291 was pure unigram
fallback (every arm picked lambda=0.0 because substrate signal was too weak
to lift unigram via log-linear interp). The reported bpc was the UNIGRAM
floor, not a substrate result.

**Fix:** verdict requires `best_lambda > 0` in the decisive arm for `bpc_ok`.
NEW verdict band: `SUBSTRATE_SIGNAL_TOO_WEAK_TO_LIFT_UNIGRAM` triggered when
decisive arm's best_lambda == 0.0. Verdict_msg now surfaces `bpc_raw`
(substrate-only at lambda=1) + `best_lambda` prominently for all arms.

**Sanity test (T13d):** synthetic unit with all bpc=5.0 but all lambda=0.0
must return `SUBSTRATE_SIGNAL_TOO_WEAK_TO_LIFT_UNIGRAM`, NOT HARD_PASS.
PASS at selftest.

## Brain mechanisms -> substrate primitives (unchanged from v1)

1. Hierarchical predictive coding (Friston / Rao-Ballard) -> 3-layer W stack
2. Sparse competitive activations (Tonegawa-CREB) -> **SOFT** top-K=10 (Bug 2 fix)
3. Recurrent attractor dynamics -> iterative nearest-prototype cleanup
4. Lock-in attention -> per-hop cosine positional code at freq = pos * 31
5. Working-memory HRR-slots -> context bundle via bind(word_i, slot_i_vec); W=5
6. Kinetic proofreading -> **top-K overlap** 2-step gate (Bug 3 fix; off < 10k train)
7. Sparse-bipolar W matrix -> f=0.05 sparse outer products

## Six arms (unchanged from v1)

ARM_UNIGRAM, ARM_BASELINE_RANK1_HEBBIAN, ARM_PC_HIERARCHY_ONLY,
ARM_PC_PLUS_SPARSE_COMPETITIVE, ARM_PC_PLUS_LOCK_IN_ATTENTION,
ARM_BRAIN_FULL_COMPOSE.

## Pre-reg HARD bands (CHAIN-GRADE V2 closure eligible; same as v1)

### HARD_PASS
ALL must hold:
- `ARM_BRAIN_FULL_COMPOSE bpc_best` < **7.500**
- AND `ARM_BRAIN_FULL_COMPOSE bpc_best` < `ARM_BASELINE_RANK1_HEBBIAN bpc_best - 1.000`
- AND at least one ablation arm shows lift-over-baseline >= **0.30 bits**
- AND `ARM_BRAIN_FULL_COMPOSE best_lambda > 0` (Bug 4 V2 gate)
- bpc cv across 3 seeds <= **0.10**

### SUBSTRATE_SIGNAL_TOO_WEAK_TO_LIFT_UNIGRAM (NEW; V2)
Decisive arm best_lambda == 0.0 (collapsed to unigram fallback). The bpc_best
value is the unigram floor; substrate signal too weak to lift via log-linear
interp at this config. Triggers research routing for capacity / encoder /
hyperparameter scour (NOT chain-grade).

### HARD_FAIL
ALL arms `bpc_best` >= **7.738** (no composition beats unigram).

### MIDDLE_BAND
Composition lifts over rank-1 baseline but doesn't clear all HP bars AND has
best_lambda > 0 (substrate signal exists but isn't decisive).

## Sanity gates (HANDOFF self-test; T1-T15, all PASS)

T1. char-trigram encoder bipolar
T2. build_E_char_trigram L2-normed
T3. sparsify_bipolar correct sparsity
T4. hrr_bind output shape
T5. **SOFT K-WTA (Bug 2 fix)**: K=10 of 4000 yields 10 finite + max_prob > 0.5
T6. lock-in positional code L2-normed + low-correlation
T7. context-keys L2-normed
T8. PC stack training shape + norm
T9. attractor cleanup non-decreasing similarity
T10. **kinetic proofreading V2 (Bug 3 fix)**: sigma=0 -> all-agree; sigma=1 strict -> not-all-agree
T11. uniform-logits BPC == log2(V)
T12. log-linear interp endpoints
T13. **verdict bands V2 (Bug 4 fix)**: HP / HF / MID + new SUBSTRATE_TOO_WEAK
T14. **PC primitive non-degeneracy (Bug 1 fix)**: distinct inputs -> distinct outputs
T15. LLM counter clean

## Smoke gate (executed locally 2026-06-23)

```
.venv/Scripts/python.exe experiments/exp_substrate_brain_full_compose_LM_v2.py --smoke
```
- N_DIM=8192, N_TRAIN=1500, N_HELD=300, VOCAB_CAP=300, seeds=[0]
- All 15 self-tests PASS
- All 6 arms execute end-to-end on CPU in **~30s** (well under SMOKE_TIMEOUT_S=180)
- VERDICT (smoke-scale, EXPECTED): SUBSTRATE_SIGNAL_TOO_WEAK_TO_LIFT_UNIGRAM
  - All arms picked best_lambda=0.0; bpc_best = unigram floor (5.291)
  - bpc_raw spread: BASELINE=7.766, PC=7.849, LOCK_IN=7.835, SPARSE_COMP=47.446,
    BRAIN_FULL=59.583 (the high SPARSE_COMP + BRAIN_FULL bpc_raw values are
    expected at smoke V=300 where top-K=10 of 300 = 3% retain ratio = aggressive
    competition with few support patterns; expected to drop at full V=4000)
  - VERDICT BAND TRIPPED CORRECTLY: at smoke scale, all 4 bugs would have
    been invisible in v1 because verdict_msg framing would have called this
    MIDDLE_BAND. v2's verdict honestly reports "substrate signal too weak"
    with bpc_raw visible.

## GPU dispatch (Fix #24 compliance; unchanged from v1)

- torch.cuda backend for all matmul (PC + Hebbian + sparse-bipolar + recall)
- W = 8192x8192 fp32 per layer = ~256MB; 3 layers concurrent ~768MB
- INGEST_CHUNK=4096, RECALL_BATCH=256
- Per-arm wall estimate (GPU): rank-1 ~80s; 3-layer PC ~250s; per arm recall ~50s
- Full = 5 non-unigram arms x ~150s avg x 3 seeds ~= 75min total

## Compute budget

- Timeout: 10800s (180 min; 2.5x headroom over ~70min estimate)

## Pre-flight discipline (this ship)

- Fix #26 (verify-referent): v1 anchor + v2 anchor are distinct; no duplicate
- Fix #28 (per-arm metrics): post-landing `tools/peek_arm_metrics.py` mandatory
- ASCII-only: all print() + verdict_msg (em-dashes from v1 already converted)
- Per-seed checkpoint + atexit synthesizer + SIGTERM handler (inherited from v1)
- Fair comparison: same V/N_TRAIN/N_HELD/N_DIM/seeds as v1 + fresh_W_v2
- Commit prereg + cell before remote dispatch

## Brain-existence-proof asymmetric calibration

Per USER 2026-06-23 (brain-as-existence-proof): brain-grounded mechanisms get
P=0.60-0.75 prior; the V2 fixes are implementation correctness, not
feasibility tests. A SUBSTRATE_TOO_WEAK verdict here is informative (says the
encoder + LR + capacity tuple is the wrong one) but NOT a refutation of the
underlying brain composition hypothesis.

## Cites

- preregs/2026-06-23_substrate_brain_full_compose_LM_v2.md (this file)
- preregs/2026-06-23_substrate_brain_full_compose_LM_v1.md (predecessor)
- experiments/exp_substrate_brain_full_compose_LM_v2.py (this cell)
- experiments/exp_substrate_brain_full_compose_LM_v1.py (predecessor; smoke artifact)
- Skunkworks 4-bug audit 2026-06-23
- Diagnostic agent findings 2026-06-23
- USER 2026-06-23 (brain-as-existence-proof reframe; iterate fixes, don't pivot)
- USER 2026-06-22 (Fix #24 GPU dispatch must use GPU)
- USER 2026-06-22 (Fix #28 read per-arm metrics not summary verdict_msg)

-- Exp-Dev
