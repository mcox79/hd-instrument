# Prereg: lexicon_induction_selectional_association_v1 (2026-08-04)

## Question
Can the substrate INDUCE new grounded WITHHOLD_ACT lexical items from raw corpus text, given only a
TINY seed (3 already-grounded withhold verbs) + the independent grounded VIEW-2 appraisal gate, using
a glass-box Resnik-style selectional-association scorer (pure corpus counting, NO borrowed
embedding/LLM/dependency parser)? If yes, the hand-supplied View-1 withhold lexicon in
`exp_self_extension_grounded_realprose_v1` is replaceable by an induced one that still mints
goal-blocker on real prose.

## Design
- Corpora (on disk, verbatim): little_women, anne_of_green_gables, tom_sawyer, wizard_of_oz
  (~400k words). Tokenized in-order (lowercase + strip punct), reusing
  `coreference_resolver.normalize_tokens` for the affect-gate view (the reused grounded organ);
  positional argument windows are needed for selectional structure (a bag-of-words set cannot encode
  argument position), so ordered tokenization supplements the set tokenizer -- honest caveat, still
  pure glass-box counting.
- SEED (tiny, 3, disjoint from targets -- fairness): {refuse, deny, conceal} (all genuine supplied-
  lexicon WITHHOLD_ACT verbs; occur enough: refuse~38 deny~14 conceal~11).
- HELD-OUT TARGETS (recovery ground truth, 9): {neglect, hide, forbid, prevent, decline, spurn,
  ignore, withdraw, resist} -- genuine withhold/refuse/block-family verbs, NOT seeded.
- NOISE CONTROLS (matched-frame, different meaning, 8): {carry, show, give, bring, hand, send, tell,
  take} -- transfer/communication verbs sharing the animate-agent / animate-beneficiary /
  abstract-patient ditransitive frame ("gave her the letter") but NOT meaning withholding. This is
  the discriminating Resnik-cap stress: selectional preference should conflate these if it types
  argument-shape not meaning.
- DISTRACTORS: auto-harvested high-frequency corpus verbs (detected by "follows a subject pronoun")
  so top-10 is genuinely competed for across the whole verb vocabulary, not just target+noise.
- Argument-structure signature per verb-lemma (pool surface forms), window W=4, MIN_OCC=4:
  f_agent_animate, f_benef_animate (right window), f_patient_abstract (right window). Animate +
  abstract lexicons are small general glass-box assets (pronouns + person-nouns; informational nouns),
  NOT tuned to test items, proper-noun-free.
- Resnik selectional-association score: prior_d = occurrence-weighted feature frequency over ALL
  pooled verbs; seed_d = pooled seed feature frequency; weight w_d = seed_d*log((seed_d+eps)/
  (prior_d+eps)) (per-class KL contribution); Score(v) = sum_d w_d * f_d(v). Rank descending.
- AFFECT GATE (VIEW-2, independent grounded appraisal): reuse `view2_goal_outcome` bit-identical from
  `exp_self_extension_grounded_realprose_v1`; affect_score(v) = fraction of v's occurrence-contexts
  that fire (animate desirer + net-unmet outcome). Gate = affect_score >= noise-control mean.
  Candidates passing BOTH (top-10 selectional AND affect gate) are the induced-and-gated set.
- FEED THE LOOP: replace `V1_WITHHOLD` with seeds + gated-recovered targets; re-run the self-
  extension loop; does it STILL mint goal-blocker (mints_goal_blocker) on the real goal-block items?
- Deterministic counting; multi-seed (affect gate + loop averaged over seeds 0..3 / the loop's 8).

## Pre-registered bands (set BEFORE looking; per the induction note part c + task bands)
- HARD_PASS: recall@10 >= 0.3 AND false-positives among noise controls < 3 (in top-10) AND the loop
  STILL mints goal-blocker with the INDUCED-and-gated lexicon. => substrate can induce new grounded
  lexical items from a tiny seed + independent view; supplied lexicon replaceable.
- HARD_FAIL: recall@10 < 0.3 OR FP >= 3. => confirms the distributional-affect cap (selectional
  preference recovers argument-shape not withholding-meaning). Pre-specified fallback: fold VIEW-2
  grounded appraisal INTO the induction-time score (not just post-hoc gate) and re-test. Report
  honestly, do NOT force a pass.
- MIDDLE: partial (e.g. recall passes but affect gate needed to clear FP, or loop mints on synthetic
  but not real gold items) -- report + route.

## Brain structures
- Selectional preference / argument-structure typing = left posterior temporal (pMTG) + IFG language
  network (argument-shape, meaning-independent).
- Affect gate = OFC/vmPFC interoceptive-affective appraisal over the situation model (the
  Andrews/Vigliocco 2009 second, non-distributional channel).

## Guards
Glass-box; NO borrowed embedding/LLM/parser (pure counts + normalize_tokens + reused view2);
predictive_coding / self_improving_loop / situation_model / view2 reused bit-identical; tiny seed;
targets held out (disjoint from seeds); deterministic; multi-seed; contamination-clean (seeds not in
target/noise sets); DIRECTIONAL (small n verbs, corpus-counting only).

## Cites
notes/research_autonomous_grounded_knowledge_induction_prior_art_2026-08-04.md (parts b/c/h);
experiments/exp_self_extension_grounded_realprose_v1.py (the validated self-extension milestone,
REAL_PROSE_SELF_EXTENSION_WORKS); Resnik 1996 (selectional association); Andrews/Vigliocco/Vinson
2009 (distributional-affect cap); Harnad 1990 / Cangelosi 2000 (symbolic theft = the mint operator).
