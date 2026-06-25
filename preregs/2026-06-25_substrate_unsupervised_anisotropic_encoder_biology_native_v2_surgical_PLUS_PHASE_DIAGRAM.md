# Pre-reg: substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM

**Date:** 2026-06-25
**Anchor:** substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM
**Cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py
**Queue:** remote_cpu_queue (numpy-only; matmul-heavy V x V at V=10000 = 400MB; bounded CPU)
**Run-mode:** full (self-test PASS; phase-diagram scan = ~3h)
**Author:** Exp-Dev (cell author; routes via Orchestrator for queue dispatch -- harness-denied push)
**Source-of-truth drill:** notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md (per-arm correction)
**Source-of-truth prior cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py + preregs/2026-06-25_substrate_unsupervised_anisotropic_encoder_biology_native_v1.md

## What changed from v1

1. **SURGICAL FOLDIAK FIX** -- the only genuine bug per drill section 3.1.
   - v1 collapsed FOLDIAK to rank-1: `sigma0_recall=0.0, eigenspread=0.9999, cosine_spread=0.6707`.
   - Root cause (per Foldiak 1990 + drill): missing per-neuron homeostatic firing-rate target.
   - Fix: `theta_i += eta_theta * (actual_rate_i - rho_target)` where rho_target = SPARSE_F = 0.02; eta_theta = 0.05.
   - v2 SELF-TEST result: `sigma0=1.000` (was 0.0) + `eigenspread=0.9208` (was 0.9999). Surgical fix works at small scale.
   - ARM renamed: `ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL` -> `ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC` to make the version difference explicit.

2. **V PHASE-DIAGRAM SCAN** over V_GRID = [200, 1000, 4000, 10000] x 3 seeds x 5 arms = 60 sub-runs.
   - N_DIM=8192 fixed (matches v1 + downstream cells).
   - SPARSE_F=0.02 fixed.
   - N_TRAIN = V * 100 (per-vocab training budget; Cell 7 + v1 convention).
   - Per Director routing: probe transition regime; at V=200 expect random saturation; at V=10000 expect random has headroom.

3. **PER-(V, seed) CHECKPOINT** via `_seed_checkpoint.write_partial_key("V<V>_seed<seed>")`.
   - Compound key supported by `_is_valid_partial` -> `_ckpt_key` precedence.
   - Atexit synthesizer recovers all completed (V, seed) units even on timeout.

4. **TOP-1 + TOP-5 ARGMAX accuracy** (Q discipline) -- robust at V=200 where random can saturate.

5. **OLSHAUSEN PROVENANCE DIAGNOSTIC** -- v1 had +0.56 BPC drift vs fair_harness rail 7.3065. v2 records the drift honestly in `detail.provenance_diagnostic` block at V=4000. Honest-scope flag per N1 verify-referent; we don't claim biology-native vs fair_harness if rails don't match.

6. **DEEPWALK + KOHONEN UNCHANGED** -- per drill sections 3.2, 3.3: DeepWalk's sigma0=0.94 is graph-structural tail-node behavior (brain-prior aligned, NOT a bug); KOHONEN is a clean null. Re-run unchanged to validate at other V.

7. **A3' label-free metric REMOVED** -- v2 focuses on BPC + sigma0 + anisotropy diagnostic per the spec's clearer phase-diagram bands (relative-to-random-BPC per V). A3' had cluster-coverage noise; BPC is the load-bearing discriminator.

## Question

Does any biology-native unsupervised anisotropic encoder mechanism beat isotropic random-bipolar on text8 BPC at ANY V in the phase diagram [200, 1000, 4000, 10000] at N_DIM=8192? With FOLDIAK now having homeostatic stability (no rank-1 collapse), AND under per-V evaluation (where random's headroom varies), does the substrate need encoder upgrade at all -- or is biology-native equivalent to random-bipolar across the regime (Mu-Viswanath-aligned negative-in-regime)?

**P_deflated estimates (per drill):**
- Any FOLDIAK_v2 cell HARD_PASS_CHAIN_GRADE at any V: 0.20 (lit-scan says low; +0.10 brain prior; -0.20 novel synthesis)
- Any biology arm HARD_PASS (non-chain-grade) at any V: 0.35
- ALL biology cells HARD_FAIL_NULL across V (substrate doesn't need encoder upgrade): 0.40 (most likely outcome per Skunkworks negative-in-regime atom)
- CONFOUND_FAIL (FOLDIAK surgical fix insufficient at scale): 0.10
- MIDDLE_BAND (mixed): 0.30

## Pre-reg HARD bands (per-(V, arm); using random_BPC AT THAT V as reference)

### Per-arm-at-V classification

- **HARD_PASS_CHAIN_GRADE:** `arm_bpc <= rand_bpc_at_V - 0.20` AND `sigma0 >= 0.95` AND `bpc_cv <= 0.05`
- **HARD_PASS:** `arm_bpc <= rand_bpc_at_V - 0.10` AND `sigma0 >= 0.90`
- **HARD_FAIL_NULL:** `|arm_bpc - rand_bpc_at_V| < 0.05` AND `sigma0 >= 0.90` (legitimate null finding)
- **CONFOUND_FAIL:** `sigma0 < 0.90` (cleanup-integrity gate per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm)
- **HARD_FAIL_HURTS:** `arm_bpc >= rand_bpc_at_V + 0.10` (engineering hurts)
- **MIDDLE_BAND:** any other case

### Cell-level verdict

- **HARD_PASS_CHAIN_GRADE:** ANY arm hits HARD_PASS_CHAIN_GRADE at ANY V
- **HARD_PASS:** any arm HARD_PASS at any V (non-chain-grade signal)
- **HARD_FAIL_NULL:** ALL biology arms hit HARD_FAIL_NULL across ALL V (informative negative; substrate-product wants LESS anisotropy at this regime; Mu-Viswanath confirmed empirically)
- **CONFOUND_FAIL:** 3+ (V, arm) cells with sigma0 < 0.90 (multiple implementation issues)
- **MIDDLE_BAND:** mixed outcomes

## Substrate-native arms (5; all unsupervised; NO labels)

1. **ARM_RANDOM_BIPOLAR_BASELINE** -- isotropic random sparse-bipolar. Reference per V.
2. **ARM_OLSHAUSEN_FIELD_SPARSE_CODING** -- forward-only SoftHebb (Moraitis 2107.05747); UNCHANGED from v1. Provenance diagnostic checks BPC drift vs fair_harness at V=4000.
3. **ARM_DEEPWALK_ON_BIGRAM_GRAPH** -- DeepWalk on bigram-cooccurrence graph (Perozzi 2014); UNCHANGED from v1. Tail-node behavior brain-prior aligned (drill section 3.2).
4. **ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC** -- Foldiak 1990 anti-Hebbian lateral inhibition + per-neuron homeostatic threshold (THE SURGICAL FIX). rho_target = SPARSE_F = 0.02; eta_theta = 0.05.
5. **ARM_KOHONEN_SOM_TOPOGRAPHIC** -- SOM with per-position XOR-tag for sigma0 distinctness; UNCHANGED from v1. Genuine null per drill section 3.3.

## Discriminator per V (per spec)

- **V=200:** below JL-margin; random should saturate (BPC near log2(200) ~7.64 limit). Biology arms expected at-most-tie. top-5 alongside top-1 for argmax-noise robustness.
- **V=1000:** transition regime; random has some headroom; biology arms may show small lift.
- **V=4000:** production (matches v1); per drill, OLSHAUSEN tied with random; FOLDIAK_v2 might now lift (was collapsed in v1).
- **V=10000:** large; random has lots of headroom; biology should show STRONGEST lift IF it ever does.

## Operating disciplines

- **D1 roofline probe MANDATORY** (60 sub-runs). Wall budget below.
- **D2 atexit + per-(V, arm) checkpoint** MANDATORY (don't lose 3h work). Compound key `V<V>_seed<seed>` supported by `_seed_checkpoint.write_partial_key`.
- **Self-test gate** PASS (validated locally; the SURGICAL FIX is verified at small scale via T3b).
- **NO local smoke for full V grid** -- too heavy (V=10000 -> 400MB W_lat for FOLDIAK alone). Local smoke at V_GRID_SMOKE=[200, 400] validates pipeline; remote_cpu runs full V_GRID.
- **Pre-reg + cell committed BEFORE dispatch** (uncommitted laptop notes invisible to autonomous pipeline -> GATE_FAIL).
- **Path-scoped commits** (no `git add -A`; canonical Store in repo).
- **ASCII only** (no unicode in scripts).
- **Per Fix #28:** per-arm + per-V metrics in `detail.by_arm_V_agg`; verdict_msg cites them; load-bearing classifier reads metrics not msg.
- **Per Fix #20:** no pipe-tail subprocess monitoring (atexit synthesizer + mtime polling).
- **Per Fix #17:** timeout = 10800s (3h) for full V grid.
- **Per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm:** sigma0 < 0.90 triggers CONFOUND_FAIL FIRST before any mechanism claim. This is honored in `_classify_arm_at_V`.

## Wall budget

Per-V estimate (3 seeds, CPU, numpy):
- V=200, N_TRAIN=20k: ~5 min/seed * 3 = 15 min
- V=1000, N_TRAIN=100k: ~15 min/seed * 3 = 45 min
- V=4000, N_TRAIN=400k: ~45 min/seed * 3 = 135 min (matches v1)
- V=10000, N_TRAIN=1M: ~60 min/seed * 3 = 180 min (FOLDIAK V x V = 400MB; one slow arm)

Total wall ~6h worst case; 3-4h typical. **timeout = 10800s (3h)** with atexit synthesizer recovering partial (V, seed) units on timeout. If first run lands HARD_FAIL_NULL at V<=4000 quickly, V=10000 may be skipped on a re-dispatch.

## Per-Fix discipline

- **Fix #26 (pre-dispatch verify-the-referent):** `tools/predispatch_check.py substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM` -> PROCEED (0 prior matches; pre-checked).
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling on `data/exp_<anchor>/partial_metrics_V<V>_seed<seed>.json`.
- **Fix #24 (GPU dispatch must actually use GPU):** acknowledged; v2 is numpy CPU on remote_cpu_queue; torch port is follow-up if V=16000+ ever becomes load-bearing.
- **Fix #28 (per-arm metrics, not summary verdict):** ALL per-arm-per-V BPC + top1/top5 + eigenspread + cosine_spread + sigma0_recall stored in `detail.by_arm_V_agg`; post-landing run `tools/peek_arm_metrics.py` BEFORE propagating cross-arm narratives.
- **Long-cells discipline:** per-(V, seed) checkpoint via `_seed_checkpoint.write_partial_key`; restartable from any (V, seed) boundary.
- **ASCII-only:** all print(), verdict_msg.

## Provenance investigation (v1 OLSHAUSEN +0.56 BPC drift)

v1 OLSHAUSEN had BPC drift +0.56 vs fair_harness rail 7.3065. Possible causes:
- Different vocab construction (v1 uses Counter most_common; fair_harness may differ)
- Different N_TRAIN scaling (v1 = 100k; need to confirm fair_harness)
- Different encoder hyperparam (alpha, learning rate, batch size)
- Different temperature in softmax (v1 uses T=1.0; fair_harness uses T=0.05 sanity)

v2 INVESTIGATES by recording in `detail.provenance_diagnostic`:
- `random_bpc_at_V4000` (the ARM_RANDOM baseline)
- `fair_harness_target` (7.3065)
- `drift_vs_fair_harness` (signed drift)
- `within_tol` (boolean; 0.20 loose tol)
- `note` (explicit honest-scope flag)

This does NOT auto-fail the run; it surfaces the gap for analysis. If drift is consistent across all V's random baselines, the cell + fair_harness use different configs (vocab / N_TRAIN / temp / etc) -- the gap is methodological-not-mechanism. If drift is V-dependent, something else is going on.

## Self-test PASS evidence

Run `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py --self-test`:

```
[selftest] starting...
[selftest] T3b: SURGICAL FOLDIAK FIX validation...
[selftest] T3b PASS: FOLDIAK v2 sigma0=1.000 eigsprd=0.9208 (v1 had sigma0=0.0 eigsprd=0.9999)
[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 5-arms shape+sigma0 + T3b SURGICAL FOLDIAK FIX validated + T4 anisotropy + T5 BPC+top1/top5 + T6 verdict-shape (NULL/HP/CONFOUND) + T7 provenance + T8 band ordering + T9 ckpt-key shape OK
```

Coverage:
- T1: char-trigram bipolar output
- T2: sparse_bipolar fraction-f exactness
- T3: all 5 arms produce (V, N_DIM) shape + sigma=0 cleanup recall >= 0.90 + isfinite all-true
- T3b: **SURGICAL FOLDIAK FIX validation** -- v2 must NOT collapse to rank-1 at small scale (v1 hit eigenspread=0.9999 + sigma0=0.0 in this regime; v2 PASSED with sigma0=1.000 + eigenspread=0.9208)
- T4: anisotropy_diagnostic returns required keys
- T5: build_hebbian_W_np + path_a_bpc finite + positive + top1/top5 in [0, 1] + top5 >= top1
- T6: compute_verdict handles HARD_FAIL_NULL / HARD_PASS / CONFOUND_FAIL correctly
- T7: provenance diagnostic recorded when V=4000 present
- T8: band ordering well-formed
- T9: per-(V, seed) checkpoint key shape composes correctly

## Cites

- notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md (source-of-truth correction; per-arm root cause)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py (forked base)
- experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py (rail 7.3065 reference)
- Foldiak 1990 PNAS Biol Cybern 64:165-170 (lateral inhibition + adaptive threshold)
- Olshausen-Field 1996 Nature 381:607-609 (V1 sparse coding)
- Moraitis et al. 2107.05747 (SoftHebb forward-only Hebbian)
- Perozzi et al. 2014 (DeepWalk)
- Kohonen 1982 (SOM topographic maps)
- USER directive 2026-06-25 (basis-vs-use-case: no labels at basis)
- Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm (cleanup-integrity gate is FIRST gate before mechanism claims)
- Mu-Viswanath spectrum-of-decisions framework (substrate may not need encoder upgrade in this regime; informative negative is acceptable outcome)

-- Exp-Dev
