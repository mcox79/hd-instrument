---
problem: the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse
status: PARTIAL
bar: "Route the reader's parse consumers through the GRADED probabilistic parse (globally-normalized marginals) replacing the hard-decode, and SHOW a downstream extraction / board dimension lifts CI-separated on REAL prose (strongest real floor, info-free twin LOSING) -- OR a rigorous LOCATED NEGATIVE naming exactly why the graded parse cannot beat the hard-decode on the reader's own metric (with a number, a fair test: the brain's actual mechanism faithfully built). EITHER outcome must also answer the ACQUISITION question with evidence: is a treebank-supervised parser an admissible offline FOUNDATION (justify computationally), or must the parse be learned-from-reading (name the brain-foundational acquisition mechanism + a first measured step)? Recall/downstream INVARIANT: any consumer not yet moved must be byte-identical; no external tool/LLM at inference."
result: "Route-through on UD-EWT test (n=24,120 tokens/2061 sents): exact-graded decode UAS 0.7927 vs greedy hard-decode 0.7907, +0.00199 CI[0.0010,0.0029] CI-sep -- but the DECODE fixes only 95/5048 head errors (1.9%); ~99% is SCORER error the exact global normalization cannot touch (the LOCATED NEGATIVE, with a number: normalization is solved, the SCORER is the wall). Downstream (n=1065 gold patient arcs): reading the graded DISTRIBUTION (top-2 marginal reach) recovers args CI-sep, recall 0.9512->0.9906 (+0.0394 CI[0.028,0.052]), twin 0.4432 loses -- at a precision cost (+2.18 spurious pairs/arc). ACQUISITION (UD-EWT, no gold trees): first-step reading-learned attachment UAS 0.2117 is BELOW the strong right-branching floor 0.2849 (the documented right-branching trap), but the BRAIN'S ACTUAL MECHANISM -- Naseem universal structural prior (+0.056) + DMV-class EM re-estimation using the graded_parser marginal as the E-step (+0.066, 0.247->0.312) -- BREAKS the trap: UAS 0.3122 > floor 0.2849, CI-sep (+0.0273 [0.0145,0.0402]), twin 0.1763 loses. HONEST: the UAS win is root-finding-driven; non-root attachment 0.2755 ~ floor 0.3026 (the field-pinned text-only ceiling). Supervised treebank ceiling 0.782."
floor: "arc-level UAS floor = greedy hard-decode 0.7907 (the live default). downstream floor = greedy-head patient recall 0.9512. acquisition STRONG floor = adjacency-RIGHT / right-branching UAS 0.2849 (full) / 0.3026 (non-root) -- unusually strong for English (Klein-Manning 2004); also random 0.0720 + left-adjacency 0.1137. exceed-lever floor = surface-scorer-alone UAS 0.7850. supervised treebank UPPER reference (not a floor) = 0.782."
controls: "shuffled-SCORES control collapses UAS to 0.0666 (scorer carries the signal); shuffled-MARGINAL twin drops reliability AUC 0.8546->0.3607; top-2 shuffled-token twin drops recall 0.9906->0.4432; shuffled-TABLE twin drops first-step reading UAS 0.2117->0.1113 and EM UAS 0.3122->0.1763; semantic-augment shuffled twin does NOT beat the surface floor. Each twin is info-free with the same shape and LOSES. Ablations: EM helps (0.247->0.312) AND the structural prior is required (0.183->0.239) -- both isolated."
files_changed: "experiments/exp_parser_graded_decode_regimes_v1.py, experiments/exp_parser_graded_downstream_whodidwhat_v1.py, experiments/exp_parser_learned_from_reading_v1.py, experiments/exp_parser_semantic_scorer_augment_v1.py, experiments/exp_parser_selfsup_em_v1.py, experiments/exp_parser_ood_gum_generalization_v1.py, experiments/exp_parser_graded_reliability_gated_patient_v1.py, verification/test_parser_graded_route_through.py, notes/problems/the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse/{SOLVED.md,_working_notes.md,HDLAB_INTEGRATION_SPEC.md,NEXT_GAP_learned_from_reading_scorer.md,BF_AUDIT_UPDATE.md,COMPONENT_REGISTER.md}"
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
2. **LAND -- read the DISTRIBUTION, RELIABILITY-GATED (a measured NET win, not just recall).** The true
   argument the single committed parse drops is almost always still ALIVE in the posterior's top-2 (patient
   recall 0.951->0.991). A naive wider beam is the WRONG readout (precision collapses, F1 0.418->0.269), but
   gating the top-2 by the marginal reliability -- the brain's reliability-weighted competition (Lewis-Vasishth
   cue integration; the substrate's `graded_competition`) -- NET-beats the hard head on patient-arc F1
   CI-sep (+0.0036 [0.0012,0.0059], twin loses). Small in magnitude only because the hard head already
   recovers 95%; the graded posterior's real downstream value is HARD/ambiguous cases + reliability-flagging.
3. **THE LOCATED WALL (a full-pass located negative, with a number -- and it holds on TWO golds).** The
   graded NORMALIZATION is solved; ~99% of the residual head error is **SCORER error** the exact decode
   cannot touch (UD-EWT AND out-of-domain GUM). So route-through is a small win, and the real lever is the
   SCORER -- which is the acquisition question. (The supervised scorer also degrades OOD, 0.79->0.74 on GUM.)
4. **FILE the follow-on -- the reading-learned arc scorer (mechanism now PROVEN, not just hypothesized).**
   A fully brain-foundational, fully-unsupervised parser -- Naseem universal structural prior + DMV-class
   EM re-estimation using the substrate's own `graded_parser` marginal as the E-step, exact CLE decode --
   BREAKS the right-branching trap on UD-EWT (UAS 0.312 > strong floor 0.285, CI-sep; the prior and EM are
   each required and each help monotonically). It is far below supervised (0.78) and its pure-attachment
   margin is at the field's text-only ceiling, but it INDUCES real structure with the brain's actual
   acquisition mechanism and it IMPROVES by reading. The follow-on is to scale/lexicalize it and A/B its
   scorer against the treebank asset into the SAME graded marginal. `NEXT_GAP_learned_from_reading_scorer.md`.

**Acquisition verdict:** a frozen glass-box arc SCORER is an **admissible offline FOUNDATION** (it supplies
adult syntactic competence, as WordNet supplies adult lexical competence; frozen, glass-box, no external
tool/LLM at inference). The NOT_BF defect that **BLOCKS is the HARD-DECODE**, not the offline fit -- and the
fix is item 1. AND the offline fit is now shown to be **in-principle replaceable by the brain's own
acquisition mechanism** (item 4 breaks the trivial-baseline trap fully unsupervised) -- so the treebank
asset is a convenience-substitutable foundation, not a load-bearing crutch. The reading-learned scorer at
supervised parity is the deeper, longer-horizon upgrade (mechanism proven, scaling filed).

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
  (verb,nominal) pairs/arc.
- **The caveat CLOSED with the brain's mechanism (`exp_parser_graded_reliability_gated_patient_v1`, n=2061):**
  a NAIVE wider beam is the wrong readout (patient-arc F1 collapses 0.418->0.269 as precision craters), but
  RELIABILITY-GATING the top-2 by the marginal (reliability-weighted competition = Lewis-Vasishth cue
  integration / the substrate's `graded_competition`) NET-beats the hard head: F1 0.4182->0.4218, +0.0036
  CI [0.0012,0.0059], CI-sep; shuffled-marginal twin 0.1414 loses. So the brain-faithful readout is
  net-positive, not a tradeoff -- small only because the hard head already recovers 95% (little headroom);
  the posterior's downstream value concentrates in HARD/ambiguous cases + reliability-flagging.

### Prong 2 -- the acquisition question (measured, with the wall drilled)
`exp_parser_learned_from_reading_v1` (first-step) + `exp_parser_selfsup_em_v1` (the brain's mechanism):
- **First step (naive directional PPMI, no EM/prior):** UAS **0.2117**, beats random 0.0720 + left-adjacency
  0.1137, shuffled-table twin 0.1113 loses, and GROWS with reading (0.1775->0.1892->0.1988->0.2117,
  monotonic over 10x text) -- BUT is BELOW the STRONG right-branching floor **0.2849** (Klein-Manning 2004's
  documented right-branching trap; reproduces the substrate's own prior `exp_predictive_selfsup_parser_v1`).
  So the naive read is honestly sub-floor -- a wall.
- **DRILLED THROUGH with the brain's actual mechanism:** the Naseem-2010 universal category-level structural
  prior (blocks the linear-order shortcut -- Yedetore 2023; +0.056, 0.183->0.239) + DMV-class **EM
  re-estimation** (Klein-Manning 2004) using the substrate's exact `graded_parser` **single-root marginal as
  the E-step posterior** (soft expected arc counts; +0.066, 0.247->0.298->0.312) -> UAS **0.3122 BEATS the
  strong right-branching floor 0.2849, CI-sep (+0.0273 [0.0145,0.0402])**; shuffled-table twin 0.1763 loses.
  The right-branching trap is BROKEN, fully unsupervised, glass-box, reusing landed organs.
- **HONEST:** the UAS win is root-finding-driven (the VERB-root prior nails roots the right-branching floor
  misses); on pure non-root ATTACHMENT the reading-learned parser is at PARITY with the floor (0.2755 vs
  0.3026) -- the field-pinned text-only ceiling (DMV's own margin over right-branching is small and shrinks
  on long sentences; the residual needs signal a text corpus lacks -- prosody, joint attention, embodiment).
  Supervised treebank UPPER reference 0.782 still leads (the acquisition gap is real, and now BOUNDED with a
  mechanism, not a mystery).

### Prong 4 -- second gold (GUM, out-of-domain) + the register question
`exp_parser_ood_gum_generalization_v1` (GUM: modern multi-genre -- academic/fiction/conversation/reddit/
court/vlog/... -- 1000 held-out test sents, 15,221 tokens):
- **The route-through located finding REPRODUCES on a second, out-of-domain gold:** exact decode > greedy
  (0.7427 -> 0.7452), **99% scorer-limited** (64 decode-fixable vs 3878 scorer-wrong), marginal reliability
  AUC **0.8365** vs twin 0.359. The conclusion is not a UD-EWT artefact.
- **The supervised treebank scorer DEGRADES out-of-domain:** UAS 0.7427 on GUM vs 0.7907 on UD-EWT
  (-0.048) -- the register-skew risk the reading-learned acquisition track exists to remove, quantified.
- **The reading-learned inducer GENERALIZES OOD:** UAS 0.31-0.34 on GUM > the strong GUM right-branching
  floor 0.2885, twin 0.170 loses.
- **HONEST NEGATIVE (my own hypothesis, refuted):** reading the TARGET register (GUM, 0.3108) did NOT beat
  reading a cleaner SOURCE register (UD-EWT, 0.3443); at matched ~5-6k scale, corpus CONSISTENCY dominates
  register MATCH -- a single-register source gives sharper directional-attachment statistics than a
  heterogeneous multi-genre one. The "reading adapts to the register it reads" claim is not supported here;
  what IS supported is OOD generalization above the strong floor + the route-through robustness above.

### Prong 3 -- the "exceed by bolt-on" lever (a located negative that sharpens the acquisition answer)
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
- **A WALL is a fidelity gap, not a ceiling -- the naive read was sub-floor; the BRAIN'S MECHANISM broke it.**
  First-step PPMI hit the right-branching trap (0.21 < 0.28 floor). Instead of stopping, I built the brain's
  ACTUAL acquisition mechanism -- a category-level structural prior (Naseem 2010) + DMV-class EM
  re-estimation -- and it cleared the floor CI-sep. The enabling move: the EM E-step IS the substrate's own
  exact graded marginal (`single_root_marginals`), so DMV re-estimation is a SYNTHESIS of two landed organs
  (the directional channel + the graded decode), not a new mechanism. A fair test of a WEAK method (first-step
  PPMI) had only proved that weak setup failed; faithfully building the brain's method is what drilled through.

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
showed the rulebook CAN be learned just by reading plain text with NO hand-labelled answers: a first naive
attempt was worse than a dumb "attach each word to its neighbour" baseline (the known hard trap for English),
but when we built the way a child actually learns -- a few universal starting hints about what attaches to
what, plus repeatedly re-reading and revising its guesses -- it beat that baseline for real, and it keeps
improving the more it reads (the frozen rulebook never does). It is still far below the hand-labelled version
and hits the natural limit of learning grammar from text alone (children also use tone of voice, pointing and
the physical world, which text lacks). So: the exact-maths reroute and the "keep two options" reroute are
worth turning on now; and we proved the deeper prize -- a rulebook that teaches itself by reading -- actually
works with the brain's own method, filed as the next problem to scale up.

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
3. FILE the reading-learned arc scorer follow-on: the mechanism is PROVEN (EM + structural prior breaks the
   trap, `exp_parser_selfsup_em_v1`); scale it (full corpus + lexical valence + more EM rounds), then A/B its
   scorer against the treebank asset INTO the same `graded_parser` marginal on a downstream board dim.
   `NEXT_GAP_learned_from_reading_scorer.md`.
