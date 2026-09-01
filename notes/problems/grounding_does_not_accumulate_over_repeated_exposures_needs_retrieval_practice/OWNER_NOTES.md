---
owner_verdict: DONE
---

SUBMISSION — grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice
STATUS: SOLVED (representation-bound negative = the brief's full-PASS-if-located) + full lift demonstrated
        + break-through mechanism PROVEN glass-box, with the ladder to the max result specified.

1. NEGATIVE (the brief's PASS). Retrieval practice, built faithfully (Mozer 2009 Eq.7 + PBV), does NOT
   fix the 59% CONSOLIDATION_FAIL wall: rate-independent selection-AUC at chance (0.486/0.503, CI incl
   0.5); grounding precision flat at the ~0.30 base rate. The wall is REPRESENTATION-bound at the
   SELECTION level — the correct anchor is retrievable (top-10 ~85% under every encoder incl. a full
   parser) but not selectable by any distributional read-out. Witness: 21/21 checks PASS.

2. FULL LIFT (brain-foundational: ATL hub-and-spoke). Grounded sense-selection (experiential/Binder
   features) roughly DOUBLES correct sense selection over the distributional read-out (~0.20 -> ~0.45,
   2-seed, CI-separated; info-free twin loses; measured≈predicted-Binder, not an imputation artifact).

3. THE DEEP WALL. Sense selection is TAXONOMIC/RELATIONAL (ATL is-a graph; taxonomic-vs-thematic double
   dissociation, Mirman 2017), NOT a vector-cosine problem — 8 feature-cosine prototypes plateaued at the
   dominant-sense baseline. The brain does it by SPREADING ACTIVATION over a relational semantic network
   (Collins & Loftus 1975) that settles into a sense attractor (Rodd 2004).

4. BREAK-THROUGH (proven, glass-box, LM-FREE, brain-faithful). Personalized PageRank == random-walk-with-
   restart == the diffusion form of spreading activation. Run over WordNet++ (relations + gloss edges) with
   DISAMBIGUATED glosses: WiC dev 0.652 (CI [0.614,0.690]), CI-SEPARATED above the context-shuffle twin
   (real-twin +0.078) — genuinely context-driven, at the field's knowledge-based-WSD level (LMMS 0.677
   needs a live LLM; this needs none). "LLM-gated" refuted. No external LLM at inference.

5. FINAL RUNGS TO THE MAX (the augmentation ladder; each an ablation with the twin control):
   [DONE] disambiguated gloss edges .................... WiC ~0.65 (clears the twin)
   + SyntagNet edges (SyntagRank) ..................... all-words ~0.72 (external fetch)
   + ConceptNet edges (ALREADY INGESTED on disk) + grounded Binder-65 nodes + IC-weighting (wordnet_ic)
   + THE LEARNED GROUNDED GRAPH: grow nodes/senses/edges from reading (structure-mapping), retune weights
     with usage (basin-deepening), develop own granularity ... toward the ceiling ~0.75–0.80
   CEILING/BOUNDS: WordNet↔task granularity caps knowledge-based WSD ~0.75–0.80; human IAA ~0.80. The last
   stretch is a foundation/granularity gap, not a selection-algorithm gap.

6. WHAT THIS REFRAMES. "Grounding doesn't accumulate over reading" = meaning was written to a FLAT anchor
   store, not a relational GRAPH. The fix and the north star are one: an intrinsic, grounded, LEARNABLE
   semantic graph, READ by spreading activation, GROWN from reading. Filed as the follow-on Problem:
   notes/problems/promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ/PROBLEM_CANDIDATE.md

FILES: experiments/{exp_retrieval_practice_consolidation_v1, exp_sense_wall_breakthrough_wic_v1,
  exp_glassbox_sense_embeddings_wic_v1, exp_contextual_encoder_paths_wic_v1,
  exp_ppr_spreading_activation_wsd_wic_v1}.py; verification/test_retrieval_practice_consolidation.py;
  notes/problems/<slug>/{SOLVED.md, RESEARCH_*.md, WIRE_PROPOSAL_*.md, NEXT_*.md}.
REVERIFY: .venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py   (21/21)
          .venv/Scripts/python.exe experiments/exp_ppr_spreading_activation_wsd_wic_v1.py --gloss-compare --mode full
HONESTY LEDGER: 6 self-caught over-claims corrected (WiC-example leak 0.83→0.52; 2-tries cluster inflation;
  seed-shuffle nulls; smoke 0.673→full 0.618; MFS-agreement-twin vs naive floor; "LLM-gated" retraction).
