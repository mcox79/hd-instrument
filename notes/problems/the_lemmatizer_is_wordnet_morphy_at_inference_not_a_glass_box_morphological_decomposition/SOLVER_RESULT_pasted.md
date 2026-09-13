## pasted by the owner 2026-09-12 22:35 (raw; strategy reads this) — the solver session's submission brief

SUBMISSION — the_lemmatizer_is_wordnet_morphy_at_inference_not_a_glass_box_morphological_decomposition   (status: SOLVED; solver scope, WIP until owner DONE)

THE BAR (met): one glass-box morphology organ (exception store + affix-detachment rules + lexical check, from a one-time
offline export), every read-path morphy call repointed, BYTE-IDENTICAL lemmas on the real input distributions, no nltk
on the read path — OR a numbered located negative. Delivered the port AND a brain-faithful optimum. NO hdlab writes
(Q111 — proposed diff in SOLVED.md); NO external tool at inference; all claims floored + info-free-twin controlled.

RESULT
• PORT (byte-identical, the bar): exact pure-python port of nltk 3.9.4 morphy reading a 2.19 MB offline WordNet-3.0
  export (data/frontend_assets/morphology/; build script committed, asset gitignored). 0 DIVERGENCES over 6,326,530
  raw comparisons (entire lexicon × {n,v,a,r,None} + all exception keys + 1.08M inflections + 29,217 UD-EWT/GUM prose
  tokens) AND 0 on the full hdlab lemma path (lemma_word/lemma_verb/is_known_word/concept_lemma/gek). External tool
  removed with zero downstream change; ~80× faster (cold load + first lemma 0.11s vs nltk 8.9s).
• OPTIMUM (measured, brain-faithful): morphy is a surface-first heuristic wrong ~4/100 vs human gold lemmas on modern
  prose (0.9603; dominant error = returns the surface when it is coincidentally a lemma: years→years, men→men). The
  dual-route obligatory-decomposition organ (Rastle-Davis + Pinker-Ullman) hits 0.9836 (+0.0233, doc-paired CI
  [0.0221,0.0246]; n=195,045/285 docs), info-free wrong-POS twin loses (0.7255), NET +4,553 fixes; GENERALIZES across
  24 genres (23/24 CI-sep, all positive, zero fitted params).
• UPSTREAM (owner directive — trace where signal is lost): the live path lemmatizes with NO POS (noun-first), and that
  missing POS costs +0.0484 — LARGER than the morphology fix. So realizing this fix REQUIRED going upstream: prototyped
  a mathematically-BF POS (generative count-based HMM, forward-backward GRADED posterior — no gradient, no tool);
  feeding it to the morphology recovers 49.5% of the perfect-POS gain (0.9389→0.9614), shuffled-POS twin loses.
• UPSTREAM-OF-POS BF (owner: confirm, or we still fail): traced top-down — tokenizer is glass-box regex (confirmed NO
  spaCy/nltk anywhere on the read path) = BF; POS inference = BF; the ONE residual is POS-category ACQUISITION from
  supervised labels (admissible offline supply, passes the no-tool-at-inference invariant, but not the brain's
  UNSUPERVISED distributional induction — named as the deepest next fix).

CONTROLS: exhaustive oracle byte-identity (0 div); info-free wrong-POS twin (loses); rule-snapshot self-test (guards
nltk drift); 24-genre generalization; frequency-arbitration probe (located sub-negative — WordNet counts conflate
inflected/lexicalized readings). Named downstream witnesses at HEAD: test_fused_sense_ranker_live 8/8, test_meaning_
fusion_live_coverage 38/38 (byte-identity preserves both); test_cn_conceptkey_binding RED at HEAD on a crude-vs-wire
check independent of morphy (port neither causes nor fixes it).

BF STATUS: glass-box morphy port = BF (exact computation, no tool at inference); dual-route optimum = BF (validated to
exceed on human gold, twin-controlled, generalizes); BF POS prototype = BF at inference (count-based generative graded
posterior), acquisition = supervised-label offline supply (residual → unsupervised induction). AUDIT UPDATE: rung 1
(lemma) moves BF_SPIRIT-w/-external-tool → BF (glass-box) on landing; new recorded deviation = POS-generic live path.

KEY REALIZATION: morphy is a surface-first ENGINEERING heuristic, not the brain's obligatory decomposition — the same
insight makes the port trivially faithful AND makes the brain-faithful organ exceed it; and the biggest lemma-rung
signal loss is upstream (the non-BF POS input), exactly the owner's thesis.

NEXT STEPS: [HIGH] land the byte-identical port (hdlab, strategy/Q111); [HIGH] the POS tagger is the real upstream
lever (raise count-based accuracy; close the acquisition gap with unsupervised category induction — the deepest BF
fix); [MED] land the dual-route optimum with a rebuild of lemma-keyed stores; [MED] the 404-break lexicalized-plural
store; [MED] the WordNet-taxonomy read-path consumers (separate problem).

REVERIFY: .venv/Scripts/python.exe verification/test_glassbox_morphology.py   (4/4: rule-snapshot, byte-identity,
exceed vs gold twin-controlled, required-upstream-POS-upgrade). FILES: experiments/{build_glassbox_morphology_asset,
glassbox_morphology,exp_glassbox_morphy_byte_identity,exp_morphy_gold_lemma_diagnosis,exp_dualroute_morphology_exceed,
exp_dualroute_generalization,exp_dualroute_optimize_and_upstream_trace,glassbox_pos_bayes,exp_glassbox_pos_bf_and_
morphology_stack}_v1.py (+ glassbox_pos_trigram.py, an unvalidated richer-cue scaffold), verification/test_glassbox_
morphology.py, data/frontend_assets/morphology/, SOLVED.md. NO hdlab writes (diff proposed).
