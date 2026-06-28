# exp_dev hand-off — research: Counterfactual reasoning primitive (Stage 3) — GAP-focused

**Filed by:** research (Opus 4.7, 1M ctx)
**Date:** 2026-06-27
**Trigger:** `d:/AI/hd-instrument/notes/research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md`
**Pause state:** check `d:/AI/hd-instrument/data/orchestrator_paused.flag` before queue_add per orchestrator discipline.

Per [[feedback-no-experiment-design-in-prompts]] — this hand-off points to the research note as the authoritative cell spec; exp_dev is the cell-author and may revise designs after independent smoke + cardinality + scale-survival check.

**CRITICAL CONTEXT (from coordinator URGENT update):** substrate ALREADY has 4 chain-grade + 1 MIDDLE_BAND counterfactual atoms verified on disk. These cells target GAPS, not duplicates:

- MEASURED@ HARD_PASS: `d:/AI/hd-instrument/data/exp_causal_intervention_isolation_v1/metrics.json` (single intervention is LOCAL, non-target degradation=0.0000)
- MEASURED@ MIDDLE_BAND: `d:/AI/hd-instrument/data/exp_causal_counterfactual_replay_v1/metrics.json` (accuracy=1.000, latency=16.864ms; latency-bound only)
- MEASURED@ HARD_PASS: `d:/AI/hd-instrument/data/exp_causal_audit_chain_depth_v1/metrics.json` (depth-50)
- MEASURED@ HARD_PASS: `d:/AI/hd-instrument/data/exp_causal_bitemporal_composition_v1/metrics.json` (CF-as-of accuracy=1.000)
- MEASURED@ HARD_PASS: `d:/AI/hd-instrument/data/exp_causal_correlational_disambig_v1/metrics.json` (causal precision=1.000 recall=1.000)

**DO NOT DUPLICATE these.** The cell designs below target the 5 un-atomized gaps.

---

## Anchor candidates (rank-ordered)

### ANCHOR 1 (highest priority, parallel-dispatchable) — Cell 1 regret-magnitude comparison primitive (vmPFC analog) [GAP A]
- **Pointer:** `d:/AI/hd-instrument/notes/research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md` section (c) CELL 1
- **Substrate-product reading:** missing vmPFC analog — the scalar comparison signal that turns counterfactual REPLAY (banked) into counterfactual REASONING. M3-load-bearing (conversational regret, choice optimization, hedging, audit-metric for EU AI Act, legal damages computation).
- **Tier hint:** chain-grade-eligible if HP; composes 5 chain-grade atoms + 1 NEW comparison readout primitive (low novelty).
- **Why now:** ~30min smoke; M3 milestone path; opens GAP E (CF generation) by providing ranking signal.
- **P_deflated:** 0.50 (cap)

### ANCHOR 2 (highest priority, parallel-dispatchable with ANCHOR 1) — Cell 2 latency optimization via delta-stack lazy surgery [GAP D]
- **Pointer:** research note section (c) CELL 2
- **Substrate-product reading:** auto-promotes existing MIDDLE_BAND atom `exp_causal_counterfactual_replay_v1` to chain-grade (latency 16.864ms → <10ms HYPOTHESIZED@); enables real-time conversational CF queries.
- **Tier hint:** engineering not science; chain-grade-eligible; promotes parent atom on HP.
- **Why now:** ~30min smoke; cheapest path to one additional chain-grade atom.
- **P_deflated:** 0.50 (cap)

### ANCHOR 3 (gated on ANCHOR 1; dependent on Cell 1 primitives) — Cell 3 nested chain-of-counterfactual [GAP B]
- **Pointer:** research note section (c) CELL 3
- **Substrate-product reading:** depth-2+ CF composition; unlocks "what if X had been Y AND given that, what if Z had been W?" — required for nested hypothesis evaluation in conversational AI.
- **Tier hint:** novel composition; MEASURED@ check required pre-full-dispatch on cumulative contamination across nests.
- **Why now:** parallel after Cell 1 lands; tests Type D from 2026-06-07 capability-extension drill (P_deflated=0.55 then; now operationalized).
- **P_deflated:** 0.38

### Deferred (Tier-2 — do not dispatch until ANCHOR 1-3 chain-grade)
- **GAP C — CF simulation with NOVEL antecedents (P_deflated=0.30):** depends on encoder upgrade per `feedback_path_c_substrate_owned_encoder_is_the_answer_USER_2026-06-23.md`.
- **GAP E — CF generation (substrate proposes CF) (P_deflated=0.25):** depends on Cell 1 regret as ranking signal + importance primitive resolution.
- **Probes 1, 3, 4 (materials science / legal NESS / economic synthetic-control):** extension cells after Cells 1-3 chain-grade.

---

## Context pointers (paths, NOT summaries)

- Research note (cell specs, brain grounding, pre-reg bands): `d:/AI/hd-instrument/notes/research_drill_2x_counterfactual_reasoning_primitive_stage3_2026-06-27.md`
- Existing counterfactual portfolio (DUPLICATE-CHECK — do NOT re-cell):
  - `d:/AI/hd-instrument/data/exp_causal_intervention_isolation_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_causal_counterfactual_replay_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_causal_audit_chain_depth_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_causal_bitemporal_composition_v1/metrics.json`
  - `d:/AI/hd-instrument/data/exp_causal_correlational_disambig_v1/metrics.json`
- Adjacent prior research drills (background):
  - `d:/AI/hd-instrument/notes/research_drill_substrate_gap_causal_counterfactual_3x_2026-06-07.md` (Pearl do-calculus + Mechanisms A/B/C)
  - `d:/AI/hd-instrument/notes/research_drill_counterfactual_capability_extension_2026-06-07.md` (Types A-E on bitemporal stack)
  - `d:/AI/hd-instrument/notes/exp_dev_to_research_ccc1v2_counterfactual_HP_4of7_2026-06-05.md` (cf-RPE delta-rule)
- Companion TOM drill (Cell 2 here composes with TOM Cell 1 agent-bank):
  - `d:/AI/hd-instrument/notes/research_drill_2x_theory_of_mind_primitive_stage3_2026-06-27.md`
- Discipline references:
  - [[feedback-discriminator-must-survive-scale]] — full-N preview arm required before full dispatch
  - [[feedback-three-smoke-disciplines-no-silent-except-smoke-fires-discriminator-band-floor-inconclusive]]
  - [[feedback-cardinality-ok-mandatory-prereg-field-for-sweep-axis-cells]]
  - [[feedback-no-hallucinated-numbers-verify-on-disk]] — all MEASURED@ numbers in research note verified via direct file read

---

## Contract

- exp_dev is cell-author; may revise cell designs after independent smoke
- Pre-reg pages MUST include CARDINALITY_OK, EXPECTED_N_UNITS, HARD_FAIL_CARDINALITY_BREACH per cell specs
- Smoke discipline 1-2-3 (no silent except, smoke fires discriminator, band-floor=MIDDLE_BAND not HARD_PASS)
- Discriminator-must-survive-scale check before full dispatch (use check C: full-N preview arm in smoke)
- Strict ordering: ANCHOR 1 || ANCHOR 2 (parallel) → ANCHOR 3 (after ANCHOR 1 HP)
- Atomize HP results per [[feedback-results-to-application-cadence]]: same cycle Store atom + hdlab/ primitive update
- ANCHOR 2 HP auto-promotes parent atom `exp_causal_counterfactual_replay_v1` — Skunkworks notification required for parent promotion

## Autonomy declaration

exp_dev owns:
- Cell-author N, V_REL choices (cell specs are starting points; may revise per smoke results)
- Smoke-vs-full N split per Cell
- Routing decision (CPU local vs remote_cpu_queue vs overnight_queue per Fix #24)
- Whether to bundle Cells 1+2 (parallel-dispatchable) into a single 7-arm cell vs two separate cells
- Whether to add additional discriminator arms beyond minimums I specified
- Choice of magnitude-encoding scheme for Cell 1 (continuous α vs 5-bin quantization — research note flags continuous α as load-bearing risk)

research does NOT own:
- Final pre-reg bands (research provides starting estimates; cell-author may tighten/loosen with justification)
- Anchor priority once new evidence lands (verdict-handler reroutes)
- The decision to dispatch GAP C / GAP E / Probe extensions — gated on Cells 1-3 chain-grading first

---

END exp_dev_handoff_research_counterfactual_reasoning_primitive_2026-06-27.md
