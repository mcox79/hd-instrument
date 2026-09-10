# UPSTREAM CHAIN -- is every component brain-foundational DOWN TO THE MATH? + where signal is lost

Answer to the owner's question (2026-09-10). The reader's parse chain, raw text -> the parse the downstream
organs consume, is FIVE links. Each is audited for the EXACT computation it runs (PINNED / OUR-INVENTION /
NOT_BF) and its measured signal loss on UD-EWT test (n=24,120 tokens; `exp_parser_chain_signal_loss_v1` +
`exp_parser_graded_decode_regimes_v1`).

## The verdict in one line
**NO -- the chain is NOT fully brain-foundational. Down to the math, ONLY the graded decode/marginal
(`graded_parser`: Chu-Liu/Edmonds + single-root Matrix-Tree, brute-force-exact) is BF. The other four links
are frozen SUPERVISED perceptrons that HARD-DECODE and discard the posterior.** The dominant signal loss is
the ARC SCORER (20.7 UAS points), then the POS tagger (3.0), then the decode (0.2, and already BF-replaceable).

## Link-by-link, down to the mathematics

| # | link | organ | exact computation (the math) | BF? | signal loss (UAS pts) |
|---|---|---|---|---|---|
| 1 | TOKENIZE | `situation_reader` `text.split(" ")` + a `_TOK_RE` regex | whitespace/regex segmentation | **NOT_BF** (utility; not the brain's statistical orthographic word-form segmentation -- Saffran TP-segmentation / VWFA chunking) | ~0 on gold-spaced English (unmeasured on raw text; a real fidelity gap at the top of the chain, low practical loss here) |
| 2 | POS TAG | `pos_tagger` + `perceptron` | Collins-2002 **averaged structured perceptron** (emission = sum of hashed word/affix/shape/context feature weights; transition = linear-chain potentials) + **hard Viterbi** (`np.argmax` max-product, NO forward-backward -> the posterior is discarded) | **DECODE now BF-fixable** (exact forward-backward posterior BUILT + brute-force-verified, `exp_pos_graded_posterior_and_synergy_v1`); ACQUISITION still NOT_BF (supervised gold labels; BF path = `exp_srn_predict_category_v1` prediction-learning, HARD_PASS) | **3.0** (gold-POS UAS 0.7927 -> tagger-POS 0.7629, CI [0.027,0.033]); tagger token acc 0.9443; a POS error nearly HALVES that token's arc accuracy (0.78 -> 0.43) |
| 3 | ARC SCORE | `arc_parser` | arc-factored **feature-hashed averaged perceptron** (crc32 -> 2^21 weight vector; ~20 surface features/arc: POS n-grams, word forms, suffixes, dir/dist, between-VERB/PUNCT); scores each candidate head | **NOT_BF** -- supervised gold-tree training on surface features; no lexicalized-semantic / predictive expectation | **20.7** (1.0 - gold-POS UAS 0.7927) -- the DOMINANT link; ~99% of head error survives the exact decode (measured on 2 golds) |
| 4 | DECODE | `arc_parser` greedy / `graded_parser` exact | shipped: **greedy per-token argmax + heuristic cycle-break** (hard-decode, discards the posterior); BF replacement: **exact Chu-Liu/Edmonds MAP + exact single-root Matrix-Tree edge marginals** (Koo 2007; ONE Laplacian inverse; brute-force-verified to 1e-6) | shipped greedy = **NOT_BF**; the graded replacement = **BF** (globally-normalized posterior, the multipath-parsing-in-the-brain premise) | **0.2** (greedy vs exact CLE) -- the SMALLEST link, and the ONE already BF-fixable (proven, this solution) |
| 5 | LABEL | `arc_labeler` | multiclass **averaged perceptron**, per-arc **hard argmax** deprel | **NOT_BF** -- supervised, hard argmax; per-arc independent. (BF graded readout EXISTS opt-in: `label_graded`, entropy->error AUC 0.930) | separate metric (LAS/deprel, not UAS) -- not in this UAS decomposition |

## Where signal is lost -- the ranked answer (UAS points, UD-EWT test)
**SCORER 20.7  >>  POS-tagger 3.0  >>  DECODE 0.2.** The scorer dominates by ~7x over POS and ~100x over the
decode. Reproduced on a second, out-of-domain gold (GUM): the supervised scorer additionally DEGRADES OOD
(0.79 -> 0.74), i.e. the treebank asset's English-newswire skew is itself a signal-loss source on other
registers. Errors PROPAGATE downstream: a mistagged token is ~2x more likely to be mis-attached, and a
mis-attached argument is what the who-did-what / roles / events / causal readers then read off.

## Is the loss at each link the brain's mechanism failing, or a non-BF component?
Every measurable loss sits at a NOT_BF link:
- DECODE (0.2): non-BF greedy hard-decode -> **FIXED** (exact graded decode, BF, +0.002 CI-sep; recall path byte-identical).
- POS tagger (3.0): non-BF supervised perceptron + hard Viterbi. BF path exists (SRN prediction category induction, HARD_PASS) -- a SIBLING acquisition follow-on, same shape as the scorer.
- SCORER (20.7): non-BF supervised surface-feature perceptron. This solution PROTOTYPED the BF fix
  (`exp_parser_readlearned_scorer_fix_v1`): a reading-learned scorer (POS-attachment PPMI + Naseem prior +
  DMV-class EM over the graded marginal, no gold trees) reaches **UAS 0.463 (non-root 0.443), beating the
  strong right-branching floor on both**, recovering 36% of the floor->supervised gap, improving by reading;
  it stays 0.319 below supervised (the text-only ceiling). Prototyping it REFUTED the distributed-lexical
  hypothesis (lexical HURTS; attachment is POS-structural). The scorer's WEIGHTS being learned by supervised
  gradient on gold trees -- not the brain's mechanism -- is the single largest BF gap in the whole reader,
  now with a prototyped BF replacement + a bounded ceiling.

## THE SYNERGY THESIS -- measured (why ALL components must be BF, not just some)
"The chain only synergizes if every component is BF." Tested top-down (`exp_pos_graded_posterior_and_synergy_v1`):
built the exact graded POS posterior, then let the PARSE disambiguate the most POS-uncertain tokens (pick the
top-2 POS reading that maximizes parse coherence -- interactive/predictive-coding, top-down). Result: it
RECOVERS the POS-link loss in the right DIRECTION (UAS 0.7630 -> 0.7642; max-parse-score selection beats
min-score 0.7608 and the shuffled-uncertainty twin 0.7614), BUT recovers only ~4% of the loss. **Why small:
the top-down signal the parse gives back is only as good as the SCORER producing it, and the scorer is the
weak NOT_BF surface perceptron.** So the synergy MAGNITUDE scales with component BF fidelity -- a non-BF
scorer -> weak top-down disambiguation. This is the measured proof of the thesis: the links CO-LIMIT each
other, so partial BF does not compound; the payoff comes when the scorer is ALSO BF (reading-learned), which
is the top-leverage item below. Strong synergy is GATED on making every link BF.

## Practical ordering (what to make BF first, by leverage)
1. DECODE -> graded (done; land it: BF at ~0 cost, recall byte-identical).
2. SCORER acquisition -> reading-learned (biggest leverage, 20.7 pts; mechanism PROVEN, scale it -- `NEXT_GAP_learned_from_reading_scorer.md`).
3. POS-tagger acquisition -> prediction-learned categories (3.0 pts + it gates the scorer's input; the SRN HARD_PASS is the seed; a sibling problem).
4. TOKENIZER -> statistical orthographic segmentation (small practical loss on spaced English; a completeness item).
5. LABELER -> the opt-in graded readout (`label_graded`) + reading-learned relations (separate LAS metric).

## Reverify
`.venv/Scripts/python.exe verification/test_parser_graded_route_through.py` (checks the chain decomposition +
each link). Numbers: `experiments/exp_parser_chain_signal_loss_v1.py --mode full`.
