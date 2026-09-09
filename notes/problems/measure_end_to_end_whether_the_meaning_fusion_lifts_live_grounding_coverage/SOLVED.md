---
problem: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage
status: PARTIAL
bar: "PASS = an END-TO-END measurement on the LIVE reading-grounding loop (a faithful harness of canonicalize_fast's read over the real reading corpus, curriculum-ordered as the loop does it) showing whether reading the sense-assignment ranking over the reliability-weighted convergent fusion (grounded + distributional [+ is-a/taxonomic identity], the landed convergent_cue_reader Bayes rule, weights/taus calibrated OFFLINE + held-out) changes the loop's OWN downstream GROUNDING-COVERAGE GROWTH metric -- with (a) the INFO-FREE TWIN (shuffled representation rows) LOSING, (b) the recall/recognition path byte-identical, (c) the number reported with a CI on the loop's own metric/population (no cross-population/scorer number). A CI-SEPARATED lift is a landable win. A rigorous LOCATED NEGATIVE -- the ranking win does NOT transfer to coverage -- is a FULL PASS if it names, WITH A NUMBER, exactly why (e.g. coverage is gated by candidate GENERATION not sense SELECTION; or the loop's coverage is exposure-bound not decision-bound), and then builds the stronger brain version and tests THAT before concluding."
result: "TWO-PART. (1) LOCATED NEGATIVE on the loop's OWN coverage-COUNT metric: the sense-assignment representation does NOT cleanly move n_grounded -- it is decision-quality-BLIND. Genuine online loop over the full curriculum (4640 sentences, curriculum-ordered, process_sentence + consolidation_pass with a swapped sense-assignment gate): INCUMBENT (distributional) grounds 143 words; the fusion grounds 133 (strict accept) to 202 (accept-all) depending ONLY on the accept threshold -- the count tracks thresh-clearing/exposure, NOT ranking correctness. And the incumbent's 143 grounded links are co-occurrence garbage (artwork->happy, google->hope, owner->fine). (2) CI-SEPARATED WIN on coverage QUALITY (the instrument the count is blind to): ranking the true SimLex-999 sense-partner against the loop's ACTUAL 556-word seed-anchor pool through canonicalize's real decision, a brain-foundational meaning representation beats the distributional incumbent CI-separated -- GROUNDED-ATL MRR@cov0.5 +0.158 CI[+0.089,+0.252] and hit@1@cov0.5 +0.106 CI[+0.021,+0.191] (all-query, n=94; both parameter-free); full-coverage MRR +0.103 CI[+0.058,+0.153]; AUF-MRR grounded-distinctive 0.232 > grounded 0.198 > fusion 0.130 > incumbent 0.037 > twin 0.010. REFINEMENT of the brief's mechanism: the transfer is carried by the GROUNDED ATL identity channel, NOT the grounded+distributional FUSION -- on the live anchor pool the distributional channel is noise, so grounded-alone >= fusion (fusion still beats incumbent +0.096 CI[+0.022,+0.189] but trails grounded)."
floor: "Strongest floor = the DISTRIBUTIONAL incumbent (the loop's live canonicalize representation): coverage-quality MRR@cov0.5 0.034, hit@1 0.000-0.033, AUF-MRR 0.037; live coverage count n_grounded 143. Info-free twins (shuffled representation rows): AUF-MRR 0.010 (fusion twin) / carries no per-word signal. On the true-BF representation prototype the sparse structured channel's own floors: bag-of-words AUF-MRR 0.030, its info-free twins 0.006-0.008."
controls: "INFO-FREE TWIN (shuffled grounded/representation rows) LOSES CI-separated on every headline (grounded vs twin MRR@0.5 +0.195 CI[+0.106,+0.298]; fusion vs twin +0.122 CI[+0.028,+0.241]; DEP-structured vs twin +0.097 CI[+0.042,+0.178]) -> the win carries real per-word meaning, not base-rate. RECALL/RECOGNITION PATH BYTE-IDENTICAL: canonicalize_fast == reference canonicalize (witness W5; only what the ranking READS changed; no hdlab written). HARNESS FAITHFULNESS positive control: the cell's INCUMBENT gate decision == the live canonicalize (accept/refuse + chosen anchor) on 40/40 random query bundles (W4). INDEPENDENT GOLD: SimLex-999 human similarity (WordNet-independent, independent of every representation). HELD-OUT: the fusion weight w is calibrated on a disjoint train split and evaluated on test; grounded/incumbent are parameter-free (evaluated on all queries, no leak). FAITHFUL POOL: candidates restricted to the loop's ACTUAL seed-anchor field (not the full vocab) -- ranking against the whole 4678-word vocab drives hit@1 to floor for every arm and hides the transfer. THRESHOLD SWEEP: coverage count reported across accept thresholds (matched selectivity) so the count comparison is not a single confounded point. PHASE-DIAGRAM densification SWEEP (k in {50,100,200} x power in {0.5 SGNS, 0.0 whitened}) -- excludes 'the structured channel is just under-optimized'."
files_changed: "experiments/exp_meaning_fusion_live_coverage_v1.py (the end-to-end transfer measurement: PART A genuine online coverage-count + PART B coverage-quality selective-prediction frontier, all arms, twins), experiments/exp_meaning_fusion_bf_representation_v1.py (the TRUE-BF representation prototype -- FIX #3/#5: ATL distinctive-feature whitened grounded + structured dependency/adjacency PPMI substitutability, convergent-cue Bayes, + the phase-diagram SVD-densification sweep), experiments/exp_meaning_fusion_bf_accept_criterion_v1.py (FIX #7: the self-calibrating SDT accept criterion on the scale-free z_top standout, replacing the fixed cosine), verification/test_meaning_fusion_live_coverage.py (scaffold-free witness, 6/6), data/exp_meaning_fusion_live_coverage_v1/metrics.json, data/exp_meaning_fusion_bf_representation_v1/metrics.json, data/exp_meaning_fusion_bf_accept_criterion_v1/metrics.json. NO hdlab/ modified (Q111 -- the hdlab proposal is stated below for the strategy session to land)."
reverify: ".venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py  (6/6: recomputes the transfer at limit=1500 + reads the full landed disk facts, incl. the three fixes). Powered headline reproducer (own-dir only): .venv/Scripts/python.exe experiments/exp_meaning_fusion_live_coverage_v1.py --mode full --no-online"
---

# What this is: the fusion does NOT lift the loop's coverage COUNT (the count is quality-blind), but a brain-foundational meaning representation lifts coverage QUALITY CI-separated -- and the lever is GROUNDED, not the grounded+distributional fusion

**The short version.** C7 proved the reliability-weighted convergent fusion beats the distributional
incumbent on the sense-assignment RANKING PROXY (MRR vs SimLex). This problem asked whether that transfers
to the live loop's downstream grounding coverage. It does -- but not the way the brief hypothesized, and
not on the metric the loop currently scores:

1. **The loop's OWN coverage-COUNT metric (`n_grounded`) is decision-QUALITY-BLIND.** A word grounds iff
   `canonicalize` finds an eligible anchor over `SENSE_MATCH_THRESH`; the count checks only that SOME anchor
   clears the threshold, never that the link is CORRECT. So the count tracks threshold-clearing and exposure,
   not ranking quality. Measured on the genuine online loop over the full curriculum: incumbent grounds 143
   words; the fusion grounds 133-202 depending ONLY on the accept threshold. There is no clean count lift --
   a **located negative, with numbers** (exactly the bar's blessed "coverage is gated by generation/exposure,
   not sense selection").
2. **Coverage QUALITY -- did the loop link the word to the RIGHT meaning? -- is where the transfer lives, and
   it is CI-separated.** Ranking the true SimLex sense-partner against the loop's actual seed-anchor pool
   through `canonicalize`'s real decision, the grounded ATL representation beats the distributional incumbent
   **+0.158 MRR / +0.106 hit@1 CI-separated**, info-free twin losing, recall path byte-identical. The
   incumbent's own coverage-quality is at floor (hit@1 ~ 0) and its 143 grounded links are co-occurrence
   garbage (`artwork->happy`, `google->hope`, `owner->fine`) -- the C7 loss, live, in the store's content.
3. **REFINEMENT of the brief's mechanism (leave-room-to-solve-it-differently).** The transfer is carried by
   the **GROUNDED ATL identity channel**, NOT the grounded+distributional FUSION. On the live anchor pool the
   distributional channel is noise, so grounded-alone (AUF-MRR 0.198) >= the fusion (0.130); the ATL
   distinctive-feature (whitened) read is the single best arm (0.232). The fusion still beats the incumbent
   CI-separated (+0.096), it just trails grounded -- consistent with C7's own grounded-dominant weight w=16.

## The measurement (faithful to the live loop)
`exp_meaning_fusion_live_coverage_v1.py`. Two instruments, because the loop's own metric cannot see quality:
- **PART A (loop's OWN coverage count, genuine online).** `process_sentence` + `consolidation_pass` with a
  custom sense-assignment `mdl_gate_fn` per arm, over the real curriculum corpus, curriculum-ordered. The
  INCUMBENT gate is byte-identical to the live `canonicalize` (witness W4, 40/40). Only what the ranking
  READS changes; the schema/exposure gate, the field growth, and the recall/recognition path are the loop's.
- **PART B (coverage QUALITY frontier, the headline).** Threshold-free selective-prediction: rank the true
  SimLex-999 near-synonym partner against the loop's actual 556-word seed-anchor pool; sort queries by each
  arm's own confidence; at coverage c report precision = hit@1 / MRR among the top-c. A better ranker
  DOMINATES the frontier. Paired bootstrap CI (3000x) over queries; info-free twin (shuffled rows) losing.

I first established on the CURRENT bytes (a probe, folded into the design) that `canonicalize`'s threshold
is a HARD gate on ALL coverage: on current code every grounded word is LINKED (0 self-grounded) and ~40% of
consolidation-survivors are refused (TAUTOLOGY_NO_ANCHOR, best_cos just under 0.45). The landed 2026-08-12
`cycle1` metrics show 124 self-grounded words -- that reflects OLD code (pre the refuse-tautology fix); on
current bytes the sense-assignment ranker gates coverage, which is why the representation matters here.

## Coverage-quality numbers (SimLex gold, loop's anchor pool, n=94 all-query / n_test=47 held-out)
| arm (rank true partner among the 556-word seed-anchor pool) | AUF-MRR | vs incumbent MRR@cov0.5 |
|---|---|---|
| INCUMBENT (distributional bag -- the live representation) | 0.037 | -- (floor) |
| info-free TWIN (shuffled rows) | 0.010 | loses CI-sep |
| GROUNDED+DISTRIBUTIONAL FUSION (C7's arm, held-out w=16) | 0.130 | +0.096 CI[+0.022,+0.189] |
| **GROUNDED ATL (the lever)** | **0.198** | **+0.158 CI[+0.089,+0.252]** |
| **GROUNDED-DISTINCTIVE (whitened ATL -- upstream BF upgrade)** | **0.232** | **+0.182 CI[+0.102,+0.275]** |

hit@1@cov0.5 grounded +0.106 CI[+0.021,+0.191]; grounded vs twin +0.195 CI[+0.106,+0.298]. The distinctive
(whitened) read is directionally best but NOT CI-separated over raw grounded (+0.024 CI[-0.036,+0.084]) --
its held-out SimLex edge does not clearly transfer to the live task (echoing C7's "BF residuals null").

## FULL-STACK-UPSTREAM: the true-BF representation, prototyped and math-audited (owner directive)
`exp_meaning_fusion_bf_representation_v1.py`. The signal-loss trace located the non-BF weak link: the
sense-assignment ranks a DISTRIBUTIONAL BAG-OF-COOCCURRENCE (NOT_BF: unordered pooling; carries relatedness,
not identity; live coverage-quality hit@1 ~ 0). Prototyped the representation that IS brain-foundational,
per-operation:

| operation | brain-foundational? (math) |
|---|---|
| grounded z-score | BF -- subtractive+divisive normalization (Carandini-Heeger) |
| grounded WHITENING (distinctive-feature) | BF -- decorrelate the shared axis = ATL privilege-distinctive-features (Patterson-Nestor-Rogers) |
| PPMI = max(0, log p(w,c)/(p(w)p(c))) | BF -- rectified pointwise MI = predictive surprise / Hebbian-predictive fixed point (Levy-Goldberg) |
| ADJ structured context (direction-typed adjacency) | BF -- sequential order intrinsic; NO parser (fully BF end-to-end) |
| DEP structured context (dependency-typed) | BF operation; parse INPUT NOT_BF (frozen supervised arceager -> fix incremental_parser) |
| SVD densification | BF -- efficient-coding / linear-autoencoder cortical dim-reduction (SVD-of-PPMI ~ SGNS) |
| convergent fusion (equal-weight sum of log-Gibbs-posteriors) | BF -- Bayes cue integration, uniform prior, no fitted params (Ma/Pouget) |
| cosine population read | BF -- population coactivation + divisive normalization (Georgopoulos) |

**Findings (full curriculum, n=94):**
- **Structured > unordered, LIVE (Levy-Goldberg confirmed):** the dependency-substitutability PPMI channel
  (DEP, AUF-MRR 0.105) beats its info-free twin CI-separated (+0.097 CI[+0.042,+0.178]) and beats the
  bag directionally (+0.075 CI[-0.003,+0.156]). Pure adjacency (ADJ, no parser) is much weaker
  (0.018) -- the dependency structure, not mere order, carries the identity signal.
- **The structured channel is EXPOSURE-limited, not a ceiling:** DEP rose 0.022 -> 0.105 as reading went
  900 -> 4640 sentences (still far below C7's 34k). But it does NOT yet exceed grounded (0.188), and fusing
  it with grounded is null (does not lift grounded at this exposure).
- **PHASE-DIAGRAM densification move (owner: "make signals dense easily"), swept and MEASURED:** truncated
  SVD densification of the sparse structured PPMI (k in {50,100,200} x power in {0.5 SGNS, 0.0 whitened})
  did NOT cross the wall -- every dense config underperforms the raw sparse channel (best 0.070 < 0.105) and
  AUF rises monotonically with k TOWARD the sparse value. The reason is mechanistic and generalizable:
  meaning-IDENTITY lives in the rare DISTINCTIVE contexts, which low-rank compression smooths away (the same
  place low-variance directions get dropped). Densify-by-WHITENING HELPS a LOW-dim shared-axis-dominated
  signal (it is exactly why grounded-distinctive 0.232 > grounded-raw 0.188); it HURTS a high-dim
  sparse-distinctive signal. So for the structured channel the lever is EXPOSURE (or a better structure),
  not compression. (Recorded in memory: densify AND measure; whiten low-dim, do not low-rank-compress
  sparse-distinctive.)

## THE THREE NON-BF WEAK LINKS -- FIXED, fully brain-foundational (owner: "fix them, right not easy")
The performance-vs-brain audit named three components in the upstream chain that were NOT fully BF. They
collapse into two real fixes (the representation fix sidesteps the parser), both prototyped + measured:

**FIX #3 (unordered bag-of-words pooling = the total identity-signal loss) AND #5 (arc-eager parser = NOT_BF
parse input) -- fixed by the SAME move: use the GROUNDED-DISTINCTIVE ATL representation, which needs NO bag
and NO parser.** The bag carries relatedness not identity (live hit@1 ~ 0); the grounded-distinctive read
(z-score = normalization, whitening = ATL privilege-distinctive-features decorrelation) beats it CI-separated
(+0.182 MRR CI[+0.102,+0.275]) and uses only the PINNED Lancaster/Brysbaert norms -- no unordered pooling, no
supervised parser. So the fully-BF representation SIDESTEPS both non-BF dependencies rather than patching
them. (The structured-DISTRIBUTIONAL channel that WOULD need a BF parser is exposure-limited and not the
lever; forcing a parser build there would be metric-chasing, not the right fix. The BF parser
`incremental_parser` remains the mapped follow-on IF that channel is later pursued at reading volume.)

**FIX #7 (the OUR-INVENTION fixed cosine `SENSE_MATCH_THRESH=0.45`) -- fixed by a self-calibrating SDT
criterion on a scale-free familiarity standout** (`exp_meaning_fusion_bf_accept_criterion_v1.py`). MEASURED:
the fixed cosine is representation-BROKEN -- 0.45 admits 22% of decisions in the distributional geometry (what
it was tuned for) but 100% in the grounded geometry (grounded cosines cluster ~0.87-0.92), spread 0.78. The
easy patch (re-sweep 0.45 per rep) is not the right fix. The BF fix: the accept decision is a FAMILIARITY
signal exceeding a CRITERION on a DIVISIVELY-NORMALIZED axis -- z_top = (s1 - mean)/std over the candidate
field (Carandini-Heeger gain control; scale-free), with the criterion set by SIGNAL-DETECTION THEORY (the
z_top at a target false-alarm rate on the info-free null; Yonelinas 2002; Bruce-Young/IAC familiarity gate).
Because z_top is scale-free, the criterion self-calibrates in ANY representation's geometry -- NO hand-set
constant, NO re-tuning when the representation changes. MEASURED: on grounded-distinctive the SDT criterion
gives a controllable precision-coverage knob (5% FA -> accept 5% at 0.600 hit@1; 20% FA -> accept 19% at
0.278), z_top ordering costs NO ranking quality vs raw cosine (+0.000 hit@1@0.5), and accept-by-z_top beats
the info-free twin CI-separated (+0.128 CI[+0.043,+0.234]). BF math verified per operation.

So the fully-BF sense-assignment decision = read canonicalize's ranking over the GROUNDED-DISTINCTIVE ATL
representation (no bag, no parser), accept by a SELF-CALIBRATING SDT familiarity criterion on the scale-free
standout (no fixed cosine). Every operation in that path is a brain computation (see the BF ledgers in the
two cells); nothing in it is an OUR-INVENTION constant or an external tool.

## The hdlab proposal (for the strategy session to land, Q111)
A map + witnessed prototype, not a landed diff. All LOCAL to the ranking's READ; the recall/recognition path
stays byte-identical (witness W5).
1. **Read `canonicalize`'s sense-assignment ranking over the GROUNDED ATL representation** (grounded-dominant;
   `grounded_similarity.grounded_vector`, or the distinctive-feature whitened `distinctive_grounded_vector`),
   NOT the distributional context bundle. On the live anchor-pool decision this is the lever
   (+0.158 MRR / +0.106 hit@1 CI-sep over the incumbent). Keep it a single-shot graded population read.
   **DOWN-WEIGHT the distributional channel to ~0 for this decision** (it is relatedness noise on the small
   anchor pool; grounded-alone >= the grounded+distributional fusion here) -- i.e. the C7 fusion-wire should
   land grounded-DOMINANT, not equal-weight, for canonicalize.
2. **REPLACE the fixed `SENSE_MATCH_THRESH=0.45` with the self-calibrating SDT familiarity criterion** on the
   scale-free z_top standout (`exp_meaning_fusion_bf_accept_criterion_v1.py`). 0.45 is representation-BROKEN
   (admits 22% in the distributional geometry, 100% in the grounded one). The BF fix -- accept iff z_top =
   (s1-mean)/std over the candidate field exceeds the criterion at a target false-alarm rate on the info-free
   null -- is scale-free and self-calibrating, so it needs NO re-tuning when the representation changes (and no
   hand-set constant). The FA rate is the precision-coverage knob (5% FA -> 0.60 hit@1 on grounded). This is
   the BF replacement for the fixed threshold, not a re-sweep.
3. **BUILD A COVERAGE-QUALITY INSTRUMENT** (correct-link rate against an independent gold), because the loop's
   current `n_grounded` COUNT is decision-quality-blind and will not show this win. Without it the lift is
   real but board-invisible.
No other downstream consumer regresses: the change is only what the ranking READS; `canonicalize_fast` ==
reference `canonicalize` (recall/completion untouched), and no hdlab was written.

## What I did NOT establish (and would withdraw first if wrong)
- **I did NOT show the fusion lifts the loop's `n_grounded` COUNT** -- it does not (the count is quality-blind).
  The first thing I would withdraw is any implied coverage-COUNT gain. The win is on coverage QUALITY
  (correct sense-links), measured on an instrument I built, against an independent gold.
- **The quality win is on the SimLex-covered subset of the anchor-pool decision** (n=94 all-query / 47
  held-out), not on every corpus word the loop grounds (most corpus words have no similarity gold). It is a
  faithful sample of `canonicalize`'s decision, not a whole-corpus correct-coverage census.
- **The distinctive-feature (whitened) upgrade is directional, not CI-separated over raw grounded** on the
  live task; I would not claim it as a separate win, only as the more-brain-foundational default.
- Absolute coverage-quality remains low (MRR ~ 0.1-0.2 among 556 anchors); I claim a decisive RELATIVE win
  over the incumbent, not a solved absolute task.

## KEY REALIZATIONS
- **Measure the metric the mechanism actually affects.** The loop's own coverage COUNT cannot see a
  sense-assignment quality improvement -- it counts threshold-clearing, not correctness. The transfer is real
  but invisible on the count; it needed a coverage-QUALITY instrument to surface. (Board-invisible win needs
  its own instrument-arm.)
- **Rank against the LIVE anchor field, not the full vocab.** Ranking the partner among all 4678 covered
  words drove hit@1 to floor for every arm and hid the transfer; restricting to the loop's actual ~556-word
  seed-anchor pool (what `canonicalize` really scans) is both faithful and where the win is visible.
- **The brief's fusion was over-specified; the identity channel is the lever.** C7's grounded+distributional
  fusion helps in the full-vocab proxy but on the live anchor decision the distributional channel is noise;
  grounded-alone is stronger. The reliability weighting was already telling us this (w grounded-dominant).
- **Densification is not universally a win -- it depends WHERE the signal lives.** Whitening a low-dim
  shared-axis signal (grounded) sharpens identity; low-rank-compressing a high-dim sparse-distinctive signal
  (structured PPMI) discards it. Moved the operating point on the phase diagram AND measured, rather than
  assuming either direction.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- `reading_grounding_loop` (BF_SPIRIT): confirmed the BF_SPIRIT residual is the REPRESENTATION the ranking
  reads (distributional bag = NOT_BF unordered pooling), now measured LIVE on the loop's coverage-quality
  (incumbent hit@1 ~ 0; grounded beats it +0.106 CI-sep). The `canonicalize_fast` graded read itself is BF
  and untouched.
- New deviation to record: the loop's coverage metric `n_grounded` (COUNT) is decision-quality-blind -- it
  cannot register a sense-assignment quality gain, so it is the wrong instrument for the meaning-channel
  landing. A correct-link coverage-quality instrument is the missing measurement organ.

---
## TLDR (plain language)
When the system reads a new word it grows its vocabulary by deciding which known word it means. We asked: if
it makes that decision with a more brain-like sense of meaning (what a thing IS -- its felt/perceptual
identity) instead of mere word-company, does it end up knowing MORE words after a real read? The plain count
of words it "learned" does NOT go up -- but that count is a bad yardstick: it only checks that the system
picked SOME match, never whether the match is RIGHT, and today most of its matches are junk (it links "owner"
to "fine", "google" to "hope"). When we measure whether the matches are CORRECT, the brain-like meaning cue
wins clearly and reliably, and the plain word-company cue is essentially never right. The winning cue is the
grounded "what it is" sense; adding word-company back in only adds noise here. We also tried the owner's
"make the signal dense" trick on a second, learned cue; it helped the perceptual cue but not the learned one
(that cue's meaning lives in rare specific clues that get blurred by compression -- it needs more reading, not
compression). Bottom line: don't expect more words learned; DO expect the words it learns to be matched to the
RIGHT meaning far more often -- and to see that, we need to start scoring match CORRECTNESS, not just counts.

## QUESTIONS
None blocking.

## NEXT STEPS
1. **(hand-off to strategy, Q111)** Land the fully-BF sense-assignment decision: read `canonicalize`'s
   ranking over the GROUNDED-DISTINCTIVE ATL representation (grounded-dominant; distributional down-weighted to
   ~0 on this decision; no bag, no parser -- FIX #3/#5), and REPLACE the fixed `SENSE_MATCH_THRESH` with the
   self-calibrating SDT familiarity criterion on the z_top standout (FIX #7). Recall path byte-identical. This
   is the C7 fusion-wire, REFINED to grounded-dominant with a brain-foundational accept gate.
2. **(the missing instrument -- prerequisite to a visible landing)** Build a coverage-QUALITY / correct-link
   metric (independent gold) into the loop's measurement, so a sense-assignment quality gain is scorable. The
   current `n_grounded` count will not show it.
3. **(the structured channel's real lever)** The dependency-substitutability channel is exposure-limited, not
   ceilinged -- it rises with reading and is BF (parse input aside). The lever is MORE READING (the
   grow-by-reading north-star) and a BF general parser (`incremental_parser`) to remove the arceager NOT_BF
   dependency -- a mapped follow-on, not this deliverable. Densification is NOT the lever for it (measured).
