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

## PRONG 2 -- the acquisition question (exp_parser_learned_from_reading_v1 + exp_parser_selfsup_em_v1)
First-step learned-from-reading UNSUPERVISED directional-PPMI attachment. NO gold heads at train.
- UAS: random 0.072 | left-adjacency 0.114 | **right-branching (STRONG) 0.285** | LEARNED 0.2117 |
  twin 0.111 | supervised CEILING 0.782.
- READING CURVE (grows): 0.1775 -> 0.1892 -> 0.1988 -> 0.2117 (monotonic, 10x text).
- CORRECTED (research drill CONT-71): the STRONG floor is adjacency-RIGHT / right-branching (~0.285-0.303),
  NOT left-adjacency. First-step reading (0.212) is BELOW it = the documented right-branching trap
  (Klein-Manning 2004; reproduces the substrate's own exp_predictive_selfsup_parser_v1 0.2716<0.2979).

### PRONG 2+ -- DRILLED THROUGH the trap with the brain's actual mechanism (exp_parser_selfsup_em_v1)
Naseem-2010 universal category-level structural prior + DMV-class EM re-estimation using
graded_parser.single_root_marginals as the E-step posterior (soft expected arc counts) + exact CLE. Full
UD-EWT (8000 maxlen-40 train, 600 test), 50s.
- static: no-prior 0.183 -> +prior(1.5) 0.239 -> +lam=0.3 0.247. (prior worth +0.056, required.)
- EM curve: 0.2466 -> 0.2984 -> 0.3122 (EM worth +0.066, monotonic).
- **EM-best UAS 0.3122 > strong right-branching floor 0.2849, CI-sep (+0.0273 [0.0145,0.0402]); twin 0.176
  loses. THE RIGHT-BRANCHING TRAP IS BROKEN, fully unsupervised, glass-box, reusing landed organs.**
- HONEST: full-UAS win is root-finding-driven (VERB-root prior); non-root ATTACHMENT 0.2755 ~ floor 0.3026
  (text-only ceiling: DMV margin small + shrinks on long sents; residual needs prosody/joint-attention/
  embodiment a text corpus lacks). Supervised UPPER ref 0.782 still leads.
- gap to supervised = 0.470 (EM recovers ~40% of supervised UAS; the acquisition gap is now BOUNDED with a
  mechanism, not a mystery).

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

## PRONG 3 -- is the scorer's residual error fixable by a reading-learned lexical cue? (exp_parser_semantic_scorer_augment_v1)
Augment the frozen surface scorer with the reading-learned lexical PPMI (Prong 2's signal), re-decode CLE,
sweep the mix weight. LOCATED NEGATIVE: surface-only UAS 0.7850 -> best-w 0.7856 (+0.0006, CI [-0.0011,
+0.0024], NOT CI-sep); higher w HURTS; twin control holds. WHY: the supervised scorer already carries a
head-word x dep-word bigram feature trained on gold arcs, so the unsupervised reading-PPMI is a weaker
estimate of a signal it already has. => the exceed path is NOT a bolt-on onto the frozen scorer; it is
REPLACING the supervised acquisition with a richer reading-learned model (Prong 2+ EM proves that path
breaks the trivial-baseline trap; scaling it to parity is the filed follow-on).

## PRONG 4 -- second gold GUM (OOD) + register question (exp_parser_ood_gum_generalization_v1)
GUM (modern multi-genre, OOD from UD-EWT). 1000 test sents / 15,221 tokens; 5000 GUM read sents; 6000 UD train.
- Route-through REPRODUCES: greedy 0.7427 -> exact 0.7452; 99% scorer-limited (64 vs 3878); marginal AUC
  0.8365 vs twin 0.359. The located finding is not a UD-EWT artefact.
- Supervised scorer DEGRADES OOD: 0.7427 (GUM) vs 0.7907 (UD-EWT), -0.048 (register skew quantified).
- Reading-learned inducer GENERALIZES OOD: 0.31-0.34 > strong GUM floor 0.2885; twin 0.170 loses.
- HONEST NEGATIVE (my hypothesis refuted): reading TARGET register (GUM 0.3108) did NOT beat reading cleaner
  SOURCE register (UD-EWT 0.3443); corpus CONSISTENCY dominates register MATCH at ~5-6k scale.

## STATUS: PARTIAL. Witness verification/test_parser_graded_route_through.py = 28 checks PASS. Ledger clean.
NO hdlab writes (Q111). The located-negative clause of the bar is fully met (99% scorer-limited, with a
number); the acquisition question is answered decisively (trap broken by the brain's mechanism); the
route-through + reading-learned scorer are proposed diffs / a filed follow-on, not landed.
