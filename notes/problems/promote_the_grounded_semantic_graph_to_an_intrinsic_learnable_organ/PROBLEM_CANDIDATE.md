---
slug: promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ
status: PROBLEM_CANDIDATE (solver-proposed; strategy to register/prioritize)
proposed_by: solver (grounding_does_not_accumulate... thread, 2026-09-01)
priority_suggestion: HIGH -- this is the project north star (LEARNER-ON via a CLEAN FOUNDATION; STRUCTURE is the lever)
---

# Promote the GROUNDED RELATIONAL SEMANTIC GRAPH to an intrinsic, learnable substrate organ

## WHY NOW (the evidence that forces this)
Drilling the `grounding_does_not_accumulate_over_repeated_exposures` ceiling to the bottom established, on gold
labels, that:
1. Per-context sense selection is NOT a vector-cosine problem -- 8 feature-cosine prototypes (grounded re-rank,
   context-gating, gloss-embedding, usage sense-embeddings, GloVe/MiniLM contextual) all sit at the dominant-
   sense baseline. Sense is TAXONOMIC/RELATIONAL (ATL hub; taxonomic-vs-thematic double dissociation, Mirman 2017).
2. The brain does it by SPREADING ACTIVATION over a relational semantic network (Collins & Loftus 1975) that
   SETTLES into a sense attractor (Rodd 2004). Personalized PageRank == random-walk-with-restart == the diffusion
   form of spreading activation (PINNED). Built glass-box/LM-free over WordNet (exp_ppr_spreading_activation_wsd_
   wic_v1): WiC dev 0.618 CI[0.580,0.657] -- BEATS the naive floor CI-separated + gloss-edges load-bearing (the
   right mechanism, "LLM-gated" REFUTED) -- but the context-shuffle twin (0.571) is close (per-context signal
   +0.05, not CI-separated), because it is a SIMPLIFIED UKB over a FROZEN, hand-built inventory.
3. We OWN the graph (WordNet, 117,659 synsets) but used it as a FLAT LOOKUP, never as a network to diffuse over.

CONVERGENCE: the original problem ("grounding does not accumulate over reading") is the SAME problem -- meaning
never accumulated because it was written to a FLAT ANCHOR STORE, not a structured GRAPH. The fix and the north
star are one: a grounded relational semantic graph, READ by spreading activation, GROWN from reading.

## THE BAR (what counts as progress; a rigorous negative is a full PASS if located)
A grounded, augmentable semantic-graph organ, read by spreading activation, that (a) CI-separates above the MFS-
AGREEMENT / context-shuffle-twin baseline on gold WSD/WiC (not just the naive floor), OR (b) if it cannot,
LOCATES the residual as the WordNet<->task GRANULARITY/COVERAGE gap (foundation, not algorithm) with the evidence
-- and in EITHER case reframes the reader's grounding write-path from a flat store to the graph.

## APPROACH (the augmentation ladder; each an ablation with the twin control)
STATIC (offline foundation, shelf-only, glass-box):
- [DONE/measuring] #1 GROUNDED NODES: attach predicted-Binder-65 to synsets (GROUNDED_PPR).
- DISAMBIGUATED gloss edges (proper WordNet++/UKB: MFS-disambiguate gloss words, or the Princeton Gloss Corpus if
  fetched) -- the drill's #1 lever (UKB ~67 vs vanilla ~58-62). SyntagNet edges (SyntagRank ~72) = external fetch.
- FOLD IN CONCEPTNET (ALREADY INGESTED: conceptnet_ingest_v1 / conceptnet_kg / multihop) -- commonsense edges.
- Edge weighting by information content (wordnet_ic on disk); tune damping ~0.85 / iters / ppr_w2w joint.
LEARNED (the north star; LARGE):
- GROW: reader adds nodes/senses/edges by structure-mapping to known concepts (grounding-by-relation; Tse 2007).
- RETUNE: usage sharpens edge weights (Rodd basin-deepening). CONSOLIDATE: prune/merge on the graph.
- OWN GRANULARITY: merge/split senses by usage (escape WordNet's fixed inventory; the ~0.75-0.80 WSD cap).

## ASSETS ON DISK
nltk WordNet (117,659 synsets + glosses) + wordnet_ic; scipy sparse (PageRank); spaCy; predicted-Binder-65;
`hdlab/wordnet_polarity_propagation.py` (spreading-activation primitive -- REUSE); ConceptNet KG organ + multi-hop;
`ultrametric_clustering` (WIRED, for sense merge/split); gold WiC + `tools.load_wsd_benchmarks`. NO LLM at inference.

## SUBSTRATE IMPACT (evaluate each adjacent organ for fidelity+optimization BEFORE wiring -- not map-only)
Read-out routes through the graph: reading_grounding_loop.canonicalize; distributional_meaning_channel (-> a node
spoke); meaning_fusion / meaning_operation_router / conceptual_meaning / semantic / grounded_similarity /
lexical_similarity; situation_reader + situation_model_* + convergent_cue_reader + predictive_reader (seed the
diffusion); semantic_control (the PFC/IFG reliability re-weighting of the walk). Write/grow: grounding_acquisition_
loop, reading_grounding_loop, hdlab/learner/*, the consolidation organ. Q111: strategy lands; substrate-central.

## CONTROLS / TRAPS (banked this thread)
- Compare to the MFS-AGREEMENT / context-shuffle TWIN, NOT the naive 0.50 floor (the floor over-credits dominant-
  sense). - Gloss edges are load-bearing (NO_GLOSS ablation ~ MFS = the pinned trap). - Believe FULL over SMOKE
  (smoke 0.673 overstated the full 0.618). - Verify too-good numbers (the WiC-from-WordNet-examples leak: 0.83->0.52).
