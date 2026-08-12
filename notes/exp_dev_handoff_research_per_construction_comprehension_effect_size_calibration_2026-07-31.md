# exp_dev hand-off — research: per-construction comprehension effect-size calibration

**Filed-by:** research (direct lit-scan, no child agents), 2026-07-31.
**Trigger:** `notes/research_per_construction_comprehension_effect_size_calibration_2026-07-31.md` — full findings, cited effect-size ranges, cumulative-curve evidence, and the recalibrated HARD_PASS bar live there. This file is the pointer-only hand-off; do not re-derive the reasoning here, read the cited note.
**Pause state:** check `data/orchestrator_paused.flag` at pickup time before shipping anything to remote/GPU queues (not checked at filing time — this is a logging/calibration change, not itself a queue-triggering action).

Per [[feedback-no-experiment-design-in-prompts]]: no inline pre-reg, thresholds, or cell code below beyond what the cited research note already pre-registers (HARD-PASS/HARD-FAIL bars are in that note's "Falsifiable predictions" section) — the cell-author owns translating those into concrete pre-reg + code changes.

---

## Anchor candidates (rank-ordered)

1. **[Primary] Re-baseline the HARD_PASS margin bar for per-competency comprehension lift from the guessed 0.08 to the evidence-grounded tiered bar, and add per-competency (not just aggregate) logging to the curriculum-loop eval.**
   - Anchor pointer: research note section 3 "Calibrated recommendation for the HARD_PASS margin bar" + the "Cheap decisive test" section.
   - Substrate-product reading: the guessed 0.08 was set near the CEILING of what even heavy, multi-week human single-skill instruction achieves (reciprocal teaching, d=0.45) — it was very likely too aggressive as a per-competency floor. Recalibrated bar: **≥0.02 floor / 0.03-0.06 expected-strong band / 0.08+ reserved as cumulative-or-strongest-single-strategy stretch**, not a per-competency gate. This directly re-reads the already-measured +0.015 thematic-roles result as a close-miss-at-the-floor rather than a clean fail.
   - Tier hint: this is a LOGGING + THRESHOLD change, not a new mechanism — cheap, near-zero engineering risk. The risk is entirely in whether the eval itself is noisy (flagged explicitly in the note's HARD-FAIL predictions: >5x inconsistency across repeated measurement on the same competency would mean recalibrate the eval, not trust any per-competency number).
   - Why now: competency #2 (coreference) is the next one in the pipeline per the growing-library-of-competencies plan; landing it without a recalibrated bar risks either a false "fail" (using the old 0.08 floor) or a false "pass" (no floor at all). This should land BEFORE coreference's result is judged.

2. **[Secondary] Instrument the curriculum-loop eval to log per-competency lift explicitly (roles alone, roles+coref, roles+coref+N) so the additive-vs-threshold cumulative-curve question gets answered from OUR OWN data, not just literature analogy.**
   - Anchor pointer: research note's "Cheap decisive test" section — zero additional compute cost, just breaking out what's already being aggregated.
   - Substrate-product reading: the literature (Simple View of Reading additive/multiplicative debate, multi-strategy>single-strategy findings, Cain/Oakhill multi-deficit profile) converges on an ADDITIVE-WITH-MILD-SYNERGY read (P_deflated=0.40, capped per lit-scan calibration penalty — this is inference from adjacent findings, not a direct measurement). The project's own cumulative curve is the actual arbiter; this instrumentation makes that measurement possible without extra experiments.
   - Tier hint: trivial to add to whatever logging harness the curriculum loop already uses; should ship alongside anchor 1, not as a separate cycle.
   - Why now: without per-competency breakdown, a flat-or-declining cumulative curve (which the note's HARD-FAIL criteria treat as evidence of a shared-bottleneck problem, not "brain-realistic smallness") would be invisible until much later in the competency-stacking plan.

3. **[Tertiary, informational only] When coreference (competency #3) lands, compare its lift against BOTH the general 0.02-0.06 band AND the directional hypothesis that coref should land HIGHER than thematic-roles (because referential-chain maintenance is closer to the core "same-thing->same-rep, update working memory" mechanism already identified as the actual bottleneck, vs. thematic-roles being a narrower/shallower construction).**
   - Anchor pointer: research note section 4 "Expected effect size for coreference."
   - Substrate-product reading: no causal training-effect-size study for coreference was found in the literature (correlational/cohesion evidence only, e.g. Halliday-Hasan referential-cohesion framework, referential-cohesion-predicts-comprehension-achievement finding) — this is a genuine evidence gap, so coref's actual measured number will be a new data point, not a confirmation of known literature. P_deflated=0.30 on the "should land higher" directional hypothesis.
   - Tier hint: not an experiment design change, just an interpretation lens to apply when the coref result comes in — flag if it's at-or-below thematic-roles' 0.015 despite coref's mechanism-centrality, since that would be a stronger anomaly signal than a simple "small number" reading.
   - Why now: sequenced behind coreference's own landing; nothing to build now, just don't discard this lens when the result arrives.

---

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_per_construction_comprehension_effect_size_calibration_2026-07-31.md` — this drill's full findings: cited effect-size table (9 sources), cumulative-curve evidence (additive-with-mild-synergy read), recalibrated HARD_PASS bar, coreference-specific estimate, falsifiable HARD-PASS/HARD-FAIL predictions for the decisive test.
- `notes/research_construction_acquisition_order_seed_and_ladder_2026-07-31.md` — the competency-ordering/acquisition-ladder context this calibration slots into (adjacent same-day note; not re-read in full for this drill, flagged for cross-reference).
- `notes/research_brain_discovery_allocation_trigger_new_construction_2026-07-31.md` — adjacent same-day note on how/when a new construction-competency gets allocated; cross-reference for whoever picks up anchor 1/2.
- Memory ref `[[feedback_comprehension_is_a_growing_library_of_construction_competencies_not_one_objective_2026-07-31]]` — the standing USER directive this calibration directly supports (gives it a cited numeric floor instead of a guessed one).
- Memory ref `[[feedback_flat_learning_result_means_broken_experiment_not_capability_ceiling_2026-07-31]]` — the discipline this note's "Cheap decisive test" and HARD-FAIL criteria directly operationalize at the per-competency level.

---

## Contract section

- Cell-author (or whoever owns the curriculum-loop eval harness) owns: the exact code change to (a) swap the 0.08 gate for the tiered bar from research note section 3, (b) add per-competency lift logging, (c) re-tag the existing thematic-roles +0.015 result under the new tier (close-miss-at-floor, not clean-fail).
- HARD-PASS/HARD-FAIL bars for the decisive test are pre-registered in the research note's "Falsifiable predictions" section — do not loosen them at pickup time without flagging the deviation explicitly.
- Do not re-run the thematic-roles experiment to chase the old 0.08 bar — the bar was wrong, not necessarily the result.

## Autonomy declaration

Research does not prescribe the exact logging schema, exact code location in the curriculum-loop harness, or exact wording of the re-tagged result. Cell-author/picker-up has full autonomy over implementation detail, subject to the recalibrated bar values and the falsifiable HARD-PASS/HARD-FAIL predictions pre-registered in the cited research note.
