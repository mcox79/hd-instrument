# exp_dev hand-off -- research: K-Fact Combination Algebraic Analysis

Filed-by: research sub-agent
Date: 2026-06-05
Trigger: notes/research_drill_substrate_evidence_integration_K_fact_combination_2x_2026-06-05.md

Per [[feedback-no-experiment-design-in-prompts]]: this file names anchor candidates and
WHY they matter. exp_dev designs the actual experiment (sweep grid, thresholds, queue
choice, timeout). No numerical grids or threshold formulas are pre-committed here.

---

## Pause state block

This handoff was written while experiments may be running. exp_dev should check
data/orchestrator_paused.flag before dispatching any anchors.

---

## Anchor candidates (rank-ordered by urgency + cheapness)

### Anchor 1 (TIER: CHEAP CPU SMOKE -- highest priority)
WHY NOW: The beta* closed-form formula (beta* = sqrt(N/K) * (1 + CoV_cos)^{-1}) is a
novel synthesis (P_deflated=0.30) that requires the cheapest possible validation.
It is directly computable from retrieved cosines and requires no new infrastructure.
If it holds, the substrate-LLM hybrid gets an automatic, tuning-free combination rule.

ANCHOR POINTER: Compare Rule 8 accuracy at beta=beta* vs beta=grid-search-optimal
across K=3,5,7 at N=1024, M=100. Measure whether beta* matches grid-search within 10%.

SUBSTRATE-PRODUCT READING: If PASS -- ship beta* as the default combination rule.
If FAIL -- the formula needs revision; fall back to fixed beta=sqrt(N/K) or grid search.

TIER HINT: CPU smoke. N=1024, K <= 7, 1000 trials per condition. < 5 min wall.

---

### Anchor 2 (TIER: CPU PROBE -- K transition boundary)
WHY NOW: Prediction 2 says VSA superposition cleanup (Rule 6) accuracy drops at
K ~ sqrt(N)/2 = 16 for N=1024. This is the BINDING architectural constraint for how
many facts can be combined in a single evidence vector. Validating it gates the
K-gate design decision (K_thresh = min(10, sqrt(N)/2)).

ANCHOR POINTER: Sweep K from 5 to 25 for Rule 6 (superposition + cleanup) at N=1024,
M=100. Measure accuracy at each K. Look for the transition from > 95% to < 80%.

SUBSTRATE-PRODUCT READING: If transition at K ~ 14-18 (HARD-PASS range) -- ship
K_thresh = sqrt(N)/2 as the architectural K gate. If transition much later (K > 20,
HARD-FAIL) -- Kanerva bound is loose for this substrate; recalibrate T2.

TIER HINT: CPU probe. Single sweep K=5..25, 500 trials per K value. 10-15 min wall.

---

### Anchor 3 (TIER: CPU VALIDATION -- Rule 8 vs Rule 1 on conflicting facts)
WHY NOW: The main claim is Rule 8 > Rule 1 by >= 5pp on conflicting-fact scenarios
at K=5. This is Prediction 1 (P_deflated=0.48). Validating this gates whether Rule 8
is actually the default or whether Rule 1 is sufficient.

ANCHOR POINTER: N=1024, M=100, K=5. Two conditions: (A) consistent facts (all K pointing
to correct answer), (B) conflicting facts (50% pointing to incorrect). Compare Rule 1,
Rule 8 (beta*), Rule 8 (beta=0.5), Rule 6, Rule 3. Measure accuracy per condition.

SUBSTRATE-PRODUCT READING: If Rule 8(beta*) >= Rule 1 + 5pp on Condition B (HARD-PASS)
-- deploy Rule 8 as default. If Rule 1 ties or beats Rule 8 (HARD-FAIL) -- combination
rule choice is less important; focus on upstream retrieval quality improvement instead.

TIER HINT: CPU probe. 2 conditions * 5 rules * 1000 trials = 10000 trials total.
20-30 min wall. Can run after Anchor 1 if Anchor 1 confirms beta*.

---

### Anchor 4 (TIER: CPU VALIDATION -- resonator non-determinism)
WHY NOW: The structural cert-hard-fail claim for resonator networks depends on
non-deterministic convergence under finite precision. Prediction 3 says >= 2% disagreement
between GPU and CPU implementations for N=1024, F=3 factors. If this is validated,
the cert-hard-fail is confirmed experimentally (not just structurally).

ANCHOR POINTER: Run resonator factorization N=1024, F=3, K=5 (5 factors per query)
on CPU float32 vs CPU float64. Compare convergence endpoints (final factor assignments).
Measure fraction of trials with disagreement.

SUBSTRATE-PRODUCT READING: If >= 2% disagreement (HARD-PASS) -- resonator is confirmed
cert-incompatible; BANNED label stands. If < 0.1% disagreement (HARD-FAIL) -- the
cert concern is theoretical but practical impact is low; may revisit cert policy.

TIER HINT: CPU probe. N=1024, F=3, 1000 trials, two float precision runs. 15-20 min wall.

---

## Context pointers

Research note:
  d:/AI/hd-instrument/notes/research_drill_substrate_evidence_integration_K_fact_combination_2x_2026-06-05.md

Prior adjacent research notes:
  d:/AI/hd-instrument/notes/research_drill_iterated_retrieval_depth_scaling_hierarchical_2x_2026-06-04.md
  d:/AI/hd-instrument/notes/research_drill_substrate_controller_hybrid_architecture_2x_2026-06-05.md

Substrate implementation reference:
  d:/AI/hd-instrument/hdlab/ (substrate codebase)

---

## Contract

exp_dev designs the experiment (sweep grid, thresholds, queue choice, timeout formula,
anchor name with _n suffix). This file provides WHY + ANCHOR POINTER + TIER HINT only.

## Autonomy declaration

exp_dev has full autonomy to:
  - Set sweep ranges and step sizes within tier constraints
  - Choose between overnight_queue and remote_cpu_queue based on wall-time estimate
  - Set HARD-PASS / HARD-FAIL / middle-band thresholds per envelope-fail-bands feedback
  - Batch Anchors 1-3 into a single experiment script if feasible
  - Skip Anchor 4 if queue depth is already sufficient from other handoffs
