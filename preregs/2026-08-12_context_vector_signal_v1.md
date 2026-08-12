# PRE-REGISTRATION -- context_vector_signal_v1

Filed 2026-08-12, BEFORE any run of `experiments/exp_context_vector_signal_v1.py`.
Author: hdi_exp_dev. Cell is a MEASUREMENT on existing organs; it modifies NOTHING in
`hdlab/reading_grounding_loop.py` or `hdlab/grounding_acquisition_loop.py`.

Prior-work check (`tools/substrate_query.sh "context vector per-encounter argmax flip rate
scramble control canonicalize sense selection"`): top-5 hits all at cosine 0.2793, BELOW the
0.30 dedup threshold. NONE at cosine > 0.30. This measurement is NOVEL, not a rediscovery.

---

## 1. Question

Does the PER-ENCOUNTER context vector produced by
`hdlab.reading_grounding_loop.context_vector_masked` carry ANY usable lemma-specific signal, as
read out by `canonicalize` / `canonicalize_fast` against the live `ConceptSpace`?

The director's hypothesis (which may be wrong): it carries NONE -- it is noise -- and that single
cause explains three separately-measured failures:

  (a) the ~90% per-encounter argmax flip rate implied by arm B's 7048 DISCONFIRM vs 788 CONFIRM
      MEASURED@d:/AI/hd-instrument/data/exp_pbv_hypothesis_v1_smoke/metrics.json:arms.B_PBV.trajectory
      (verified off disk by this author: n_disconfirm 7048, n_confirm 788, disconfirm share
      7048/7836 = 0.8994);
  (b) PBV's inability to verify -- primary bands HARD_FAIL, P1 0.285714, P3 0.071428
      MEASURED@d:/AI/hd-instrument/data/exp_pbv_hypothesis_v1_smoke/metrics.json:verdict_msg
      (re-verified: `"verdict": "HARD_FAIL"`);
  (c) context-conditioned sense selection at chance, 0.4809 vs floor 0.4634, C1 swap drop 0.0100
      vs required 0.05  CITED@notes/context_conditioned_sense_selection_v2_2026-08-12.md.

## 2. What is measured

Encounter = one (lemma, source-sentence) pair that the REAL reading loop actually flagged, taken
in trace order from `state.evidence`, with the source sentence recovered from
`state.sentence_pool`. Encounter identity is fixed ONCE (from the REAL run) and every condition
scores THE SAME encounters -- fully paired design.

Two REGIMES, both read out by the SAME unmodified `canonicalize_fast` against the SAME anchor
space, so the only difference between them is what vector is handed in:

* **PER-ENCOUNTER regime** -- argmax over `sign(one trace's context_vec)`. This is what
  `make_pbv_fns._encounter_best` does.
* **TRACE-SUM regime** -- argmax over `sign(np.sum([t.context_vec for t in item.traces]))`. This
  is `_make_grounding_gate` at `hdlab/reading_grounding_loop.py:567` and the regime over which
  the 0.0100 swap-drop was measured.

Measuring both is the point: the VET named per-encounter-noise and trace-sum-collapse as two
DIFFERENT candidate causes and they have opposite signatures (sec 6).

## 3. Conditions (arms)

| arm | context supplied per encounter | what it destroys | can fail? |
|---|---|---|---|
| REAL | the encounter's own masked context window | -- | n/a |
| SCRAMBLE_SENT (**PRIMARY NULL**) | a DIFFERENT encounter's real context window, assigned by a global permutation, then re-masked for the target lemma | the lemma<->context association ONLY | YES |
| SCRAMBLE_WORD | the same NUMBER of content words, re-dealt from the global pooled multiset of all context words | lemma association AND within-sentence co-occurrence | YES |
| LESION_RANDOM | a fresh uniform bipolar +/-1 vector, seeded deterministically per encounter | everything (pure-noise ceiling) | YES |
| LESION_ZERO | the all-zero vector | everything, degenerately | **NO -- see sec 7** |

SCRAMBLE_SENT is the PRIMARY null because it is the only one that preserves the exact geometry
(a real sentence's bag-of-content-words bundle, hence matched vector norm/sparsity/word-repetition
statistics) while removing precisely the thing under test. SCRAMBLE_WORD is secondary: it also
perturbs within-sentence co-occurrence, so a REAL-vs-SCRAMBLE_WORD gap is ambiguous between
"lemma-specific signal" and "real sentences are internally coherent".

Encounters whose context window is EMPTY under ANY arm (all-stopword after masking) are dropped
from ALL arms, so n is identical across arms. n_dropped is reported.

## 4. Metrics

Per-encounter regime, per arm:
* **FLIP RATE** -- within a lemma, over its encounters in stream order, the fraction of ADJACENT
  pairs whose argmax anchor differs. Restricted to lemmas with >= 2 encounters. Primary statistic.
* **MODAL SHARE** -- per lemma, the share of its encounters whose argmax equals that lemma's modal
  argmax; reported as the mean over lemmas. Robust companion to flip rate (order-free).
* **INFORMATIVE RATE** -- share of encounters with best_cos >= PBV_INFORMATIVE_MIN = 0.30.
* **ANCHOR CONCENTRATION** -- top-1 anchor's share of all argmaxes; normalized entropy over the
  argmax distribution.
* **ARGMAX-IN-WINDOW RATE** -- share of encounters whose argmax anchor is literally one of the
  content words present in that encounter's own context window (diagnostic D3, sec 6).

Across arms:
* **ARGMAX AGREEMENT MATRIX** -- for each ordered pair of arms, the share of encounters on which
  the two arms select the SAME anchor; reported RAW and CHANCE-CORRECTED. Chance agreement =
  `sum_a p_i(a) * p_j(a)` over the two arms' own argmax marginals; excess = (raw - chance) /
  (1 - chance) (a Cohen's-kappa-style correction). Raw agreement alone is uninterpretable when
  the argmax marginal is concentrated, so the corrected figure is the load-bearing one.

Trace-sum regime, per arm:
* per-lemma trace-sum argmax; REAL-vs-SCRAMBLE agreement (raw + chance-corrected);
* anchor concentration of the trace-sum argmax across lemmas;
* **PREFIX-SUM FLIP RATE** -- flip rate of the argmax of the RUNNING prefix sum as traces
  accumulate (does summing converge to a stable answer, and to WHOSE answer).

Confidence intervals: CLUSTER bootstrap resampling LEMMAS (not encounters), 2000 resamples,
percentile 95% CI. Encounters within a lemma are not independent; a per-encounter Wilson interval
would be anticonservative and is NOT used. The REAL-minus-SCRAMBLE difference is bootstrapped on
the SAME resampled lemma sets (paired), so its CI accounts for the pairing.

## 5. Anchor space

Primary: the FINAL `ConceptSpace` from the REAL reading-loop run over the stream, held FIXED
across all arms and both regimes. Fixing it removes anchor-space GROWTH as a confound -- a third
candidate cause the director's framing did not name.

Secondary (space-drift check, REAL + SCRAMBLE_SENT only): each encounter re-scored against the
ConceptSpace snapshot taken at the END of its own curriculum SEGMENT. If the fixed-space flip rate
and the snapshot-space flip rate differ materially, part of the observed instability is space
drift, not the context vector, and that must be said.

Eligibility (`hdlab.closed_class_lexicon.is_eligible_meaning`) is applied to anchors exactly as
`make_pbv_fns` applies it, via `canonicalize_fast(eligible_mask=...)`.

## 6. Pre-registered decision rules and EXPECTED DIRECTION

Let `f_R` = REAL per-encounter flip rate, `f_S` = SCRAMBLE_SENT flip rate, `D = f_S - f_R`
(positive means REAL is MORE stable), and `K_RS` = chance-corrected REAL-vs-SCRAMBLE_SENT argmax
agreement.

**PRIMARY VERDICT (per-encounter regime):**

* `CONTEXT_IS_NOISE` (director's hypothesis SUPPORTED) iff **D < 0.05 AND the 95% CI of D contains
  0** AND `K_RS <= 0.05` is NOT required -- noise predicts K_RS near 0 too, but K_RS is reported as
  corroboration, not as a gate.
* `CONTEXT_CARRIES_SIGNAL` (director's hypothesis **REFUTED** -- diagnosis must go elsewhere) iff
  **D >= 0.10 AND the 95% CI of D excludes 0**. Equivalently: REAL is clearly more stable than a
  geometry-matched scramble, so the per-encounter vector is not noise and the instability has
  another source (space drift, threshold calibration, or the read-out).
* `MIDDLE_BAND_WEAK_SIGNAL` otherwise (0.05 <= D < 0.10, or D >= 0.10 with a CI touching 0). Read
  as: a real but weak signal swamped by the read-out -- NOT a clean confirmation of either side.

**SECONDARY VERDICT (trace-sum regime):**

* `TRACE_SUM_DEAD` iff REAL-vs-SCRAMBLE_SENT trace-sum agreement is RAW >= 0.80 **and**
  chance-corrected `<= 0.10` -- i.e. the sum returns the same anchor no matter which contexts went
  in, and it does so because the answer is a generic attractor, not because the inputs agreed.
* `TRACE_SUM_ALIVE` iff chance-corrected agreement >= 0.20 AND materially exceeds the
  per-encounter chance-corrected figure.
* `TRACE_SUM_MIDDLE` otherwise.

**SIGNATURE TABLE (how the two regimes separate the two candidate causes):**

| per-encounter | trace-sum | diagnosis |
|---|---|---|
| noise | dead, and REAL==SCRAMBLE converge on the SAME few anchors | ONE root cause: the vector is noise; summing noise converges to a frequency backbone. Three walls collapse into one. |
| noise | alive | impossible-looking; would mean summing CREATES signal -> suspect a bug, investigate before reporting |
| signal | dead | the TRACE-SUM COLLAPSE is the culprit; per-encounter is fine; fix the read-out, not the encoder |
| signal | alive | neither is dead; the PBV failure is elsewhere (threshold, eligibility, space drift) |

**MY PRE-COMMITTED EXPECTATION, stated before looking:** I expect `MIDDLE_BAND_WEAK_SIGNAL` with
D in [0.05, 0.20] and `f_R` still high in absolute terms (0.70-0.90). Reasoning: a lemma's own
sentences necessarily repeat some collocates, so a bag-of-words bundle CANNOT be literally
information-free; but with d=256, ~10^3-10^4 anchors, and cosine SD ~ 1/sqrt(256) = 0.0625 the
argmax over thousands of near-tied anchors is dominated by sampling noise. So I expect the
director's strong form ("no usable signal") to be directionally right about USABILITY while being
technically refuted as "zero signal". I expect `TRACE_SUM_DEAD`. I will report whichever way it
lands, including if it refutes the director.

Diagnostic D3 (`ARGMAX-IN-WINDOW RATE`) exists to separate two readings that both predict PBV
failure but are DIFFERENT diagnoses: (i) the argmax is noise; (ii) the argmax is trivially just
some word that happened to appear in this window, so it flips with the window's word draw. High
argmax-in-window under REAL and LOW under SCRAMBLE_SENT = (ii), and that is NOT "noise" -- it
would be a read-out defect, and must be reported as such.

## 7. Controls that CANNOT fail -- declared

* **LESION_ZERO cannot fail.** A zero vector makes `canonicalize_fast` return `(lemma, 0.0)` at
  line 279 for every encounter, so its flip rate is 0.000 and its informative rate 0.000 BY
  CONSTRUCTION. It is reported ONLY as a pipeline sanity check (if it is not exactly 0.000 the
  harness is wrong) and carries NO verdict weight. It is NOT the director's requested "lesioned"
  arm for inferential purposes -- `LESION_RANDOM` is, and that one CAN fail.
* A per-lemma-CONSTANT lesion would likewise be pinned at flip rate 0.000; it is not run.
* **Is SCRAMBLE a valid null for this geometry?** For SCRAMBLE_SENT, yes: the encoder is a
  permutation-invariant bag-of-content-words bipolar bundle, so swapping WHICH real sentence
  supplies the window preserves the vector's distributional geometry exactly (same construction,
  same length distribution, same word-frequency profile) and removes only the lemma association.
  A WITHIN-lemma shuffle (permuting a lemma's own encounters among themselves) would NOT be a
  valid null -- flip rate over a fixed multiset is near-invariant to ordering, so it could not
  fail; it is explicitly NOT used.
* Chance-corrected agreement is mandatory precisely because raw agreement CANNOT fail when the
  argmax marginal is concentrated on a few generic anchors.

## 8. Integrity / harness gates (must all pass or the run is void)

* `trace_alignment_ok` -- for every lemma, `len(state.evidence[lemma]) == len(item.traces)`, and
  the recomputed `context_vector_masked(sentence, lemma)` is BIT-IDENTICAL to the stored
  `trace.context_vec` for every encounter. This is the real_code_path proof: the encounter table
  is the loop's own, not a re-derivation that might drift.
* `arms_must_differ` -- sha256 over each arm's stacked context matrix; all five distinct.
* `paired_n_equal` -- every arm scores the identical encounter set.
* `no_leak_ok` -- no arm's context window contains a token whose lemma equals the target.
* `lesion_zero_pinned` -- LESION_ZERO flip rate == 0.000 exactly (harness sanity).
* `deterministic_seeding` -- all RNG from fixed integer seeds / hashlib; no builtin `hash()`, no
  `list(set())` ordering (PROT-023 / gate F.5).
* `cardinality_ok` -- EXPECTED_N_ARMS = 5, EXPECTED_N_REGIMES = 2.

## 9. Compute architecture

Class **(b) sequential-CPU with justification**, with the scoring vectorized.
* The reading-loop pass is genuinely sequential (encounter N's gap-gate depends on what was
  grounded before N) and is the existing organ, run unmodified.
* All argmax scoring is ONE batched matmul per arm: `(n_enc x 256) @ (256 x n_anchors)`. At
  n_enc ~ 3.1e4 and n_anchors ~ 1e4 that is ~8e10 FLOPs per arm, seconds under BLAS. GPU buys
  nothing at this size and the cell must run inline-local.
* Storage strategy: **no_storage / no_composition** -- this cell stores nothing and composes no
  primitives; it reads out an existing accumulator.
* Wall-time budget: single foreground call, `timeout: 600000`. Smoke at 200 sentences/segment
  first; FULL at 1500/segment (identical to the PBV smoke stream, so the numbers are directly
  comparable to the 7048/788 figure).

## 10. Gates A-F (per exp_dev sec 15)

* A `sweep_alignment_verdict: ALIGNED` -- no swept parameter; the arm axis is categorical and each
  arm changes exactly the intended input.
* B `bracket_includes_discriminating_band` -- N/A, no sweep axis. The discriminating quantity is a
  DIFFERENCE between arms; sec 6 pre-commits the bands. `discriminating_fraction: n/a_no_sweep`.
* C `composition_edges` -- one edge: `context_vector_masked -> canonicalize_fast`. Natural output
  shape = bipolar (256,) ; natural input shape = bipolar (256,) raw-sum. `SHAPE_MATCH`.
* D `positive_control_arms` -- the cell REPRODUCES the loop's own encounter table bit-identically
  (gate `trace_alignment_ok`, sec 8) at the SAME regime as the PBV smoke (same stream, same 1500/
  segment cap), and cross-checks its per-encounter informative rate against arm B's MEASURED
  `informative_encounter_rate` 0.393912
  MEASURED@d:/AI/hd-instrument/data/exp_pbv_hypothesis_v1_smoke/metrics.json:arms.B_PBV.trajectory.informative_encounter_rate,
  tolerance 0.10 absolute. NOTE the expected direction of deviation: arm B scored each encounter
  against the LIVE space at that moment, this cell scores against the FINAL space, so exact
  equality is NOT expected and a deviation is informative rather than disqualifying -- it is
  reported, and only a deviation > 0.10 flags `POSITIVE_CONTROL_DRIFT` for interpretation.
* E `functional_requirements` -- (1) "recover the loop's real encounters": `state.evidence` +
  `sentence_pool`, verified bit-identical. (2) "score an argmax the way the mechanism does":
  `canonicalize_fast` verbatim. (3) "remove the lemma-context association without changing the
  geometry": SCRAMBLE_SENT. (4) "bound the noise ceiling": LESION_RANDOM. (5) "separate the two
  regimes": trace-sum vs per-encounter over identical inputs. No new mechanism is designed.
* F.1 `real_code_path_exercised: [ReadingLoopState, process_sentence, ConceptSpace,
  canonicalize_fast, context_vector_masked, HDFactStore]` -- the self-test constructs the REAL
  objects at ~12 sentences.
* F.2 `substrate_signature_checked: [canonicalize_fast, context_vector_masked, process_sentence,
  HDFactStore]` -- base/portable kwargs only.
* F.4 `guard_baseline_validated` -- the only break-guard is `lesion_zero_pinned`, which is a
  harness identity check, not a control-beats-baseline guard. Declared N/A with reason.
* F.5 `deterministic_seeding: true`.

## 11. Other mandated fields

* `cell_chunked: false` (no seed axis; a single deterministic pass, checkpointed per chunk by the
  loop's own `checkpoint`).
* `start_marker_written: true`; `crash_diagnostic_present: true`; `heartbeat_present: true`.
* `defensive_error_checking: passed_all_4_patterns`.
* `final_metrics_atomicity: tmp_replace`.
* `arms_differ_verified: true` (set at smoke).
* `calibration_check: "default_ok_for_this_regime"` -- thresholds PBV_INFORMATIVE_MIN 0.30 and
  SENSE_MATCH_THRESH 0.45 are taken VERBATIM from the organ under measurement; this cell tunes
  nothing. All primary statistics (flip rate, agreement) are threshold-FREE argmax quantities, so
  the verdict cannot be moved by a threshold choice.
* `crlb_n/a: "the primary statistic is a DIFFERENCE in flip rate between paired arms; there is no
  estimator whose variance a Cramer-Rao bound constrains. The relevant feasibility floor is the
  argmax-noise floor, which is MEASURED directly by LESION_RANDOM rather than assumed."`
* `baseline_in_band` -- the relevant band check is that SCRAMBLE_SENT flip rate is not itself
  pinned at 1.000 (which would leave no room for REAL to be more stable). If SCRAMBLE_SENT flip
  rate > 0.98, the comparison is ceiling-limited and the cell reports
  `MIDDLE_BAND_CEILING_LIMITED` instead of a primary verdict.
* `progress_logging: "print_flush_true"`.
* `discriminator-fires` (META_RULE_K): the discriminator here is the REAL-vs-SCRAMBLE contrast.
  Smoke must show LESION_RANDOM flip rate materially ABOVE LESION_ZERO's pinned 0.000 and the
  agreement matrix non-degenerate; if every arm returns the identical argmax everywhere, the
  harness is broken and the cell must halt rather than report a null.

## 13. AMENDMENTS (filed 2026-08-12 AFTER the SMOKE, BEFORE the FULL -- fully disclosed)

Two pre-registered bands were found MIS-SPECIFIED by the smoke. Both amendments are recorded here
and both UNAMENDED outcomes are still computed and written to metrics.json
(`prereg_literal_primary`, `prereg_literal_secondary`), so nothing is hidden by the change.
Disclosure discipline note: amendment A1 moves the verdict TOWARD a result that REFUTES the
director's hypothesis, i.e. away from the answer the spawn prompt leaned toward -- it is recorded
here precisely so a reader can check it was not motivated reasoning in either direction.

**A1 -- ceiling guard fired on the NULL arm alone.** Sec 11 said "if SCRAMBLE_SENT flip rate >
0.98, the comparison is ceiling-limited". Its stated rationale was that a pinned scramble leaves
"no room for REAL to be more stable". The smoke DIRECTLY FALSIFIED that premise: scramble 0.9953,
REAL 0.7666, D = +0.2287 with a 95% CI of [+0.2042, +0.2543] that excludes 0 and 100% of bootstrap
replicates above 0. Worse, as written the guard can ONLY suppress a positive and can NEVER rescue
a null -- the opposite of what a validity guard is for. And a scramble flip rate near 1.0 is the
CORRECT value for a working null (independent argmax draws over ~10^3 anchors give a coincidence
rate of ~1/n_anchors), not an artifact. AMENDED: `ceiling_limited` requires BOTH arms above 0.98.

**A2 -- TRACE_SUM_ALIVE was written backwards.** Sec 6 defined DEAD as HIGH REAL-vs-SCRAMBLE
trace-sum agreement (correct: the sum returns the same anchor regardless of input) but ALSO
defined ALIVE as HIGH chance-corrected agreement (>= 0.20). Both cannot be true; under the
literal text no observation could ever be classified ALIVE. AMENDED to the direction the sec 6
SIGNATURE TABLE actually requires:
* `TRACE_SUM_DEAD_GENERIC_ATTRACTOR` -- raw agreement >= 0.80 AND kappa <= 0.10 (unchanged).
* `TRACE_SUM_DEAD_NO_GAIN_OVER_SCRAMBLE` -- the real sum buys nothing: REAL minus SCRAMBLE_SENT
  summed-match rate at SENSE_MATCH_THRESH < 0.05 AND the prefix-sum flip-rate gain < 0.05.
* `TRACE_SUM_ALIVE` -- raw agreement < 0.30 (the summed answer still DEPENDS on which contexts
  went in) AND at least one of the two separation criteria above is met.

No other band, arm, metric, seed, or corpus scope changed. The FULL run is judged by the amended
spec as stated here, which was frozen before the FULL was launched.

## 12. What this cell does NOT claim

It does not measure sense selection, grounding correctness, or PBV abandonment. It does not
re-open the ruling in the PBV landed-VET sec 6. It measures ONE thing: whether the per-encounter
context vector, and its trace-sum, carry lemma-specific information as read out by the existing
argmax. A `CONTEXT_IS_NOISE` result is BAD news about the representation and GOOD news
methodologically (three walls, one root cause); it is to be reported plainly and NOT softened to
protect the PBV build, which was correctly constructed and is not what is on trial here.
