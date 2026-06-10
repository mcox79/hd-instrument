# exp_dev hand-off -- research: substrate confidence binary negative 2x

Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_substrate_confidence_binary_negative_2x_2026-06-10.md
Urgency: HIGH -- LAP4-3 HARD_FAIL + ECE=0.325 closed the raw-margin per-sample
         calibration line; research identifies 5 rescue paths with ranked P_deflated

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the
descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: trained_confidence_head_v1 (cheapest decisive test)

Anchor pointer: Research note Section 6.1 (TRAINED-CONFIDENCE-HEAD)
Substrate-product reading: Linear probe trained on cleanup residual delta_z = z - xi_winner
to predict per-sample correctness. Pre-reg: r >= 0.40 HARD-PASS, r < 0.20 HARD-FAIL.
If HARD-PASS, continuous per-sample confidence is achievable and routes to customer
claim revision (graded confidence for RAG re-ranking use case).
If HARD-FAIL, confirms binary is the structural ceiling; close per-sample confidence line.
Tier hint: CPU laptop, <1 hr. Uses existing calibration data from PP-277/PP-281 runs.
Why-now: Cheapest discriminating test between "binary is structural" and "trained signal
exists." Gates all other confidence-rescue anchors. Run before any ensemble work.

Pre-reg bands:
  HARD-PASS: Pearson r >= 0.40, AUC >= 0.70 on held-out 20% split
  MIDDLE-BAND: r = 0.25-0.40 (sufficient for routing; customer claim revision)
  HARD-FAIL: r < 0.20 (confirms delta_z carries no per-sample signal)

### Anchor 2: multi_feature_confidence_v1 (parallel cheapest test)

Anchor pointer: Research note Section 6.2 (MULTI-FEATURE-ENSEMBLE)
Substrate-product reading: Logistic regression on [margin, top5_density, top5_variance]
features from single cleanup pass. Tests whether geometric multi-feature signal exceeds
margin-only (r=0.10). Pre-reg: r >= 0.30 HARD-PASS.
Tier hint: CPU laptop, <30 min. Can run in parallel with Anchor 1.
Why-now: If Anchor 1 requires training data collection, Anchor 2 runs on existing
exports immediately. Joint result disambiguates: if both fail, confirms LAP4-3 finding
is structural, not fixable by feature engineering.

Pre-reg bands:
  HARD-PASS: r >= 0.30 AND improvement >= 0.05 over margin-only r=0.10
  MIDDLE-BAND: r = 0.20-0.30 (partial improvement; insufficient for product claim)
  HARD-FAIL: r < 0.20 OR no improvement over margin-only

### Anchor 3: generative_sampling_confidence_v1

Anchor pointer: Research note Section 6.4 (GENERATIVE-SAMPLING) + Section 3.4
Substrate-product reading: Replace hard sign() with M=10 stochastic Bernoulli samples
at beta=2.0. Confidence = fraction of passes agreeing on winner. Requires temperature
parameter added to cleanup code. Tests: (a) does stochastic sampling give per-sample
r >> 0.10? (b) does it hurt retrieval accuracy?
Tier hint: CPU laptop, 1-2 hr.
Why-now: If Anchors 1+2 both fail (confirming binary is structural), generative sampling
is the next hypothesis (stochastic dynamics recover continuous signal). But run only
AFTER Anchor 1+2 results are in.

Pre-reg bands:
  HARD-PASS: r >= 0.38 AND retrieval accuracy degradation < 1%
  MIDDLE-BAND: r = 0.25-0.38 OR accuracy drops 1-3%
  HARD-FAIL: r < 0.20 OR accuracy drops > 3%

### Anchor 4: population_confidence_k50_v1

Anchor pointer: Research note Section 6.3 (POPULATION-CONFIDENCE) + Section 2.5
Substrate-product reading: K=50 independent substrate instances with independent
random codebook seeds. Confidence = fraction agreeing on winner. If per-sample r >= 0.45,
ensemble confidence is the path; if r < 0.25, codebook correlation prevents independence.
Tier hint: CPU laptop, 2-4 hr. Only run if Anchors 1-3 all fail or produce MIDDLE-BAND.
Why-now: Most expensive rescue path; run last in sequence. If this also fails, confirms
binary is the hard structural ceiling for this substrate architecture.

Pre-reg bands:
  HARD-PASS: r >= 0.45, ECE <= 0.05 (independence assumption holds)
  MIDDLE-BAND: r = 0.30-0.45 (partial benefit; batch-application viable)
  HARD-FAIL: r < 0.25 (codebook correlation kills ensemble benefit)

### Anchor 5: active_inference_convergence_confidence_v1

Anchor pointer: Research note Section 6.5 (ACTIVE-INFERENCE-CONFIDENCE) + Section 3.5
Substrate-product reading: Record iteration count t* to convergence in iterative cleanup.
Confidence = T - t*. If correlated with accuracy, this is a zero-cost confidence signal
already available from PP-272 style active inference runs.
Tier hint: CPU laptop, <30 min. Nearly free to add instrumentation to existing loops.
Why-now: Cheapest architectural augmentation. Most likely to fail (theory predicts
r ~ 0.15-0.25 in retrieval phase), but worth a single run to confirm or rule out.

Pre-reg bands:
  HARD-PASS: r >= 0.25 (interpretable; low-confidence queries have higher mean t*)
  MIDDLE-BAND: r = 0.15-0.25
  HARD-FAIL: r < 0.15 (all queries converge in 1-2 steps; no signal)

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_substrate_confidence_binary_negative_2x_2026-06-10.md
- Prior conformal coverage drill: d:/AI/hd-instrument/notes/research_drill_negative_conformal_coverage_2x_2026-06-08.md
- Prior exp handoff (conformal): d:/AI/hd-instrument/notes/exp_dev_handoff_research_conformal_coverage_2x_2026-06-08.md
- Prior modern Hopfield drill: d:/AI/hd-instrument/notes/research_drill_field_modern_hopfield_5x_2026-06-07.md
- WAVE-4 LAP4-3 HARD_FAIL and PP-281 binary AUC=0.998 results: check data/exp_LAP4-3/ and data/exp_PP-281/ for metrics.json

---

## Contract

exp_dev is authorized to:
- Run Anchors 1 and 2 in parallel immediately (CPU only, <1 hr each, cheap).
- Run Anchor 5 in parallel with Anchors 1-2 (instrumentation only, nearly free).
- Run Anchor 3 after Anchors 1+2 results are in, if both are MIDDLE-BAND or below.
- Run Anchor 4 only if Anchors 1-3 are all MIDDLE-BAND or HARD-FAIL.

exp_dev is NOT authorized to:
- Redesign the cleanup architecture (adding temperature parameter requires orchestrator sign-off on substrate API change).
- Run cloud GPU for any of these anchors (all are CPU-viable).
- Claim continuous confidence is achievable until at least one anchor achieves HARD-PASS.

## Autonomy declaration

exp_dev owns: anchor sequencing, hyperparameter choices within the named anchors,
script implementation, metrics.json format, queue routing.
exp_dev does NOT own: verdict interpretation, cap_map updates, customer claim revision.
Verdict interpretation is Orchestrator/verdict_handler scope.
