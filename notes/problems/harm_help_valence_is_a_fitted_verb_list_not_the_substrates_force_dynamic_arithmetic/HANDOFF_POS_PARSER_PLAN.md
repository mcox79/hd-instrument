# HANDOFF + PLAN (read first after compaction) -- harm/help SOLVED; next = POS then parser

**Solver session (opus 4.8). Slug:** `harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic`.
**Constraints unchanged:** WRITE ONLY `experiments/`, `verification/`, this problem folder. NOT `hdlab/` (Q111 -- strategy
lands; propose diffs). Glass-box, NO external LLM at inference. THE DISK OUTRANKS THE BRIEF. Full report discipline
(TLDR/QUESTIONS/NEXT STEPS, plain language). Strategic forks = PROSE, never AskUserQuestion.

## 1. harm/help itself is DONE + brain-foundational (SOLVED.md is complete; WIP until owner_verdict: DONE)
The decision was a fitted verb-LIST + in-process FrameNet parse -> rebuilt as the **force-dynamic arithmetic**:
`harm/help = sign(force_effect x endstate_valence)` (Wolff force structure REUSING `force_dynamics_lexicon`/
`patient_tendency`; endstate valence = grounded Warriner via `affect_lexicon`), gated by **graded affectedness =
E[proto-patient degree | WordNet sense]** (Beavers x SemCor sense-freq; tau=0.40 plateau), minus subject-experiencer
psych verbs (`psych_verb_frames`). LIVE: **0.944 vs frame-list 0.778, paired +0.167 CI[+0.056,+0.278]**, no-regress,
info-free twin loses. Decision oracle ceiling **0.958** (residual = `scratch`, CONFIRMED WSD-bound: Warriner conflates
scratch-itch/scratch-skin; result-participle read doesn't help; a bodily-integrity prior was TESTED + REJECTED).

Also built + witnessed (all reuse BF machinery, NOT hand islands):
- **Bayesian POS category posterior** (`exp_pos_bayesian_category_v1.py`): P(NOUN|word,DP-head) = lexical prior x
  syntactic likelihood (syn-LR=8.08); recovers civilian/intern/medic; target recall 0.40->0.70.
- **Coref pronoun attribution** (`exp_fd_harm_help_coref_pronoun_v1.py`, witness 2/2): Centering resolver +
  gendered-role-noun supply -> pronoun harm/help patients attributed to the right character **0.00 -> 0.917**.
- **RIGOROUS extraction fix** (`exp_fd_harm_help_learned_extraction_v1.py`, witness 3/3): (a) deterministic VOICE
  labeler correction (be/get+participle nsubj -> nsubj:pass); (b) LEARNED `argstruct_patient_ranker` (Bayesian cue
  integration) for obj/obl + its P as a detection gate. Corpus recall 0.718 / precision 0.779 (= tuned hand rules,
  but principled). This is the DEPLOYMENT (not the hand extractor `exp_fd_harm_help_robust_extraction_v1.py`, which
  was the DIAGNOSTIC/harness).

**Witnesses (all green):** `test_fd_harm_help_arithmetic.py` 9/9, `test_pos_nominal_head_correction.py` 6/6,
`test_fd_harm_help_robust_extraction.py` 8/8, `test_fd_harm_help_coref_pronoun.py` 2/2,
`test_fd_harm_help_learned_extraction.py` 3/3. Ledger: malformed 0.

## 2. THE KEY FINDING -- signal-loss trace (this is why POS+parser are next)
`exp_fd_harm_help_signal_trace_v1.py` (THE SCOREBOARD -- gold-ablation on UD-EWT, n=627 affecting undergoers):

| feed each stage GOLD | undergoer recall | isolates |
|---|---|---|
| full pipeline | 0.7895 | -- |
| gold POS | 0.8581 | POS loss ~0.07 |
| gold heads | 0.8612 | parser-head loss ~0.07 |
| gold POS + gold heads (LABELER ceiling) | 0.9075 | labeler ~0.09 |

**Per-lost-undergoer: POS 30% / parser-head 36% / arc-LABELER 33%** (NOT scorer-bound -- my earlier claim was WRONG).
- LABELER third: **FIXED** (voice correction + learned argstruct ranker; §1 rigorous fix).
- POS third: **LONG-TAIL, 16 error classes** (PRON->SCONJ 7, NOUN->VERB 6, VERB->AUX 5, ...) -> retraining, NOT a
  deterministic fix.
- PARSER-head third: **DIVERSE attachment** (patient mis-attached to wrong VERB 20x / NOUN 16x / ADJ 6x) -> scorer
  retraining. Confirmed WALL: exact-MST decode +0.0016; richfeat 0.78 / mst_retrain 0.72 (both WORSE); marginals
  small (+0.0065 per substrate's own landing, though mu[widow<-robbed]=0.459 recovers specific 1-best misses).

Ceiling math: perfect POS+parser -> ~0.90-0.92 (labeler-corrected). Real-prose extraction headroom ~0.75 -> ~0.90.

## 3. THE PLAN (owner-agreed ordering: POS first, parser second, as SEPARATE cluster briefs)
**POS is the immediate next work (higher ROI: cascades into the parser -- ~0.05 of the "parser" loss is bad POS).**

### STEP A -- prototype a brain-foundational POS tagger (the tractable, high-ROI one). Two BF routes to try:
1. **Distributional lexical-category posterior** (generalize the nominal-head Bayesian fix to ALL positions):
   P(UPOS_i | word_i, syntactic-context) = distributional/lexical prior P(UPOS|word) x contextual likelihood.
   Prior from a large corpus / the shipped embeddings (`hub_ppmi_svd_200d.pkl`, `meaning_sense_signatures`) / WordNet
   -- the brain learns category from DISTRIBUTION (Harris), NOT a supervised perceptron. Current `pos_tagger.py` is
   NOT_BF (avg-perceptron, hard Viterbi).
2. **Graded POS marginals**: `pos_tagger.py`'s `__bf_note__` says it "discards marginals" -- use the forward-backward
   POSTERIOR P(tag|position) (graded category, brain-faithful) instead of hard Viterbi, and let the parser/labeler
   consume the uncertainty. (Check if StructuredPerceptron exposes marginals / add forward-backward.)
   TARGET the 16-class long-tail (esp. PRON->SCONJ relative pronouns, VERB<->AUX, NOUN<->VERB).
   MEASURE on `exp_fd_harm_help_signal_trace_v1.py` (gold-POS row is the ceiling for the POS third); expected
   who-was-affected ~0.75 -> ~0.83. RE-MEASURE the cascade into the parser after.

### STEP B -- parser (SECOND, only after POS; bigger build, bounded payoff ~0.85-0.90):
   Constraint-based / graded parser. Substrate BF base: `hdlab/graded_parser.py` (exact Matrix-Tree marginals, Koo
   2007). Scorer needs better features/retraining (the alternative assets are worse). Do POS first -- it may recover
   enough of the cascade to shrink the parser's marginal payoff. Same scoreboard.

### SCOPE: both as their OWN cluster briefs (parser/tagger are named fleet mega-clusters), NOT under harm/help.
Harm/help stays SOLVED -- do not hold it open.

## 4. PROPOSED hdlab DIFFS (Q111 -- strategy lands; all in SOLVED.md)
1. `force_dynamics_valence.harm_help` -> the force-dynamic arithmetic (retires the LU set + FrameNet parse).
2. `pos_tagger` -> the Bayesian nominal-head correction (+ the STEP-A BF tagger when built).
3. `arc_labeler` -> the deterministic VOICE correction (nsubj->nsubj:pass); route obj/obl through the existing
   `argstruct_patient_ranker`.
4. `_assign_affect` (situation_reader.py:2016) -> route through the reader's (e.lemma, patient) [affect-routing].
5. coref -> gendered-role-noun gazetteer extension.

## 5. REPRODUCE (scoreboards + witnesses)
```
.venv/Scripts/python.exe experiments/exp_fd_harm_help_signal_trace_v1.py            # THE scoreboard (POS/head/label)
.venv/Scripts/python.exe experiments/exp_fd_harm_help_role_corpus_validation_v1.py  # UD-EWT undergoer recall/precision
.venv/Scripts/python.exe verification/test_fd_harm_help_learned_extraction.py       # 3/3 (voice + learned ranker)
.venv/Scripts/python.exe verification/test_fd_harm_help_arithmetic.py               # 9/9 (the decision)
.venv/Scripts/python.exe tools/problem_ledger.py --check                            # malformed 0
```
Frontend assets: `data/frontend_assets/{pos_tagger_ud_ewt_upos.json, arc_parser_hashed_ud_ewt.npz,
arc_labeler_hashed_ud_ewt.json, argstruct_patient_ranker_ud_ewt.json}`. Gold: `data/corpora/ud_english_ewt/`.
Wrap the frontend tagger with `exp_pos_bayesian_category_v1.bayesian_correction` when measuring (POS cascade).
```
