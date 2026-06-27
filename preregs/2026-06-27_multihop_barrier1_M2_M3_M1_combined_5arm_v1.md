# Prereg: multihop_barrier1_M2_M3_M1_combined_5arm_v1

Date: 2026-06-27
Anchor: multihop_barrier1_M2_M3_M1_combined_5arm_v1
Cell: experiments/exp_multihop_barrier1_M2_M3_M1_combined_5arm_v1.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive; CPU-feasible
       per drill estimates ~4-5 hr full run)
Wave: Drill 4 rank-1 multi-hop; 3-mechanism stack META_BARRIER_1 test
Primitives composed:
  - HRR-style bipolar binding (in-cell; pointer-chain conventions from
    exp_substrate_multihop_pointer_chain_hybrid_v2_BASELINE_RAIL_FIXED)
  - chain-grade NREM-replay primitive (pattern; for M2)
  - chain-grade KG ingest 588 (type-constraint mask for M1)
  - in-cell stabilizer-vector fit (M3; greedy bit-flip; cheap)

## Motivation

META_BARRIER_1 (atomized 2026-06-25): 4 substrate-native multi-hop
closure attempts REFUTED at random-bipolar isotropic regime
(consolidation / pointer-chain / WM-scaffold / CSP-gated). META_M7
parallel-vote also regime-artifact. Multi-hop beyond 2 hops is currently
the largest OPEN substrate-product limit. Production rail anchor:
  per-hop cleanup ~ 0.69 -> compounding gives depth-5 ~ 0.145 +/- 0.02

Drill (research_drill_multihop_barrier1_quadruple_negative_3x_2026-06-27)
identified 3 categorically novel mechanisms NOT covered by 28
prior-drilled angles:

  M1 GROVER amplification (post-hoc; sqrt-N speedup; type-constrained
     reflect-about-mean/reflect-about-target; classical numpy
     implementation; quantum-inspired; un-drilled scope-expansion field)
  M2 NREM-REPLAY-COMPACT (adaptive replay-driven shortcut creation;
     uses chain-grade NREM-replay primitive pattern to BIND direct
     A->endpoint atoms for frequently-traversed chains; brain analog:
     Buzsaki 2015 SWR replay; AI analog: Dyna-Q / DQN replay buffer)
  M3 STABILIZER-VECTOR (per-hop margin lift via bind-to-stabilizer;
     enzyme transition-state stabilization analog: Fersht 1999;
     intermediate-supervision in DL; learned per-hop scaffold vector
     raises cleanup margin WITHOUT primitive replacement)

The 3 mechanisms address error compounding at 3 INDEPENDENT layers:
  - M1: readout layer (amplify correct over noise)
  - M2: structural layer (turn multi-hop into single-hop via shortcuts)
  - M3: per-hop primitive layer (raise margin without replacement)

ARM_COMBINED tests synergistic stack: M2 creates shortcuts -> M3 raises
per-hop margin on fallback walks -> M1 amplifies endpoint distribution
with type-constraint mask.

## ARMS (5; cardinality_ok mandatory)

- ARM_BASELINE
  per-hop cleanup pointer-chain walk; anchors ~0.145 at depth-5 +/- 0.04
  (regime sanity rail)
- ARM_M1_GROVER_AMPLIFICATION
  baseline + type-constraint + Grover K=3 iterations
- ARM_M2_NREM_REPLAY_COMPACT
  baseline + replay-driven shortcut atoms for top-freq chains;
  shortcut-or-fallback at query time with margin threshold tau
- ARM_M3_STABILIZER_VECTOR
  baseline + per-hop trained stabilizer S_k (greedy bit-flip; fit on
  STABILIZER_FIT_N_CHAINS=100 train chains)
- ARM_COMBINED
  M2 shortcut tried first -> on miss/low-margin, M3-stabilized walk
  -> M1 Grover amplification on endpoint distribution

ALL arms share the SAME train chain set + SAME W_base. M2's W_m2 adds
shortcut bindings; M3's S is fit on W_base. Query chains are DISJOINT
from train chains (different start atoms).

## Pre-reg bands (HARD-LOCKED; META_PROSPECTIVE_BANDS_FRESH_SEEDS)

HARD_PASS_META_BARRIER_1_BROKEN (all must hold):
  - ARM_COMBINED depth-5 mean top1 >= 0.65
    (META_BARRIER_1 BROKEN; multi-hop closure beyond 2 hops achieved
    via M2+M3+M1 stack)
  - AND ARM_BASELINE depth-5 mean top1 in [0.105, 0.185]
    (regime sanity rail confirms 4-prior-refute regime is reproduced;
    cell is interpretable)
  - AND cardinality_ok: 5 arms x len(SEEDS)=3 x len(DEPTHS)=4 = 60
    arm entries actually completed across full run (HARD_FAIL on breach)

MIDDLE_BAND_PARTIAL_BARRIER_BREACH:
  - ARM_COMBINED depth-5 in [0.30, 0.65) AND ARM_BASELINE in sanity band

HARD_FAIL_META_BARRIER_1_NEGATIVE:
  - ARM_COMBINED depth-5 < 0.30
  - AND no individual M1/M2/M3 arm exceeds ARM_BASELINE by > 0.05
    at depth-5
  - Atomization implication: adopt M5 honest-acceptance framing
    (substrate is structurally 2-hop-permanent; product layer chains
    2-hop primitives with external state-tracking; PFC + hippocampus
    analog; chain-of-thought analog)

HARD_FAIL_STACK_NOT_SYNERGISTIC:
  - ARM_COMBINED depth-5 < 0.30 BUT individual arm lift >= 0.05
    (mechanisms exist but don't stack additively; further composition
    work needed; not a barrier-negative)

HARD_FAIL (other):
  - SANITY RAIL breach: ARM_BASELINE depth-5 NOT in [0.105, 0.185]
    (regime not reproduced; cell uninterpretable)
  - D4 cardinality breach
  - D3 caught exception in any arm
  - D2 mechanism inert: n_shortcuts_added==0 OR n_replay_events==0

## Cardinality (D4 mandatory)

EXPECTED_N_UNITS_FULL = SEEDS x ARMS x DEPTHS = 3 x 5 x 4 = 60 arm
entries TOTAL across full run.
HARD_FAIL_CARDINALITY_BREACH = observed_n_arm_entries != 60 OR any
single seed has != 20 arm entries.

Smoke EXPECTED_N_UNITS = 1 x 5 x 1 = 5 arm entries.

## Discriminator-must-survive-scale (D1)

Smoke uses FULL V_C=200, FULL N_CHAINS_TRAIN=500, FULL K_SET=20 (the
mechanism discriminators all depend on these scales):
  - M1 Grover speedup scales with sqrt(V_C/K_SET); reducing V_C breaks
    the test of sqrt-N amplification at production scale.
  - M2 shortcut formation requires N_CHAINS_TRAIN >= 500 for top-freq
    set to be meaningful; smaller train set yields no shortcuts.
  - M3 stabilizer fit needs ~100 train chains; included in N_CHAINS_TRAIN.

Smoke reduces ONLY:
  - N_DIM from 8192 to 2048 (matmul size; mechanism unchanged)
  - SEEDS from [7,17,23] to [7]
  - N_CHAINS_QUERY from 200 to 50
  - DEPTHS from [2,3,5,8] to [5] (depth-5 is the discriminator)

Smoke must show ARM_COMBINED > ARM_BASELINE by >= 0.05 at depth-5 OR
stop and route back (D2 smoke-fires-discriminator).

Note: USER 2026-06-27 NO LOCAL directive => no local smoke. Smoke
parameters defined here for cell completeness; full dispatch goes
straight to remote_cpu_queue.

## SANITY RAIL (hard abort path; cell uninterpretable)

- ARM_BASELINE depth-5 mean top1 NOT in [0.105, 0.185]
  (anchors ~0.145 from 4-prior-refute regime; if breached, the regime
  is broken and ARM_COMBINED's verdict is uninterpretable)
- ARM_BASELINE depth-1 (if depth=1 included in DEPTHS) below 0.50
  (single-hop should clear 0.69 in this regime; below 0.50 indicates
  regime breakage)

DEPTHS=[2,3,5,8] full; smoke=[5] only so depth-1 sanity is implicit
not enforced for smoke.

## Substrate-only-decode gate (load-bearing)

n_llm_calls per seed = 0 (numpy-only mechanism; no transformers,
no encoders, no LLM dispatch).

## Real data / synthetic provenance

Random bipolar atoms + random predicate selection per chain (matches
pointer-chain v2 conventions). The mechanisms being tested are
chain-walk + amplitude amplification + replay-compaction + per-hop
stabilization on synthetic substrate state; no corpus semantics needed.
allow_synthetic=True.

## Compute budget

Per drill estimates: M2 (10 replay passes * 500 train chains * 5 hops
= 25k chain-walks) + M3 (50 stabilizer steps * 100 train chains * 5
hop positions = 25k cleanup ops for fit) + M1 (Grover K=3 iter * 4
depths * 5 seeds * 200 chains_query) + query phase (5 arms * 4 depths
* 200 chains * varying depth) at N_DIM=8192.

Estimated per-seed wall: ~80-100 min (CPU-bound matmul N=8192).
Total full run (3 seeds): ~4-5 hr remote CPU.
Recommended --timeout: 21600s (6 hr; 1.5x buffer above 4 hr estimate).

Smoke estimate: 1 seed * 1 depth * 5 arms at N_DIM=2048: ~10-15 min.

## Honest scope

This cell tests the 3-mechanism stack (M1+M2+M3) at production scale
against the 4-prior-refute baseline rail. It does NOT test:
  - M4 metric-position (drill rank 4; separate cell if stack-MIDDLE)
  - M5 honest-acceptance framing (not a cell; adopted if HARD_FAIL_NEG)
  - Individual chain-of-thought / LLM orchestration as outer loop
  - Real KG/corpus chains (random bipolar regime; semantic chains may
    behave differently)

## Verdict logic (4-class)

HARD_PASS_META_BARRIER_1_BROKEN: ARM_COMBINED >= 0.65 at depth-5 AND
  sanity rail OK.
MIDDLE_BAND_PARTIAL_BARRIER_BREACH: ARM_COMBINED in [0.30, 0.65) AND
  sanity rail OK.
HARD_FAIL_META_BARRIER_1_NEGATIVE: ARM_COMBINED < 0.30 AND individual
  lift < 0.05 (stack disproves; adopt M5).
HARD_FAIL_STACK_NOT_SYNERGISTIC: ARM_COMBINED < 0.30 but individual
  lift >= 0.05 (mechanisms exist but don't compose).
HARD_FAIL (other): D3 / D4 / sanity / D2 violations.

## SCHEMA-VET 5b per-arm HP scope

Each arm's metrics fully reported in metrics.json per_seed.arms[]:
  - arm_name (per arm-depth entry)
  - depth (per arm-depth entry)
  - top1 (per arm-depth entry; per-seed)
  - n_queries (per arm-depth entry; per-seed)
  - per_step_acc (ARM_BASELINE only; per-hop accuracy decomposition)
  - n_shortcut_hits / n_shortcut_misses / n_fallback_hits (ARM_M2)
  - n_stack_hits (ARM_COMBINED)
  - wall_s (per arm-depth; per-seed)

Verdict reads per-arm aggregates (mean_top1 / std_top1 / cv_top1)
not summary text (Fix #28); aggregate computed in compute_verdict()
via _agg(arm_name, depth) helper.

## Atomization on landing

HARD_PASS: META_BARRIER_1_BROKEN_VIA_M2_M3_M1_STACK atom; chain-grade
  candidate after 5-seed reproducibility on next cell.
MIDDLE_BAND: META_BARRIER_1_PARTIAL_BREACH atom; identify load-bearing
  mechanism + dispatch single-mechanism cell at higher resolution.
HARD_FAIL_NEG: META_BARRIER_1_QUADRUPLE_NEGATIVE_PLUS_TRIPLE atom;
  adopt M5 honest-acceptance framing in PLAN.md + master-plan; pivot
  substrate-product story.
