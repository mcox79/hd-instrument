# Adjacent-component brain-fidelity map (2026-08-29) -- for planning next problems

Framing: Zwaan & Radvansky's event-indexing situation model has FIVE dimensions
(TIME, SPACE, CAUSATION, ENTITIES, GOALS/intentionality). This problem built the TIME
before/after test; the map below is grounded from disk (`ls hdlab/`, `substrate_map`,
the causal experiment inventory) and evaluates each adjacent dimension for
brain-foundational fidelity + leverage, to seed the next problems.

| dimension | built? (disk) | brain-foundational status | capability / limitation | leverage as next problem |
|---|---|---|---|---|
| **TIME** | `graded_temporal_context`, `sequence_memory`, `temporal_trace`, + the NEW temporal-order register (this problem) | Front-end PINNED-faithful (Reichenbach + connectives); order register representation now MEASURED (discrete adequate, continuous = confidence layer) | Answers before/after (1.000 isolated), serves causal direction; LIVE wiring under-fires (had-gate + per-sentence) | **WIRING FIX (this problem's landing)** -- highest-certainty gain |
| **SPACE** | `location_register` (owner-DONE, EXCELLENT) | PINNED (Talmy PATH/deixis; categorical nodes) | where_is / presence intervals; extraction gated 0.909 | Landing queued; coref caps real-prose (mapped) |
| **ENTITIES** | rich: `coref` stack, `factorized_entity_store`, `event_centrality_coref`, `situation_reader` | Mixed; coref is the real-prose bottleneck (~0.65) | who-did-what; state history NOT tracked (see below) | Coref improvement is a standing cap; **entity STATE history is a gap (below)** |
| **CAUSATION** | `_causal_network` (live) + MANY `exp_causal_*` (heavily explored) | **PLACEHOLDER** -- live organ is order-agnostic + "reducible to connective-else-most-recent" (its OWN VET caveat); not genuine causal/force-dynamics reasoning | Extracts cause->outcome links from connectives/adjacency; no plausibility, direction was order-agnostic | **HIGH: the least genuinely-built dimension. The TIME register now supplies the precedence constraint (cause precedes effect, 1.000 vs 0.000 serve). A genuine causal-plausibility organ that consumes temporal precedence is a strong next problem** |
| **GOALS / ToM** | substantial: `belief_partition` (ToM), `goal_typing`, `goal_achievement`, `goal_outcome_relation`, `intent_classifier` | Partly PINNED (belief partition landed) | goal typing / belief partition; goal-timeline (what an agent knew WHEN) not composed with TIME | Medium: compose the TIME register with the belief timeline (what an agent knew at time T) |

## Two concrete, high-incidence gaps this problem's measurements EXPOSED (evidence on disk)

1. **The perfect-ASPECT resultant/prior-STATE channel is DROPPED, and it is the DOMINANT 'had'
   construction (27% of real pluperfects).** `exp_temporal_order_extraction_recall_v1`: of 139
   spaCy-reference pluperfects on real LitBank, **27% are copular/stative "had been X"** ("had been an
   excellent woman", "had been ill", "had been born") -- a prior STATE of an entity, which the perfect
   aspect marks (Ferretti/Kutas/McRae 2007: aspect feeds the entity/state layer, not the order layer).
   Our extractor CORRECTLY skips these for ordering (they are not events), but NOTHING consumes them as
   entity STATE HISTORY. **Candidate next problem: an entity-state / resultant-state dimension** that reads
   "had been X" into a per-entity prior-state register (composes with the ENTITY dimension + the SPACE
   location register's interval bookkeeping). High incidence, PINNED brain basis, currently absent.

2. **CAUSATION is a connective placeholder and now has its missing ingredient.** The live causal organ is
   order-agnostic (verified: `situation_reader._read_causation` + `_causal_network` docstring). Cause
   MUST precede effect (Zwaan -- temporal order constrains causation); the TIME register supplies exactly
   that (Phase C serve: 1.000 vs 0.000 on flashback-causal). **Candidate next problem: a causal-direction /
   plausibility organ** that consumes the temporal precedence constraint instead of the order-agnostic default.

## Fidelity notes carried forward (mapped, not walls for THIS problem)
- Tense EXTRACTION for EVENTS is solid (event-pluperfect recall 0.911 window -> 0.941 clause-binder; ~6%
  residual), so the ordering mechanism is NOT extraction-capped in practice -- the earlier "wall" was
  inflated by counting copular STATES as missed events. A full syntactic parser buys only ~6% on events.
- The continuous magnitude line does NOT reproduce the TCM forward-contiguity asymmetry (it is a settled
  magnitude, not a drifting context). This is a RECALL/retrieval signature, not a before/after JUDGMENT
  capability, so it is correctly out of scope for this problem -- only relevant if a downstream episodic
  RECALL task needs forward-biased reconstruction.
