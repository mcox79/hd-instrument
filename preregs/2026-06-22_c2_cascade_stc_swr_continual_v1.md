# Pre-reg: c2_cascade_stc_swr_continual_v1

**Date:** 2026-06-22
**Anchor:** c2_cascade_stc_swr_continual_v1
**Cell:** experiments/exp_c2_cascade_stc_swr_continual_v1.py
**Source-of-truth pre-reg (brain-drill #2 5x DEEPER L4):** notes/research_brain_drill_2_CLS_continual_learning_5x_DEEPER_2026-06-22.md
**Author:** Exp-Dev (brain-drill #2 5x DEEPER payload; novel-synthesis P_deflated=0.40 per Research lit-scan calibration)

## Scientific question

Does a THREE-MECHANISM nested-timescale consolidation primitive (cascade-synapse
metaplasticity + STC tag-and-capture + SWR-gated selective replay on expanding
intervals) rescue continual learning at alpha=3.0, where c1's uniform 1:1 replay
mechanism is expected to collapse?

c1 (uniform 1:1 replay) HARD_FAILed smoke this arc; below the alpha cliff
(alpha=0.5) codebook-NN cleanup masks any collapse (recall=1.000 every arm).
The 5x DEEPER drill says: 1:1 replay is SHALLOW CLS; biology runs THREE
nested timescales (Fusi 2005, Frey-Morris 1997, 2024-2025 large-SWR evidence).

## Mechanism (substrate-faithful)

For each W entry (i, j):
- Plain Hebbian-superposition for C1_BASELINE and NO_REPLAY arms.
- For CASCADE_STC_SWR arm:
  (a) **Cascade synapse:** depth state d in {0, 1, 2, 3}; per-entry plasticity
      p_d = (1/2)^d; writes apply only to entries where Bernoulli(p_d) fires.
  (b) **STC tag-and-capture:** each write computes tag = sigmoid(beta * margin)
      where margin = top1 - top2 in codebook for the TRUE value (refuse-gate
      analog). Tags above theta_tag=0.5 promote depth (cap at D_max=3) for the
      top-recruited W entries.
  (c) **SWR-gated selective replay on expanding intervals:** after each ingest
      cycle (j>0), replay TOP-TAG events from PRIOR TASKS at lags {1, 2, 4, 8, ...}.
      Budget = REPLAY_BUDGET_PER_INGEST * M_per_task (same as C1 1:1 baseline).
  (d) **Slow noise-floor decay:** each cycle, entries with d>0 transition d -> d-1
      with rate THETA_DECAY_RATE=0.02.

Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM forward calls).
Composes with U1 refuse-gate (tag uses margin); orthogonal to V_C x N_DIM and to kWTA
(brain-drill #1).

## Arms (Fix #16 discriminator)

- **NO_REPLAY**: write-only, no replay; forgetting-floor baseline.
- **C1_BASELINE**: classical 1:1 uniform replay; the c1 mechanism that HARD_FAILed smoke this arc.
- **CASCADE_STC_SWR**: full three-mechanism nested-timescale primitive.

Three arms isolate (a) is replay needed at all (NO_REPLAY vs C1), and (b) does cascade-STC-SWR
beat uniform 1:1 (C2 vs C1) -- the headline mechanism test.

## Fixed config

N_DIM=4096 ; J_tasks=12 ; alpha=3.0 (discriminating regime; well above c1's tested cliff) ;
M_per_task = round(alpha * N_DIM / J) = 1024 ; SEEDS=[7,17,23] ; D_max=3 ;
theta_tag=0.5 ; tag_beta=4.0 ; theta_decay_rate=0.02 ; replay_budget=1:1 per ingest cycle
(same compute as C1 baseline so it is mechanism-fair) ; K_EVALS=[3, 6, 12] ;
NOISE_FRAC=0.10 ; N_RECALL_STEPS=3.

## Pre-registered HARD bands (research drill #2 P_deflated=0.40)

**HARD_PASS (chain-grade, ALL of):**
- C2_CASCADE_STC_SWR retention at k=12 >= 0.85
- C1_BASELINE retention at k=12 < 0.60 (baseline collapse confirmed at alpha=3.0)
- NO_REPLAY retention at k=12 < 0.30 (forgetting floor below baseline)
- C2 retention > C1 retention at k_mid >= 6 (mechanism kicks in mid-stream, not just at end)
- cv_C2 at k=12 <= 0.06 across 3 seeds (mechanism reproducible)
- substrate-only-decode: zero LLM forward calls

**HARD_FAIL (mechanism wrong):**
- C2 retention at k=12 < 0.40, OR
- C2 retention <= C1 retention at k_mid >= 6 (cascade-STC-SWR adds nothing over uniform), OR
- substrate-only-decode gate violated (n_llm > 0)

**MIDDLE_BAND:** between (partial mechanism; routes to single-mechanism ablations
CASCADE_ONLY / STC_ONLY / SWR_ONLY in a follow-up cell).

## Version markers (anti-r1b mean-reproduction-failure)

Baked into metrics.json:
- consolidation_arm (per-unit)
- D_max (=3)
- theta_tag (=0.5)
- tag_function (="sigmoid_margin")
- replay_schedule_mode_C2 (="expanding")
- replay_schedule_mode_C1 (="uniform_1to1")
- alpha (=3.0)
- corpus_provenance (="synthetic_bipolar_keys")

## Discriminating-regime requirement (C5)

alpha=3.0 is well above c1's tested cliff (alpha=0.5 codebook-NN masks collapse).
At this regime all three arms must DIFFERENTIATE:
- NO_REPLAY should collapse fastest (forgetting floor).
- C1_BASELINE should collapse but more slowly (replay helps a bit but is uniform/dumb).
- CASCADE_STC_SWR should survive (mechanism is mechanism-discriminating).

If all three arms collapse together: alpha is too aggressive (capacity ceiling); route to
secondary cell at alpha=2.0. If all three arms succeed together: alpha is too gentle (cliff
not engaged); route to higher alpha.

## Compute budget

- Per-arm per-seed: ~30 min on remote_cpu (N_DIM=4096, J=12, M=1024; cascade adds ~1.2x overhead
  via per-entry Bernoulli mask).
- 3 arms x 3 seeds = 9 runs; total ~270 min wall = ~4.5 hours full-pipeline (parallelism via
  runner; per-seed-resumable so partial progress survives kills).
- Smoke wall estimate: ~3 min (N_DIM=1024, J=4, alpha=1.0, 1 seed, 3 arms).

## Self-tests (asserted at import time)

1. cascade depth update: tag>theta promotes entries; tag<theta does not.
2. plasticity p_d at d=3 equals 0.125 (1/8).
3. expanding-interval schedule at j=8 returns lags [7, 6, 4, 0].
4. _LLM_CALL_COUNTER remains 0 throughout.

## Composition path

If c2 HARD_PASSes:
- Route to c3_cascade_real_KG_continual_v1 (real KG ingest on FB15k-237 or ConceptNet).
- Compose with brain-drill #1 kWTA-VQ at write/read.
- Update hdlab/cascade_w.py primitive.

If c2 HARD_FAILs:
- Route to research for single-mechanism ablation (CASCADE_ONLY / STC_ONLY / SWR_ONLY arms).
- Open question: is the substrate fundamentally different from biology re: continual ingest?

If c2 MIDDLE_BAND:
- Phase 2 cell with secondary D_max sweep + tag-function ablation.

## ASCII-only / commit-before-dispatch / per-seed-resumable / smoke gate first.
