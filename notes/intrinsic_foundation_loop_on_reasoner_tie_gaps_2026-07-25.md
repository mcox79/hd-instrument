# INTRINSIC FOUNDATION LOOP on the reasoner's OWN tie-gaps (design-of-record 2026-07-25)

USER (2026-07-25): the substrate's LEARNING must intrinsically (1) DETERMINE it needs foundation,
(2) ACQUIRE info in whatever rep is optimal + consistent, (3) SLEEP-consolidate to tie things together.
"let's do it - make it happen and verify it works." => close the ingestion-learn-sleep loop AROUND the
reasoner's own gap signal + VERIFY end-to-end IMPACT (tie-resolution), not just "it ran".

## THE INTRINSIC LOOP (compose banked pieces; do NOT rebuild them)
1. GAP DETECTION (intrinsic, NO hand-picking): run hdlab/reasoner.py on ARC-Challenge; its OWN outputs
   flag gaps = TIES (both choices co-derive; the 44 GENUINE ties, tie_transition_detail.json lemma) +
   ABSTAINS (no derivation). These ARE the substrate saying "I lack the meaning to decide/derive here."
2. ACQUISITION (ANSWER-AGNOSTIC = the anti-leak crux): for the CONCEPTS in each gap (NOT the answer),
   acquire discriminating definitional/propositional facts from WorldTree tablestore (KINDOF / per-topic
   DEFINITION / IFTHEN / USEDFOR / SYNONYMY) through the hd_fact_store trust-gate (hdlab/hd_fact_store.py,
   29531). Autopsy showed the tie discriminators are DEFINITIONAL/DIRECTIONAL (solute=the-dissolved-one;
   photosynthesis->sugar+O2; heat-removed->condensation), NOT sensorimotor -> definitional facts are the
   right acquisition. Learner-MDL (29487) picks encoding (rule vs episodic).
3. CONSOLIDATION (sleep, ties-together): sleep-loop over the acquired facts -> generalize to a rule where
   compression>=1, else KEEP_EPISODIC (definitional specifics = assignment-lookup, episodic EXPECTED, fine).
   Link acquired facts to the reasoner's concept nodes.
4. RE-DECIDE (wire at reasoner decision seam self.enc / _combiner_score): the choice whose proposition is
   SUPPORTED by the acquired discriminating facts wins. GENERAL meaning-match, NOT hand-wired fact->choice.

## VERIFY (can-fail ladder, leak-controlled -- the whole point)
- ARM 0 BASELINE: reasoner ties, correct_after ~0.36 (reproduce 29570 exact = positive control).
- ARM 1 ORACLE-ACQUISITION (upper bound / CEILING): GIVEN the answer-agnostic discriminating definitional
  fact for the tied concepts, can a meaning-match tie-break resolve the tie? If even given the right acquired
  fact the tie does NOT break -> the loop CANNOT work over this rep (honest kill, routes deeper). This arm
  is the decisive diagnostic.
- ARM 2 AUTONOMOUS LOOP (the real number): substrate DETECTS gap -> acquires the fact ITSELF (retrieve
  definitional facts for gap concepts through trust-gate) -> consolidates (sleep) -> re-decides. No answerKey
  ever seen; gap-flags computed answer-agnostically.
- ARM 3 SCRAMBLE (must-fail): acquired facts SHUFFLED across concepts -> the gain MUST collapse (proves the
  RIGHT acquired meaning drove it, not just "more vectors").
- REPORT: ARM2 vs ARM0 (does the intrinsic loop lift ties?) + ARM2 vs ARM1 (fraction of ceiling the
  autonomous acquisition captures = acquisition/retrieval-precision gap) + ARM3 collapse + gold_only 26@1.00
  preserved. HELD-OUT, scramble-clean, difficulty-on.

HONEST EXPECTATION (deflated): may be MIDDLE/HONEST-NEG because the decision meaning-match is still over thin
GloVe. ARM 1 is the crux: ARM1 breaks ties => bottleneck is acquisition-precision (TRACTABLE, huge result);
ARM1 also fails => the decision needs deeper grounding than definitional-fact-supply (cheaply learned).
EITHER outcome is genuinely informative -- a real can-fail test, not a construction-determined win.

## POINTERS (reuse, don't rebuild)
- reasoner.py (DerivationReasoner; nodes_for/_content_words seam line 278/353; _combiner_score decision)
- tie set: data/exp_arc_reasoner_link_precision_tie_prune_v1/tie_transition_detail.json (GENUINE ties)
- hd_fact_store.py (29531 trust-gate); Learner-MDL (exp cells for 29487); sleep-loop cell (ingest_learn_sleep_loop cycle cells)
- WorldTree tablestore v2.1: data/corpora/worldtree/.../tablestore/v2.1/tables/{KINDOF,SYNONYMY,...}.tsv + inference-patterns DEFINITION tables
- autopsy: scratchpad/binder_preflight.py + tie-question dump (definitional/directional discriminators)
- rules already loaded: data/rules/arc_science_typed_rules_v1.json (233 vetted)
LOCAL-only; no push. VET on landing (skunkworks) BEFORE the result drives anything.
