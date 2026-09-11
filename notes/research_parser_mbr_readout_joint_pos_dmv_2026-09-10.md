# Research: graded-competition readout for arc decode + joint POS/parse co-adaptation (2026-09-10)

Self-read by research (Opus), no sub-agent fan-out (per task instruction). Scope: the treebank-free
reading-learned dependency parser front-end (PPMI + Naseem prior + DMV-class EM, exact single-root
Matrix-Tree marginals as E-step, exact Chu-Liu/Edmonds decode; UAS 0.406; oracle shows gold head in
top-5 marginal for 78% of PP/clausal arcs vs 25% committed).

## HEADLINE

**Q1 is (mostly) not a missing-signal problem — it is a DECODE-OBJECTIVE mismatch, and the fix is
already 95% built on disk.** `hdlab/arc_parser.py` (line 26) says outright: the shipped greedy decode
"discards Matrix-Tree marginals"; the opt-in exact-CLE mode (`decode="exact"`) runs Chu-Liu/Edmonds on
the RAW arc-score matrix `A` (line 933-936 of `arc_parser.py`), not on the marginals — and per that
file's own comment it "changes heads ONLY on the cycle/invalid-tree sentences (UAS +0.002 CI-sep)".
`hdlab/graded_parser.py` already ships `single_root_marginals` (Koo et al. 2007), `chu_liu_edmonds`
(exact MST), and `second_best_tree` (Camerini-Fratta-Maffioli 1980) — all brute-force self-tested. The
missing piece is a fourth decode mode: feed the MARGINALS (not the raw scores) into the SAME
`chu_liu_edmonds` call. That is Minimum-Bayes-Risk (MBR) tree decoding — a well-established,
non-neural, decision-theoretic result (Smith & Smith 2007 EMNLP-CoNLL "Probabilistic Models of
Nonprojective Dependency Trees"; Koo et al. 2007 companion paper; McDonald & Satta 2007 IWPT
tractability proof; PCFG analog Goodman 1996 maximum-expected-recall parsing) — and it requires ZERO
new training signal, ZERO new features, and reuses code that is already brute-force-verified.

**Q2's joint POS/parse loop has a direct precedent (Christodoulopoulos, Goldwater & Steedman 2012,
"Turning the pipeline into a loop") that reports convergence, not drift, when POS is re-estimated from
the parser's own structural-role marginals.** The stabilizers that distinguish it from the naive
linear-neighbour self-training that already drifted here are (a) TWO genuinely different evidence
views feeding the retype (distributional context vs. structural role) rather than one view echoing
itself, and (b) alternating hard/soft objectives (Spitkovsky, Alshawi & Jurafsky 2011 "Lateen EM":
alternating Viterbi-EM and soft-EM, each round validated against the other, single alternation already
SOTA for English grammar induction) as an explicit anti-drift gate. Both are exact, tractable,
treebank-free. Confidence on the SPECIFIC magnitude of gain for this pipeline is lower than on the
mechanism (see calibration below) — this is the correct SECOND priority, not the first.

## Cheap decisive test

**For Q1 (do first, ~1 day):** add `decode="mbr"` to `ArcParser.parse`: compute
`marg = single_root_marginals(A, n, temp=1.0)` (already computed when `want_marginals=True`), build a
dense matrix `M[h][i] = marg[i][h]`, and call the EXISTING `chu_liu_edmonds(M, n)` on `M` instead of on
`A`. Re-run the oracle decomposition on the PP/clausal arc subset (the same subset that showed
78%-top5 vs 25%-committed) and compare UAS: greedy (0.406 baseline) vs exact-on-raw-scores (+0.002,
already known) vs exact-on-marginals (new). No retraining, no new features, marginals already
self-tested against brute force — this is a same-day, near-zero-risk experiment.

**For Q2 (do second, after Q1 lands, ~3-5 days):** implement ONE lateen-style alternation: (a) run the
existing tag-then-parse pipeline to convergence (current behavior, unchanged); (b) freeze
`theta_parse`, compute per-word-TYPE structural-role feature vectors from the SAME marginals (expected
soft counts of "heads an nsubj/obj arc," "is dependent of DET," mean valence — all free, already
computed in the E-step); (c) re-estimate OPEN-CLASS tag posteriors only (freeze the closed-class
scaffold) by mixing the existing distributional tag posterior with the new structural-role posterior in
log-space (additive-log-then-softmax — the SAME combination rule already pinned and coded in
`hdlab/graded_competition.py`); (d) re-run DMV EM from these updated tags; (e) accept the round only if
EITHER the soft-EM data log-likelihood OR the Viterbi-tree assignment cost improves (Lateen EM's
cross-validation gate), else roll back. One alternation, measured against the current staged-pipeline
UAS 0.406 baseline.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Q1 — MBR decode:**
- HARD-PASS: UAS on the PP/clausal arc subset improves by >=8 points absolute (recall on that arc-type
  subset moving meaningfully toward the 78% top-5-reachable ceiling) with no regression (>1 point) on
  other arc types or overall UAS. This would mean most of the 0.53 reachable-headroom gap was a pure
  decode-objective mismatch, recoverable for free.
- PARTIAL: 2-8 points gain on PP/clausal, confirming the mechanism is real but the residual gap is
  genuine posterior miscalibration (the marginal itself doesn't sharply favor gold even when gold is
  reachable) — in that case the graded-competition entropy/margin readout (below) becomes the
  right SECOND lever (precision-controlled admission, not more point-accuracy).
- HARD-FAIL: <2 points change either direction. This would mean the current exact-CLE-on-raw-scores
  decode is ALREADY close to what MBR-on-marginals would produce (i.e., the model's scores and its
  marginals rank candidates almost identically), and the 78%-vs-25% gap must be attributed to something
  else — most likely the oracle's "top-5" reachability criterion counting candidates that the SINGLE
  best tree can never simultaneously satisfy (global tree-consistency competition among PP/clausal
  arcs for the same limited "budget" of attachment sites), which would redirect the fix toward the
  reliability-gated SET-VALUED readout (admit multiple heads, don't force one tree) rather than any
  single-tree decode change.

**Q2 — joint POS/parse loop:**
- HARD-PASS: >= 1 lateen alternation round is ACCEPTED (per the dual-objective gate) AND overall UAS
  improves by >=1.5 points with no cross-validation-gate rejection cascade (i.e., it doesn't immediately
  roll back every round).
- HARD-FAIL: the very first alternation is rejected by the dual-objective gate (both soft-EM likelihood
  and Viterbi cost get worse), OR it is accepted but UAS regresses — this would replicate the earlier
  linear-neighbour self-training drift and indicate the "two independent views" assumption (Blum &
  Mitchell 1998 co-training precondition) does not hold well enough here (distributional context and
  structural role are more correlated / share more error modes than hypothesized) — in that case,
  STOP the joint-loop direction rather than iterating further alternations hoping for recovery (per
  [[feedback-dont-generalize-a-narrow-failure-to-impossible]], test ONE more variant — e.g. anchor MORE
  categories, not just closed-class — before declaring the direction closed).

## Cross-thread synthesis

This directly extends `notes/problems/discrete_where_the_brain_is_graded_in_parsing_and_role_assignment/RESEARCH_graded_competition_brain_mechanism.md`
(owner-DONE, landed as `hdlab/graded_competition.py`) rather than opening a new mechanism. That drill
already established, PRIMARY-VERIFIED:
- additive-cue-activation -> softmax IS the exact Bayesian posterior for discrete cue integration
  (McClelland 2013: `net_i = log P(h_i) + sum_j log P(e_j|h_i)`, output = softmax(net)) — PINNED.
- MAP-optimality (Bishop PRML Sec 1.5): argmax of the TRUE posterior is accuracy-optimal by
  construction, so a graded readout CANNOT beat its own argmax on point accuracy — its value is the
  DISTRIBUTION (uncertainty/precision control), not a better point estimate. This is the theoretical
  reason Q1's "convert headroom into point-accuracy via a cleverer readout of the SAME posterior" is
  the wrong frame for a single item. It generalizes cleanly to the STRUCTURED/tree case via MBR: you
  cannot beat argmax-of-the-posterior AT THE PER-ARC level, but the CURRENT decode is not even
  computing argmax-of-the-posterior AT THE TREE level (it's argmax of the raw joint SCORE, a different
  object under a global one-tree-per-sentence constraint) — so there IS free headroom, but it comes
  from fixing a decode/objective bug, not from inventing new disambiguation signal. Once decode is
  posterior-optimal (MBR), the MAP-optimality ceiling applies for real, and further Q1 gains require
  either a better POSTERIOR (Q2, more/better signal) or precision-controlled SET-valued output
  (abstention), not a cleverer point-readout.
- point entropy of the maintained distribution is the correct, novel currency for flagging WHERE a
  discrete decision errs (gold-free) — directly reusable per-arc on the marginal to build the
  "reliability" signal Q1 asked for: `graded_competition.graded_pick(supports={"marginal": log
  p(e)}, weights={"marginal": 1.0})` gives entropy + margin per word for free, zero new invention.
- the competition DYNAMICS (settling vs. racing) is neurally unresolved for sentence processing; Lewis
  & Vasishth 2005's cue-based retrieval (`A_i = B_i + sum_k W_k S_ki`, retrieval probability via
  softmax/Boltzmann over activations, latency `T_i = F * exp(-f*A_i)`) is the RACE-family instantiation
  already cited there and reusable directly for per-word head-competition (the "candidate heads compete
  as retrieval targets for a single dependent slot" framing is literally the ACT-R chunk-retrieval
  setup, just with the model's marginal standing in for cue-match strength).

Precision control for the ~1.1-extra-pairs-per-arc cost (admitting spurious arcs under a flat top-2
readout): the fix is to make k ADAPTIVE to the per-word entropy/margin rather than fixed. Emit 1
candidate when `entropy(d) < tau` (confident majority of words), emit the smallest marginal-ranked
prefix whose cumulative mass clears a calibrated coverage threshold when `entropy(d) >= tau` (the
"adaptive prediction set" / cumulative-softmax-thresholding idea, Romano, Sesia & Candes 2020 — an
ENGINEERING/statistical technique, not neuroscience-pinned, cited here only as the standard tool for
turning a calibrated threshold into a bounded-false-admission set). Since only PP/clausal arcs are
genuinely ambiguous, this should concentrate the extra-candidate cost where the extraction win was
actually earned and cut it elsewhere.

## Substrate-product implications

In plain terms: the parser currently computes a good probability cloud over where each word's head
could be (the marginal), but then, when it commits to ONE final structure, it throws that cloud away
and instead maximizes a different, cruder number (a raw match score) that is not guaranteed to agree
with the cloud. That mismatch is a likely primary cause of why the single best guess misses so often on
the hardest attachment types (prepositional phrases, subordinate clauses) even when the right answer is
clearly visible nearby in the cloud. The proposed fix does not require teaching the model anything new
-- it requires making the "pick one final structure" step actually use the probability cloud it already
computed, which is close to a one-function change reusing code already tested against a brute-force
reference. Expected cost: under a day of engineering plus a same-day experiment; expected benefit, if
it pans out, is a meaningful chunk of the already-measured "the right answer was right there" gap
closing for free. The second idea (letting the parser's own structural judgments refine what counts as
a noun vs. a verb, rather than deciding that once at the start and never revisiting it) is a bigger,
riskier build with a real prior-art precedent showing it CAN work (results converge in that published
system) but is not guaranteed to work here, and there is a concrete, cheap tripwire (the dual-objective
accept/reject gate) that stops it automatically before it repeats the earlier regression if it starts
misbehaving.

**Risk of this recommendation:** the HARD-FAIL band for Q1 is real -- it is possible the raw arc scores
and the marginals already rank candidates almost identically for this model (i.e., the gap is not a
decode bug at all), in which case the fix does nothing and the actual explanation is a harder,
structural one (global tree-competition among simultaneously-plausible PP attachments). The cheap test
resolves this within a day either way, so the downside of trying is small.

## Citations (verified count)

PRIMARY/DIRECT source pages fetched or previously primary-verified on disk in this project (5):
1. `hdlab/graded_competition.py` + `notes/problems/.../RESEARCH_graded_competition_brain_mechanism.md`
   — on-disk, previously primary-source-verified (McClelland 2013, Levy 2008, Lewis & Vasishth 2005,
   Bishop PRML, Swets et al. 2008 all cited there with page/equation numbers).
2. `hdlab/arc_parser.py` (read directly, lines 26, 875-940) — on-disk, direct code read.
3. `hdlab/graded_parser.py` (read directly, lines 1-494) — on-disk, direct code read, cites Koo et al.
   2007 and McDonald-Satta 2007 / Smith-Smith 2007 in its own docstrings already.
4. Spitkovsky, Alshawi & Jurafsky 2011, "Lateen EM: Unsupervised Training with Multiple Objectives,
   Applied to Dependency Grammar Induction" (EMNLP 2011) — confirmed via search-result summary
   (alternates hard/soft EM objectives; single alternation SOTA for English DGI); NOT fetched
   primary-source PDF (extraction failed, see calibration note).
5. Christodoulopoulos, Goldwater & Steedman 2012, "Turning the pipeline into a loop: Iterated
   unsupervised dependency parsing and PoS induction" (NAACL WILS workshop) — fetched via WebFetch;
   partial extraction (loop mechanism + "converges" claim + stabilizers confirmed; exact per-iteration
   numbers NOT extracted, genuine gap).

SEARCH-SUMMARY-ONLY (not primary-PDF-verified this session, PDF extraction failed both times) (3):
6. Smith & Smith 2007, "Probabilistic Models of Nonprojective Dependency Trees" (EMNLP-CoNLL 2007) —
   MBR-via-marginals claim corroborated by 3 independent search-result summaries + standard NLP
   knowledge, not by primary-source equation quoting.
7. Koo, Globerson, Carreras & Collins 2007, "Structured Prediction Models via the Matrix-Tree Theorem"
   (EMNLP-CoNLL 2007) — this is literally the paper already cited BY NAME in the task's own pipeline
   description and already cited in `hdlab/graded_parser.py`'s docstrings; O(n^3) marginal computation
   confirmed via search summary.
8. McDonald & Satta 2007, "On the Complexity of Non-Projective Data-Driven Dependency Parsing" (IWPT
   2007) — edge-factored tractability confirmed via search summary; the specific Hamming-loss-MBR
   reduction (expected accuracy is edge-decomposable => solvable by the same MST algorithm on
   marginals) is standard textbook material (Goodman 1996 PCFG analog) applied here by me, not a
   verbatim quote from this paper.

Total: 8 sources, 5 primary/on-disk-verified, 3 search-summary-only. Per lit-scan calibration policy,
P estimates below are deflated accordingly.

**Calibration (per [[feedback-lit-scan-calibration-penalty]]):**
- P(MBR-on-marginals mechanism is mathematically sound and applicable as described) = 0.80 (well-
  established decision theory + PCFG/dependency-parsing precedent; deflated from ~0.95 for incomplete
  primary-source verification of Smith & Smith 2007's exact equations).
- P(MBR swap yields >=8pt PP/clausal gain on THIS pipeline specifically, i.e. HARD-PASS not PARTIAL/
  HARD-FAIL) = 0.45 (genuine empirical uncertainty about whether this model's raw scores already
  approximate its own marginal ranking; this is a novel-synthesis-scale claim about an unmeasured
  system, capped at 0.50 per policy).
- P(joint POS/parse lateen loop converges rather than drifts on this pipeline) = 0.40 (real prior-art
  precedent for convergence, but the earlier same-project self-training drift is a genuine negative
  data point on a RELATED mechanism; deflated for that specific project history).

## TLDR
The tool that turns the parser's best-guess cloud of possible sentence structures into one final
answer is currently throwing away that cloud and using a cruder number instead — a one-function fix
(already mostly built) should recover some of the "right answer was right there but missed" problem for
free, testable in about a day. A second, bigger idea — letting the parser's structural judgments help
correct its own word-category guesses over a few rounds — has real precedent that it can work, but is
riskier and has a built-in automatic stop switch if it starts making things worse, same as an earlier
similar idea did.

## QUESTIONS
None.

## NEXT STEPS
1. exp_dev: add `decode="mbr"` mode to `hdlab/arc_parser.py` / `hdlab/graded_parser.py` (feed
   `single_root_marginals` output into the existing `chu_liu_edmonds`); re-run the oracle decomposition
   on the PP/clausal subset; grade against the HARD-PASS/PARTIAL/HARD-FAIL bands above.
2. Contingent on (1) landing PARTIAL or better: wire the `graded_competition.graded_pick` entropy/margin
   readout onto the per-arc marginal as the adaptive-k precision control for the extraction consumer
   (replacing the flat top-2 admit-rule that costs ~1.1 extra pairs/arc).
3. After (1): design the ONE-alternation lateen POS/parse loop (Q2) as a SEPARATE, smaller follow-up
   experiment gated by its own dual-objective accept/reject rule; do not combine with (1) in the same
   test (keep the decode fix and the joint-retyping fix separately falsifiable).
