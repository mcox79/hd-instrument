# exp_dev hand-off — research: Curry-Howard depth-5+ proof-chain scaling + LANE B forecast

Filed-by: research:opus 2026-06-13
Trigger: forward-looking depth-7-12+ forecast drill; see notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md

Pause state: check data/orchestrator_paused.flag before shipping. If paused, only the cheap forecast-validation smoke (CELL-DEPTH-FORECAST) and authoring-prep anchors are permitted; queue-burst on PRIORITY-2 anchors is gated.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns the experiment-design layer. The anchors below are pointers + WHY, not pre-designed cells. exp_dev should self-design per envelope-fail-bands and ship via queue_add.sh with smoke-gate.

---

## Anchor candidates (rank-ordered)

### 1. CELL-DEPTH-FORECAST (cheap, ~30 min CPU) — PRIORITY-0 GATE
- Pointer: pre-BATCH-19 corpus longest-path-to-axiom histogram + Hill-estimator alpha + avg premise count per leaf
- Substrate-product reading: VALIDATES the forecasting model BEFORE committing 200+ atom LANE B authoring. If substrate corpus is NOT scale-free (Hill alpha > 3.0) or avg premise count is anomalous, the Mathlib/AFP/Mizar priors DO NOT extrapolate; the depth-7+ forecast must be redone.
- Tier hint: cheap CPU; structural; no queue burst needed; non-pause-blocking
- Why-now: gates all PRIORITY-1 anchors below; cheap; no GPU; aligns with 11th methodology rule (verify-before-asserting) on forecast model

### 2. CELL-IND-PRINCIPLE-LIBRARY (PRIORITY-1) — INDUCTION-PRINCIPLE AUTHORING
- Pointer: author well-founded induction + structural induction + course-of-values induction + mutual induction as substrate atoms with full CHTV typing
- Substrate-product reading: empirically critical depth-amplifier per Mathlib evidence. One well-founded induction principle gives access to depth-30+ chains via recursion structure. Without this, ceiling will cap below 7 even at LANE B scale.
- Tier hint: T0/T1 foundational; structural authoring; cheap CPU once authored; high downstream fan-in
- Why-now: gate condition for KP P5 firing per prediction F4; should ship BEFORE BATCH 19-26 ingest

### 3. CELL-SIGMA-PI-TYPES (PRIORITY-1) — DEPENDENT-TYPE RICHNESS
- Pointer: ship PI/SIGMA type subcommands (already drafted in roadmap) with full CHTV-2 alpha-equivalence verification
- Substrate-product reading: dependent typing is empirically how Mathlib reaches depth 84 on Pythagorean. Substrate cannot reach depth 7+ on nontrivial mathematics without sigma/pi types. Roadmap PI/SIGMA should ship with depth-7+ ingest, NOT after.
- Tier hint: T0 foundational; substantial design (CHTV-2 needed); structural
- Why-now: gate condition for KP P5 firing per prediction F4; alpha-equivalence is roadmap

### 4. CELL-TYPECLASS-HIERARCHY (PRIORITY-2) — ALGEBRAIC TYPE-CLASS AUTHORING
- Pointer: author algebraic type-class hierarchy (group, ring, field, module, vector_space, ...) with structural inheritance edges in generalized-typing-context
- Substrate-product reading: Mathlib's structural design via type classes gives compositional depth amplification. Each type class adds a layer that compounds with other layers. Without this, deep proofs become flat-graph chains instead of compositional graphs.
- Tier hint: T1 algebra-class; ~50-100 atoms; moderate authoring cost; high downstream fan-in
- Why-now: hub-and-spoke depth amplifier; aligns with L6-PROOF FINDER 62pct authoring-gap prioritization recipe (downstream_fanin x cross_capability_breadth x is_leaf)

### 5. CELL-HUB-LEMMA-AUTHORING (PRIORITY-2) — TOP-50 HUB LEMMAS
- Pointer: identify and author the top-50 hub lemmas (predicted in-degree >= P95 of substrate-corpus distribution) explicitly with deep CHTV chains
- Substrate-product reading: per Mathlib alpha=1.81 scale-free in-degree, deep chains route through a FEW central hub lemmas. Authoring these explicitly with depth-5+ chains gives 78pct of node savings (Mathlib REFACTOR-top-10 empirical finding).
- Tier hint: T1/T2 hub atoms; ~50 atoms; high downstream fan-in; SHARES_MATH amortization compounds
- Why-now: post BATCH 19-26 + post CELL-IND-PRINCIPLE + CELL-SIGMA-PI; hub-and-spoke depth amplifier

### 6. CELL-SYMBOLIC-REPAIR (PRIORITY-3, NICE-TO-HAVE) — SHARES_MATH REPAIR OPERATOR
- Pointer: implement a "repair operator" that retries failed L6-PROOF FINDER branches via SHARES_MATH equivalence-class substitution
- Substrate-product reading: substrate-novel angle on PALM-style symbolic repair. PALM uses LLM correction; substrate would use equivalence-class substitution. Tests SHARES_MATH amortization claim from prediction F5.
- Tier hint: design + impl ~3-5 hours; substrate-novel
- Why-now: tests F5 falsifiability; not gate condition; nice-to-have for depth-amplification quantification

---

## Context pointers (paths, not summaries)

- Research note: notes/research_DRILL_forward_looking_curry_howard_depth_5_plus_proof_chain_scaling_LLM_categorical_gap_2026-06-13.md
- L6-PROOF FINDER HARD-PASS context: memory file substrate_L6_PROOF_FINDER_HARD_PASS_20_20_SOUND...md
- KP knowledge promotion context: memory file substrate_CELL_KP_knowledge_promotion_operator_P1_P4...md
- CHTV-1 verifier context: memory file substrate_CHTV1_substrate_as_verifier_HARD_PASS...md
- 62pct authoring-gap prioritization recipe: notes/research_drill_L6_PROOF_FINDER_62pct_authoring_gap_leaf_prioritization_strategy_depth_corpus_expansion_2x_2026-06-13.md
- universal-vs-field-specific H3 (field-specific signal extractors angle): notes/research_drill_universal_vs_field_specific_promotion_interaction_operator_3x_USER_strategic_directive_2026-06-13.md
- alternatives-audit Reservation A (soft-tier classification): notes/research_drill_alternative_architectures_vs_current_3_axis_substrate_dont_lock_in_prematurely_USER_directive_2x_2026-06-13.md

---

## Contract

- exp_dev self-designs cells per envelope-fail-bands; pre-reg HARD-PASS / HARD-FAIL bands at smoke-gate
- Per [[feedback-no-experiment-design-in-prompts]]: research provides pointers + substrate-product reading; exp_dev owns design layer
- Per pause flag: if paused, ship only CELL-DEPTH-FORECAST + non-queue-burst authoring prep (CELL-IND-PRINCIPLE + CELL-SIGMA-PI authoring drafts); gate queue-burst on resume
- Per 11th methodology rule: any macro-metric claim (e.g. depth-ceiling improvement) requires held-out test methodology; new test atoms authored AFTER mechanism shipment

## Autonomy declaration

exp_dev is authorized to:
- self-design any of the 6 anchors above with own envelope-fail-bands
- pick anchor order based on current queue depth + pause flag + cost-benefit per envelope
- skip any anchor whose HARD-FAIL is structurally guaranteed by current corpus state (e.g. skip CELL-DEPTH-FORECAST if pre-BATCH-19 already analyzed)
- compound anchors if cheaper (e.g. CELL-IND-PRINCIPLE + CELL-SIGMA-PI as joint smoke)
- substitute substrate-novel anchors if exp_dev sees a cheaper decisive cell I missed

Filed-for: depth-7-12+ trajectory + KP P5 firing readiness + substrate-product positioning at LANE B scale.
