---
owner_verdict: DONE
---

PROBLEM: build_the_composed_scalar_magnitude_meaning_channel   —   STATUS: SOLVED
(WIP until owner_verdict: DONE; reverify: .venv/Scripts/python.exe verification/verify_composed_magnitude_channel.py)

WHAT WAS BUILT
- The composed scalar-magnitude meaning channel (ScalarMagnitudeChannel, glass-box): dimension-select (semantic
  control) → grounded oriented signed-magnitude axis (antonym poles for evaluative dims; Lancaster perceptual for
  denotational) → markedness degree (−log freq) → FPE(log degree) place code in FHRR, comparator = unbind.
- The word-class operation router: gradable adj → magnitude op; noun/verb/classificatory-adj → gloss.

BAR CLEARED (full power, CI-verified)
- Composed channel beats BOTH the incumbent single cosine (0.100) AND the strongest single sub-op (antonym axis
  0.412), pooled multi-dim recovery 0.504: +0.404 and +0.092 [+0.083,+0.101] CI-sep; random/shuffled/structure-free
  twins lose. FPE-log preserves the Weber property on-substrate after linear→log (LOG ratio-CV 0.000 vs LINEAR
  0.79); comparator unbind decodes log-ratio corr 1.000.
- Router beats BOTH a gloss-only reader (0.424; misses gradable-adj magnitude: op 0.756 vs gloss 0.181, +0.575
  CI-sep) AND a magnitude-only reader (0.339; magnitude is not a similarity op — noun sim 0.066 vs gloss 0.599);
  N/V read-outs identical under routing (no regression).

THE DISK SHARPENED THE BRIEF (more brain-faithful than "three operations")
- Pole and degree UNIFY into one oriented place code (opponent pools → peaked code → oriented axis; the oriented
  projection orders within-scale intensity 0.72 ≈ markedness 0.77). The composition's real win is dimension-ROUTING
  + per-dim GROUNDING + the FPE-log Weber COMPARATOR, not a 3-readout stack.
- Comparison system (the brain's actual use): composed beats the incumbent on human "which is more X" 0.762 vs
  0.554 (+0.21 CI-sep), Moyer distance effect +0.34; the categorical pole gives the semantic-congruity structure
  (same-pole graded / cross-pole categorical, AUC 1.00) the incumbent inverts (0.22).

DEEP OPTIMIZATION DRILLS (walls interrogated, not accepted)
- Sharper gradability gate: WordNet pertainym flags classificatory adjectives (catches 303 has_antonym misroutes).
- EVALUATIVE space is BIVARIATE, not one bipolar axis: an orthogonal, embedding-recoverable co-activation/
  ambivalence dimension (0.552 held-out) the valence axis is blind to; separates ambivalent-vs-neutral 0.90 vs 0.63.
- Opponent-pool readout null was a WEAK-SUBSTRATE artifact (antipodal GloVe centroids), not a ceiling — researched
  and refuted; the brain's pools are genuinely separate.
- Negative-differentiation ASYMMETRY is LEXICAL, not representational: count-controlled on NRC EmoLex it vanishes/
  reverses (positive categories more distinct) — consistent with Cowen-Keltner 2017.
- Affect is HIGH-DIMENSIONAL and that's a SUPPLY choice, NOT a substrate limit: every basic emotion carries variance
  beyond VAD; the NRC supply is 5.5-D; GloVe compressed it to 2.0 — but the FHRR substrate encodes all 8 emotion
  channels losslessly (recovery AUC 1.00, restores 5.55-D, separates anger-vs-fear 1.00 where VAD is at chance 0.36).

PROPOSED HDLAB DIFF (strategy lands it, Q111)
- ADD hdlab/scalar_adjective_operation.py = the composed channel (per-dim grounded oriented axis; markedness degree;
  bind(DIM_key, POLE_key, FPE_log(degree)); comparator = unbind). Reuses hdlab/binding, situation_model_accumulate.
- UPGRADE hdlab/quality_relation.py Channel B from LINEAR to FPE-LOG + pole/dim binding; replace the 23-word hand
  lexicon with a grounded-degree lexicon.
- ROUTE the meaning read-out by word class; gate = (has_antonym OR satellite) AND NOT pertainym-relational.
- GROUND evaluative dims MULTI-DIMENSIONALLY: valence + co-activation (SentiWordNet) + specific-emotion channels
  (NRC EmoLex, ~5.5-D) bound as separate FHRR channels — not a single valence axis, not read from GloVe.
- Wire dimension selection to hdlab/semantic_control. Do NOT replace verb gloss with VerbNet; do NOT use one global
  ATOM axis; do NOT read fine degree from the projection (markedness is the signal).

NOT ESTABLISHED / HONEST CAVEATS
- The composed>best-sub-op margin is driven by concreteness routing; on evaluative dims composed==antonym axis.
- Gradability gate is coarse (valence ≠ gradability); routing is justified by magnitude-is-not-a-similarity-op.
- pole-KEY vs pole-SIGN are equivalent for congruity (markedness asymmetry untested on available golds).
- Remaining frontier is DATA-blocked, not mechanism-blocked: comparison RT/error, comparison-class re-anchoring,
  experiential/appraisal emotion differentiation — need behavioral/physiological data static rating golds lack.

FILES: experiments/exp_composed_magnitude_channel_v1.py, exp_operation_router_v1.py,
exp_composed_magnitude_comparison_v1.py, exp_opponent_pool_readout_v1.py, exp_bivalent_evaluative_channel_v1.py,
exp_negative_differentiation_v1.py, exp_negative_differentiation_emolex_v1.py, exp_evaluative_high_dimensionality_v1.py,
exp_multiemotion_fhrr_code_v1.py; verification/verify_composed_magnitude_channel.py; 2 RESEARCH notes + SOLVED.md;
data/* dirs + data/nrc_emolex/. NO hdlab/ changed.
