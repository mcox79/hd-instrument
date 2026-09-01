# NEXT-PRIORITY BUILD: the LIVING, GROUNDED SEMANTIC GRAPH (the substrate's ATL relational hub)

Surfaced by the PPR spreading-activation break-through (SOLVED.md 8e; exp_ppr_spreading_activation_wsd_wic_v1.py):
per-context sense selection is spreading activation over a relational semantic GRAPH. We already own the graph
(WordNet, 117,659 synsets) but used it as a flat lookup. The realization: promote a RELATIONAL SEMANTIC GRAPH
to an INTRINSIC substrate organ (the ATL relational hub), read by spreading activation, GROUNDED at the nodes,
and -- the north star -- LEARNED/GROWN over time.

## DONE NOW (owner "do 1 now") -- AUGMENT #1 (static, offline, shelf-only)
- GROUNDED NODES: attach predicted-Binder-65 vectors to WordNet synsets (from lemmas + gloss words);
  GROUNDED_PPR = z-fuse spreading-activation with grounded coherence to the context (hub-and-spoke +
  spreading activation together). Built in the PPR cell (GROUNDED_PPR_dev arm); measure vs plain PPR.
- Gloss edges (WordNet++) already in (load-bearing: NO_GLOSS ablation ~ MFS).
- ON THE SHELF to fold in next (static augment): CONCEPTNET is ALREADY INGESTED (conceptnet_ingest_v1,
  conceptnet_kg_eval, substrate_conceptnet_kg_inference_transfer, remote_conceptnet_multihop) -> add
  commonsense relational edges; `hdlab/wordnet_polarity_propagation.py` ALREADY does spreading activation
  over WordNet (reuse the primitive). SyntagNet/BabelNet NOT on disk (would need a download = foundation
  build, owner-auth for external fetch).

## FLAGGED NEXT-PRIORITY (owner asked: "flag 2 and 3 as the next priority build?") -- YES.
This IS the project north star (LEARNER-ON via a CLEAN FOUNDATION; STRUCTURE is the lever): make the graph a
LIVING organ.
- #2 GROW FROM READING: when the reader meets a new word/sense, ADD a node + relations by structure-mapping
  to known concepts (grounding-by-relation; Tse 2007 schema, Gentner). RETUNE edge weights with usage (Rodd
  basin-deepening). This reframes the ORIGINAL problem: "grounding accumulates over reading" = writing
  STRUCTURED RELATIONS into a growing graph, not appending to a flat anchor store (which is WHY nothing
  accumulated). CONSOLIDATION organ operates on the graph (prune/merge/strengthen).
- #3 OWN GRANULARITY: let the graph MERGE/SPLIT senses by usage -> escape WordNet's fixed, too-fine inventory
  (the WordNet<->WiC granularity mismatch that caps knowledge-based WSD ~0.75-0.80). The brain grows its own
  sense list, not Princeton's.
- Scope: LARGE program (use PROBLEMS, not a solo grind). Seed = WordNet; the LEARNED GROWTH is the originality.

## SUBSTRATE IMPACT (organs a graph-diffusion, grounded meaning organ touches -- EVALUATE before landing)
READ-OUT organs that currently do vector-cosine / flat-lookup and would ROUTE THROUGH the graph:
- `reading_grounding_loop.canonicalize` (nearest-anchor by cosine) -> spreading-activation sense assignment.
- `distributional_meaning_channel` (the substitutability read-out) -> a node FEATURE / spoke on the graph.
- `meaning_fusion.py`, `meaning_operation_router.py`, `conceptual_meaning.py`, `semantic.py`,
  `grounded_similarity.py`, `lexical_similarity.py`, `verb_lexical_similarity.py` -> meaning read routed via
  graph diffusion + grounded nodes.
- `situation_reader.py`, `situation_model_accumulate/multibank.py`, `situation_focus.py`,
  `convergent_cue_reader.py`, `predictive_reader.py`, `gap_driven_reader.py` -> seed spreading activation with
  the situation; the situation model IS structured knowledge over the graph.
- `semantic_control.py` -> the PFC/IFG reliability re-weighting of the diffusion (already named!).
WRITE / GROW organs (the #2/#3 program):
- `grounding_acquisition_loop.py`, `reading_grounding_loop.py`, `hdlab/learner/*` -> write nodes/edges into
  the graph; the consolidation/cleanup organ prunes/merges on it.
EXISTING graph/propagation prior art to REUSE (don't reinvent):
- `wordnet_polarity_propagation.py` (spreading activation primitive), the ConceptNet KG organ + multi-hop
  inference, `ultrametric_clustering` (WIRED) for sense merge/split.
CAVEAT: this is a substrate-CENTRAL change (a new intrinsic organ many read-outs route through) -> Q111
strategy lands; verify each adjacent organ's brain-fidelity + optimization potential before wiring (do not
map-only). The invariant holds: WordNet/ConceptNet/PPR are static glass-box assets; NO LLM at inference.
