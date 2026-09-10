# Working notes -- parser graded route-through + acquisition

Solver session, 2026-09-10. NO hdlab writes (Q111). Threads capped. Glass-box, no LLM at inference.

## The frame (brain mechanism)
- The brain parses INCREMENTALLY + PROBABILISTICALLY: maintains a graded, globally-normalized distribution
  over structures; downstream reads WITH the uncertainty (surprisal theory Hale 2001 / Levy 2008; lexicalist
  expectation MacDonald 1994; Now-or-Never bounded memory Christiansen-Chater 2016).
- The live reader HARD-DECODES: greedy per-token argmax + heuristic cycle-break over a FROZEN SUPERVISED
  surface-feature averaged-perceptron (arc_parser), discards the posterior. 5 of 8 live NOT_BF organs.
- The graded posterior ALREADY EXISTS in-substrate: hdlab.graded_parser computes exact single-root
  Matrix-Tree marginals + exact CLE MAP over the SAME scorer (brute-force-verified). Normalization solved.

## PRONG 1a -- decode-regime comparison + error decomposition (exp_parser_graded_decode_regimes_v1)
UD-EWT test, n=24,120 tokens / 2061 sents, 13s.
- UAS: greedy(FLOOR) 0.7907 | exact-CLE 0.7927 | marginal-argmax 0.7942 | shuffled-scores-ctrl 0.0666.
- exact-CLE vs greedy: +0.00199, CI [0.0010, 0.0029] -> CI-SEPARATED (real but tiny).
- ERROR DECOMPOSITION (the located mechanism-diff): of 5048 greedy head-errors, exact decode FIXES 95
  (1.9%); ~99% survive the exact global decode = PURE SCORER ERROR. 7.23% invalid greedy trees.
  => the graded NORMALIZATION is solved; the SCORER is the wall.
- Graded marginal reliability: AUC 0.8546 (marginal of the picked head separates right-from-wrong
  attachment) vs shuffled-marginal twin 0.3607 -> a strong real reliability signal.

## PRONG 1b -- downstream who-did-what (exp_parser_graded_downstream_whodidwhat_v1)
UD-EWT test, n=1065 gold (verb->obj/dobj) patient arcs, 5s.
- Patient-arc RECALL: greedy-head(FLOOR) 0.9512 | exact-head 0.9521 | marg-head 0.9521 |
  TOP-2 graded reach 0.9906 | top-2 shuffled twin 0.4432.
- better POINT decode vs greedy: +0.0009, CI [0.0, 0.0028] -> NOT CI-sep (too few heads change to move
  a downstream metric). Honest located-negative for "decode-as-point-estimate helps downstream".
- READING THE DISTRIBUTION (top-2 reach) vs greedy: +0.0394, CI [0.0282, 0.0516] -> CI-SEP; twin loses.
  The true argument the single parse drops is almost always ALIVE in the posterior (0.951->0.991).
- HONEST precision cost: top-2 admits +2.18 spurious (verb,nominal) pairs / gold arc. So the distribution
  CONTAINS the missing signal; the reader needs competition/reliability (the AUC-0.855 marginal) to cash
  it, not a naive wider beam. (This is the mechanism behind the prior +0.0065 who-did-what win.)

## PRONG 2 -- the acquisition question (exp_parser_learned_from_reading_v1)
Learned-from-reading UNSUPERVISED directional-PPMI attachment (POS + lexical, distance/locality prior,
CLE decode). NO gold heads at train. UD-EWT: 12,329 train sents read, 600 test, 29s.
- UAS: random 0.072 | adjacency 0.114 | LEARNED-FROM-READING 0.2117 | shuffled-twin 0.111 |
  supervised-treebank CEILING 0.782.
- READING CURVE (grows with reading): 0.1775 -> 0.1892 -> 0.1988 -> 0.2117 (monotonic, 10x text).
- Verdicts: signal-in-stream TRUE, beats-adjacency TRUE, twin-loses TRUE, grows-with-reading TRUE.
- gap to supervised = 0.570 (first-step reading recovers ~27% of supervised UAS).

### Admissibility verdict (computational argument)
- What makes the parser NOT_BF is TWO things: (a) HARD-DECODE [Prong 1 = the fix: consume the graded
  posterior]; (b) the scorer's SUPERVISED-TREEBANK acquisition.
- (a) is the DEFECT THAT BLOCKS -- it discards the graded distribution the brain maintains, and Prong 1b
  shows the discarded distribution holds recoverable signal. FIX = route consumers through the marginals.
- (b) the frozen glass-box arc SCORER is an ADMISSIBLE offline FOUNDATION: it supplies adult syntactic
  competence (as WordNet supplies adult lexical competence), frozen + glass-box, NO external tool/LLM at
  inference. The load-bearing brain property is the GRADED posterior, which the treebank scorer CAN supply
  (marginals) -- the reader just discards it. Prong 2 proves syntax-from-reading is a VIABLE path (signal
  in stream, grows with reading) but far from parity at first-step -> the deeper BF upgrade is a filed
  follow-on (a DMV-class valence+EM+incremental reading-learned scorer), not this problem's blocker.

## PRONG 3 (attempt) -- is the scorer's residual error SEMANTIC? (the "exceed" lever)
Hypothesis: the surface-feature scorer's 99%-of-error residual is where lexical-SEMANTIC selectional
expectation (verb->argument fit; reuse predictive_reader / grounded_similarity) carries signal the surface
perceptron lacks. If a grounded selectional cue ranks the GOLD head above the WRONG predicted head on a
meaningful fraction of residual errors, that is the brain-faithful path to EXCEEDING the frozen scorer.
[measurement below]
