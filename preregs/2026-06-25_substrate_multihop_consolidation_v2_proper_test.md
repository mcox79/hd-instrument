# Pre-reg: substrate_multihop_consolidation_v2_proper_test

**Authored:** 2026-06-25 by exp_dev (coordinated blitz Agent 1 of 3 — Cell B).
**Cell:** `experiments/exp_substrate_multihop_consolidation_v2_proper_test.py`
**Lane:** 1 (substrate-native; pure numpy).
**Routing intent:** local_cpu_queue (CPU-feasible; ~30min wall estimated for 3 seeds).
**Prior cell:** `experiments/exp_substrate_multihop_consolidation_memory_v1.py` (K_THRESH=1 wrote answer-tuples by construction → Skunkworks META_M4).

## Why v2 exists

v1 used K_THRESH=1 on ALL queries (including the held-out evaluation queries),
which meant the consolidator wrote `(s, R_compound, o)` answer-tuples directly
into W BEFORE evaluation. Skunkworks META_M4 ruled this is by-construction
saturation — the cell tested the memory primitive's ability to memorize visible
answer tuples, not the substrate's ability to generalize multi-hop chains.

**v2 is the PROPER multi-hop generalization test:**
1. K_THRESH > 1 (consolidator must SEE chain K times before writing compound atom)
2. Held-out chains NEVER visible to consolidator (the consolidation decision
   is based ONLY on training queries; held-out chains are evaluated using
   the trained codebook)
3. Apples-to-apples baseline: fixed predicate pair (p1=0, p2=1) matching the
   beta-sweep regime that produced the ~0.65 naive baseline

## Strategic intent

Test whether substrate consolidation (Squire-Wixted hippocampal-cortical replay
analog) genuinely LIFTS multi-hop generalization above the naive 0.65 ceiling on
**previously-unseen chains** (heldout), or whether v1's apparent lift was pure
by-construction saturation.

## Config

| Param | Value | Reason |
|---|---|---|
| N_DIM | 8192 | matches beta-sweep regime |
| V_CONCEPTS | 200 | matches beta-sweep regime |
| V_PREDICATES | 2 (fixed p1=0, p2=1) | matches beta-sweep regime (single chain class) |
| N_CHAINS_TRAIN | 200 | training chains visible to consolidator |
| N_CHAINS_HELDOUT | 50 | held-out chains NEVER visible to consolidator |
| SEEDS | [7, 17, 23] | 3 seeds for cv check |
| K_THRESH_GRID | [1, 3, 5, 10] | phase-diagram scan |

## Arms (6)

1. **ARM_NAIVE_HARD_2HOP**: control; standard chained retrieval; must reproduce ~0.65 ± 0.03
2. **ARM_CONSOL_KTHR_1_CONTROL**: replicates Cell 4 v1 — proves the by-construction trap
   - Expected: training_top1 → ~1.000 (saturation); heldout_top1 ≈ NAIVE + ε
3. **ARM_CONSOL_KTHR_3**: substantive memory test
4. **ARM_CONSOL_KTHR_5**: K_THRESH=5
5. **ARM_CONSOL_KTHR_10**: K_THRESH=10
6. **ARM_HYBRID_KTHR_3_PLUS_CLEANUP**: Wave14R-style cleanup for unconsolidated + consolidation for frequent

## Two metrics per arm (LOAD-BEARING per Fix #28)

- `top1_TRAINING`: visible chains — saturates for K_THRESH=1 (the trap)
- `top1_HELDOUT`: NEVER visible — **the genuine multi-hop generalization test**

## HARD bands on HELDOUT (the only metric that matters)

- **HARD_PASS_BREAK_CEILING**: ARM_HYBRID or ARM_KTHR_3 `heldout_top1 ≥ 0.85`
- **HARD_PASS**: best `heldout_top1 ≥ 0.75`
- **HARD_FAIL**: ALL consolidation arms `heldout_top1 ≤ NAIVE + 0.03`
- **MIDDLE_BAND**: partial signal

## Sanity rails

- NAIVE reproduces 0.65 ± 0.03 (beta-sweep regime apples-to-apples)
- ARM_KTHR_1: `training ≥ 0.95` AND `heldout ≤ NAIVE + 0.03` (empirically proves by-construction trap;
  the v1 reproduction is itself a methodological proof point)

## Phase-diagram scan

K_THRESH = {1, 3, 5, 10} + train/heldout split. Operating envelope: at what
K_THRESH does consolidation transition from saturation to genuine generalization?
The K_THRESH=1 control + K_THRESH ≥ 3 substantive arms together map this transition.

## Q discipline

- Held-out queries are CONSTRUCTED FRESH per seed (split is reproducible from
  seed but never seen by consolidator)
- Bands physically achievable: at V_C=200 N=8192, the naive ~0.65 ceiling is
  well-documented; the 0.85 break-ceiling is 0.20 above noise floor which is
  consistent with Wave14R-style cleanup-attractor lift
- All bands locked BEFORE smoke or full data collected

## Fix #28 discipline

- Per-arm metrics reported (6 arms × 2 metrics each); verdict_msg cites per-arm numerics
- HELDOUT metric is the DISCRIMINATOR; TRAINING metric is the sanity-rail (saturation flag)

## Pre-registered expectation (Q-discipline)

- ARM_NAIVE_HARD_2HOP heldout ~ 0.65 ± 0.03 (regime-matched baseline)
- ARM_CONSOL_KTHR_1_CONTROL training ~ 1.000 (the by-construction trap fires; saturation rail)
- ARM_CONSOL_KTHR_1_CONTROL heldout ~ NAIVE + small ε (compound atoms for unseen chains;
  the trap proves itself by training saturating but heldout staying at baseline)
- ARM_CONSOL_KTHR_3/5/10 heldout: UNCERTAIN — the substantive test (genuine multi-hop generalization)
- ARM_HYBRID_KTHR_3_PLUS_CLEANUP heldout: most likely to break 0.85 (cleanup-attractor + consolidation)

**Expected verdict:** P(HARD_PASS_BREAK_CEILING) = 0.30; P(HARD_PASS) = 0.45;
P(HARD_FAIL or MIDDLE_BAND) = 0.55. Skewed pessimistic because the META_M4 ruling
implies the consolidation mechanism may not transfer to heldout chains — that's
exactly what v2 is testing for the first time honestly.

## Disposition

- HARD_PASS_BREAK_CEILING → Skunkworks for landed-VET; if chain-grade, route as
  Barrier 1 closure via consolidation primitive
- HARD_FAIL → route NEGATIVE to Research for 2x revival drill (the
  consolidation primitive doesn't generalize; revival = "what other multi-hop
  rescue mechanism applies?")
- MIDDLE_BAND → Skunkworks VET + Research drill on which K_THRESH regime is
  most discriminating

## Operational disciplines

- D1 roofline (CPU): pure numpy on N=8192/V_C=200 with 250 chains × 6 arms × 3 seeds
  ≈ ~20-40min; sub-PROT-019 timeout floor
- D2 atexit + per-seed checkpoint mandatory
- Self-test PASS gate (verified; empirically demonstrates the by-construction trap)
- LOCAL SMOKE PASS gate
- ASCII only
- Substrate-only (`_LLM_CALL_COUNTER = [0]`)

## Cites

- `experiments/exp_substrate_multihop_consolidation_memory_v1.py` (v1 with K_THRESH=1 trap)
- Skunkworks META_M4 ruling (by-construction-saturation; K_THRESH=1 writes answer tuples)
- Last night's `substrate_resonator_softchain_beta_sweep_v1` HARD_FAIL (beta-sweep baseline 0.65)
- Wave14R cleanup primitive (for hybrid arm)
