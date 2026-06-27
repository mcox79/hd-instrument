# Prereg: substrate_multihop_brain_pushback_composition_v1

Date: 2026-06-27
Anchor: substrate_multihop_brain_pushback_composition_v1
Cell: experiments/exp_substrate_multihop_brain_pushback_composition_v1.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Wave: Cycle 1 — load-bearing test that META_BARRIER_1 was prematurely declared
Timeout: 28800s (8h)

## Motivation

USER push-back 2026-06-27 (drill
`notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`):
"i do not accept those limitations. how does the brain do it" — explicit
rejection of substrate-product permanent 2-hop framing. The drill
re-audited 5 prior multi-hop refutations and concluded 4 of 5 tested
CARICATURES of brain mechanisms rather than the brain mechanisms
themselves:

- Refute 1 (CONSOLIDATION v1-v3): used SHARED W for compound atoms;
  brain uses SEPARATE cortex W vs hippocampus W.
- Refute 2 (POINTER-CHAIN v1/v2): per-hop binding into SHARED W; brain
  uses SEPARATE PFC scratchpad with persistent activity.
- Refute 3 (WM-SCAFFOLDED v1): likely held intermediates in SHARED W
  (code audit pending); brain uses dedicated scratchpad bank.
- Refute 4 (CSP-GATED ITERATED CLEANUP v1): binary abort; brain uses
  graded confidence (population code).
- Refute 5 (PARALLEL-VOTE v1/v2): "regime artifact" framing; within-cell
  K-scaling actually showed monotonic lift; should retest as soft LDPC.

This cell composes 3 brain-correct architectural fixes (R1+R2+R3) as
ONE 5-arm test. The COMBINED arm at depth-5 >= 0.65 is chain-grade-
eligible (BARRIER 1 BROKEN; CERT +1).

## Mechanisms (3 brain-correct architectural fixes)

### R1: NREM-replay-into-W_C (composes B1 + B5 + B7)

Brain mechanism: complementary-learning-systems (McClelland-McNaughton-
O'Reilly 1995) + sharp-wave-ripple replay (Foster-Wilson 2006) + schema
chunking (Tse et al. 2007). Replay extracts A->C shortcuts from frequent
A->B->C exposure; shortcuts go into SEPARATE cortex W, leaving
hippocampal W untouched.

Substrate-native implementation:
- Build W_H (hippocampal) from training chains via Hebbian binding.
- Simulate offline NREM replay over chains; compute continuous trace
  amplitude (cosine of retrieved state with true endpoint).
- M-CFU-style cohort top-K: split into R1_REPLAY_COHORTS=5 cohorts,
  take top-K=30 chains per cohort with amp >= 0.55 (CONTINUOUS, not
  binary frequency-gated — per v4 fairness drill correction).
- Write A->C shortcut triples into SEPARATE W_C using R[0] as the
  shortcut predicate.
- Multi-hop query: try W_C first (single-hop shortcut lookup); fall back
  to per-hop W_H walk on miss.

Composes 2 chain-grade substrate primitives: TWO_TIER (CERT chain-grade
generational) + NREM replay (CERT chain-grade lock-in amp).

### R2: PFC-scratchpad-SEPARATE-W (B2)

Brain mechanism: Miller-Cohen 2001 PFC as separate persistent-activity
store; Constantinidis-Klingberg 2016 working-memory in dedicated neural
populations.

Substrate-native implementation:
- Dedicated W_PFC matrix (initialized to zeros per query) holds clean
  intermediates.
- Each hop reads W_H, writes top-1 cleaned prediction to W_PFC at slot
  i+1 (using E[slot_idx] * R[0] as slot key).
- Next hop queries W_H using the clean intermediate from W_PFC (not
  the noisy chain state).

W_H is READ-ONLY across hops (SEPARATE-W discipline; runtime assertion).

### R3: Bidirectional-meet-in-middle (B3)

Brain mechanism: Foster-Wilson 2006 reverse SWR replay; Pfeiffer-Foster
2013 pre-trial reverse replay anticipates goal. Both forward and reverse
replay co-occur; meet-in-middle planning.

Substrate-native implementation:
- Forward walk from chain[0][0] via W_H.
- Backward walk from chain[depth-1][2] via W_H using HRR-involutive
  unbinding (bipolar self-inverse: R[p] * R[p] = (1/n) * ones; shape-
  preserving for L2-normalized bipolar; chain-grade primitive).
- Meet criterion: scan (fwd_state at step k) vs (bwd_state at step
  depth-k) for any k; commit on exact match OR cosine >= 0.30.
- sqrt-speedup over forward-only error compounding.

### COMBINED arm (R1 + R2 + R3 stacked)

- First try R1 W_C shortcut.
- On miss, run R3 bidirectional with R2 W_PFC scratchpad holding both
  forward and backward intermediates.
- Commit on shortcut OR meet OR forward final == goal.

## ARMS (5 mandatory)

- ARM_BASELINE (per-hop cleanup; depth-5 SANITY RAIL 0.145 +/- 0.05)
- ARM_R1_REPLAY_INTO_W_C
- ARM_R2_PFC_SCRATCHPAD
- ARM_R3_BIDIRECTIONAL
- ARM_COMBINED_R1_R2_R3

All arms share E, R, W_H, test_chains; differ only in which mechanism
runs on top.

## Pre-reg bands (HARD-LOCKED PROSPECTIVE; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

Target depth: 5 (chain-grade threshold per drill decision tree).

HARD_PASS_BARRIER_BROKEN (chain-grade-eligible; CERT +1):
  - ARM_COMBINED depth-5 mean >= 0.65
  - AND ARM_COMBINED > MAX(R1, R2, R3) (composition wins individual)
  - AND ARM_COMBINED > BASELINE + 0.45 (massive lift)
  - AND cv across seeds <= 0.08
  - AND BASELINE depth-5 in [0.10, 0.20] on majority of seeds (regime
    validated)

HARD_PASS_INDIVIDUAL_WINS:
  - Any individual R1/R2/R3 depth-5 mean >= 0.50
  - AND > BASELINE + 0.30
  - AND cv <= 0.08

MIDDLE_BAND:
  - ARM_COMBINED depth-5 in [0.45, 0.65)
  - OR any individual R-arm depth-5 in [0.30, 0.50)

HARD_FAIL:
  - ARM_COMBINED depth-5 < 0.25 (pivot to X1 primitive replacement)
  - OR ARM_COMBINED within 0.05 of ARM_BASELINE (composition doesn't help)

RAIL_SANITY_BREACH (uninterpretable):
  - ARM_BASELINE depth-5 outside [0.10, 0.20] on majority of seeds

## Cardinality (META_RULE_H mandatory)

EXPECTED_N_UNITS_FULL = 5 arms * 3 seeds * 4 depths = 60 arm-depth-seed entries.
EXPECTED_N_UNITS_SMOKE = 5 arms * 1 seed * 2 depths = 10 entries.
HARD_FAIL_CARDINALITY_BREACH = observed != expected (verdict flag).

## Discriminator-must-survive-scale (D1)

Smoke uses FULL-N parameters (N=8192, V_C=200, P=10) with reduced
n_chains=50 (vs full 200) + 2 depths (vs full 4) + 1 seed (vs full 3).
The 5-arm separation at depth-5 is the discriminator; baseline at
depth-5 must reproduce 0.145 +/- 0.05 even at smoke scale (full-N
preserves the per-hop ~0.69 floor).

Note: USER 2026-06-27 NO LOCAL directive => no full local smoke. Cell-
author selftest (small-N=1024 V=60) ran locally and PASSED (validates
mechanism correctness + SEPARATE-W assertions + HRR involutive sanity);
full smoke runs on remote_cpu via gate.

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; substrate primitives
only; no transformers / no encoders).

## BRAIN_MECHANISM_VS_CARICATURE checks (load-bearing per drill)

Runtime assertions (cell raises RuntimeError on violation; results
uninterpretable):
- W_H is READ-ONLY during all arm executions; SEPARATE W_C / W_PFC
  matrices for R1 / R2 / COMBINED.
- R3 backward direction uses bipolar HRR-involutive unbinding (R[p] *
  R[p] = (1/n) * ones for L2-normalized bipolar; selftest verifies).
- R1 replay uses CONTINUOUS amplitude gating (min_amp=0.55), NOT binary
  frequency gating (v4 drill correction; replay-as-OPERATOR not
  replay-as-SIGNAL).

## META_RULE_J (no silent except)

The cell uses no bare `except:` blocks. The atexit synth handler catches
exceptions during partial aggregation but RE-RAISES after logging
(record-and-halt; no silent swallow). The selftest uses assertions
(crash-and-halt on violation).

## Real data / synthetic provenance

The cell uses random bipolar key/value pairs (matches v3/v4 base; the
mechanism is about composition of architectural fixes, NOT corpus
semantics). allow_synthetic=True is appropriate; cell asserts no real-
corpus dependency.

## Compute budget

Per seed (full): 5 arms * 4 depths * 200 test_chains. Dominant cost is
matrix-vector products on N=8192 (W is 8192x8192 = 256MB float32).
- W_H build: ~1-2s
- W_C build (replay): ~5-10s per seed
- Per-arm-per-depth: ~10-30s (depth-8 longest)
- Total per seed: 5 * 4 * 20s = ~400s + W builds ~ ~450s
- 3 seeds: ~1400s nominal; add 4x safety for matrix-op scaling and
  unforeseen costs => ~5600s expected; cap at 8h (28800s) timeout.

PROT-019 compliance: anchor name does NOT contain `_n<N>` suffix (since
multiple depths and tier-specific paths make N-binding brittle); cell
N=8192 is hardcoded in the production config block.

PROT-021 compliance: cell imports experiments._seed_checkpoint
(resumable_seeds, write_partial_key, aggregate_partials, write_metrics).
Long timeout (28800s >= 14400s) requires checkpoint per PROT-021 — held.

## Honest scope

This cell tests whether composing 3 brain-correct architectural fixes
(R1 NREM replay into separate W_C + R2 PFC scratchpad in separate W_PFC
+ R3 bidirectional meet-in-middle) lifts substrate multi-hop past the
chain-grade depth-5 0.65 threshold. It does NOT test:

- R4 RECURRENT-ATTRACTOR-PER-HOP (B8 rate-coded soft-completion; drill
  rank 4; separate cell if R1+R2+R3 only MIDDLE_BAND)
- R5 GRADED-CONFIDENCE-OUTPUT (refines CSP-gated; drill rank 5)
- N1 SCHEMA-EXTRACTED-WITHOUT-STORAGE-POLLUTION (new mechanism from
  drill; orthogonal axis)
- N2 RATE-CODED-SOFT-COMPLETION (new mechanism from drill)
- B4 LDPC bidirectional soft-message (gap1 5x rank-1; separate cell)
- B6 external scaffolding (product-layer; no cell needed)

If COMBINED < 0.25 (HARD_FAIL_PIVOT), the drill specifies pivot to X1
primitive replacement (substrate's W and binding primitives are
fundamentally insufficient; need different math). If MIDDLE_BAND, the
drill specifies queue N1 isolation audit + R4 attractor as follow-ups.

## Decision tree (post-verdict)

- HARD_PASS_BARRIER_BROKEN: BARRIER 1 BROKEN; substrate multi-hop is
  chain-grade-eligible; atomize as CERT; update cap_map; ship hdlab/
  primitive update SAME CYCLE (per USER 2026-06-22 results-to-application
  cadence).
- HARD_PASS_INDIVIDUAL_WINS: one of R1/R2/R3 alone is the lever;
  Skunkworks tier-rules (chain-grade vs measured-mechanism); follow-up
  cell to ablate composition margin.
- MIDDLE_BAND: queue N1 isolation audit + R4 attractor (next-wave cells
  per drill).
- HARD_FAIL_PIVOT: pivot to X1 primitive replacement; substrate's W is
  insufficient; need different math.
- HARD_FAIL_FLAT: composition adds no value; one of the SEPARATE-W
  assumptions or the meet-criterion is wrong; debug-cycle.
- RAIL_SANITY_BREACH: cell uninterpretable; regime broken; re-design.

## SCHEMA-VET 5b per-arm HP scope

Each arm's metrics fully reported in metrics.json per_seed as
`arm_<name>_depth_<d>`:
- top1 (per-arm; per-seed; per-depth)
- elapsed_s_arm (per-arm; per-seed; per-depth)
- mechanism-specific extras (shortcut_hit_rate / meet_rate /
  fwd_only_top1 / bwd_only_top1 / mean_meet_step / shortcut_hits /
  meet_hits / fallback_fwd_hits / pfc_writes / pfc_reads /
  per_step_acc / shortcut_attempts / fallback_used)

Verdict reads per-arm aggregates not summary text (Fix #28); aggregate
fields per arm at target_depth=5: mean_top1, cv_top1, baseline_breaches
count, cardinality_ok flag, observed_units count.

## Reference

Drill: `notes/research_drill_brain_multihop_7mechanism_inventory_USER_PUSHBACK_2026-06-27.md`
Section: "Recommended composition sequence" — R1+R2+R3 as ONE 5-arm
cell; M2 NREM-compact and M3 stabilizer as second-wave once R1-R3
outcomes inform mechanism layer.

5-mechanism re-audit referent: drill Sections "Refute 1" through
"Refute 5"; documents each prior META_BARRIER_1 atom as a CARICATURE
test rather than a brain-mechanism test.
