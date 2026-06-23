# Pre-reg: c2_cascade_stc_swr_continual_v2

**Date:** 2026-06-22
**Anchor:** c2_cascade_stc_swr_continual_v2
**Cell:** experiments/exp_c2_cascade_stc_swr_continual_v2.py
**Source-of-truth post-mortem:** notes/c2_cascade_stc_swr_timeout_postmortem_and_reauthor_spec_2026-06-22.md
**Source-of-truth original prereg (mechanism unchanged):** preregs/2026-06-22_c2_cascade_stc_swr_continual_v1.md
**Author:** Exp-Dev (Director Option A+C re-author per timeout post-mortem)

## Why v2 (Director post-mortem)

v1 HARNESS_TIMEOUT at wall=9000s (2.5hr) on remote_cpu. Mechanism (cascade-synapse + STC tag-and-capture + SWR-gated expanding-interval replay) is sound per brain-drill #2 5x DEEPER spec; only the scale was over-estimated. Per-cell cost: N_DIM=4096 -> per-write outer-product is 16M ops; 12 tasks x 1024 writes x 3 arms x 3 seeds ~= 7.5hr.

Director-prescribed Option A+C combined:

- **A (N_DIM 4096 -> 2048):** 4x faster outer-product (drops per-write cost)
- **C (drop NO_REPLAY arm):** forgetting-floor well-established from c1; redundant. 2 arms instead of 3 (saves 33% wall).

Wall estimate: ~60-75 min remote_cpu (vs v1's ~7.5hr).

## Scientific question (unchanged from v1)

Does a TWO-MECHANISM nested-timescale consolidation primitive (cascade-synapse + STC tag-and-capture + SWR-gated selective replay on expanding intervals) rescue continual learning at alpha=3.0 -- well past c1's tested cliff at alpha=0.5 -- relative to a uniform 1:1 replay baseline (C1)?

## Mechanism (substrate-faithful, identical to v1)

For each W entry (i, j):
- Plain Hebbian-superposition for C1_BASELINE arm.
- For CASCADE_STC_SWR arm:
  (a) **Cascade synapse:** depth state d in {0, 1, 2, 3}; per-entry plasticity p_d = (1/2)^d; writes apply only to entries where Bernoulli(p_d) fires.
  (b) **STC tag-and-capture:** each write computes tag = sigmoid(beta * margin) where margin = top1 - top2 in codebook for the TRUE value (refuse-gate analog). Tags above theta_tag=0.5 promote depth (cap at D_max=3) for top-recruited W entries.
  (c) **SWR-gated selective replay on expanding intervals:** after each ingest cycle (j>0), replay TOP-TAG events from PRIOR TASKS at lags {1, 2, 4, 8, ...}. Budget = REPLAY_BUDGET_PER_INGEST * M_per_task (same compute as C1 1:1 baseline -- mechanism-fair).
  (d) **Slow noise-floor decay:** each cycle, entries with d>0 transition d -> d-1 with rate THETA_DECAY_RATE=0.02.

Forward-only Hebbian-compatible. Substrate-only-decode preserved (zero LLM forward calls). Composes with U1 refuse-gate (tag uses margin); orthogonal to V_C x N_DIM and to kWTA (brain-drill #1).

## Arms (Fix #16 discriminator; 2 arms)

- **C1_BASELINE**: classical 1:1 uniform replay (the c1 mechanism; the bar).
- **CASCADE_STC_SWR**: full two-mechanism nested-timescale primitive (cascade + STC + SWR).

C2-vs-C1 at k=6 is the load-bearing mechanism comparison. NO_REPLAY arm dropped per Director post-mortem (forgetting-floor well-established from c1; redundant).

## Fixed config

N_DIM=2048 (vs v1's 4096; Option A); J_tasks=12; alpha=3.0 (discriminating regime; past c1's cliff); M_per_task = round(alpha * N_DIM / J) = 512; SEEDS=[7,17,23]; D_max=3; theta_tag=0.5; tag_beta=4.0; theta_decay_rate=0.02; replay_budget=1:1 per ingest cycle (same compute as C1 baseline); K_EVALS=[3, 6, 12]; NOISE_FRAC=0.10; N_RECALL_STEPS=3.

## Pre-registered HARD bands (per Director post-mortem; k=6 is the load-bearing comparison)

**HARD_PASS (chain-grade, ALL of):**
- CASCADE_STC_SWR retention at k=6 >= 0.85
- (CASCADE_STC_SWR retention - C1_BASELINE retention) at k=6 >= 0.20 (mechanism-discriminating in overload regime past c1's cliff)
- cv_C2 at k=6 <= 0.06 across 3 seeds (mechanism reproducible)
- substrate-only-decode: zero LLM forward calls

**HARD_FAIL (mechanism wrong):**
- CASCADE_STC_SWR retention at k=6 < 0.40, OR
- CASCADE_STC_SWR retention <= C1_BASELINE retention at k=6 (cascade-STC-SWR adds nothing over uniform), OR
- substrate-only-decode gate violated (n_llm > 0)

**MIDDLE_BAND:** between (partial mechanism; routes to single-mechanism ablations CASCADE_ONLY / STC_ONLY / SWR_ONLY in a follow-up cell).

## Discriminating-regime requirement (C5)

alpha=3.0 is well above c1's tested cliff (alpha=0.5 codebook-NN masked collapse). At this regime the two arms must DIFFERENTIATE:
- C1_BASELINE should collapse (uniform 1:1 replay is the c1 mechanism that hit cliff in overload).
- CASCADE_STC_SWR should survive (mechanism is mechanism-discriminating).

If both arms collapse together: alpha too aggressive (capacity ceiling); route to secondary cell at alpha=2.0. If both arms succeed together: alpha too gentle (cliff not engaged); route to higher alpha.

## Version markers (anti-r1b mean-reproduction-failure; baked into metrics.json)

- anchor_name = "c2_cascade_stc_swr_continual_v2"
- config_version (includes N_DIM=2048, arms list, all mechanism constants)
- consolidation_arm (per-unit)
- D_max (=3)
- theta_tag (=0.5)
- tag_function (="sigmoid_margin")
- replay_schedule_mode_C2 (="expanding")
- replay_schedule_mode_C1 (="uniform_1to1")
- alpha (=3.0)
- corpus_provenance (="synthetic_bipolar_keys")
- v2_change_set = "N_DIM=4096->2048 + drop NO_REPLAY arm (Director Option A+C)"

## Compute budget

- Per-arm per-seed: ~10-12 min on remote_cpu (N_DIM=2048, J=12, M=512; cascade adds ~1.2x overhead).
- 2 arms x 3 seeds = 6 runs; total ~60-75 min wall (vs v1's ~7.5hr at N=4096 with 3 arms).
- Smoke wall estimate: ~2-3 min (N_DIM=512, J=4, alpha=1.0, 1 seed, 2 arms).
- timeout=7200s (2hr) gives ~2x slack over ~60-75min estimate.

## Self-tests (asserted at import time)

1. cascade depth update: tag>theta promotes entries; tag<theta does not.
2. plasticity p_d at d=3 equals 0.125 (1/8).
3. expanding-interval schedule at j=8 returns lags [7, 6, 4, 0].
4. _LLM_CALL_COUNTER remains 0 throughout.

## Composition path

If c2-v2 HARD_PASSes:
- Atomize SAME CYCLE per results-to-application cadence (USER 2026-06-22).
- Update hdlab/cascade_w.py primitive.
- Route to c3_cascade_real_KG_continual_v1 (real KG ingest on FB15k-237 or ConceptNet).
- Compose with brain-drill #1 kWTA-VQ at write/read.

If c2-v2 HARD_FAILs:
- Route to research for single-mechanism ablation (CASCADE_ONLY / STC_ONLY / SWR_ONLY arms).
- Consider whether substrate continual-ingest fundamentally diverges from biology.

If c2-v2 MIDDLE_BAND:
- Phase 2 cell with secondary D_max sweep + tag-function ablation.

## ASCII-only / commit-before-dispatch / per-seed-resumable / smoke gate first.
