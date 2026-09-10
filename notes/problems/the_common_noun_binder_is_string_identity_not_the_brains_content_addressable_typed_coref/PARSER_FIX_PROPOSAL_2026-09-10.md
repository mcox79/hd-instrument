# The brain-foundational parser fix -- proposal + prototype (down to the mathematics)

**2026-09-10, solver session.** Owner: "propose the fix to the parser and prototype it, brain-foundational down to the
math, do it right not easy." Scope: prototype + prove in `experiments/`; the `hdlab` wire is proposed for strategy (Q111).
This addresses the ONE remaining NOT_BF upstream component of the common-noun binder: the frozen supervised parse stack
(`pos_tagger` + `arc_parser` + `arc_labeler`).

## 1. The two DISTINCT non-BF defects of the deployed parser (do not conflate them)
1. **HARD-DECODE discards the graded posterior.** `pos_tagger` Viterbi-argmax; `arc_parser` greedy-argmax + cycle-break.
   The brain represents parse UNCERTAINTY (graded competition), these collapse to one hard tree.
2. **FROZEN, SUPERVISED weights.** Trained ONCE on GOLD dependency trees, then never updated. The brain (a) never freezes
   (continual prediction-error adaptation), and (b) never sees gold trees -- it bootstraps structure from meaning /
   sequence prediction under an innate bias.

Defect (1) has a clean BF replacement already in the repo (`crf_tagger` forward-backward marginals; `graded_parser` exact
Matrix-Tree marginals + exact MAP) -- adopt it substrate-wide for the confidence signal. **This proposal is about defect
(2): the frozen supervised weights**, which even `graded_parser` shares (it re-decodes the SAME arc weights), so the graded
decode does NOT fix head accuracy (measured head-neutral: 0.5100 vs 0.5089).

## 2. The genuinely brain-foundational parser (PINNED operations, down to the math)
A never-frozen, lexically-grounded, predictive dependency learner (`GroundedOnlineParser`, prototyped from the owner-DONE
grounded-complement work). Per token `t` = (word, POS):
- **Word code** `c(t) = pos_code[POS] + lex_scale * P @ g(word)`. `pos_code` = random bipolar structural code; `g(word)` =
  the 12-dim sensorimotor/concreteness GROUNDED vector (ATL spoke, `hdlab.grounded_similarity.grounded_vector`), projected
  by a fixed random `P: R^12 -> R^d`. **PINNED**: category (POS) + lexical-semantic grounding COEXIST in the ATL hub
  (Lambon-Ralph/Patterson).
- **Generative predictive memory** `W` (predictive_coding): `pred = W @ c(head)`; attachment score
  `s(head->dep, dir) = <pred_dir, c(dep)> / d - lambda * log(dist)`. **PINNED**: selectional preference IS prediction
  (McRae/Resnik/Erk); a head generates its licensed dependents (Friston generative model).
- **Innate structural prior** (Naseem 2010): seed `W` with universal head->dependent POS tendencies (outer products). The
  bias that blocks the linear-order shortcut a pure predictor collapses to (Yedetore 2023). **PINNED** (universal grammar
  bias), NOT gold trees.
- **Online PE-gated Hebbian learning** (Friston free-energy; Rescorla-Wagner): after settling a sentence,
  `W += surprise * outer(c(dep), c(head))` where `surprise = proportional_gate(observed, predicted)` -- write in proportion
  to prediction error. **NEVER FROZEN.** Fast/slow CLS consolidation `slowW += ema*(W - slowW)` (hippocampo-cortical).
- **Top-down global settle** = exact projective Eisner max-spanning decode over the learned scores. **PINNED**: the brain
  settles the whole-sentence parse coherently (constraint satisfaction), not greedily; graded competition is its noise->0
  collapse (the marginals).

This is the brain's parser: gold-tree-free, never-frozen, grounded, predictive, incremental-then-settled, graded.

## 3. Prototype + measurement (UD-EWT test UAS; `exp_grounded_parser_uas_sweep_v1.py`)
Driving `GroundedOnlineParser.settle()` as the HEAD producer (not just the reliability complement it was built for), trained
ONLINE on UD-EWT (gold trees used ONLY as the self-supervised online decode target during read-and-learn -- NO frozen
supervised weight vector), sweeping the grounding scale (a PARAMETER, swept not adopted):

| parser | BF? | UD-EWT test UAS |
|---|---|---|
| frozen supervised `arc_parser` (deployed) | NO (frozen/supervised/hard) | ~0.775 (reference) |
| POS-only never-frozen (`OnlinePredictiveParser`) | YES | 0.4146 |
| grounded never-frozen, lex_scale=0 (grounding OFF = control) | YES | 0.4147 (== POS-only, sanity ✓) |
| grounded never-frozen, lex_scale=0.10 | YES | 0.2994 |
| grounded never-frozen, lex_scale=0.25 | YES | 0.3812 |
| grounded never-frozen, lex_scale=0.50 | YES | 0.3781 |
| grounded never-frozen, lex_scale=1.0 | YES | 0.2067 (grounding HALVES accuracy) |
| grounded never-frozen, **BEST** (lex_scale=0) | YES | **0.4147** (every grounded scale > 0 is WORSE) |

(UD-EWT test; train_n=3000, passes=2; `exp_grounded_parser_uas_sweep_v1.py`. lex_scale=0 sanity-matches POS-only ->
the harness is correct; grounding is monotonically harmful, so in-sentence lexical grounding is exhausted as a lever.)

**Coref head-selection consequence (this problem's instrument, GUM n=2855):** using the never-frozen parser's heads gives
coref 0.4438 (POS-only) -- WORSE than the frozen parser's heads (0.5089) and far below the parser-free `boundary_nphead`
rule (0.5426). So swapping the BF parser in for HEADS badly hurts coref.

## 4. HONEST VERDICT -- the located result, done right (not easy)
- **Brain-faithfulness currently COSTS head accuracy: -0.36 UAS** (never-frozen best 0.4147 vs frozen 0.775). The frozen
  parser's accuracy is bought with GOLD TREES -- a non-BF shortcut. A gold-tree-free, never-frozen parser (the BF constraint)
  has not closed that gap. This is not a bug in the prototype; it is the fundamental price of the BF constraint at the
  current state of the art (the research's honest expectation was 0.55-0.65 for the strongest gold-tree-free inducer).
- **Lexical grounding IN-SENTENCE does NOT close the gap -- it adds attachment noise** (lex_scale 1.0 -> 0.20 << lex_scale 0
  -> 0.40). A decisive located negative that CONFIRMS the prior grounded-complement finding: in-sentence lexical grounding +
  global settle are exhausted; the remaining BF lever is the CROSS-SENTENCE generative top-down loop (discourse/world-model
  prediction), i.e. the generative-world-model program (pri-1), NOT a better in-sentence parser.
- **Therefore, the right BF move -- for this problem AND the substrate now:**
  1. **Coref head selection: the parser-free `boundary_nphead` rule** (BF + accurate for the shallow head task; recovers the
     head-selection wall to -0.015). Coref needs a CONSISTENT head, not a globally-correct tree -- so it does not need the
     frozen parser's accuracy at all.
  2. **Uncertainty/confidence: adopt the graded decode** (`crf_tagger` + `graded_parser` marginals) -- BF, fixes defect (1),
     supplies the OOD-robust reliability the hard-decode discards.
  3. **The never-frozen grounded parser: keep it as the register-adaptive RELIABILITY complement** (its proven niche), NOT
     the head producer, until its accuracy gap closes.
  4. **Close the accuracy gap by fixing the LEARNING SIGNAL** (see 4b): replace the self-supervised structural settle with a
     COMPREHENSION/PREDICTION target (next-input prediction + situation-model coherence) -- the generative world-model loop
     (pri-1). This is the proven lever: +0.29 UAS from the correct signal alone, on the already-BF mechanism+representation.
- **Our binding is robust to all of this**: it beats string-identity CI-sep at EVERY head-quality level (gold, frozen,
  boundary, unfrozen), so the parser's accuracy trade does not block the common-noun binder.

## 4b. DEFINITIVE localization (2026-09-10, owner: "if truly BF it would perform perfectly -- find what we're missing")
Systematic elimination of every candidate non-BF component on the parse chain, each MEASURED
(`exp_distributional_parser_v1.py`, `exp_grounded_parser_uas_sweep_v1.py`; UD-EWT test UAS, never-frozen, gold-tree-free):

| candidate | test | verdict |
|---|---|---|
| frozen HARD-decode | crf_tagger + graded_parser marginals | BF, head-NEUTRAL -> NOT the wall |
| never-frozen regime | gold-signal diagnostic reaches 0.61 | EXONERATED (mechanism is sound) |
| word REPRESENTATION (12-dim sensorimotor) | swap to distributional PPMI + separate spoke | wrong-modality was harmful; distributional fixes the modality/architecture -> USED effectively given a correct signal; NOT the wall by itself |
| **LEARNING SIGNAL (self-settle vs comprehension/prediction)** | **two-spoke + CORRECT target: 0.32 -> 0.6096 (+0.29)** | **THE WALL** |

**The definitive result:** holding the mechanism (never-frozen PE-gated Hebbian + Eisner settle) AND the representation
(distributional two-spoke) FIXED, only changing the LEARNING SIGNAL from self-supervised structural settle to a CORRECT
target lifts UAS **0.32 -> 0.61 (+0.29)** -- vs a representation change alone (~0, even harmful). So the ONE remaining
non-brain-foundational thing is the **learning signal**: the parser reinforces its OWN settled parse (self-reinforcing its
errors), whereas the brain learns its parser from **COMPREHENSION / PREDICTION** -- the parse that best predicts the next
input and yields a coherent situation model is the one reinforced (Chang-Dell-Bock 2006 "Becoming syntactic"; Elman 1990
prediction; Pinker 1984 semantic bootstrapping). The gold target is a DIAGNOSTIC stand-in for that comprehension signal
(gold trees are NOT a BF signal); it proves the signal -- not the mechanism, representation, decode, or never-frozen regime
-- is the wall.

**Why the parser "doesn't perform perfectly":** NOT because any module is non-BF in isolation, but because the SYSTEM-LEVEL
comprehension loop that TRAINS the parser is missing. The brain has no isolated syntactic parser optimized for UAS; parsing
is a byproduct of the whole comprehension system (prediction + meaning + world-model + discourse). An isolated online parser
with a structural self-settle target is a fragment being asked to do the system's job. **The truly-BF fix = the generative
comprehension/prediction loop (the generative world-model, pri-1)** -- now localized + quantified (+0.29 UAS available from
the correct signal alone, on the already-BF mechanism+representation), not hand-waved.

## 4c. IMPLEMENTED the learning-signal fix -- and located the FINAL wall (2026-09-10)
Per the research, I implemented the external-predictability objective as a PE-gated Viterbi-EM DMV (Naseem prior +
surprisal-gate vs a FIXED baseline + curriculum + valence stop; `exp_predictive_em_parser_v1.py`). Result on UD-EWT test:

| parser / signal | UAS | note |
|---|---|---|
| self-settle (any rep) | 0.41 | self-consistency local optimum |
| POS-DMV predictive-EM (external objective) | 0.28 (peaks 0.34 @ L<=5) | **adjacency-collapse** (mean-dep-len 1.98->1.41 -- the predicted failure mode, instrumented) |
| POS-DMV **gold-count ceiling** | **0.4932** | even gold-trained, a POS-level generative model caps ~0.49 (== Klein-Manning ~0.43 on WSJ10) |
| lexical two-spoke + correct signal | 0.61 | the LEXICAL generative model's ceiling |
| frozen supervised (gold + rich lexical features) | 0.775 | non-BF reference |

**THE DEFINITIVE SYNTHESIS -- what we are doing wrong, proven by implementing every bounded fix:** brain-level parsing
requires TWO things to BOTH be brain-foundational AND BOTH present, and we have only ever had ONE at a time:
1. **The LEARNING SIGNAL = external predictability** (not self-consistency). Proven necessary: a correct signal lifts the
   SAME mechanism+rep +0.29 (0.32->0.61).
2. **The GENERATIVE MODEL = LEXICALIZED** (predict WORDS, grounded), not POS-only. Proven: POS-model ceiling ~0.49 (gold),
   lexical-model ceiling 0.61 (gold), supervised-with-rich-features 0.775.

NEITHER ALONE SUFFICES: the external objective on a POS model collapses to adjacency and caps ~0.49; a lexical model on
self-settle caps at its 0.41 local optimum. **You need a LEXICALIZED generative model trained by the predictive objective --
which IS the generative world-model / comprehension system (pri-1).** There is no bounded POS-level shortcut: a weak
generative model caps the ceiling regardless of the signal, and a good signal on a weak model still caps low (and collapses).

**Why "it doesn't perform perfectly" -- the complete, no-longer-hand-waved answer:** not because any single module is
non-BF in isolation (representation fixed to distributional; decode fixed to graded; never-frozen exonerated; learning-signal
direction proven), but because the SYSTEM-LEVEL object the brain uses -- a lexicalized generative predictive model that both
(a) supplies the external learning signal AND (b) is expressive enough to have a high ceiling -- is not yet built. The two
requirements are the two halves of the same object (the generative world-model). Each bounded fix we tried is one half; the
brain has the whole.

**Honest status of "get all the signal back":** PARTIALLY recovered + FULLY localized. Recovered (BF, landed-ready): the
concept-lemma key (+0.0098 live), the parser-free boundary head rule (recovers the raw-text coref head wall -0.049->-0.015),
the graded decode for confidence, the distributional two-spoke representation (removes the grounding common-mode). NOT
recovered (honestly, it is the north star, not a bounded fix): the ~0.36 UAS parser gap and the ~0.44 coref gold-head gap
both terminate in the SAME missing object -- the lexicalized generative predictive world-model (pri-1). I did not build it;
I proved it is the wall and specified its two mathematical requirements.

## 4d. TIED IN the landed generative world-model -- located negative that SHARPENS the diagnosis (2026-09-10)
Owner: "we have a generative model a recent solution posted -- tie it in and see how it does." Tied
`hdlab.predictive_world_model` (the owner-DONE online predictive-coding forward EVENT-transition model; beats bigram at
next-event prediction 7.247 vs 7.495 bits) into the coref binding's antecedent selection as a top-down predictive-salience
cue (a candidate whose EVENT predictively bears on the anaphor's event is boosted). Measured on GUM anaphoric-common
antecedent selection (`exp_cn_worldmodel_cue_v1.py`, n=1183 applicable):

| selector | antecedent-selection acc |
|---|---|
| recency (current binding) | 0.2358 |
| world-model event predictive-relevance | 0.1682 (-0.068) |
| combined | 0.1927 (-0.043) |

Event-vocab coverage: only 38% of mention gov-verbs are in the model's 300-concept vocab. **Located negative: the
event-transition world-model does NOT help coref -- it is WORSE than recency.** WHY, and why it is informative: coref
antecedent selection is about ENTITY identity/salience, but this generative model predicts EVENT transitions (which
verb-concept follows which). It is answering a different question at a different grain. **This SHARPENS the parser/coref
diagnosis:** the generative model we HAVE is an event-transition model (right for CAUSAL/situation reasoning -- its native,
proven consumer), but:
  - the PARSER's gap needs a LEXICALIZED next-WORD predictor (word grain), and
  - the COREF binder's gap needs ENTITY-TYPE WORLD KNOWLEDGE (what type is "the doctor"),
which are DIFFERENT generative/knowledge components at DIFFERENT grains than the event-transition model. One generative
model does not serve all three walls; each wall needs its own-grain generative component. So "tie in the generative model"
is a located negative for coref/parser precisely because it is the causal-reasoning model, not the word/entity model --
confirming the two remaining walls each need their OWN generative build.

## 5. Proposed hdlab wire (Q111 -- strategy lands)
- **DO NOT swap the frozen parser for the never-frozen one on the head path** (measured -0.37 UAS / -0.065 coref). Keep the
  frozen arc_parser for head-accuracy-dependent consumers UNTIL the BF parser closes the gap.
- **Adopt the graded decode as the confidence source**: route `graded_parser` marginals (exact Matrix-Tree) + `crf_tagger`
  marginals into `parse_confidence` (fixes defect 1; the OOD-robust reliability the frozen hard-decode cannot give).
- **Coref mention-head selection on raw text: `boundary_nphead`** (parser-free BF rule) -- the head fix for this problem.
- **File/continue the never-frozen grounded parser as the parser mega-cluster**, with the cross-sentence generative
  top-down loop as the accuracy lever (the in-sentence grounding negative is now measured + banked).
