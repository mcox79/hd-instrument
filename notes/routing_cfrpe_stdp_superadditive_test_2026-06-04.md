# Routing -- cf-RPE + STDP superadditive heterogeneous-pairing test

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical test (1 cell + 2 baseline references; CPU)
**Source:** cf-RPE + sparse shared-axis 2x drill landed 2026-06-04 (research_drill_cfrpe_sparse_shared_axis_negative_2x)

---

## Capability question

Does combining cf-RPE (task-supervised axis) + STDP-asymmetric (temporal axis) compose SUPERADDITIVELY at substrate bigram task, validating the heterogeneous-pairing hypothesis from today's shared-axis drill?

Per drill: cf-RPE + Drosophila sparse combined ADDITIVELY (both task-supervised axis; collinear gradients). Predicted heterogeneous pairings (task + temporal) should give superadditive composition. cf-RPE + STDP is the cheapest test of this prediction.

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512`

**Cell C1:** cf-RPE rank-1 substitution + W_total = W_Hebbian + 0.5*W_STDP-asymmetric at bigram V=512 N=512, 5 seeds

Reference baselines (from Bundle A v394):
- cf-RPE alone HP at bigram (Cell A2): gap_cf
- STDP-asymmetric alone MIDDLE at bigram (Cell A4): gap_stdp

**Pre-reg per drill prediction:**

- **HARD-PASS (superadditive):** Cell C1 gap > 0.70 nats AND 4/5 seeds (validates heterogeneous pairing)
- **MIDDLE-BAND (modest improvement):** Cell C1 gap in [max(gap_cf, gap_stdp), 0.70 nats]
- **HARD-FAIL (still additive/sub-additive):** Cell C1 gap <= max(gap_cf, gap_stdp)

Critical: HP threshold of 0.70 nats is the algebraic prediction from drill (orthogonal-axis sqrt-sum bound). MIDDLE means partial superadditivity. HF means shared-axis hypothesis applies more broadly than predicted (task + temporal still share an effective axis at bigram task).

## Resource

Local CPU. Reuses Bundle A scaffolds for cf-RPE + STDP architectures.

## Cost ceiling

$0 CPU. Per-seed wall ~60-90s. Total ~5-10 min for 5 measurements.

## P_deflated (per today's methodology)

**P_algebraic = 0.65**: heterogeneous-pairing hypothesis is algebraically clean (PCGrad orthogonal-gradient sqrt-sum composition); lit anchor in shared-axis drill

**P_implementation:**
- P_convergence = 0.75 (both architectures converge cleanly individually)
- P_budget = 0.85 (N=512 substrate-class; trivial)
- P_no_subsumption = 0.95 (both W-modifying)
- P_task_match = 0.60 (bigram is at substrate's primary validated domain; superadditive gain may be capped by max-task-gap ceiling)
- Joint P_implementation ~ 0.36

**P_joint = 0.65 * 0.36 ~ 0.23 for HP at gap > 0.70 nats**

LOW per-cell P but the test is the LOAD-BEARING empirical validation of today's architectural taxonomy.

## Engineering scope

~1-2h:
- Combined cf-RPE + STDP architecture (reuse Bundle A scaffolds; integrate)
- 5-seed eval at bigram V=512 N=512 (reuse Bundle A eval harness)
- Comparison to baselines (compute gap_cf, gap_stdp from existing Bundle A data; report combined gap vs both)

Reuses Bundle A scaffolds substantially.

## Strategic outcome

### If HP (gap > 0.70 nats, superadditive)

- Heterogeneous-pairing hypothesis EMPIRICALLY VALIDATED
- Architectural taxonomy (task + temporal + capacity + compositional axes) confirmed as design principle
- Opens path to Bundle F-class combined architecture (task + temporal + capacity) for trigram+ tasks
- Cap_map: founding for "substrate heterogeneous architectural pairings compose superadditively"

### If MIDDLE (partial superadditivity)

- Pairing provides some gain but not full superadditive
- Identifies that task + temporal are NEAR-orthogonal at bigram (not fully orthogonal)
- Inform: 3-axis pairings (task + temporal + capacity) may achieve full superadditivity

### If HF (still additive/sub-additive)

- Heterogeneous-pairing hypothesis refuted at substrate-class scale
- Architectural taxonomy needs revision (axes share effective gradient direction more broadly than predicted)
- Substrate's combined-architecture gain may be fundamentally capped near single-architecture max
- Major recalibration of Bundle F predictions

---

## What this is (plain language)

Bundle A combined cf-RPE + Drosophila sparse landed as ADDITIVE (both target task-supervised axis; combined gain ~ max-of-two-alone).

Today's drill identified the algebraic taxonomy: cf-RPE and Drosophila sparse are both task-supervised; their combined update lives in same W subspace.

Predicted: HETEROGENEOUS pairings (different gain axes) compose superadditively. Cheapest test: cf-RPE (task) + STDP (temporal). If superadditive gain > 0.70 nats: heterogeneous-pairing principle validated empirically.

This is the LOAD-BEARING empirical test of today's architectural-composition theory.

---

## Strategic context

Connects to:
1. cf-RPE + sparse shared-axis 2x drill (landed; predicted this empirical test)
2. Bundle A combined results (cf-RPE + sparse MIDDLE; additive)
3. Bundle F combined-everything (pending; this test validates the underlying composition principle)
4. Bundle E results (position-binding + STDP HP at trigram; temporal + temporal pairing; SAME-axis combination empirical anchor for comparison)

If C1 HP: Bundle F's combined-everything prediction strengthens (multi-axis composition validated).
If C1 HF: Bundle F's combined-everything prediction weakens (combinations may be capped near single-architecture max).

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: single load-bearing cell + 2 reference baselines from existing data
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchor uses `_n512_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=5

---

**END.**

**Exp-Dev:** small ~5-10 min CPU test once engineered (~1-2h). Verdict drives architectural-composition theory validation + Bundle F prediction refinement.
