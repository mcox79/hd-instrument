# exp_dev hand-off -- research: innate scaffolding / core-knowledge kernel

Filed-by: research sub-agent
Date: 2026-07-09
Trigger: notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md
Urgency: MEDIUM -- foundational-program drill, no existing cell blocked on this; cheapest anchor
(dual-number double-dissociation probe) requires no store-format change and is CPU-only synthetic.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ranked anchor candidates only. Experiment design details (exact
corpus construction, ablation mechanics, seed grid) are to be authored by exp_dev from the research
note's Falsifiable Predictions section. Do NOT treat the description below as an implementation spec.

---

## Anchor candidates (rank-ordered)

### Anchor 1: dual-number double-dissociation probe (cheapest, highest-P, no store-format change)

Anchor pointer: Research note "Cheap decisive test" section + Falsifiable Prediction 1.

Substrate-product reading: Tests whether biology's lesson "build TWO structurally distinct number
primitives (small-N exact parallel-individuation via fixed-cardinality pointer array; large-N
approximate ratio/Weber-scaled magnitude code), never one unified module" transfers to this substrate.
Hyde & Spelke (2011) found a double dissociation in infants (distinct ERP components, distinct scaling
laws) -- this cell asks whether an analogous double dissociation is measurable here via PAIRED
ablation: corrupt the small-N pointer-array module and measure delta on small-set exact-tracking vs
large-set ratio-discrimination; separately corrupt the continuous magnitude channel and measure the same
delta pair.

Tier hint: CPU-only, synthetic corpus (no ingest dependency), cheap to smoke and cheap to FULL.

Why-now: No existing cell in the substrate implements a fixed-cardinality small-N pointer-array
primitive alongside the existing continuous magnitude/similarity code -- this is new scope, not a
reopen. Directly actionable without waiting on any other in-flight cell.

Pre-reg bands (full detail in research note Falsifiable Prediction 1):
  HARD-PASS: perturbing pointer-array degrades small-set task >=2x more than large-set task, AND
    vice versa for magnitude-channel perturbation (clean double dissociation both directions).
  HARD-FAIL: both perturbations degrade both tasks roughly equally (within 1.3x) -- no dissociation,
    unified magnitude code sufficient.
  MIDDLE: dissociation in one direction only.

### Anchor 2: parsimony/hierarchy prior at consolidation/decode time

Anchor pointer: Research note Falsifiable Prediction 2.

Substrate-product reading: Tests Perfors, Tenenbaum & Regier's result (a general parsimony/Occam prior
alone, without a language-specific hierarchy rule, favors hierarchical grammars because they are more
compact) transferred to this substrate's binding operator -- add an explicit shorter/nested-encoding-
preferred regularizer and measure held-out compositional-generalization delta vs unregularized baseline
at matched capacity.

Tier hint: likely CPU, depends on which binding/consolidation cell it extends (exp_dev to identify
nearest existing consolidation cell to extend rather than building from scratch).

Why-now: this is the single most concrete "innate bias, not innate content" recommendation from the
drill and has an existing ML-literature precedent (MDL / Bayesian Occam's razor) reducing implementation
risk relative to Anchor 3.

Pre-reg bands (full detail in research note Falsifiable Prediction 2):
  HARD-PASS: regularizer improves held-out compositional accuracy by >=15% relative over unregularized
    baseline at matched capacity.
  HARD-FAIL: no measurable benefit, or regularizer degrades in-distribution accuracy by more than any
    held-out gain.

### Anchor 3: privileged-basis-relation-set seeding (higher novelty, higher risk)

Anchor pointer: Research note Falsifiable Prediction 3.

Substrate-product reading: Tests whether seeding the relation-vocabulary with a ~6-10-item basis
(containment, support, contact, link, path/source-goal, up-down, blockage/help/hinder) as high-frequency
structurally-simple binding templates speeds convergence on downstream compositional relation tasks vs
cold-start fully-open vocabulary -- directly engages the existing open-relation-vocabulary tension (see
Context pointers).

Tier hint: depends on existing relation-vocabulary/ingest cell exp_dev identifies as nearest extension
point; likely needs a small synthetic relation corpus.

Why-now: lower priority than Anchors 1-2 -- P_deflated is the lowest of the three (0.30) and risk of
over-fitting to the "core six" at the expense of open-vocabulary coverage is real per the research note's
own HARD-FAIL condition. Recommend running AFTER Anchor 1 (cheaper, more decisive, less risk of
polluting the open-vocabulary design if wrong).

Pre-reg bands (full detail in research note Falsifiable Prediction 3).

### Anchor 4 (exploratory, do not dispatch without further scoping): Carey placeholder-bootstrapping
recipe for exact-cardinality

Anchor pointer: Research note Falsifiable Prediction 4.

Substrate-product reading: most speculative -- Carey herself concedes the "modeling processes" step
(analogy/induction/abduction composing placeholder structures with core-system content) is a sketch, not
a computational account. Flagging for visibility, NOT recommending dispatch until Anchors 1-2 land and
inform whether the substrate's existing analogy/induction operators are even suitable building blocks.

---

## Context pointers (file paths, not summaries)

- Research note (this drill): d:/AI/hd-instrument/notes/research_innate_scaffolding_core_knowledge_kernel_2026-07-09.md
- Cross-thread sibling drills (same-day, informs "structural vs content grounding" distinction):
  - notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md
  - notes/research_grounding_cascade_depth_multihop_mechanism_2026-07-09.md
  - notes/research_brain_independent_channels_resolve_compounding_error_tension_2026-07-09.md
- Open relation-vocabulary tension (Anchor 3 directly engages this):
  notes/project_substrate_open_relation_vocabulary_no_closed_enum_USER_2026-07-03.md (see MEMORY.md
  "Ingest+relation-vocab" line)
- Existing self-margin taxonomy precedent (independent confirmation of "build N distinct mechanisms, not
  one" design lesson): notes/reference_self_margin_taxonomy_splits_by_decode_regime_2026-07-06.md
- Existing correlation-hurts-capacity precedent (relevant to keeping store-codes near-random while
  adding compositional structure): notes/reference_correlation_hurts_associative_store_capacity_decouple_from_retrieval_2026-07-08.md

---

## Contract section

This handoff proposes FOUR ranked anchors (1 recommended first, 2 second, 3 third, 4 exploratory-only).
Exp_dev authors exact corpus construction, ablation/perturbation mechanics, and seed grid for whichever
anchor(s) it picks up. Do NOT treat the anchor descriptions above as implementation specs.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchor(s) to pick up first (Anchor 1 recommended cheapest/highest-P, but exp_dev may
  reprioritize based on current queue state)
- Choosing synthetic corpus size, seed counts, and exact ablation/perturbation implementation within the
  pre-registered bands above
- Identifying the nearest existing cell/module to extend for Anchors 2 and 3 (consolidation cell for
  Anchor 2, relation-vocabulary/ingest cell for Anchor 3)
- Choosing local CPU vs remote_cpu_queue routing per the SMOKE-only-local rule

Exp_dev is NOT autonomous in:
- Dispatching Anchor 4 without further scoping (flagged exploratory-only; the underlying mechanism is
  explicitly conceded-underspecified by its own source literature)
- Declaring CG promotion (Skunkworks/VET decides tier per landed-VET discipline)
- Treating Anchor 3's privileged-basis-set as a move toward a closed relation enum -- the research note
  and existing project directive both require the open-vocabulary system to remain able to construct
  novel relations compositionally; Anchor 3 only tests SEEDING priority, not closure
