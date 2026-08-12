# exp_dev hand-off — research: additive vs compositional comprehension measurement

**Filed by:** research (Sonnet, single-pass), 2026-07-31.

**Trigger:** `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` — lit-scan (Simple View of Reading multiplicativity, Kintsch C-I integration, Tomasello construction parasitism, Perfetti lexical-quality bottleneck) concludes the growing-library value structure is COMPOSITIONAL/bottleneck, not additive, and that the measured +0.015 blended-comprehension lift from adding the roles competency is likely a dilution artifact of averaging over items that don't structurally require roles.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time; this hand-off is a research→exp_dev pointer only, not a queue-ship instruction.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names anchors + pointers only. exp_dev designs N/M/K, thresholds, and implementation. No numerical parameters are prescribed here beyond what's already in the cited research note's pre-registered HARD-PASS/HARD-FAIL bands (those ARE the pre-reg, not a prescription to exp_dev to invent different ones).

---

## Anchor candidates (rank-ordered)

1. **Cheap decisive re-slice of ALREADY-LOGGED #1+#2 metrics (near-zero compute, do this FIRST)**
   - Anchor pointer: `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` section "Cheap decisive test."
   - Substrate-product reading: partition the existing name-maintenance / competitive-coreference / overwrite query results into role-CRITICAL vs role-INDIFFERENT buckets (role-CRITICAL = items only answerable by using agent/patient role info to disambiguate between competing entities) and recompute the with-roles vs without-roles delta per bucket, using metrics/logs already on disk from the #1+#2 run. No new training.
   - Tier: analyzer-only / local (post-hoc on existing checkpoints+logs).
   - Why now: this is the single fastest way to determine whether the small blended lift undersells the roles competency (measurement artifact, HARD-PASS pattern) or accurately reflects a real capability gap (HARD-FAIL pattern) — see the note's pre-registered HARD-PASS/HARD-FAIL/MIDDLE-BAND bands. Should gate whether further roles-competency training investment is warranted before building competency #3.

2. **Competency #3 (cross-sentence coreference) build, using bottleneck-tiered item design**
   - Anchor pointer: `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` section 3 "Concrete design for competency #3."
   - Substrate-product reading: build coref items tagged at construction time into Tier 0 (entity-only, unambiguous antecedent), Tier 1 (role-competitive, requires #1 AND #2 jointly), Tier 2 (role-reversal-under-coref, compounds the still-open voice-invariant-role wall). Pre-registered HARD-PASS: Tier-1 accuracy >=0.70 WITH roles AND falls to <=0.55 when roles are ablated (pre-role checkpoint) on the SAME held-out Tier-1 items — the ablation comparison is the load-bearing addition, turning correlation into a causal compositional demonstration. HARD-FAIL: Tier-1 stays <=0.55 even with roles present (integration/wiring gap), or Tier-1 lift from roles is negligible (<=0.05) despite high accuracy (construction-validity failure — model solving via a shortcut like recency, not role info).
   - Tier: likely GPU (multi-item-tier, ablation requires 2 checkpoint evals per item).
   - Why now: this is the next competency per the acquisition-order note (`notes/research_construction_acquisition_order_seed_and_ladder_2026-07-31.md`); building it with the bottleneck-tiered item design from the start avoids repeating the additive-blend measurement mistake.

3. **HARD_PASS metric definition change (process/infra item, not a queue ship)**
   - Anchor pointer: `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` section 3, final paragraph.
   - Substrate-product reading: change the standing HARD_PASS criterion for future competency additions from "additive margin on blended overall score" to "lift on the AND-gated/bottleneck item subset, ablation-verified" — apply this to anchor #2's design and retroactively to any future competency library additions (#4+).
   - Tier: N/A (definitional/process, folds into anchor #2's pre-reg).
   - Why now: cheap to adopt now while only 2 competencies exist; expensive to retrofit after several more competencies are blended into one score.

---

## Context pointers (paths, not summaries)

- `notes/research_additive_vs_compositional_comprehension_measurement_2026-07-31.md` — full lit-scan + verdict + measurement redesign (this hand-off's source).
- `notes/research_construction_acquisition_order_seed_and_ladder_2026-07-31.md` — developmental ORDER (competency #3 = cross-sentence coreference, consumes #2 role output).
- `notes/research_cross_frame_entity_stability_lever_2026-07-31.md` — entity mechanism (competency #1).
- Prior voice-invariant-role notes (`notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md`, `notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md`) — the still-open role-mechanism wall that Tier 2 coref items will compound.
- Whatever run/log directory holds the #1+#2 blended-metric result referenced in the motivating result (+0.015 blend, climb_role=0.045, byte-identical entity metrics) — exp_dev/orchestrator should locate the specific metrics.json/log path at dispatch time; not pinned here since research did not have that path.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS/HARD-FAIL/MIDDLE-BAND bands already drafted in the research note; exp_dev may refine but should preserve the ablation-comparison structure (it's the load-bearing mechanism, not a stylistic choice).
- Self-test per [[feedback-formula-selftests]].
- Anchor #1 should ship/run BEFORE anchor #2's full build — it's a cheap gate on whether #2's item design or #1's own remediation is the right next move.
- status_log entry per anchor with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact item counts, seed counts, ablation checkpoint selection, queue routing (Tier A/B/C), ETA, smoke profile, FULL profile, and may adjust the HARD-PASS/HARD-FAIL numeric bands if the research note's proposed values prove miscalibrated against the actual item pool. exp_dev may also decide anchor #1 is fast enough to run inline/local without a formal queue ship.
