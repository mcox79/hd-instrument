---
owner_verdict: DONE
---

SUBMISSION -- build_sg_lite_self_supervised_scale_generative_sense_predictor
status: SOLVED (advances the parent north-star). WIP until owner_verdict: DONE. No hdlab/ written (Q111). Witness 12/12 from source; ledger malformed: 0.
reverify: .venv/Scripts/python.exe verification/test_event_role_and_knowledge_scaling.py   # 12/12

RESULT (strict document-disjoint SemCor, subordinate senses, subject-weighted acc, n=2676; MFS floor 0.6831; a_s floors NB 0.198 / centroid 0.22; all margins CI-separated, info-free twin loses):
- a_s raised to 0.326 (APEX) over the located-negative 0.198 -- via the brain's biased-competition/semantic-control readout (diagnostic-context query) + knowledge, twin losing, no net regression over MFS. Meets the bar.
- The BRIEF's mechanism (role-filler/event target) is a RIGOROUS LOCATED NEGATIVE -- 4 convergent tests (frozen readout, end-to-end replacement, fusion, under the best readout), with the mechanism (event prediction is the wrong shape for gloss-reconstruction).
- KNOWLEDGE lever: a_s rises with reading corpus 8M 0.255 -> 41M 0.280 -> 277M 0.291 (paired CI-sep), then representation takes over.

THE FULL DRILL (where the signal is lost + how far we can go):
- Attribution (corrected mid-drill): the binding cap is the CONTEXT REPRESENTATION (Stage-2 query encoding), NOT coverage (48%-unseen recovered as well as seen) and NOT sense-discrimination (the grounded-graph organ caps 0.27 < word2vec 0.33).
- Ceiling, triangulated (3 research drills + 5 prototypes): the wall is CONTEXTUAL INPUT ENCODING; a small glass-box encoder on frozen w2v cannot cross it (< bag, over-fit AND regularized); static multi-sense embeddings are a research dead-end (circular, brain-unfaithful for polysemy). SOTA 0.53 needs a contextual encoder = the transformer/invariant fork (owner decision, in SOLVED.md).
- HEADLINE / NEXT FOCUS (owner-flagged): KNOWLEDGE GROWTH is the biggest lever (gloss 0.239 -> rich 0.320, +0.081 CI-sep) BUT MUST BE HIGHLY CONTROLLED -- raw/naive organic growth REGRESSES the score (-0.015; same as raw learn_from_text 0.274->0.267), only CONSOLIDATED (SyntagNet-quality) knowledge helps. The learner's growth MUST pass a consolidation/quality gate -- the "clean foundation" north star, now a measured REQUIREMENT.

CONTROLS: strict doc-disjoint (leak catch); shuffled-situation twin loses CI-sep at every point; wrong-role twin; fusion; random-context-subset; topic-confound split; paired bootstraps with CI + null p95. Witness 12/12 reproduces the located negatives, the knowledge rise, the top-k + diagnostic gains, and W9/W10 (knowledge growth boosts + must-be-controlled) FROM SOURCE.

FILES: experiments/exp_sg_lite_{event_role_readout,event_target_gestalt,knowledge_scaling,selectional_fit_readout,signal_loss_trace,diagnostic_context_readout,brain_gap_attribution,syntactic_query_wsd,context_encoder_wsd_v1,context_encoder_wsd_v2,knowledge_growth_diagnostic}_v1.py; verification/test_event_role_and_knowledge_scaling.py (12/12); notes/problems/<slug>/SOLVED.md; 3 research notes (notes/research_wsd_*_2026-09-03.md). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT sec 2b.

FOR STRATEGY (ordered): (1) [TOP] build the CONTROLLED knowledge-growth / consolidation gate for the learner -- biggest lever (+0.081) but NEGATIVE if uncontrolled; (2) wire the diagnostic-context (biased-competition) readout, default-off/witnessed/Q111; (3) the contextual-encoding fork past ~0.35 is a separate owner decision, not the near-term lever; (4) fix queue_add.sh (rc=1; box+venv healthy -- the direct-SSH-to-.venv bypass works).

DO NOT OVERCLAIM: a_s ~0.33 is far below human (~0.6-0.7; the 0.72 figure is OVERALL not subordinate-only) -- the residual is contextual encoding + grounding, glass-box-hard but understood, NOT an LLM requirement.
