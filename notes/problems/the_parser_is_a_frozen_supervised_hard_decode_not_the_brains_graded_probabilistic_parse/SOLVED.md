---
problem: the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse
status: PARTIAL
bar: "Route the reader's parse consumers through the GRADED probabilistic parse (globally-normalized marginals) replacing the hard-decode, and SHOW a downstream extraction / board dimension lifts CI-separated on REAL prose (strongest real floor, info-free twin LOSING) -- OR a rigorous LOCATED NEGATIVE naming exactly why the graded parse cannot beat the hard-decode on the reader's own metric (with a number, a fair test: the brain's actual mechanism faithfully built). EITHER outcome must also answer the ACQUISITION question with evidence: is a treebank-supervised parser an admissible offline FOUNDATION (justify computationally), or must the parse be learned-from-reading (name the brain-foundational acquisition mechanism + a first measured step)? Recall/downstream INVARIANT: any consumer not yet moved must be byte-identical; no external tool/LLM at inference."
result: "Route-through on UD-EWT test (n=24,120 tokens/2061 sents): exact-graded decode UAS 0.7927 vs greedy hard-decode 0.7907, +0.00199 CI[0.0010,0.0029] CI-sep -- but the DECODE fixes only 95/5048 head errors (1.9%); ~99% is SCORER error the exact global normalization cannot touch (the LOCATED NEGATIVE, with a number: normalization is solved, the SCORER is the wall). Downstream (n=1065 gold patient arcs): reading the graded DISTRIBUTION (top-2 marginal reach) recovers args CI-sep, recall 0.9512->0.9906 (+0.0394 CI[0.028,0.052]), twin 0.4432 loses -- at a precision cost (+2.18 spurious pairs/arc). ACQUISITION (UD-EWT, 12,329 train sents read, no gold trees): learned-from-reading UNSUPERVISED attachment UAS 0.2117, beats adjacency 0.1137 + random 0.0720, twin 0.1113 loses, GROWS with reading 0.1775->0.2117 monotonic; supervised treebank ceiling 0.7820 (gap 0.570)."
floor: "arc-level UAS floor = greedy hard-decode 0.7907 (the live default). downstream floor = greedy-head patient recall 0.9512. acquisition floor = adjacency (nearest-neighbour) UAS 0.1137 + random 0.0720. exceed-lever floor = surface-scorer-alone UAS 0.7850."
controls: "shuffled-SCORES control collapses UAS to 0.0666 (scorer carries the signal); shuffled-MARGINAL twin drops reliability AUC 0.8546->0.3607; top-2 shuffled-token twin drops recall 0.9906->0.4432; shuffled-TABLE twin drops learned-from-reading UAS 0.2117->0.1113; semantic-augment shuffled twin does NOT beat the surface floor. Each twin is info-free with the same shape and LOSES."
files_changed: "experiments/exp_parser_graded_decode_regimes_v1.py, experiments/exp_parser_graded_downstream_whodidwhat_v1.py, experiments/exp_parser_learned_from_reading_v1.py, experiments/exp_parser_semantic_scorer_augment_v1.py, verification/test_parser_graded_route_through.py, notes/problems/the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse/{SOLVED.md,_working_notes.md,HDLAB_INTEGRATION_SPEC.md,NEXT_GAP_learned_from_reading_scorer.md,BF_AUDIT_UPDATE.md,COMPONENT_REGISTER.md}"
reverify: ".venv/Scripts/python.exe verification/test_parser_graded_route_through.py"
---

# WHAT TO INTEGRATE (executive summary)

The graded probabilistic parse the brief points at **already exists and is brute-force-exact**
(`hdlab.graded_parser`: single-root Matrix-Tree marginals + exact Chu-Liu/Edmonds MAP). This solution
routes the reader's parse consumers through it and measures the result on **real modern prose (UD-EWT)**,
and it answers the deeper acquisition question with a number. Three things land (all BF, all reuse,
recall path byte-identical), and one big prize is filed as a follow-on:

1. **LAND -- consume the graded posterior, drop the fitted logistic.** Flip the reader's parse to the
   exact graded decode (`ArcParser.parse(decode="exact")`; +0.002 UAS CI-sep, heads change only on the
   7.2% invalid-tree sentences) and replace the NOT_BF fitted-logistic `parse_confidence` with the raw
   graded **marginal reliability** (AUC 0.855 > logistic 0.736 -- a learned component REMOVED). Detail in
   `HDLAB_INTEGRATION_SPEC.md`.
2. **LAND -- read the DISTRIBUTION, not the single head.** The true argument the single committed parse
   drops is almost always still ALIVE in the posterior's top-2 (patient recall 0.951->0.991, CI-sep). The
   reader should admit the top-2 marginal heads into the role competition (it partially does, via
   `predicate_argument_frontend`), ranked by the marginal reliability (to pay the +2.18-pairs/arc
   precision cost brain-faithfully, not with a wider beam).
3. **THE LOCATED WALL (a full-pass located negative, with a number).** The graded NORMALIZATION is solved;
   ~99% of the residual head error is **SCORER error** the exact decode cannot touch. So route-through is a
   small win, and the real lever is the SCORER -- which is the acquisition question.
4. **FILE the follow-on -- the reading-learned arc scorer.** The attachment signal is demonstrably in the
   raw stream and GROWS with reading (0.177->0.212 unsupervised, monotonic); the frozen perceptron cannot
   do that. A DMV-class valence+EM+incremental reading-learned scorer is the brain-foundational path to
   EXCEED the frozen treebank scorer. `NEXT_GAP_learned_from_reading_scorer.md`.

**Acquisition verdict:** a frozen glass-box arc SCORER is an **admissible offline FOUNDATION** (it supplies
adult syntactic competence, as WordNet supplies adult lexical competence; frozen, glass-box, no external
tool/LLM at inference). The NOT_BF defect that **BLOCKS is the HARD-DECODE**, not the offline fit -- and the
fix is item 1. The reading-learned scorer is the deeper, longer-horizon upgrade (viable, proven, filed).

---

# 1. THE BRAIN MECHANISM (what we are replicating)

The brain parses **incrementally and probabilistically**: it maintains a graded, globally-normalized
distribution over structures and downstream reads WITH the uncertainty (surprisal theory -- Hale 2001,
Levy 2008; lexicalist constraint-based expectation -- MacDonald 1994, Trueswell-Tanenhaus; Now-or-Never
bounded memory -- Christiansen-Chater 2016). PINNED at the computational level: **assign a normalized
probability to each candidate structure and never hard-commit an unreliable arc.** OUR-INVENTION-UNDER-TEST
(and here refuted as a big lever): that swapping the decode alone materially changes what the reader reads.

The live reader instead **hard-decodes**: greedy per-token argmax + heuristic cycle-break over a frozen
supervised surface-feature averaged-perceptron, discarding the posterior. That is 5 of the 8 live NOT_BF
organs and the deepest upchain component.

# 2. WHAT WE MEASURED

### Prong 1a -- route-through on the parser's own metric + the error decomposition
`exp_parser_graded_decode_regimes_v1` (UD-EWT test, 24,120 tokens):
- UAS: greedy hard-decode **0.7907** (floor) | exact-CLE MAP **0.7927** | marginal-argmax **0.7942** |
  shuffled-scores control **0.0666**. exact-CLE vs greedy **+0.00199, CI [0.0010, 0.0029]** -> CI-separated.
- **Error decomposition (the located mechanism-diff):** of 5048 greedy head-errors the exact global decode
  fixes **95 (1.9%)**; the other **~99% is pure SCORER error** the exact normalization cannot touch. 7.23%
  invalid greedy trees. => *the graded normalization is solved; the SCORER is the wall.*
- Graded marginal reliability AUC **0.8546** vs shuffled-marginal twin **0.3607** (the raw marginal is a
  strong, real per-arc reliability signal -- and it BEATS the fitted-logistic `parse_confidence` at 0.736).

### Prong 1b -- downstream: does reading the distribution recover arguments on real prose?
`exp_parser_graded_downstream_whodidwhat_v1` (UD-EWT, 1065 gold verb->obj/dobj arcs):
- Patient-arc recall: greedy head **0.9512** (floor) | exact/marg head 0.9521 | **top-2 graded reach 0.9906**
  | top-2 shuffled twin 0.4432.
- Better POINT decode vs greedy: +0.0009, **CI includes 0** (honest negative -- too few heads change to move
  a downstream metric).
- **Reading the DISTRIBUTION (top-2 reach) vs greedy: +0.0394, CI [0.028, 0.052] -> CI-sep; twin loses.**
  The brain's "keep alternatives alive" claim, confirmed with a number. Honest cost: +2.18 spurious
  (verb,nominal) pairs/arc -> the distribution HOLDS the signal; a brain-faithful reader needs competition/
  reliability (the AUC-0.855 marginal) to cash it, not a naive wider beam.

### Prong 2 -- the acquisition question (a first measured step)
`exp_parser_learned_from_reading_v1` (UD-EWT, 12,329 train sents read, NO gold heads at train):
- Learned-from-reading UNSUPERVISED directional-PPMI attachment UAS **0.2117**, beats adjacency **0.1137** +
  random **0.0720**, shuffled-table twin **0.1113** loses; supervised treebank ceiling **0.7820** (gap 0.570).
- **Reading curve (grows with reading): 0.1775 -> 0.1892 -> 0.1988 -> 0.2117** (monotonic over 10x text) --
  the property the frozen perceptron LACKS. Mechanism: directional lexical + POS co-occurrence PPMI
  (Hebbian-predictive association; Levy-Goldberg) + locality prior (Now-or-Never), decoded by the SAME
  exact CLE. So ONLY the scorer's acquisition differs from the wired parser.

### Prong 3 -- the "exceed" lever (a located negative that sharpens the acquisition answer)
`exp_parser_semantic_scorer_augment_v1` (UD-EWT): augmenting the surface scorer with the reading-learned
lexical PPMI does NOT exceed it -- best-w UAS 0.7856 vs surface-only 0.7850, +0.0006 CI [-0.0011,+0.0024],
NOT CI-sep; higher weights HURT; twin control holds. **Why:** the supervised scorer already carries a
head-word x dep-word bigram feature trained on gold arcs, so the unsupervised reading-PPMI is a strictly
weaker estimate of a signal it already has. => the exceed path is NOT a bolt-on; it is replacing the
supervised acquisition with a richer reading-learned model (the filed follow-on).

# 3. WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST

- I did NOT show a big board-level lift from the route-through -- and the decomposition explains why (99%
  scorer-limited). The honest headline is a **located negative with a number** on the decode, plus a
  genuine but bounded downstream recall win (top-2 reach) and a proven-viable acquisition path.
- I did NOT land anything in `hdlab/` (Q111). All results are in `experiments/` + `verification/`; the
  proposed diffs are in `HDLAB_INTEGRATION_SPEC.md`.
- The top-2 reach's downstream value is a RECALL win at a precision cost; the net-F depends on the
  competition/reliability selection the reader wires on top (prior `predicate_argument_frontend` +0.0065).
  **If one number is wrong, withdraw the top-2 downstream framing first** and keep the arc-level located
  result + the acquisition curve (both are the most robust, twin-controlled findings).
- The learned-from-reading UAS (0.21) is a FIRST-STEP PPMI model, deliberately the simplest reading model;
  it is not a claim that reading parses well, only that the signal is present and grows.

# 4. KEY REALIZATIONS (the enabling moves)

- **Decompose the error into DECODE vs SCORER.** The whole problem reframes once you separate "the greedy
  heuristic left an invalid tree" (1.9%, fixable by exact normalization) from "the scorer scored the gold
  arc below a wrong one" (99%, untouchable by any normalization). This is what turns "route through the
  graded parse" from a hoped-for lever into a measured small win + a located wall.
- **The graded posterior's value downstream is as a DISTRIBUTION TO READ, not a better point estimate.**
  Point decode is flat; top-2 reach is CI-sep. The brain keeps alternatives alive; the win is in the
  alternatives, not in a crisper single guess.
- **Test the acquisition claim by learning the scorer from raw reading and watching it GROW.** A frozen
  perceptron's UAS is a constant; a reading-learned scorer's UAS rises with text. That growth curve is the
  cleanest evidence that syntax-from-reading is the brain's viable path -- and the axis on which we can
  eventually exceed the frozen treebank.

# 5. ADJACENT COMPONENTS + AUDIT

See `BF_AUDIT_UPDATE.md` (parser-cluster verdicts), `COMPONENT_REGISTER.md` (created/evaluated + BF state),
`NEXT_GAP_learned_from_reading_scorer.md` (the DMV-class reading-learned scorer follow-on). Cross-solution:
this solution's WALL is the arc SCORER (`arc_parser`, the treebank perceptron); its consumed INPUTS are the
POS tags (`pos_tagger`) + the raw token stream. Both feed `notes/CROSS_SOLUTION_IMPROVEMENT_MAP.md` Target 1.

---

## TLDR (plain language)
The reader works out sentence structure by running a fixed rulebook, picking the single best structure and
throwing away the alternatives and any sense of how sure it was. We rerouted it to keep the full graded
picture the brain keeps. Result: doing the maths exactly right, instead of the quick approximate way, fixes
only about 2% of the mistakes -- because 98-99% of the mistakes are the rulebook itself being wrong, not the
shortcut. But keeping the top TWO possibilities instead of one recovers almost all the sentence roles the
single guess drops (from 95% up to 99%), which is exactly how the brain avoids committing too early. And we
showed the rulebook CAN be learned just by reading lots of text (no hand-labelled answers): that reading-
learned version is far weaker for now, but -- unlike the frozen rulebook -- it keeps getting better the more
it reads. So: the exact-maths reroute and the "keep two options" reroute are worth turning on now; the big
prize is a rulebook that learns from reading, which we proved is possible and filed as the next problem.

## QUESTIONS
None blocking. One judgement call for strategy: whether to land the top-2 graded reach as a default-on
reader change now (it is a recall win with a precision cost that the existing role competition must gate),
or to gate it behind the reliability marginal first. My recommendation: land items 1 (exact decode + marginal
reliability) unconditionally; wire item 2 (top-2 reach) through the competition, measured on the board.

## NEXT STEPS
1. LAND `ArcParser.parse(decode="exact")` on the reader path + swap `parse_confidence` logistic -> graded
   marginal reliability (both BF, recall path byte-identical). `HDLAB_INTEGRATION_SPEC.md`.
2. WIRE the top-2 marginal reach into the role competition, reliability-ranked; measure who-did-what on the
   modern board.
3. FILE the reading-learned arc scorer (DMV-class valence + EM + incremental prediction) -- the
   brain-foundational path to EXCEED the frozen treebank scorer. `NEXT_GAP_learned_from_reading_scorer.md`.
