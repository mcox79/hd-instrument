# exp_dev hand-off -- research: active-intervention query-selection grounding

Filed-by: research sub-agent
Date: 2026-07-09
Trigger: notes/research_active_intervention_query_selection_grounding_2026-07-09.md
Urgency: HIGH -- cheapest of four mechanisms tried in this arc (single changed sampling line in an
already-landed FULL cell), directly redirected-to by the just-landed
`HARD_FAIL_PASSIVE_EXOG_INSUFFICIENT_REDIRECT_ACTIVE_INTERVENTION` verdict.

---

## Pause state

Experiment below is PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ranked anchor candidates only. Experiment design details (exact
acquisition-function implementation, seed grid, threshold tuning) are to be authored by exp_dev from the
research note's Falsifiable Predictions section. Do NOT treat the description below as an implementation
spec.

---

## Anchor candidates (rank-ordered)

### Anchor 0 (do FIRST, near-zero cost, not really a new experiment): confirm per-index residual is
cheaply computable from the existing `ExogAnchor` forward pass

Anchor pointer: Research note "Cheap decisive test" Step 0.

Substrate-product reading: `experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py`'s `_recon_cos`
(line 346) already computes an aggregate reconstruction-cosine over a probe set; confirm whether a
per-INDEX (not just aggregate) residual is already extractable from that function's internals without new
code, before writing an acquisition-function helper from scratch.

Tier hint: read-only, ~10 minutes.

### Anchor 1: `B2_ACT` -- replace uniform-random exog-target sampling with own-uncertainty-driven
(BALD-style) selection

Anchor pointer: Research note S2 (concrete design) + "Cheap decisive test" + Falsifiable Prediction row 1.

Substrate-product reading: the landed `B1_EXOG` arm samples its shared reconstruction target via uniform
random choice within each branch's own disjoint fold
(`experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py:499`,
`a_idx = rng.choice(pool, size=min(exog_bs, pool.shape[0]), replace=False)`). This is the exact mechanism
research identified as the likely reason `B1_EXOG` failed to decorrelate (`corr=0.382`, essentially
unmoved from `B1_crossfit`'s `0.393`): both branches chase the SAME task-objective structure even though
they sample disjoint index pools. `B2_ACT` replaces that one line with a residual/uncertainty-ranked biased
sample (reusing `hdlab/predictive_coding.py` `residual_magnitude` and/or the file's own `_recon_cos`
machinery) so each branch's already-diverged internal state drives it toward DIFFERENT candidate indices --
instantiating the active-inference/BALD "chosen queries extract more information" result and the
interventional-causal-discovery result that distinct interventions carry independent, non-redundant
constraints a shared passive schedule cannot.

Tier hint: CPU-only, reuses 100% of existing harness/instrumentation/losses; new code is limited to the
acquisition-function helper and the one changed sampling line. Research note estimates this as the
CHEAPEST of the four mechanisms tried in this arc (DG transform, B1 cross-fit, B1+EXOG shared target,
B2_ACT).

Why-now: directly redirected-to by the just-landed `HARD_FAIL_PASSIVE_EXOG_INSUFFICIENT_REDIRECT_ACTIVE_
INTERVENTION` verdict (`data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json`); the research note's
own literature synthesis converges on exactly this mechanism (self-chosen, per-agent-distinct query
selection) as the load-bearing ingredient across all four scanned literatures.

Pre-reg bands (full detail in research note Falsifiable Predictions table; SAME bands already encoded in
this cell's own `config_version` string, so no new threshold invention needed):
  HARD-PASS: `corr(failmask) <= 0.20` AND `grounding >= 0.50` AND `perturb_ratio >= 2.0`.
  HARD-FAIL: `corr(failmask) >= 0.35` (matches this cell's own `HFa>=0.35` bar -- no material improvement
    over `B1_EXOG`'s already-measured `0.382`).
  MIDDLE_BAND: `corr(failmask)` in `(0.20, 0.35)` OR grounding/perturbation conditions only partially met.

### Anchor 2 (fallback, only if Anchor 1's naive version plateaus): explicit cross-branch
anti-correlation term

Anchor pointer: Research note S2 "Fallback arm" + Falsifiable Prediction row 2.

Substrate-product reading: per Millidge, Tschantz & Buckley's (2021) active-inference critique and the
diversity-driven-RL literature (both cited in the research note), cross-agent decorrelation is usually an
EXPLICITLY ENGINEERED property, not a free emergent consequence of independent per-agent choice. If
Anchor 1's naive version (own-uncertainty ranking only, no cross-branch coordination) plateaus near the
already-seen `~0.38` band, add a cheap periodic exchange of each branch's top-K candidate indices and
deprioritize indices the OTHER branch also currently favors -- stays within the existing disjoint-fold,
no-shared-gradient discipline (index lists only, not gradients or representations).

Tier hint: small incremental addition to Anchor 1's code; do not build until Anchor 1's naive result is in
hand (per the research note's own Step 0/Step 1 sequencing -- don't pre-build the fallback speculatively).

Why-now: LOWER priority than Anchor 1 -- contingent on Anchor 1's naive result. Research note sets
P(naive sufficient)=0.35, i.e. leans toward needing this fallback, but the cheap naive test should run
first regardless.

Pre-reg bands: same HARD-PASS/HARD-FAIL bands as Anchor 1 (row 2 of the Falsifiable Predictions table
frames this as "does naive alone suffice, or is the fallback needed").

---

## Important pre-registered contingency (read before interpreting ANY result from this arm)

If `B2_ACT` (with or without the Anchor 2 fallback) ALSO lands within `~0.35-0.42` of `corr(failmask)`, this
would be the FOURTH consecutive mechanism (after DG `0.377`, B1 `0.393`, B1+EXOG `0.382`) clustering at
essentially the same value despite being theoretically distinct interventions. Per the research note's S3
and Falsifiable Prediction row 3, this is pre-registered as a signal to redirect toward a shared
discrete-channel/game-architecture ceiling (specifically the `MessageChannel`/candidate-set structure common
to ALL four arms), NOT to attempt a fifth upstream-data/objective mechanism. Do not treat a 4th plateau as
"just another negative to route back to research" -- route it to a targeted architecture probe per the
research note's own Falsifiable Prediction row 3 framing.

---

## Context pointers (file paths, not summaries)

- Research note (this drill):
  d:/AI/hd-instrument/notes/research_active_intervention_query_selection_grounding_2026-07-09.md
- Cell to extend: experiments/exp_selfplay_b1_exog_predictive_anchor_v1.py
  (function `train_arm()`, line 499 is the exact change point; `_recon_cos` line 346,
  `_anchor_loss`/`ExogAnchor` lines 320-346, `causal_perturbation_ratio` line 378, `ARM_NAMES` line 232)
- Existing precision-weighting primitives to reuse: hdlab/predictive_coding.py
  (`residual_magnitude`, `proportional_gate`)
- Landed metrics this hand-off is triggered by (read directly, not summarized elsewhere):
  data/exp_selfplay_b1_exog_predictive_anchor_v1/metrics.json
- Prior arc notes (context, not to be re-derived):
  notes/research_exogenous_referent_grounding_predictive_coding_2026-07-09.md,
  notes/research_selfplay_upstream_blindspot_brain_fix_2026-07-09.md,
  notes/research_selfplay_shared_estimator_independence_speaker_listener_2026-07-09.md,
  notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md (Prediction C /
  `causal_perturbation_ratio` reused unchanged here)

---

## Contract section

This handoff proposes one near-zero-cost verification step (Anchor 0), one cheap, directly-buildable
primary anchor (Anchor 1, `B2_ACT`), and one contingent fallback (Anchor 2, only if Anchor 1's naive
version plateaus). Exp_dev authors the exact acquisition-function implementation, seed grid, and threshold
tuning within the pre-registered bands above. Do NOT treat the anchor descriptions as implementation specs.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchor(s) to pick up first (Anchor 0 -> Anchor 1 recommended order)
- Choosing the exact acquisition-function implementation (residual-ranked softmax sampling, top-K biased
  sampling, or any other own-uncertainty-driven scheme) within the pre-registered HARD-PASS/HARD-FAIL bands
- Deciding whether to build Anchor 2 speculatively alongside Anchor 1, or strictly sequentially per the
  research note's Step 0/Step 1 discipline (sequential is recommended but not mandatory)
- Choosing local CPU vs remote_cpu_queue routing per the SMOKE-only-local rule

Exp_dev is NOT autonomous in:
- Declaring this arc's decorrelation problem solved or closed based on a `B2_ACT` HARD-PASS alone -- the
  research note explicitly bounds any pass as closing a specific structural blind spot, not achieving
  embodied/enactivist grounding (see research note S3)
- Treating a 4th consecutive `~0.38` plateau as a reason to attempt a 5th upstream-data mechanism instead of
  routing to the pre-registered architecture-probe contingency above
- Merging the acquisition-function change into the existing `_anchor_loss`/`ExogAnchor` reconstruction
  objective itself -- this hand-off proposes changing WHICH indices are sampled, not the loss/objective
  structure, which should remain unchanged from `B1_EXOG` for a clean, apples-to-apples comparison
