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
  4. **Close the accuracy gap via the cross-sentence generative world-model** (pri-1) -- the named, quantified BF lever.
- **Our binding is robust to all of this**: it beats string-identity CI-sep at EVERY head-quality level (gold, frozen,
  boundary, unfrozen), so the parser's accuracy trade does not block the common-noun binder.

## 5. Proposed hdlab wire (Q111 -- strategy lands)
- **DO NOT swap the frozen parser for the never-frozen one on the head path** (measured -0.37 UAS / -0.065 coref). Keep the
  frozen arc_parser for head-accuracy-dependent consumers UNTIL the BF parser closes the gap.
- **Adopt the graded decode as the confidence source**: route `graded_parser` marginals (exact Matrix-Tree) + `crf_tagger`
  marginals into `parse_confidence` (fixes defect 1; the OOD-robust reliability the frozen hard-decode cannot give).
- **Coref mention-head selection on raw text: `boundary_nphead`** (parser-free BF rule) -- the head fix for this problem.
- **File/continue the never-frozen grounded parser as the parser mega-cluster**, with the cross-sentence generative
  top-down loop as the accuracy lever (the in-sentence grounding negative is now measured + banked).
