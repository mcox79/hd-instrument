# Does a prediction-error-gated write rule produce substitutability? MEASURED, not built.

`experiments/exp_predictive_coding_write_gate_dissociation_v1.py`, FULL run, commit-pending.
Machinery reused, never reimplemented: `hdlab/predictive_coding.py` (`residual_magnitude`,
`threshold_gate`, `proportional_gate`, called verbatim), `exp_surprise_weighted_update_v1`'s cached
observation stream (`scratch/night/obs_stream_v1.npz`, 153,352 occurrences / 5,491 anchors / d=256,
never re-tokenised), `exp_dissociation_score_instrument_v1`'s (DSI) licensed 242-pair-per-cell
matched population and `auc_of`/`auc_bootstrap` scorer.

## Regression gate: 8/8 PASS, plus a second STREAM gate

DSI's 8 cached checks reproduced to 4 decimals: F_ORTHOGRAPHIC 0.5000, F_FREQUENCY 0.4901,
F_SCRAMBLE 0.4664, F_CONSTANT_PROTOTYPE 0.5431, KNOWN_ANSWER 0.9599, RANDOM_VECTOR_STORE 0.4862,
INCUMBENT_LIVE_STORE 0.0710, RAW_COUNT_FULL_ACCUM 0.0510 -- all delta 0.0000. A second,
cell-specific STREAM regression gate (not present in prior sibling cells) rebuilds A0 by plain
summation of the cached observation stream over all 5,491 anchors and checks it against the live
store: `mean_cos_rebuilt_A0_vs_LANDED_anchor_matrix = 1.000000` (exact), and the rebuilt A0's own
AUC on the matched-pair population = 0.0710, delta -0.000001 vs DSI's cached number. Both gates
PASS. INSTRUMENT_LICENSED.

## Surprise distribution on THIS population -- reported first, and it is NOT degenerate

Measured over every occurrence (n=33,907) of every one of the 617 matched-pair member words,
residual_mag against each word's own self-referential running (accept-all) accumulator, using
`predictive_coding.residual_magnitude` verbatim:

| stat | this population (617 words) | prior population (`exp_surprise_weighted_update_v1`, KA-pool words, n=368) |
|---|---|---|
| mean | 0.4497 | 0.853 |
| p10 | 0.3556 | 0.6525 |
| p50 (median) | 0.4497 | 0.875 |
| p90 | 0.5151 | 1.0128 |

Pre-registered degeneracy test (median >= 0.80 AND p90-p10 <= 0.20): **NOT degenerate**
(median 0.4497, spread 0.1595). This is a materially different, healthier distribution than the
prior cell found on a different population -- the earlier "no informative tail" finding does not
transfer here. The mechanism gets a fair test on this population: the AUC results below are not
an artifact of a collapsed signal.

## Arm-by-arm AUC (FULL, N_BOOT=10000, CI half-width shown)

| arm | AUC | CI95 | half-width | band |
|---|---|---|---|---|
| A0_INCUMBENT | 0.0710 | [0.0507, 0.0930] | 0.0212 | BELOW 0.5 |
| P2_PREDICTION_WEIGHTED | 0.0728 | [0.0523, 0.0954] | 0.0216 | BELOW 0.5 |
| P1 @ T0.4039 (p25) | 0.0961 | [0.0723, 0.1230] | 0.0254 | BELOW 0.5 |
| N1 @ T0.4039 | 0.0971 | [0.0717, 0.1243] | 0.0263 | BELOW 0.5 |
| P1 @ T0.4497 (p50) | 0.1526 | [0.1201, 0.1869] | 0.0334 | BELOW 0.5 |
| N1 @ T0.4497 | 0.1368 | [0.1057, 0.1692] | 0.0318 | BELOW 0.5 |
| P1 @ T0.4862 (p75) | 0.2268 | [0.1873, 0.2687] | 0.0407 | BELOW 0.5 |
| N1 @ T0.4862 | 0.2165 | [0.1775, 0.2572] | 0.0399 | BELOW 0.5 |
| P1 @ T0.5151 (p90, BEST) | 0.3079 | [0.2619, 0.3547] | 0.0464 | BELOW 0.5 |
| N1 @ T0.5151 | 0.3007 | [0.2546, 0.3485] | 0.0470 | BELOW 0.5 |
| N2_ANTI_GATE (all 4 T) | 0.5000 | [0.5000, 0.5000] | 0.0000 | degenerate, see below |

No arm at any threshold is CI-separated above 0.5. Best point AUC (P1 @ T0.5151, the p90 threshold,
the strictest gate) is 0.3079, still well below chance.

## The paired margin that decides it: P1 vs its own rate-matched N1

At the best threshold (T0.5151): P1 AUC=0.3079 vs A0 AUC=0.0710 -> paired margin +0.2369, CI
[0.1921, 0.2831], **A_ABOVE_B (CI-separated)**. P1 vs N1 (same threshold, same per-lemma accept
COUNT, gate fires at random): margin +0.0071, CI **[-0.0565, 0.0703], NOT_SEPARATED**. This pattern
(P1 beats A0, P1 does not beat its own rate-matched N1) holds at all four thresholds -- N1's point
AUC tracks P1's within ~0.01-0.02 at every one of them (0.0971 vs 0.0961; 0.1368 vs 0.1526; 0.2165
vs 0.2268; 0.3007 vs 0.3079).

**STOP-IF (ii) fired: the gain is the gating RATE, not prediction error.** Accepting fewer
occurrences per word moves the AUC away from the co-occurrence-dominated incumbent regardless of
WHICH occurrences are kept -- a random draw of the same size does the same thing. This matches
plan sec 6.15's organ-level finding exactly ("every intervention that ADDS accumulated corpus
content moves us AWAY from substitutability"): reading less is what helps, not reading
selectively.

## N2_ANTI_GATE collapsed to a degenerate empty store -- structural, not a measurement of direction

At all four thresholds, N2 (accept iff residual_mag < T) has `acceptance_rate = 0.0000`,
`n_tokens_accepted = 0`. Cause, found by inspection: every lemma's FIRST occurrence has an
undefined self-referential predictor (accumulator is all-zero), and
`predictive_coding.residual_magnitude`'s own convention reads that as maximal residual (1.0). Since
every threshold swept is < 1.0 (they are the population's own p25-p90, all in [0.40, 0.52]), the
first occurrence is NEVER < T, so N2 rejects it -- and because nothing was ever accepted, the
accumulator stays at zero forever, so EVERY later occurrence also reads residual_mag=1.0 (same
undefined-predictor convention) and is also rejected. N2 is a permanent self-locking empty store,
not a genuine "accept the least surprising" arm. Its AUC of exactly 0.5000 with a zero-width CI is
a deterministic tied-ranks artifact of an all-zero constant store, not a "ties chance" finding, and
must not be read as evidence about direction. P1 does not have this problem (its first occurrence,
residual 1.0, is always >= any T < 1.0, so P1 always gets a warm start). **The fix, if this
supplementary check mattered enough to rebuild it, is a warm start: unconditionally accept each
lemma's first occurrence, then begin gating from occurrence 2.** Not built here -- N2 is
supplementary, not one of the two arms (P1, its rate-matched N1) that carry the STOP-IF decision,
and the brief's build-vs-name-the-fix rule applies.

## Composition (mean score on SET P vs SET S, plus their difference; "winner/gold co-occurrence
## share" has no referent on this AUC instrument -- see note below)

| arm | mean(SET P, substitutable) | mean(SET S, co-occurring) | P-S | accept rate | tokens |
|---|---|---|---|---|---|
| A0_INCUMBENT | 0.1508 | 0.3708 | -0.2200 | 1.0000 | 33,907 |
| P2_PREDICTION_WEIGHTED | 0.1530 | 0.3595 | -0.2065 | 0.9999 | 33,905 |
| P1 @ T0.5151 | 0.0534 | 0.1113 | -0.0580 | 0.1581 | 5,362 |
| N1 @ T0.5151 | 0.0561 | 0.1318 | -0.0757 | 0.1581 | 5,362 |
| N2 @ T0.5151 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |

Every arm scores SET S (the co-occurring, non-substitutable set) higher than SET P (the
substitutable, zero-co-occurrence set) -- P-S is negative everywhere, i.e. every store, gated or
not, is still fundamentally reading corpus co-occurrence rather than substitutability. Gating
shrinks BOTH means (less accumulated content, lower cosine overall) and shrinks the co-occurrence
gap (P-S moves from -0.22 at A0 toward -0.058-0.076 at the strictest P1/N1), but N1 shrinks the gap
by about as much as P1 does, at the identical token count -- consistent with the RATE, not
SELECTION, reading above.

**On "winner/gold co-occurrence share and their ratio":** this vocabulary is native to a hit@1
pool-based readout instrument (a per-item argmax "winner" against a candidate pool). The
dissociation-AUC instrument has no such object -- it is a rank-sum AUC separating two
disjoint-by-construction sets (SET P: WordNet-synonym, zero corpus co-occurrence; SET S: top-decile
co-occurring, no close WordNet relation), never a ranked pool with one selected winner per item.
Forcing that framing onto this instrument would misrepresent what was measured. The adapted,
faithful analogue reported above -- mean score on each set and their difference -- carries the same
information the winner-share check is for (is the arm's ranking still driven by co-occurrence?) and
answers it directly: yes, at every gating level tested.

## Plain-language answer

**No.** Gating writes by prediction error moves the AUC toward chance as you accept fewer
occurrences per word, but a random gate matched to the exact same acceptance rate moves it by
almost exactly the same amount. The improvement is coming from writing less, not from writing the
right things. Prediction error, as implemented here (a single running self-accumulator predicting
its own next occurrence, no separate predictor, no warm start), does not carry a usable
substitutability signal on this instrument.

## What this does and does not settle

- Does NOT settle the general supervision hypothesis from 6.18 -- a parallel cell is testing
  whether a tuned unsupervised count method clears 0.5, which would relocate the missing thing to
  hyperparameters rather than supervision entirely. This cell's result is narrower and survives
  either way: PREDICTION ERROR AS A WRITE GATE, specifically, does not produce substitutability.
- The surprise signal itself is NOT the blocker here (it is healthy, non-degenerate, and the
  pre-registered bootstrapping concern from `exp_surprise_weighted_update_v1` does not reproduce on
  this population) -- so this is a clean negative about the MECHANISM, not an underpowered test.
- N2_ANTI_GATE's collapse is a real, reportable structural property of self-referential anti-gating
  without a warm start; it does not bear on the P1-vs-N1 decision above.

## Files

- Cell: `experiments/exp_predictive_coding_write_gate_dissociation_v1.py`
- FULL metrics: `data/exp_predictive_coding_write_gate_dissociation_v1/metrics.json`,
  `data/exp_predictive_coding_write_gate_dissociation_v1/units.jsonl`
- SMOKE metrics: `data/exp_predictive_coding_write_gate_dissociation_v1_reduced/metrics.json`,
  `.../units.jsonl`
- Verdict string: `PREDICTIVE_CODING_WRITE_GATE__STOP_IF_ii_P1_BEATS_A0_BUT_NOT_N1__GAIN_IS_GATING_RATE_NOT_PREDICTION_ERROR`
