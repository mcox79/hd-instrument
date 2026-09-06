---
problem: wire_a_defer_consumer_for_calibrated_confidence_and_realize_precision_weighting
status: SOLVED
bar: "PASS = a glass-box DEFER-CONSUMER (a head-driven readout that DOWN-WEIGHTS / ABSTAINS on low-confidence arcs and falls back to its prior, driven by the landed calibrated confidence) that turns the landed signal into a CI-separated SELECTIVE-RELIABILITY or DEFER-POLICY accuracy gain on the LIVE reader over the current BLANKET reader (commit-on-all), on MODERN gold, with a RANDOM-confidence info-free TWIN LOSING (the calibration must be load-bearing, not \"abstaining-on-anything-helps\"), NO-regress on non-consumers (parse heads + every non-deferring dim byte-identical), AND the read-cost / additive no-regress check that lets strategy FLIP precision_weight_roles default-ON (net-positive on a live metric -- including whether the ~2 parses/read cost can be removed by reusing the shared parse). Report the risk-coverage curve + CI half-width + null p95, recompute floors per population. A rigorous located NEGATIVE -- the defer-consumer, faithfully built, does NOT lift a live reader's reliability (e.g. FALL-BACK adds nothing because the head-independent patient has no better prior to fall back to; ABSTAIN trades coverage without a defensible operating point), with the exact cause named -- is a FULL PASS."
result: "POSITIVE. A glass-box DEFER-CONSUMER that ABSTAINS below a DEV-chosen threshold tau (chosen on UD-EWT train, applied on UD-EWT test + QA-SRL, unseen) -- consuming the FROZEN landed hdlab.parse_confidence calibrator -- lifts accuracy-on-ANSWERED over the BLANKET reader (commit-on-all) on THREE modern instruments: who-did-what PATIENT UD-EWT (n=1255) blanket 0.8789 -> answered 0.9662 at coverage 0.661 (+0.0873 CI[+0.0710,+0.1044]); PATIENT QA-SRL (n=8225) 0.2982 -> 0.3543 at coverage 0.468 (+0.0560 CI[+0.0456,+0.0664]); obl/spatial ATTACHMENT UD-EWT (n=2294) 0.7581 -> 0.8496 at coverage 0.629 (+0.0916 CI[+0.0770,+0.1067]). The RANDOM-confidence info-free twin at matched coverage does NOT gain (patient UD +0.0053 / QA -0.0024 / obl -0.0087). FLIP-ON cost: folding (heads,conf,marg) into the ONE shared parse removes the duplicate arc-eager parse for free (-0.840 ms/read) and the inert global-arc_parser a2_marg cue is droppable (obl AUC 0.7233->0.7181, -0.0052), so the defer path needs ZERO extra parses -- net-neutral flip-on. TWO located negatives, faithfully built + fully attributed (each a full-pass form): (a) FALL-BACK adds nothing (patient position fall-back -0.0016 UD / -0.0356 QA -- the head-independent patient has no better prior; obl locality fall-back nets 0 -- the parser beats locality even on its shakiest conf-quartile, 0.5436 vs 0.3537); (b) the UPSTREAM small-beam parse posterior (LOSS 1) does NOT out-calibrate the landed confidence -- across k=6/8/16 all three beam readouts (agreement/margin/Hale-entropy) are <= the greedy raw arc conf, because the parser is LOCALLY NORMALIZED (label bias; Andor 2016) and half its errors are SEARCH failures (gold in the beam on only 0.492 of wrong obl arcs)."
floor: "Per population the strongest floor is the BLANKET live reader (commit-on-all, ignore confidence): who-did-what PATIENT 0.8789 (UD-EWT n=1255) / 0.2982 (QA-SRL n=8225); obl/spatial 0.7581 (UD-EWT obl/nmod n=2294). The RELIABILITY-SIGNAL floor is the RANDOM-confidence twin at matched coverage (what a naive abstain-on-anything reaches): +0.0053 / -0.0024 / -0.0087 -- the deployed defer gain CI-separates above it. For the FALL-BACK arms the floor is the PRIOR ALONE (always fall back): position 0.8422 (patient UD) / locality 0.4076 (obl) -- both far below the parser, which is why fall-back nets 0. For the UPSTREAM the floor is the greedy raw arc conf AUC 0.615 (patient) / 0.721 (obl) -- the beam does not clear it."
controls: "(1) RANDOM-confidence info-free TWIN at matched coverage: patient UD +0.0053 / QA -0.0024 / obl -0.0087 -> the calibration is load-bearing, not abstaining-helps (its selective delta IS the null; the real effect clears it ~10-16x). (2) DEPLOYED tau chosen on DEV (UD-EWT train) applied on TEST (UD-EWT test + QA-SRL, unseen) -> a real operating point, not an in-sample top-k ranking (the predecessor's diagnostic). (3) FALL-BACK attribution: always-fall-back (prior alone) 0.8422/0.4076 loses to the parser, and on the shakiest conf-quartile the parse still beats the prior (obl 0.5436 vs locality 0.3537) -> the located negative is 'no head-independent prior is good enough', not a wiring bug. (4) UPSTREAM attribution: gold-in-beam-when-wrong 0.492 (half the errors are search failures the beam cannot reach) + QBC ensemble-agreement AUC 0.696 ~= raw 0.721 (an independent parser adds nothing) -> the wall is the parser's LOCAL normalization, not beam width. (5) ADDITIVE / no-regress: defer(conf, None) is False for all arcs + tau=-inf answered==blanket (byte-identical) -> every non-deferring consumer + parse head is unchanged."
files_changed: "experiments/exp_defer_consumer_v1.py (the headline: the DEFER-CONSUMER -- abstain/fall-back/graded policies with a DEV-chosen tau on the LIVE readers, modern gold, twin + no-regress controls, sentence-clustered bootstrap CIs), experiments/exp_defer_upstream_smallbeam_v1.py (the UPSTREAM component: a faithful small-beam arc-eager decode + beam-marginal reliability + QBC ensemble agreement + oracle-coverage diagnostic -- the located negative for LOSS 1), experiments/exp_defer_readcost_v1.py (the FLIP-ON cost: the fold removes the duplicate parse; the a2_marg drop makes the defer path net-zero-parse), verification/test_defer_consumer_organ.py (scaffold-free witness, 6/6), notes/problems/wire_a_defer_consumer_for_calibrated_confidence_and_realize_precision_weighting/SOLVED.md. NO hdlab/ written (Q111 -- prototype; the proposed additive policy + fold wire is stated in section 6 for strategy to land)."
reverify: ".venv/Scripts/python.exe verification/test_defer_consumer_organ.py"
---

## SHORT VERSION

The predecessor built a calibrated per-arc parse confidence (AUC 0.615->0.858) and PROVED its sensitivity by
RANKING the live readers' picks (selective@50 on the in-sample top-half). That is a diagnostic, not a policy --
nothing DEFERS. This problem builds the CONSUMER that ACTS: a DEFER POLICY with a threshold tau chosen on DEV and
applied on TEST that CHANGES the reader's output. On modern gold, having the reader ABSTAIN below tau lifts its
accuracy-on-ANSWERED over the blanket reader, CI-separated, with a random-confidence twin flat:

- **who-did-what PATIENT** (UD-EWT): 0.8789 -> **0.9662** at 66% coverage (+0.0873 CI-sep). QA-SRL: 0.2982 ->
  **0.3543** (+0.0560 CI-sep).
- **obl/spatial ATTACHMENT** (UD-EWT): 0.7581 -> **0.8496** at 63% coverage (+0.0916 CI-sep).

And the flip-on is now CHEAP: folding the confidence into the single shared parse removes the duplicate parse
(-0.84 ms/read) and the one cross-parser cue is droppable, so emitting the confidence + deferring on it adds
**zero extra parses**. Two things faithfully built that did NOT work, each fully understood: FALL-BACK to a
head-independent prior adds nothing (there is no better pick to fall back to), and the UPSTREAM small-beam parser
does not out-calibrate the landed confidence (the parser is locally normalized -- label bias -- and half its
errors are search failures). So the robust, deployable win is ABSTAIN, and the north-star for the rest is a
globally-normalized parser (a separate problem).

## 1. HOW THE BRAIN DOES THIS (the opening move)

PINNED-BY-EVIDENCE (computation): precision-weighting = weight a downstream commitment by the inverse-variance
reliability of the estimate driving it (Ernst & Banks 2002 MLE cue combination; Friston 2010 active inference: an
unreliable cue is DOWN-WEIGHTED, never hard-committed). Decision confidence GATES commitment / opt-out (Kepecs et
al. 2008 OFC vevaiometric; Kiani & Shadlen 2009 decline-when-unsure). The ABSTAIN policy is exactly the
Kiani-Shadlen opt-out; the FALL-BACK prior is Late-Closure locality (Frazier & Rayner 1982; recency of activation,
Lewis-Vasishth 2005). OUR-INVENTION-UNDER-TEST (the application): gating the THEMATIC-ROLE readout on parse
confidence -- upheld by the predecessor and, here, realized as a deployed policy with the info-free twin losing.
The GRADED down-weight arm is the continuous Friston/Ernst-Banks form (a graded_competition cue combination where
the parse cue's weight IS its calibrated precision); ABSTAIN is its degenerate opt-out.

## 2. THE HEADLINE -- the DEFER-CONSUMER, deployed tau, on MODERN gold

I drive the ACTUAL deployed readers (structural_patient_pick; the parser's obl/nmod attachment), attach the
FROZEN landed `hdlab.parse_confidence` calibrated confidence to each role arc, and apply a DEFER POLICY. tau is
chosen ONCE on UD-EWT train (dev, target 75% coverage -> defer the shakiest ~quarter) and applied unchanged on the
unseen test sets. The reader ABSTAINS below tau; the metric is accuracy-on-ANSWERED vs the blanket reader (which
commits on all). CIs are paired sentence-clustered bootstrap (arcs within a sentence are correlated).

| reader (modern gold) | n | blanket | answered_acc @ dev-tau | coverage | delta CI | twin |
|---|---|---|---|---|---|---|
| who-did-what PATIENT UD-EWT | 1255 | 0.8789 | **0.9662** | 0.661 | +0.0873 [+0.0710,+0.1044] | +0.0053 |
| who-did-what PATIENT QA-SRL | 8225 | 0.2982 | **0.3543** | 0.468 | +0.0560 [+0.0456,+0.0664] | -0.0024 |
| obl/spatial ATTACHMENT UD-EWT | 2294 | 0.7581 | **0.8496** | 0.629 | +0.0916 [+0.0770,+0.1067] | -0.0087 |

Risk-coverage (obl, calibrated): 10%=0.965 / 25%=0.937 / 50%=0.887 / 75%=0.812 / 100%=0.758. The reader is right
on ~96% of the arcs it is most confident about and abstains on the rest.

This is the bar's POSITIVE form: a CI-separated DEFER-POLICY / selective-reliability gain on the LIVE reader over
the blanket reader, on modern gold, with the random-confidence twin LOSING (the calibration is load-bearing) and a
DEPLOYED operating point (tau from dev, not an in-sample ranking -- the key advance over the predecessor's
diagnostic). QA-SRL's lower coverage (0.468) is honest: QA confidences are systematically lower (harder domain),
so a fixed dev tau defers more there -- the operating point still CI-separates.

## 3. THE TWO LOCATED NEGATIVES -- faithfully built, fully understood (each a full-pass form)

### 3a. FALL-BACK adds nothing (both readers) -- there is no better head-independent prior
Below tau, swapping the parse-arc pick for a prior does NOT raise ABSOLUTE accuracy:
- **PATIENT** (position prior): -0.0016 (UD) / -0.0356 (QA). The dev optimizer picks a low tau. Cause: the labeled
  patient readout is head-INDEPENDENT and robust (the predecessor's +0.086 finding) -- when it is uncertain,
  position is a WORSE reader, so there is nothing better to fall back to. ABSTAIN is its robust form.
- **OBL** (Late-Closure locality prior): nets 0 (the dev optimizer picks tau=0 -> never fall back). Cause, measured
  directly: the parser beats locality **even on its shakiest confidence-quartile** (parse 0.5436 vs locality
  0.3537). The graded down-weight arm degenerates to the same (prior_prec=0). So the located negative is precise:
  no head-INDEPENDENT prior is good enough; the fall-back that COULD beat the parse on its shaky arcs is the
  parse's OWN 2nd alternative -- which the greedy parser does not expose (LOSS 1 -> section 3b).

### 3b. The UPSTREAM small-beam parse posterior does NOT out-calibrate the landed confidence (LOSS 1)
I prototyped the brain-foundational upstream lever the predecessor named (give the greedy parser the AGENT organ's
competition property): a FAITHFUL small-beam arc-eager decode (SAME weights, SAME features, proper local-softmax
log-prob accumulation; only greedy argmax -> top-k beam), reading reliability three brain-foundational ways --
beam head-AGREEMENT, Lewis-Vasishth top1-top2 MARGIN, Hale-2006 parser-state ENTROPY.

| k | patient: raw / agreement / margin / neg-ent | obl: raw / agreement / margin / neg-ent |
|---|---|---|
| 8 | 0.615 / 0.549 / 0.550 / 0.547 | 0.721 / 0.699 / 0.700 / 0.713 |
| 16 | 0.615 / 0.571 / 0.572 / 0.548 | 0.721 / 0.737 / 0.736 / 0.738 |

ALL beam readouts are <= the greedy raw conf (obl at k=16 is a hair above raw 0.737 but still below the LANDED
calibrated confidence 0.736... it does not beat what we already have). It is a LOCATED NEGATIVE, and I drilled the
mechanism to the bottom (per the standing directive to research every wall fully):

- **Degeneracy**: the beam collapses to the greedy path on 74% (patient) / 56% (obl, k=8) of arcs -- the local
  scores are peaked, so the maintained distribution carries no extra information there.
- **Search vs scoring failure (the decisive diagnostic)**: on the parser's WRONG obl arcs, gold is in the beam
  only **0.492** of the time. So ~half the errors are SEARCH failures (the correct analysis fell off the beam =
  garden-path beam-pruning; Jurafsky 1996) that NO reweighting can recover, and the in-beam half is mis-weighted.
- **Ensemble agreement adds nothing**: query-by-committee over an INDEPENDENTLY-trained parser (arc_parser vs
  arc-eager head agreement) has AUC 0.696 ~= raw 0.721; deploying it as a fall-back net-REGRESSES (0.717 < 0.758).

**Root cause (literature-confirmed, dispatched research drill).** The parser is LOCALLY NORMALIZED and trained for
GREEDY decoding (dynamic-oracle averaged perceptron), so its action scores are not a globally-normalized posterior
over parses -- the classic LABEL-BIAS pathology (Bottou 1991; Lafferty, McCallum & Pereira 2001; Andor et al. 2016
prove globally-normalized > locally-normalized and that BEAM WIDTH does not fix it). Hale-2006 entropy and
Levy-2008 surprisal are defined over a globally-normalized generative grammar, NOT a discriminative local scorer
-- so BOTH the label-bias theory and the psycholinguistics PREDICT this negative. The beam IS the brain-foundational
mechanism (small-beam ranked-parallel; garden paths = beam-pruning); the wall is our parser's TRAINING. **The
single most brain-foundational next lever is a globally-normalized parse scorer with an EXACT posterior
(edge-factored Matrix-Tree marginals -- McDonald & Satta 2007 / Koo et al. 2007; or Andor-style beam-in-the-loop
global training) -- a different model, filed as a separate problem, not an inference-time fix.**

## 4. READ-COST / FLIP-ON EVIDENCE (net-neutral cost)

Today the opt-in path issues extra parses: `_cached_parse_heads` (l.1527) calls `parse_with_conf(...)[0]` and
DISCARDS conf/marg, then `_cached_parse_conf` (l.1544) parses the SAME sentence AGAIN to recover them, and
`_patient_arc_confidence` also calls the global arc_parser for the a2_marg cue. Measured (UD-EWT):

- arc-eager `parse_with_conf` **0.840 ms/sentence**; global arc_parser **0.997 ms/sentence**.
- **THE FOLD**: cache the full `(heads, conf, marg)` tuple from the ONE parse the reader already runs -> the
  duplicate arc-eager parse is removed for FREE (**-0.840 ms/read**; conf/marg are already computed and thrown away).
- **THE a2 DROP**: the global-arc_parser a2_marg cue is INERT for the patient (predecessor) and costs the obl
  calibrator only **0.0052 AUC** (0.7233 -> 0.7181). Drop it -> the obl defer path also scores off the single
  shared arc-eager parse.
- **Net**: after the fold, emitting the confidence + deferring on it adds **ZERO extra parses** (patient path;
  obl path too if a2 dropped, else +0.997 ms). Flip-on is net-neutral -- the cost objection is removed.

## 5. NO-REGRESS ON NON-CONSUMERS (additive)

`defer(conf, None)` returns False for every arc (tau=None), and the abstain policy at tau=-inf is byte-identical
to the blanket reader (answered==blanket, witness W6). The consumer is READ-ONLY over the parse and changes NO
head (the predecessor's W5). So the parse heads and every non-deferring dim are byte-identical; only a consumer
that OPTS to defer changes behavior (it declines to answer -- the intended "know what you don't know", not a
regression).

## 6. PROPOSED hdlab CHANGE (Q111 -- strategy lands it)

Purely ADDITIVE + a cost fix; default-safe, then flip-on.

1. **Remove the duplicate parse (the cost fix).** In `hdlab/situation_reader.py`, have `_cached_parse_heads`
   (l.1520) cache the FULL `(heads, conf, marg)` tuple from its single `parse_with_conf` call (today it keeps only
   `[0]`), and have `_cached_parse_conf` (l.1532) read from that shared cache instead of re-parsing. This is the
   -0.840 ms/read save that makes flip-on net-neutral. Drop the a2_marg cue from the obl calibrator path (or fold
   the arc_parser margin into the shared parse) so the obl defer path needs no 2nd parser (-0.0052 AUC, worth it).
2. **Build the DEFER-CONSUMER over the head-driven readout (the new piece).** Add a policy: for each role arc,
   score `PC.calibrated_patient_confidence` / `PC.calibrated_obl_confidence`; if `PC.defer(conf, tau)`, ABSTAIN
   (emit the role with a `defer=True` / low-confidence flag so the reasoning phase treats it as uncertain) rather
   than asserting it. Expose tau as `precision_weight_tau` (already a flag, l.1075). Do NOT fall back to a
   head-independent prior (section 3a -- it adds nothing); ABSTAIN is the deployable action. tau is a frozen
   dev-chosen scalar (e.g. the 75%-coverage operating point); ship the risk-coverage curve so the reasoning phase
   can pick its own coverage.
3. **Flip `precision_weight_roles` default-ON** once (1) lands (net-neutral cost) -- the EMISSION is byte-identical
   to every scored dim (additive); the DEFER behavior is the consumer's opt-in via tau. Do NOT wire the RAW arc
   margin (weak); do NOT wire the small-beam posterior (located negative); do NOT re-attach the parse.

## 7. ADJACENT COMPONENTS + WHAT I DID NOT ESTABLISH

- **who-did-what PATIENT / obl** -- the demonstrated consumers. Revisit: YES (add the ABSTAIN policy + the fold).
- **the greedy arc-eager parser** -- LOSS 1 root cause. Its local normalization caps every parse-confidence lever
  (section 3b). *Brain-status:* an OUR-INVENTION greedy scorer standing in for a globally-normalized ranked-parallel
  grammar. **Follow-on: a globally-normalized parser with exact Matrix-Tree marginals** (the north-star; would also
  give the PATIENT arc a real competition margin and enable a genuine 2nd-best fall-back).
- **the AGENT reader** (Competition-Model margin) -- already HAS the competition property (raw margin AUC 0.76);
  the predecessor precision-weighted it. Not re-touched.
- **NOT established**: (a) an ABSOLUTE-accuracy gain -- the deliverable is reliability (abstain), and fall-back
  does not raise absolute accuracy (section 3a, an expected located negative); (b) the live LitBank board number
  (19c, banned as load-bearing -- I measured modern UD-EWT + QA-SRL); (c) the SPACE register end-to-end (the obl
  attachment IS its modern reliability arc; the register is the additive-safe downstream consumer); (d) a
  globally-normalized parser (named follow-on, out of scope).

## 8. KEY REALIZATIONS (the enabling moves)

- **A deployed policy is a different deliverable from a ranking diagnostic.** The predecessor ranked picks and
  reported selective@50 on the in-sample top-half; the CONSUMER needs a FIXED tau chosen on DEV and applied on
  TEST, and must CHANGE the output (abstain). Choosing tau on dev and reporting the test coverage you actually get
  is what makes it deployable rather than a sensitivity demonstration.
- **The FALL-BACK negative and the UPSTREAM negative are the SAME wall.** Fall-back fails because there is no good
  head-independent prior to fall back to; the prior that WOULD beat the parse on its shaky arcs is the parse's own
  2nd alternative -- which the greedy parser cannot expose. Measuring "parse beats locality even on the shaky
  quartile" (0.5436 vs 0.3537) is what connected them.
- **gold-in-beam-when-wrong is the diagnostic that bounds the whole upstream lever.** 0.492 means HALF the parser's
  errors are search failures no reweighting can recover -- so a better DECODER (beam) is provably not the fix; a
  better MODEL (global normalization) is. This turned "beam doesn't help" into a bounded, literature-grounded verdict.
- **The cheapest win was reading the source: `_cached_parse_heads` throws conf/marg away and `_cached_parse_conf`
  re-parses.** The single biggest flip-on blocker (the extra parse) is a one-line caching fix, measured at -0.84
  ms/read -- the confidence is already computed.
- **Consume the FROZEN landed calibrator, don't re-fit.** Scoring with `hdlab.parse_confidence` (not a fresh
  logistic) proves the DEFER gain is the LANDED signal's live value, exactly what a flip-on decision needs.

## 9. AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md section 2b -- parse_confidence / precision-weighting)

- The filed flip-on follow-on is **realized (prototyped, not yet wired)**: a DEFER-CONSUMER that ABSTAINS on the
  landed calibrated confidence lifts LIVE selective reliability on modern gold (patient 0.8789->0.9662 UD /
  0.2982->0.3543 QA; obl 0.7581->0.8496; all CI-sep, random-confidence twin flat), with a DEPLOYED dev-chosen tau.
- **Flip-on cost RESOLVED**: the ~2 parses/read is removable -- fold `(heads,conf,marg)` into the one shared parse
  (-0.840 ms/read) + drop the inert a2_marg cue (-0.0052 obl AUC) -> the defer path is net-ZERO extra parse.
  Recommend flipping `precision_weight_roles` default-ON after the fold lands.
- **NEW located negative (LOSS 1 sharpened)**: a faithful small-beam decode of the greedy arc-eager parser does
  NOT out-calibrate the landed confidence (beam readouts <= raw greedy conf across k=6/8/16; gold-in-beam-when-wrong
  0.492). Root cause = LOCAL normalization / label bias (Andor 2016), not decoding width. The north-star for the
  parser-confidence residual is a GLOBALLY-NORMALIZED scorer with exact marginals (Matrix-Tree; McDonald-Satta
  2007), NOT an inference-time beam -- this sharpens the predecessor's "needs a small-beam distributional parser".
- **FALL-BACK confirmed as the expected negative**: neither the head-independent patient (position prior) nor the
  obl reader (locality prior) has a better prior to fall back to; ABSTAIN is the deployable action. Record: the
  robust defer action is ABSTAIN, not FALL-BACK.

---

### TLDR (plain English)
Our reader now produces a trustworthy "how sure am I" number for each grammar decision it uses to work out who did
what and where things attach -- but until now nothing used it, so the reader stated every answer as fact, shaky
ones included. I built the piece that ACTS on that certainty: when a decision is below a fixed confidence bar
(set once on a practice set, then used unchanged on fresh text), the reader HOLDS BACK instead of asserting a
coin-flip. On modern writing this makes it markedly more reliable on the answers it does give -- who-was-acted-on
goes from right about 88 in 100 to about 97 in 100 (answering the confident two-thirds), and where-things-attach
from 76 to 85 in 100 -- and a scrambled fake-certainty control does NOT do this, so the certainty is really
carrying the load. I also removed the main reason not to switch this on: the certainty was being computed by
parsing each sentence twice; caching one parse instead makes it essentially free, so turning it on costs nothing.
Two honest dead-ends, both chased to the bottom: (1) instead of holding back, letting the reader FALL BACK to a
simple default guess adds nothing -- when the grammar engine is unsure, the simple guesses are worse than it is,
so there is nothing better to switch to; (2) I tried to make the grammar engine itself produce a richer certainty
by having it keep several competing analyses instead of one -- and it doesn't help, because this engine was trained
to make one greedy choice, so half the time the right analysis isn't even among the ones it keeps. The fix for
that is a differently-built grammar engine (a known, separate piece of work). The payoff of what DID work: a reader
that knows which of its answers to trust, which is exactly what any later reasoning has to stand on.

### QUESTIONS
None. (The consumer clears the bar's CI-separated + twin-losing + deployed-tau + net-neutral-cost conditions on
three modern instruments; the two located negatives are faithfully built and attributed to a named cause with the
literature confirming; the flip-on cost is resolved. One judgment call: I graded SOLVED because a real,
twin-controlled, DEPLOYED-policy reliability gain landed on the live readers -- the bar's positive form -- with the
fall-back and upstream negatives as full-pass secondary findings, not the headline.)

### NEXT STEPS (ordered)
1. **LAND the fold + the ABSTAIN defer-consumer (strategy / Q111) -- section 6.** Cache `(heads,conf,marg)` once
   (removes the duplicate parse), add the abstain policy on the head-driven readout keyed on `precision_weight_tau`,
   then flip `precision_weight_roles` default-ON (net-neutral cost, additive emission).
2. **Add a MODERN selective-reliability board arm** so this live defer gain is board-VISIBLE (the board scores
   blanket accuracy on 19c gold; reuse this cell's answered-acc-at-dev-tau + twin).
3. **File the globally-normalized parser** (exact Matrix-Tree marginals / Andor beam-in-the-loop) -- the north-star
   that would give a genuine parse posterior (better confidence AND a real 2nd-best fall-back), recovering the
   ~half of parser errors that are search failures. This is where the remaining parse-confidence reliability lives.
4. **DO NOT**: wire the RAW arc margin (weak); wire the small-beam posterior (located negative, label bias); use
   FALL-BACK for the patient/obl defer (adds nothing -- ABSTAIN); re-attach the parse; or quote a fall-back
   absolute-accuracy gain (there is none -- an expected located negative).
