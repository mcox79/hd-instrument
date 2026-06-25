# Pre-reg: substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak

**Date:** 2026-06-25
**Anchor:** substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak
**Cell:** experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py
**Queue:** remote_cpu_queue (numpy-only; matmul-bounded; FOLDIAK V x V kernel removed in v2b)
**Run-mode:** full (self-test PASS; phase-diagram scan = ~2-2.5h after FOLDIAK drop)
**Author:** Exp-Dev (cell author; routes via Orchestrator for queue dispatch -- harness-denied push)
**Source-of-truth drill:** notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md (per-arm correction)
**FOLDIAK redesign request:** notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md
**Source-of-truth prior cells:**
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py (immediate parent; FOLDIAK arm removed in v2b)

## What changed from v2 (substantive scope change)

**FOLDIAK arm DROPPED entirely** -- per exp_dev re-investigation (2026-06-25), the v2 surgical homeostatic fix (theta_i += eta*(y_i - rho_target)) was insufficient: the underlying bug is ALGORITHMIC (per-row vs per-dim axis flip in the codebook normalization + theta update path), NOT a BLAS/precision issue. Patching the algorithm in-place carried high risk of introducing new bugs without an adequate bench. v2b takes the clean approach: drop the arm in this cell, file a v3 redesign request with Research (per-output-dim theta + bounded W_lat + scale-matched T3b at V>=1000), and proceed with the other 4 arms now.

Concrete removals in v2b:
1. `ARM_FOLDIAK_ANTI_HEBBIAN_LATERAL_v2_HOMEOSTATIC` removed from `ARMS`
2. `encoder_foldiak_anti_hebbian_v2_homeostatic` function deleted
3. FOLDIAK removed from `ENCODERS` registry
4. `N_FOLDIAK_ITER` config dropped (no longer referenced)
5. T3b self-test FOLDIAK assertion removed (no arm to validate)
6. T6 verdict-fixture lists updated from 5-element to 4-element arrays
7. `CONFIG_VERSION` schema retag: `subUnsupAnisBio-v2b-NO_FOLDIAK_PHASE_DIAGRAM`
8. `summary` prefix retagged: `BIO4xV` (was `BIO5xV`)
9. `honest_scope` updated: "4-arm biology-native UNSUPERVISED anisotropic encoder phase-diagram scan ... FOLDIAK arm DROPPED in v2b per exp_dev 2026-06-25 investigation"

What was PRESERVED (load-bearing):
- V phase-diagram scan over V = [200, 1000, 4000, 10000] for the 4 remaining arms
- D2 atexit + per-(V, seed) checkpoint via `_seed_checkpoint.write_partial_key`
- Per-V per-arm metrics in `detail.by_arm_V_agg`
- All other self-tests (T1, T2, T3, T4, T5, T6, T7, T8, T9)
- Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm (still applies to remaining 4 arms)
- Top-1 + top-5 argmax accuracy (Q discipline)
- OLSHAUSEN provenance diagnostic vs fair_harness rail 7.3065 at V=4000
- Per-(V, arm) classification using random_BPC AT THAT V as reference
- HARD bands: HP_CHAIN_GRADE_BPC_LIFT >= 0.20 + sigma0 >= 0.95 + cv <= 0.05, etc.

## Question

Does any of the 3 biology-native unsupervised anisotropic encoder mechanisms (Olshausen / DeepWalk / Kohonen) beat isotropic random-bipolar on text8 BPC at ANY V in the phase diagram [200, 1000, 4000, 10000] at N_DIM=8192? With FOLDIAK removed from the lineup pending v3 redesign, AND under per-V evaluation (where random's headroom varies with V), does the substrate need encoder upgrade at all from any of the surviving biology-native mechanisms -- or is biology-native equivalent to random-bipolar across the regime (Mu-Viswanath-aligned negative-in-regime)?

**P_deflated estimates (per drill, deflated for FOLDIAK absence which was the only nominally-novel mechanism):**
- Any biology arm HARD_PASS_CHAIN_GRADE at any V: 0.10 (deflated from v2's 0.20 because FOLDIAK was the highest-priors arm; surviving arms are well-studied with mostly-null priors)
- Any biology arm HARD_PASS (non-chain-grade) at any V: 0.25
- ALL biology HARD_FAIL_NULL across V (substrate doesn't need encoder upgrade from these arms): 0.50 (MOST LIKELY; informative negative)
- CONFOUND_FAIL (3+ cells with sigma0 < 0.90): 0.05 (low; FOLDIAK was the only known sigma0 problem)
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

## Substrate-native arms (4 in v2b; all unsupervised; NO labels)

1. **ARM_RANDOM_BIPOLAR_BASELINE** -- isotropic random sparse-bipolar. Reference per V.
2. **ARM_OLSHAUSEN_FIELD_SPARSE_CODING** -- forward-only SoftHebb (Moraitis 2107.05747); UNCHANGED from v1/v2. Provenance diagnostic checks BPC drift vs fair_harness at V=4000.
3. **ARM_DEEPWALK_ON_BIGRAM_GRAPH** -- DeepWalk on bigram-cooccurrence graph (Perozzi 2014); UNCHANGED from v1/v2. Tail-node behavior brain-prior aligned (drill section 3.2).
4. **ARM_KOHONEN_SOM_TOPOGRAPHIC** -- SOM with per-position XOR-tag for sigma0 distinctness; UNCHANGED from v1/v2. Genuine null per drill section 3.3.

(FOLDIAK arm dropped; v3 redesign filed with Research.)

## Discriminator per V (per spec)

- **V=200:** below JL-margin; random should saturate (BPC near log2(200) ~7.64 limit). Biology arms expected at-most-tie. top-5 alongside top-1 for argmax-noise robustness.
- **V=1000:** transition regime; random has some headroom; biology arms may show small lift.
- **V=4000:** production (matches v1); per drill, OLSHAUSEN tied with random.
- **V=10000:** large; random has lots of headroom; biology should show STRONGEST lift IF it ever does.

## Operating disciplines

- **D1 roofline probe MANDATORY** (48 sub-runs after FOLDIAK drop; 4 arms x 4 V x 3 seeds). Wall budget below.
- **D2 atexit + per-(V, arm) checkpoint** MANDATORY (don't lose 2-2.5h work). Compound key `V<V>_seed<seed>` supported by `_seed_checkpoint.write_partial_key`.
- **Self-test gate** PASS (validated locally; T3b removed since FOLDIAK dropped).
- **NO local smoke for full V grid** -- pipeline already exercised under v2 smoke (V=200 LANDED in `data/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM_smoke/`); v2b cell is structurally identical for the 4 surviving arms.
- **Pre-reg + cell committed BEFORE dispatch** (uncommitted laptop notes invisible to autonomous pipeline -> GATE_FAIL).
- **Path-scoped commits** (no `git add -A`; canonical Store in repo).
- **ASCII only** (no unicode in scripts).
- **Per Fix #28:** per-arm + per-V metrics in `detail.by_arm_V_agg`; verdict_msg cites them; load-bearing classifier reads metrics not msg.
- **Per Fix #20:** no pipe-tail subprocess monitoring (atexit synthesizer + mtime polling).
- **Per Fix #17:** timeout = 10800s (3h) for full V grid (over-budget; FOLDIAK was the slow arm at V=10000 so the 2-2.5h estimate has headroom).
- **Per Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm:** sigma0 < 0.90 triggers CONFOUND_FAIL FIRST before any mechanism claim. Still honored in `_classify_arm_at_V`.

## Wall budget (revised after FOLDIAK drop)

Per-V estimate (3 seeds, CPU, numpy; 4 arms):
- V=200, N_TRAIN=20k: ~3 min/seed * 3 = 9 min
- V=1000, N_TRAIN=100k: ~10 min/seed * 3 = 30 min
- V=4000, N_TRAIN=400k: ~30 min/seed * 3 = 90 min (FOLDIAK was 30-40% of v1 wall here)
- V=10000, N_TRAIN=1M: ~25 min/seed * 3 = 75 min (FOLDIAK V x V = 400MB was the dominant cost; without it V=10000 is now matmul-bound on random/Olshausen/Kohonen only)

**Total wall ~3.5h worst case; 2-2.5h typical.** `--timeout 10800` (3h) is the safety budget; atexit synthesizer recovers partial (V, seed) units on timeout.

## Per-Fix discipline

- **Fix #26 (pre-dispatch verify-the-referent):** `tools/predispatch_check.py substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak` -> PROCEED (new anchor; 0 prior landings; 0 prior atoms; no duplicate-dispatch risk).
- **Fix #20 (no pipe-tail subprocess monitoring):** monitor via mtime polling on `data/exp_<anchor>/partial_metrics_V<V>_seed<seed>.json`.
- **Fix #24 (GPU dispatch must actually use GPU):** acknowledged; v2b is numpy CPU on remote_cpu_queue; torch port is follow-up if V=16000+ ever becomes load-bearing.
- **Fix #28 (per-arm metrics, not summary verdict):** ALL per-arm-per-V BPC + top1/top5 + eigenspread + cosine_spread + sigma0_recall stored in `detail.by_arm_V_agg`; post-landing run `tools/peek_arm_metrics.py` BEFORE propagating cross-arm narratives.
- **Long-cells discipline:** per-(V, seed) checkpoint via `_seed_checkpoint.write_partial_key`; restartable from any (V, seed) boundary.
- **ASCII-only:** all print(), verdict_msg.

## Provenance investigation (v1 OLSHAUSEN +0.56 BPC drift)

UNCHANGED from v2. v2b still records in `detail.provenance_diagnostic` at V=4000:
- `random_bpc_at_V4000` (the ARM_RANDOM baseline)
- `fair_harness_target` (7.3065)
- `drift_vs_fair_harness` (signed drift)
- `within_tol` (boolean; 0.20 loose tol)
- `note` (explicit honest-scope flag)

## Self-test PASS evidence

Run `.venv/Scripts/python.exe experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2b_no_foldiak.py --self-test`:

```
[selftest] starting...
[selftest] PASS: T1 trigram + T2 sparse_bipolar + T3 4-arms shape+sigma0 (FOLDIAK dropped) + T4 anisotropy + T5 BPC+top1/top5 + T6 verdict-shape (NULL/HP/CONFOUND) + T7 provenance + T8 band ordering + T9 ckpt-key shape OK
```

Coverage:
- T1: char-trigram bipolar output
- T2: sparse_bipolar fraction-f exactness
- T3: all 4 arms produce (V, N_DIM) shape + sigma=0 cleanup recall >= 0.90 + isfinite all-true (asserts `len(ENCODERS) == 4`)
- T3b: REMOVED in v2b (no FOLDIAK arm)
- T4: anisotropy_diagnostic returns required keys
- T5: build_hebbian_W_np + path_a_bpc finite + positive + top1/top5 in [0, 1] + top5 >= top1
- T6: compute_verdict handles HARD_FAIL_NULL / HARD_PASS / CONFOUND_FAIL correctly with 4-arm fixtures
- T7: provenance diagnostic recorded when V=4000 present
- T8: band ordering well-formed
- T9: per-(V, seed) checkpoint key shape composes correctly

## Cites

- notes/research_drill_all_negatives_plus_oom_solution_2026-06-25.md (source-of-truth correction; per-arm root cause)
- notes/exp_dev_to_research_FOLDIAK_v3_redesign_request_2026-06-25.md (FOLDIAK v3 redesign request; drop-decision rationale)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v1.py (original v1 base)
- experiments/exp_substrate_unsupervised_anisotropic_encoder_biology_native_v2_surgical_PLUS_PHASE_DIAGRAM.py (immediate parent; FOLDIAK arm removed in v2b)
- experiments/exp_fair_harness_sparse_bipolar_T_PINNED_witness_v1.py (rail 7.3065 reference)
- Olshausen-Field 1996 Nature 381:607-609 (V1 sparse coding)
- Moraitis et al. 2107.05747 (SoftHebb forward-only Hebbian)
- Perozzi et al. 2014 (DeepWalk)
- Kohonen 1982 (SOM topographic maps)
- USER directive 2026-06-25 (basis-vs-use-case: no labels at basis)
- Skunkworks META_RULE_sigma0_cleanup_integrity_gate_per_arm
- Mu-Viswanath spectrum-of-decisions framework (substrate may not need encoder upgrade in this regime; informative negative is acceptable outcome)

-- Exp-Dev
