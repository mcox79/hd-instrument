# exp_dev hand-off -- research: phase4 v2 anchored regression rescue (v2.5 confidence-gated)

Filed-by: research (Opus 2x DEEP drill)
Trigger: research note d:/AI/hd-instrument/notes/research_drill_phase4_v2_anchored_regression_2x_2026-06-11.md
Pause state: respect data/orchestrator_paused.flag; this hand-off is queue-triggering and pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off names anchors and points at substrate-product readings. It does NOT prescribe internal cell mechanics; exp_dev is the autonomous designer.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (Tier-1, highest priority) -- v2.5 confidence-gated rescue, both gating directions

- **Pointer**: rescue of Phase-4 v2 (math word-problem heuristic anchoring) using cleanup-margin as the gating signal.
- **Substrate-product reading**: validates the architectural pattern that heuristic overlays in substrate pipelines MUST be confidence-gated, with cleanup-margin as the native gating function. If PASS, this unlocks the general "MoE-style heuristic routing" capability across the substrate -- not just for Phase-4 math but for all schema-overlay points.
- **Tier hint**: existence-proof tier (one composition-matched cohort; multi-seed if HP boundary hit).
- **Why-now**: same problem set as v1/v2 head-to-head, same CPU laptop runner, no new training -- 2-hour decisive cycle. Five mature literatures converge on the gating-is-missing diagnosis, so the design space is well-bounded.

### Anchor 2 (Tier-2, dependent on Anchor 1) -- conformal calibration of gating threshold

- **Pointer**: if Anchor 1 PASS at a hand-picked best-tau, the production-deployment question is "what tau in production?" Venn-Predictor or RC3P conformal calibration gives distribution-free coverage guarantees on the gating decision.
- **Substrate-product reading**: turns a heuristic threshold into a calibrated guarantee -- product-shippable abstention/routing surface.
- **Tier hint**: small CPU smoke; conformal/calibration field has 33% yield, 6 drills -- adjacent angle.
- **Why-now**: hold pending Anchor 1 verdict.

### Anchor 3 (Tier-2, alternative if Anchor 1 HARD-FAIL) -- heuristic redesign

- **Pointer**: if BOTH gating directions in Anchor 1 fail to recover v1, the heuristic itself is structurally wrong. Candidate redesigns: drop unit-cues for role-binding (use only schema-overlay top-1 retrieval); expand unit-cue dictionary with contextual disambiguation; replace unit-cues with HMM-emission counts (per substrate-classical-NLP 2026-06-11 finding).
- **Substrate-product reading**: closes Phase-4 with a non-anchored architecture; substrate-as-classical-NLP-substrate path validated.
- **Tier hint**: existence-proof tier; CPU runner.
- **Why-now**: hold pending Anchor 1 verdict.

---

## Context pointers (paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_phase4_v2_anchored_regression_2x_2026-06-11.md  (this drill's full synthesis incl. HARD-PASS / HARD-FAIL thresholds)
- d:/AI/hd-instrument/notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md  (Phase 3 routing -- adjacent design)
- d:/AI/hd-instrument/notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md  (Tier-2 schema codebook -- the substrate-side artifact gating is applied to)
- C:/Users/marsh/.claude/projects/d--AI/memory/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md  (HMM forward-backward marginal = classical-substrate cleanup-margin analog)
- C:/Users/marsh/.claude/projects/d--AI/memory/substrate_v32_engineered_wrapper_2026-06-11.md  (wrapper pattern; gating is a wrapper, not a core change)
- d:/AI/hd-instrument/notes/strategy_decisions_2026-06-11.md  (cycle 232 verdict; Phase-4 triple-HF batch context)

---

## Contract section

- Heuristic anchoring overlays MUST be wrapped in a confidence-gated router (cleanup-margin or analog) in any v2.5+ design.
- Calibration set for tau MUST be held out from test cohort; no peeking.
- BOTH gating directions (heuristic-when-low-margin vs heuristic-when-high-margin) must be tested -- literature is split.
- Must report margin distributions on heuristic-helps vs heuristic-hurts subgroups for diagnostic post-mortem regardless of PASS/FAIL.
- Lift threshold: > 2*SE per [[feedback-method-overclaim-lift-validation]].
- Composition-matched smoke before full cohort per [[feedback-smoke-test-methodology]].

## Autonomy declaration

exp_dev decides:
- Which cohort split to use for calibration vs test (a substrate-side detail).
- Whether to run anchor-1 only or anchor-1 + anchor-2 in parallel given runner availability.
- Internal cell mechanics, smoke-vs-full design, multi-seed policy.
- Whether to hold anchor-3 pending anchor-1 verdict (preferred) or pre-queue speculatively.

This hand-off intentionally specifies WHAT to test (gating architecture) and WHY (literature convergence + cap_map narrative correction), not HOW to wire the cells.
