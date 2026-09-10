# SCOUTING: the parser blast radius (strategy pre-scout, 2026-09-10)

A strategy-side head-start for the solver (and a scale check for the owner). The parser is the deepest UPCHAIN
component: routing it through the graded probabilistic parse touches many consumers, so the landing must be
STAGED (per-consumer no-regress), not a single swap. Enumerated on-disk (`grep` of hdlab imports); re-verify before
acting — this can go stale.

## Live consumers of each NOT_BF parser organ (the blast radius)
| organ | # hdlab consumers | consumers |
|---|---|---|
| `pos_tagger` | **12** | candidate_generator, causation_typing, completeness_checker, consequence_learning_loop, crosstype_live_adapter, joint_relation_frontend, perceptual_access_ledger, predicate_detector, predictive_world_model, reading_grounding_loop, situation_reader, space_reader |
| `arc_parser` | **9** | candidate_generator, causation_typing, completeness_checker, graded_parser, joint_relation_frontend, perceptual_access_ledger, reading_grounding_loop, situation_reader, space_reader |
| `arc_labeler` | **6** | causation_typing, crosstype_live_adapter, perceptual_access_ledger, predicate_argument_frontend, reading_grounding_loop, situation_reader |
| `arceager_parser` | **2** | crosstype_live_adapter, situation_reader |
| `parse_confidence` | **1** | situation_reader |

## The key structural facts (verify first)
- **`graded_parser` ALREADY imports `arc_parser`** — it is the graded-marginal wrapper over the same arc-factored
  features. So the route-through is: consumers that call `arc_parser`'s hard-decode → call `graded_parser`'s
  globally-normalized Matrix-Tree MARGINAL instead. The organ to reuse exists; the work is the consumer migration
  + the acquisition question.
- **`parse_confidence` (1 consumer, situation_reader)** is the smallest, cleanest first target: its fitted logistic
  is already beaten by the graded parser's `obl_reliability_marginal` (AUC 0.782 > logistic) — the registry note.
  A good STAGE-1 (single consumer, measured replacement in hand).
- **`situation_reader` consumes all 5** — it is the integration point; the board dims live off its `read()`. Any
  route-through must show no-regress there (board self-test AGG 0.6294 is the current baseline).
- **`arceager_parser` (2 consumers)** is nearly contained (crosstype_live_adapter + situation_reader) — a bounded
  migration once the graded path is proven.

## Suggested staging (per the brief's "route-through, staged")
1. `parse_confidence` → the graded Matrix-Tree marginal (1 consumer, replacement measured, cleanest).
2. `arceager_parser` → the graded/incremental path (2 consumers, bounded).
3. `arc_parser`/`arc_labeler` hard-decode → `graded_parser` marginals, consumer-by-consumer with a per-consumer
   no-regress + the board AGG check, since 9-12 organs inherit the parse.
4. The ACQUISITION question (treebank-supervised foundation vs learned-from-reading) runs alongside — the pri-2
   directional grow-by-reading channel (`reading_grounding_loop.track_directional_context_counts`) is the first
   parser-free structure signal to build on.

*(This is a MAP, not a decision. The solver owns the method; re-enumerate on disk — imports move.)*
