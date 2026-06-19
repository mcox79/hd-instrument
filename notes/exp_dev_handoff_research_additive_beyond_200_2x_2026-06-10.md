# exp_dev hand-off -- research: additive-beyond-200-2x
Filed-by: research sub-agent
Date: 2026-06-10
Trigger: notes/research_drill_additive_beyond_200_2x_2026-06-10.md
Per [[feedback-no-experiment-design-in-prompts]]: no inline experiment design below.
Exp-dev reads context pointers and designs the anchors autonomously.

---

## Pause state
Experiments are running. This hand-off is auto-discoverable on next exp_dev emergency-refill
cycle (scan notes/exp_dev_handoff_*.md sorted by mtime).

---

## Why this hand-off is actionable now

The 2x research drill on additive-only certification beyond 200 edits identifies a SPECIFIC,
testable root cause for the MIDDLE_BAND finding and THREE ranked architecture fixes. The cheapest
fix (KEY-ROTATION, Path B) requires approximately 50 lines of Python, zero new hyperparameters,
and can run on laptop CPU in under 1 hour. The other paths are incremental extensions. All four
paths are pre-registered with HARD-PASS and HARD-FAIL thresholds in the research note.

---

## Anchor candidates (rank-ordered)

### Anchor 1: KEY-ROTATION certification at K=500 and K=1000 [TIER-1, CPU, URGENT]

Anchor pointer: substrate_continual_key_rotation_certification_v1

Substrate-product reading:
  The MIDDLE_BAND at 200-250 reconsolidation edits is caused by partial-reconsolidation residual
  accumulation, not by the M/N capacity cliff. KEY-ROTATION (retire old key, issue fresh random
  key for updated concept, explicit erase of old binding) eliminates residual accumulation by
  algebraic construction. If HARD-PASS at K=1000 is confirmed, the additive-only architecture
  is certifiable to 1000+ edits without N scaling -- a direct product differentiator vs ROME/MEMIT.

Tier hint: TIER-1 (resolves an active MIDDLE_BAND certification gap directly)
Why now: This is the cheapest test (laptop CPU, numpy, < 1 hour). Zero new hyperparameters.
  Resolves the D2.3 RECONSOLIDATION-EDIT gap from the continual suite 4/4 battery.

Pre-registered bands from research note:
  HARD-PASS: recall@1 >= 0.90 at K=1000 reconsolidation edits
  MIDDLE_BAND: recall@1 in [0.80, 0.90) at K=1000
  HARD-FAIL: recall@1 < 0.80 at K=500 (erase-write leaves residual; N too small)

### Anchor 2: RECALL-CURVE shape discrimination (NAIVE condition) [TIER-2, CPU]

Anchor pointer: substrate_continual_recall_curve_kw_shape_v1

Substrate-product reading:
  The NAIVE baseline recall curve (without KEY-ROTATION) measured at K = 50, 100, 200, 250, 400,
  500, 1000 will discriminate between three degradation models: sharp cliff (catastrophic),
  KWW stretched-exponential (marginal rigidity), and linear decay (pure noise accumulation).
  The shape determines what engineering path is needed at production scale.

Tier hint: TIER-2 (informs long-horizon deployment planning; does not block current certification)
Why now: Runs alongside Anchor 1 at zero additional cost (same test harness, different condition).

Pre-registered bands:
  HARD-PASS: recall curve fits KWW stretched-exponential (beta < 1) -- marginal rigidity, fixable
  MIDDLE_BAND: recall curve shows linear decay -- pure noise accumulation, KEY-ROTATION sufficient
  HARD-FAIL: recall curve shows sharp cliff at K < 200 -- N=4096 is too small for current edit load

### Anchor 3: CRYSTALLIZED-CORE core-stability at K=500 [TIER-2, CPU]

Anchor pointer: substrate_continual_crystallized_core_v1

Substrate-product reading:
  CRYSTALLIZED-CORE (frozen-key registry + mutable periphery with periodic consolidation) provides
  algebraically guaranteed core recall regardless of edit count. If core-recall >= 0.95 at K=500
  with a 50/50 core/periphery split, the architecture is ready for production-scale evaluation at
  K=5000.

Tier hint: TIER-2 (production readiness gate for long-horizon GDPR-correct operation)
Why now: Requires one additional implementation step beyond KEY-ROTATION (the core/periphery split
  and the theta_sim gate). Best run after Anchor 1 confirms KEY-ROTATION works.

Pre-registered bands:
  HARD-PASS: core-recall@1 >= 0.95 at K=500 total edits
  MIDDLE_BAND: core-recall@1 in [0.90, 0.95) at K=500
  HARD-FAIL: core-recall@1 < 0.90 at K=500 (core leaks; theta_sim threshold needs tightening)

### Anchor 4: HOMEOSTATIC-RENORM stability gate [TIER-3, CPU, low priority]

Anchor pointer: substrate_continual_homeostatic_renorm_v1

Substrate-product reading:
  Periodic multiplicative W rescaling (B=50 writes) prevents norm drift and maintains retrieval
  SNR. Needed for very long horizons (K >> 1000) even with KEY-ROTATION. Requires verifying that
  renormalization does not degrade recall on already-stored items -- a simple smoke test before
  enabling in production.

Tier hint: TIER-3 (supports K >> 1000 but Anchors 1-3 must pass first)
Why now: Lower priority. Run only if Anchor 1 HARD-PASS is confirmed and K=5000 target is set.

Pre-registered bands:
  HARD-PASS: renormalization does not degrade any stored-item recall below threshold
  HARD-FAIL: renormalization immediately degrades recall on stored items (W_target_norm miscalibrated)

---

## Context pointers

Research note (full derivations, formulas, literature): 
  d:/AI/hd-instrument/notes/research_drill_additive_beyond_200_2x_2026-06-10.md

Prior self-modification 5x note (broader mechanism context):
  d:/AI/hd-instrument/notes/research_drill_self_modification_5x_2026-06-10.md

Continual scale 2x note (M/N scaling context, 10K push paths):
  d:/AI/hd-instrument/notes/research_drill_continual_scale_2x_2026-06-10.md

Continual suite complete hand-off (4/4 HARD_PASS battery, D2.3 gap identification):
  d:/AI/hd-instrument/notes/exp_dev_to_research_CONTINUAL_SUITE_COMPLETE_2026-06-10.md

---

## Contract section

Research delivers: mechanism analysis, architecture paths, pre-registered bands.
Exp-dev owns: anchor design, implementation, dispatch, result reporting.
Research does NOT design anchor code. Exp-dev does NOT interpret verdicts strategically.

---

## Autonomy declaration

Exp-dev may dispatch Anchors 1 and 2 immediately on next cycle without additional orchestrator
authorization -- they are CPU-only, < 1 hour, and directly address a pre-existing MIDDLE_BAND
certification gap (D2.3 RECONSOLIDATION-EDIT) that was already authorized as part of the
continual learning sprint.

Anchors 3 and 4 should be queued after Anchor 1 verdict is available.
