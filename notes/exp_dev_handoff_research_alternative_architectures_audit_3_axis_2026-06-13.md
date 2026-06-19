# exp_dev hand-off -- research: alternative architectures audit vs current 3-axis substrate

Filed-by: research:opus  2026-06-13
Trigger: USER 2x deep-research drill (verbatim: "make sure we're reconsidering this as we go - we don't want to get locked into something and overlook potentially more useful frameworks"); plus "we might be the first ones to build a system exactly like ours"
Source research note: d:/AI/hd-instrument/notes/research_drill_alternative_architectures_vs_current_3_axis_substrate_dont_lock_in_prematurely_USER_directive_2x_2026-06-13.md
Pause state: respect data/orchestrator_paused.flag if set; do not auto-ship.

Per [[feedback-no-experiment-design-in-prompts]]: this handoff names anchors and the substrate-product reading. Cell design is exp_dev's autonomy.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST): CELL-AAA-1 Bayesian tier overlay
- Pointer: 100 atoms from current cycle's KP outputs; add P(T_i|atom) field; compare retrieval precision@10 hard label vs argmax posterior.
- Substrate-product reading: confirms or refutes Reservation A (Bayesian posterior overlay). HARD-PASS = soft overlay ships as ~80-150 LOC additive feature; HARD-FAIL = monotonic tier label survives unchanged.
- Tier hint: Tier-2 (substrate-architectural validation cell).
- Why now: cheapest of the three audit cells; uses existing atoms and existing tier assignments; ~1 hour CPU on remote desktop. Highest information-per-CPU-hour of the three.

### Anchor 2: CELL-AAA-2 Content-type first-class storage partition
- Pointer: 200 atoms, test retrieval-from-FORMAL-only-partition vs retrieval-from-mixed-partition for math-axiom test query.
- Substrate-product reading: confirms or refutes Reservation B. HARD-PASS = promote content-type from attribute to first-class storage; HARD-FAIL = keep as attribute.
- Tier hint: Tier-2.
- Why now: directly informs L6-PROOF FINDER batch prioritization. If HARD-PASS, partition-first authoring strategy compounds with downstream_fanin x cross_capability_breadth recipe.

### Anchor 3: CELL-AAA-3 Substrate-load-bearing axis empirical witness
- Pointer: 20 TOOLS atoms + 20 MATERIALS atoms; test SHARES_MATH out-degree ratio prediction.
- Substrate-product reading: confirms or refutes Reservation C (genuine novelty of load-bearing axis). HARD-PASS = axis is real and confers measurable property; HARD-FAIL = axis collapses to noise or to existing Soar procedural/declarative distinction.
- Tier hint: Tier-3 (axis-validation; speculative).
- Why now: this is THE substrate-novel architectural claim. If HARD-FAIL, the 3-axis architecture should be re-considered as 2-axis (epistemic + content-type) and the work-saved is structural. HIGH-INFORMATION even on negative result.

### Anchor 4 (FOLLOW-UP if Anchor 1 HARD-PASS): Bayesian KP-update operator
- Pointer: extend KP from "argmax confidence" to "posterior update over T-distribution".
- Substrate-product reading: 6th promotion path joins the 5 already validated (frequency + DRUM + SHARES_MATH + sleep-replay + Curry-Howard).
- Tier hint: Tier-2.
- Why now: only run if AAA-1 HARD-PASS; otherwise skip.

### Anchor 5 (FOLLOW-UP if Anchor 2 HARD-PASS): Field-partition-first KP authoring batch
- Pointer: re-rank L6-PROOF FINDER 80-atom batch by FORMAL-partition-first then downstream_fanin recipe.
- Substrate-product reading: compounds with the L6-PROOF prioritization recipe; tests Reservation B's downstream effect.
- Tier hint: Tier-2.
- Why now: only run if AAA-2 HARD-PASS.

### Anchor 6 (PRE-MORTEM / RESERVED): Sheaf-theoretic content-type partitioning at 100M atom scale
- Pointer: reserved for substrate post-100M-atom-scale ceiling event.
- Substrate-product reading: pre-mortem alternative architecture if substrate hits a content-type partitioning ceiling.
- Tier hint: TBD (deferred).
- Why now: NOT NOW. Bookmark in cap_map as pre-mortem alternative.

---

## Context pointers (paths, not summaries)

- d:/AI/hd-instrument/notes/research_drill_alternative_architectures_vs_current_3_axis_substrate_dont_lock_in_prematurely_USER_directive_2x_2026-06-13.md (this drill)
- d:/AI/hd-instrument/notes/research_drill_universal_vs_field_specific_promotion_interaction_operator_3x_USER_strategic_directive_2026-06-13.md (companion drill from same day; H3 first-class partition routing)
- d:/AI/hd-instrument/notes/research_drill_curry_howard_atoms_as_types_substrate_dependent_types_proof_verification_2x_2026-06-12.md (compatibility with Bayesian-typed extension)
- d:/AI/hd-instrument/notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md (downstream batch)
- d:/AI/hd-instrument/notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (KP mechanism context; 5 promotion paths)

---

## Contract

- exp_dev decides cell design; this handoff names anchors and substrate-product reading, NOT experimental method.
- Each anchor cell pre-registers HARD-PASS / HARD-FAIL per its sub-cell spec in research note section (b).
- Smoke gate per existing exp_dev protocol; remote verify after ship.
- All compute on remote desktop CPU per [feedback all CPU compute on remote desktop not local laptop].
- ASCII-only outputs in scripts; substrate-quality-first; literature-is-not-oracle; brain-can-do-it 5-substrate-paths threshold.

## Autonomy declaration

exp_dev MAY:
- Re-order anchors based on dependency or smoke-result feedback.
- Combine AAA-1 + AAA-3 in a single CPU pass if data structures align.
- Drop AAA-3 if early signal from AAA-1 suggests it would interfere.
- Defer Anchors 4 + 5 indefinitely if precursors HARD-FAIL.

exp_dev MUST:
- Honor pause flag.
- Pre-register HARD-PASS / HARD-FAIL bands per substrate methodology rules.
- Report POSITIVE OR NEGATIVE result honestly; do not pad.
- Treat HARD-FAIL on Anchor 3 as architectural information (architecture may move to 2-axis), not as cell failure.
