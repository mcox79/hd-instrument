# ORGAN A -- THE WRITE-RULE STEP LADDER: WHICH STEP DESTROYS SUBSTITUTABILITY?

Cell: `experiments/exp_writerule_step_ladder_v1.py`. FULL landed, code_version v1.2, 48s,
`data/exp_writerule_step_ladder_v1/metrics.json`. Smoke (`--grid reduced`, n=300) landed first at
`data/exp_writerule_step_ladder_v1_reduced/metrics.json`. **v1.2 is a correction round** on v1.1
(monotonicity-bug fix) after the coordinator caught an apparent sign disagreement with the sibling
cell -- section 0b below is the resolution, and it changes the sentence this note leads with.

## 0a. THE MONOTONICITY CONSTRUCTION BUG (v1.0 -> v1.1, kept for the record)

v1.0's first FULL run printed `WRITERULE_LADDER_LEAK_DETECTED`. It excluded R3 out of the
monotonicity chain array entirely (meaning to exempt only the R2->R3 transition), which made R2 and
R4 artificially adjacent and scored a two-step movement as a one-step "leak". Fixed in v1.1 with
three PER-LEG checks (`[R1,R2]`, `[R3,R4]`, `[R4,R5]`); the underlying arm accuracies never changed.

## 0b. THE SIGN RECONCILIATION WITH `exp_pipeline_stage_oracle_ladder_v1` -- RESOLVED, IN WRITING

**The coordinator is right that two numbers looked like a contradiction, and the cause was found:
this cell's own PROSE mislabelled two directions. The underlying data was never in conflict.**

Both cells difference the IDENTICAL quantity with the IDENTICAL formula and sign convention
(`FB.margin`: `point = hit@1(upstream_arm) - hit@1(downstream_arm)`), on the SAME reused DIAG_B1 /
DIAG_B2 arm constructions:

| step | this cell's `drop_point` | sibling's `drop_point` | agreement | plain reading |
|---|---|---|---|---|
| ACCUMULATE (single occ -> full accum) | **-0.0263** [-0.0343,-0.0186] | **-0.0263** [-0.0343,-0.0186] | bit-for-bit | a **GAIN of +0.0263** |
| CODE_PROJECT (unprojected -> projected) | **+0.0123** [+0.0060,+0.0188] | **+0.0123** [+0.006,+0.0188] | bit-for-bit | a **LOSS of -0.0123** |

**A negative `drop_point` means the downstream arm scored HIGHER (a GAIN); a positive `drop_point`
means the downstream arm scored LOWER (a real LOSS).** `band="BELOW"` means "upstream sits below
downstream" (downstream higher = GAIN); `band="ABOVE"` means "upstream sits above downstream"
(downstream lower = LOSS). An earlier draft of this note's own prose read these backwards --
calling ACCUMULATE's GAIN "the largest drop" / "the step with the largest accuracy cost", and
calling CODE_PROJECT's LOSS a case of "projection genuinely helping accuracy". **Both were wrong
readings of a correctly-computed number.** v1.2 adds an explicit `direction_of_step_a_to_b` field
(`GAIN`/`LOSS`/`FLAT`) to every row of the RANKED_DROP_TABLE in the metrics so no future reader has
to re-derive the sign, and this note is rewritten below to state directions in plain language
throughout, never via a bare signed number.

**Corrected ranked drop table** (n=3994, paired bootstrap):

| rank (by \|drop\|) | step | direction | magnitude | CI95 |
|---|---|---|---|---|
| 1 | ACCUMULATE (single occ -> full accum, background ALSO accumulated) | **GAIN** | +0.0263 | [+0.0186,+0.0343] |
| 2 | CODE_PROJECT (unprojected -> d=256 projected) | **LOSS** | -0.0123 | [-0.0188,-0.0060] |
| 3 | NORMALISE (graded -> sign-quantised) | loss, not significant | -0.0016 | [-0.0085,+0.0051] NOT_SEPARATED |
| 4 | FILTER (unfiltered -> filtered) | loss, not significant | -0.0009 | [-0.0033,+0.0016] NOT_SEPARATED |

ACCUMULATE (a gain) still dominates the ranked-|drop| table at 64% of total movement -- STOP-IF (i)
still fires, but the correct reading is **"one step is doing almost all of the WORK, and that work
is a gain, not a loss"**, not "one step destroys almost everything". CODE_PROJECT is the only
CI-separated genuine LOSS among the four steps.

## 1. THE DECISIVE ARM -- THE COORDINATOR'S SUSPECTED READING, TESTED, NOT ADOPTED

**The question:** does R2->R3's ACCUMULATE gain come from more evidence, from summing it into one
vector, or both -- and does summing throw part of the evidence back away, as suspected?

**Design.** Background (every OTHER anchor) held at single-occurrence throughout. ONLY the target
item's own cue/row varies: `RANDOM_SINGLE` (its own first occurrence, R2's construction exactly),
`SUM_ALL` (its full-accumulation row swapped in), `BEST_SINGLE_ORACLE` (every one of its own profile
occurrences -- mean 31.0, median 20 per item -- tried individually against the SAME fixed
background; any hit counts). n=300 (cost-bounded subsample of the composition idx_probe),
self-tested with a discriminator-fires fixture (a "loud decoy" occurrence buries a "correct"
occurrence so RANDOM_SINGLE and SUM_ALL both miss and only the oracle finds it -- proved the
instrument can actually discriminate the three arms before trusting it on real data).

**Result, all three margins CI-separated:**

| arm | hit@1 (n=300) | margin vs RANDOM_SINGLE |
|---|---|---|
| RANDOM_SINGLE | 0.0367 | -- |
| **SUM_ALL** | **0.0100** | **-0.0266 [-0.0500,-0.0033], BELOW** |
| **BEST_SINGLE_ORACLE** | **0.3033** | **+0.2664 [+0.2167,+0.3133], ABOVE** |

BEST_SINGLE_ORACLE vs SUM_ALL: +0.2930 [+0.2400,+0.3433], ABOVE.

**The reading, stated as the coordinator asked, and it is SHARPER than the suspected version, not
merely confirmed:** holding the competitive field fixed, summing an anchor's occurrences does not
merely "throw part of the gain away" -- **it scores WORSE than a single arbitrary occurrence**
(0.0100 vs 0.0367), while the retrievable information is an order of magnitude larger than either
(0.3033 via an oracle that only ever looks at ONE occurrence at a time). This is DIFFERENT from and
does not contradict R2->R3's population-level +0.0263 GAIN: that comparison ALSO deepens every
competing anchor, so the whole competitive landscape gets diluted together and relative
discriminability can rise even while the SUM ITSELF is, per-target, a worse representation than a
single well-chosen sentence. **Two true, non-contradictory statements about different comparisons:**
"more evidence, summed into everyone's store together, nets a population-level gain" and "summing
one anchor's own evidence, holding its competitors fixed, is worse than not summing at all."

**"Accumulate without collapsing" SURVIVES as the build target, and this arm is the direct evidence
for it, not an inference from the population-level number.** The oracle ceiling (0.30) is roughly
2.5x the incumbent's own real read-out (0.0481) and ~8x RANDOM_SINGLE -- summing is actively
destroying reachable signal, not merely failing to add it.

## 2. THE STEP LIST (unchanged from v1.1) -- WHAT WAS ENUMERATED AND HOW

Read `hdlab/grounding_acquisition_loop.py` and `hdlab/reading_grounding_loop.py` directly, verified
against and extending `exp_pipeline_stage_oracle_ladder_v1` (e28d1b8d6). **The Director's five-item
sketch (filter / code / accumulate / normalise / superpose) collapses to FOUR live steps** --
FILTER, CODE (the sketch's "superposition with every other word" is the SAME event as CODE, not
separate: cross-talk lives inside the one shared-basis d=256 projection), ACCUMULATE, NORMALISE.

**NORMALISE (sign quantisation) is OFF BY DEFAULT since 2026-08-14** (`GRADED_COMPARATOR`, env
`HD_GRADED_COMPARATOR`, default ON means sign() never fires). **This recontextualises the whole
arc: every headline number in this programme, including the 79.3% no-relation and 4.24x
co-occurrence figures, was measured with quantisation NOT firing. Anyone who believed quantisation
was in the live path was wrong.**

## 3. GATES

REGRESSION (lam=0.00 full population) 0.0223 vs 0.0223 PASS. K1 KNOWN-ANSWER: addressing
0.9975-1.0000 on all 5 rungs (gate 0.95) PASS. N1 NULL (deranged assignment): 0.000000 vs chance
0.00018, PASS. ARMS-MUST-DIFFER: 11 of 11 distinct digests. `R4` reproduces this arc's exact-key
headline (0.0481) bit-for-bit.

## 4. MONOTONICITY -- HELD, PER LEG

FILTER, CODE_PROJECT, NORMALISE each checked as a genuinely-adjacent pair (reused
`check_monotone_nonincreasing`, same convention the sibling cell uses): **MONOTONE, 0 leaks, all
three legs.** ACCUMULATE (R2->R3) is excluded from this assertion for the same reason the sibling
excludes its own B1->B2: more accumulated evidence is not a downstream information-loss transform.

## 5. WINNER COMPOSITION -- MEASURED AT EVERY RUNG FOR THE FIRST TIME

`n_probe=700`, one shared, seeded, paired index subset across all 5 rungs.

| rung | no-close-WordNet-relation fraction | winner-query co-occur (frac ever) | gold-query co-occur (frac ever) | ratio |
|---|---|---|---|---|
| R1 UNFILTERED_SINGLE_OCC | 0.8529 | 65.4% | 22.0% | 4.36x |
| R2 FILTERED_SINGLE_OCC | 0.8400 | 66.0% | 23.9% | 3.97x |
| R3 FILTERED_FULL_ACCUM | 0.7971 | **94.4%** | 60.3% | 3.82x |
| R4 PROJECTED_GRADED_FULL_ACCUM | 0.8000 | 90.6% | 50.4% | 4.11x |
| R5 PROJECTED_SIGN_FULL_ACCUM | 0.8071 | 74.0% | 43.0% | 3.88x |

Only ACCUMULATE (R2->R3) CI-separates on the WordNet axis: no-relation rate **-0.0430
[-0.0800,-0.0086]** (slightly IMPROVES). But co-occurrence tells the sharper story: the winner's
"ever co-occurs with the query" share nearly triples across the SAME step, **66.0% -> 94.4%** (and
gold's does too, 23.9% -> 60.3%, which is why the RATIO barely moves even as the absolute share
jumps). **ACCUMULATE is the step that pulls winners toward the query's own corpus neighbours,**
visible only because both composition axes were measured at the same rung -- the WordNet axis alone
would have hidden it, and would have suggested (wrongly) that accumulation helps relation-type
purity.

## 6. STOP-IF, PRECISELY, INCLUDING THE CODED-VS-WRITTEN DISAGREEMENT (coordinator item 1)

- **(i) FIRED, corrected direction:** ACCUMULATE dominates the ranked-|drop| table (64% of the
  total), but it is a **GAIN**, not a loss -- "one step does almost all the work" is right;
  "one step destroys almost everything" is not.
- **(ii) does not apply.**
- **(iii): the CODED verdict field and this note's WRITTEN conclusion DISAGREE, and the metrics.json
  now states why (`STOP_IF_iii_LOOSE_TRIGGER_DISAGREES_WITH_STRICT`).** A loose, mechanical trigger
  (any step with a CI-separated composition move) fires on ACCUMULATE. The brief's literal wording
  requires accuracy to be FLAT at that step; ACCUMULATE's own accuracy move is the LARGEST of the
  four (a real +0.0263 GAIN), not flat, so it does NOT satisfy (iii) as written. v1.2's `rep[
  "STOP_IF_FIRED"]` now reports only the STRICT reading (empty for (iii)); a separate field records
  the disagreement explicitly so a future grep of the verdict string is never misled by a trigger
  the author has already disowned. The real, correctly-stated finding is a DISSOCIATION, not a
  flat-accuracy flip: the one step with the largest (gain-direction) accuracy move is ALSO the only
  step whose composition CI-separates, and it separates in OPPOSITE directions on the two composition
  axes (WordNet: improves; co-occurrence share: nearly triples).
- **(iv) monotonicity leak: did not fire** on the v1.1+ per-leg check.
- **(v) K1 held.**

## 7. ONE PLAIN-LANGUAGE SENTENCE

**Summing an anchor's occurrences into one vector is worse than keeping even one arbitrary
occurrence (holding everything else fixed), while the retrievable signal sitting across those same
occurrences is roughly eight times larger than either -- the write rule's real defect is not
"too little accumulation" but "accumulation collapsed into a sum instead of kept separate", and the
step that most needs replacing is ACCUMULATE, without changing FILTER, CODE, or NORMALISE.**

## 8. WHAT THIS DOES NOT LICENSE

- FILTER is isolated only at single-occurrence depth (disclosed scope limit); a full-accumulation
  FILTER rung remains unmeasured.
- The composition and decisive-arm instruments run on n=700 / n=300 of 3994 scored items
  (cost-bounded, reported with their own n throughout).
- This cell LOCALISES; it does not rebuild the write rule. A separate agent (ORGAN F) is
  concurrently running an accumulation-depth sweep with token-matched and frequency-stratified
  controls, well past the ~72-sentence depth used here -- this cell does not duplicate that scope
  and does not edit its files.
- Nothing here claims a brain structure computes second-order co-occurrence or performs summation;
  every operator laddered is OUR INVENTION UNDER TEST. PINNED: only the complementary-learning-
  systems framing (cortex extracts cross-episode regularities; hippocampus keeps the episode) that
  motivated asking this question.
