---
owner_verdict: DONE
---

SOLVER SUBMISSION — the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code

STATUS: PARTIAL (rigorous located-negative on the bar + a deep, fully-researched forward map). Glass-box, NO LLM,
NO hdlab/ writes (Q111 — results + proposed changes; strategy lands). Threads capped. Reverify:
.venv/Scripts/python.exe verification/test_ppc_meaning_representation.py  (57/57).
READ FIRST: SOLVED.md "WHAT TO INTEGRATE" executive summary; COMPONENT_REGISTER.md (created/proposed/evaluated + BF
state); HDLAB_INTEGRATION_SPEC.md; NEXT_GAP_generative_predictive_meaning.md; ALL_BF_UPSTREAM_TRACE.md; BF_AUDIT_UPDATE.md.

THE BAR RESULT: item 1 PASS — intrinsic precision = accumulated-evidence GAIN (Ma/Pouget) tracks correctness,
CI-separated above the point-vector peakedness baseline on TWO golds (SimLex+SimVerb). item 3 PASS — recall path
byte-identical. item 2 LOCATED NEGATIVE — precision-weighted fusion cannot beat equal-weight Bayes; a FITTED weight
also fails (0.317<0.324); thoroughly closed across the full exposure range (34k→534k lines) and both precision forms.
Equal-weight is Bayes-optimal here; the reweighting lever does not exist on this task.

LAND NOW (Q111 — all BF, all reuse, recall path byte-identical; HDLAB_INTEGRATION_SPEC.md):
  1) PARSER-FREE learned channel = ConceptSpace ROUTE-B store + DIRECTIONAL typing + existing PPMI — removes the
     NOT_BF pos_tagger/arceager at no accuracy cost; grows by reading (SEQ 0.07→0.16, ~80% of the ontology). BF.
  2) AFFECTIVE-VALENCE dimension (reuse affect_lexicon + Warriner) — un-blinds meaning to antonymy: syn-vs-antonym
     AUC 0.535→0.75 without WordNet, CI-sep, twin collapses. BF. (grounded_similarity omits this dimension.)
  3) convergent_cue_reader.w (a fitted OUR-INVENTION = NOT_BF) → intrinsic per-query GAIN RATIO; wire
     population-consensus RELIABILITY → deferral (CI-sep, +0.049 @ N=30 — the reader can tell when a read is reliable,
     achieved by a phase-diagram move off the sparse 3-cue operating point). BF.

EVALUATED / UPGRADED (BF state): pos_tagger/arceager NOT_BF → routed around; ConceptSpace ROUTE-B BF_SPIRIT → reused;
grounded_similarity BF_SPIRIT (relation-blind on antonymy, omits VAD); conceptual_meaning/WordNet BF_SPIRIT (only
antonym discriminator but supplied, gain anti-tracks); distributional_meaning_channel BF_SPIRIT (reuse its PPMI);
affect_lexicon BF_SPIRIT (reused); attractor/cleanup_family BF (recall path untouched, byte-identical). AUDIT UPDATE:
row 2 fix + non-BF register row 10 built; new deviation logged (convergent_cue_reader.w).

VS THE BRAIN / WHERE WE LOSE SIGNAL: best fused read ~0.26–0.33 MRR vs a competent reader ~0.7–1.0. Every component
is BF and near its own ceiling; the loss is REPRESENTATIONAL DEPTH — our channels encode "which words pattern alike",
not "what a word means". Measured: learned meaning is RELATION-BLIND (syn-vs-antonym AUC 0.51–0.53; only supplied
WordNet 0.87). Fixed in 3 brain-foundational layers, none using WordNet: (1) affective valence — BUILT/CI-sep;
(2a) scalar/spatial path-direction — BUILT (increase/decrease −0.78, open/close −0.54); (2b) transfer converses
(buy/sell) — WALL RESEARCHED TO THE BOTTOM: polarity is in the role-bound argument heads → needs argument-role
parsing + FHRR binding (co-occurrence of any flavor structurally cannot reach it), the generative-world-model layer.

NEXT PRIORITY STEPS: (1) land the 3 items above; (2) FILE the generative role-binding meaning channel (transfer
converses) — mechanism fully specified in NEXT_GAP §5c; (3) grow the learned channel by reading to ontology parity
(still rising at 1.5M); (4) end-to-end live grounding-coverage measurement.

HONEST BOUNDS: the stated bar's headline is a settled located-negative, not a capability win; the genuine wins
(parser removal, valence, deferral) sit on adjacent axes; nothing landed (by Q111 design). QUESTIONS: none blocking —
one call for you: whether to split the antonymy layers (1/2a/2b) into their own filed problem so this submission is
purely the PPC-representation result.
