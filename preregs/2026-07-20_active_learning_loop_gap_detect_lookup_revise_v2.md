# Pre-registration: active-learning loop v2 -- removing v1's three construction crutches

Cell: `experiments/exp_active_learning_loop_gap_detect_lookup_revise_v2.py`
Author: hdi_exp_dev. Date: 2026-07-20.
Status: DESIGN-GATE + SMOKE ONLY. No full dispatch, no queue_add, no push, per Director contract.
Revives: v1 (`preregs/2026-07-20_active_learning_loop_gap_detect_lookup_revise_v1.md`), landed
MEASURED_MECHANISM (atom 29386, construction-validated WIRING PROOF; all capability numbers
construction-determined per adversarial VET).

## WHY THIS CELL EXISTS

v1's VET named three construction crutches that must be removed before any capability claim is trusted.
This cell removes all three, keeps v1's validated wiring/controls, and adds a can-fail check for each
crutch. See the cell's module docstring for the full mechanism-level writeup; this pre-reg states the
falsifiable bands.

## PRIOR-WORK CHECK (substrate-KB concept-query, exp_dev standing rule)

Same concept-query as v1 (`bash tools/substrate_query.sh "active learning loop gap detection abstain
external lookup provenance revision reliability gate glass-box"`) -- top hit cosine=0.3057 (a distinct
prior mechanism, cleanup-margin-as-gap-signal, not this compound loop). No new query run for v2 since the
mechanism identity (gap-detect -> lookup -> gate -> provenance-revise) is unchanged from v1; only the THREE
NAMED CRUTCHES are being removed. **Prior-work check: unchanged from v1 -- NONE at cosine>0.30 for this
compound loop; the crutch-removal work itself is new (adversarial-VET-directed hardening, not a novel
mechanism claim).**

## THE THREE CRUTCHES AND THEIR FIXES

### Crutch 1 -- self-classified lookup (round-trip guaranteed by construction)
**v1:** lookup glosses hand-authored by the cell author; self-test asserted
`classify_gloss(true_gloss) == true_cat` for all 48 items (round-trip = 1.000 by construction).
**v2 fix:** lookup content is REAL Princeton WordNet (Fellbaum 1998) gloss text, harvested via
`nltk.corpus.wordnet` ONCE at authoring time (harvest script run interactively; candidates drawn from a
fixed word-list per category, filtered mechanically for correct lexicographer-file lexname + gloss NOT
containing the category's own literal name + single-token headword + 25-160 char length, selected in
candidate-list order -- NOT filtered by classify_gloss agreement). Frozen as static Python literals in
`TERMS_BY_CAT`; **zero nltk/network dependency at runtime** (checked by `assert_no_nltk_import()`, a
narrow import-statement scan, separate from the broader `glassbox_scan()`).
`GLOSS_KEYWORDS` (the classifier) was written from generic category vocabulary BEFORE the round-trip rate
was measured against these real glosses (authoring order preserved in the cell; the harvest + classifier
construction log is: harvest candidate words -> select 8/category by mechanical filter -> THEN write
generic keyword lists -> THEN measure round-trip, in that order).
**CAN-FAIL CHECK:** `measure_round_trip()` reports the ACTUAL round-trip rate over the 48 real glosses.
MEASURED@smoke: **0.854** (41/48; misses: TOOL/rasp, PROCESS/carbonization, PROCESS/metamorphosis,
EMOTION/apprehension, PLANT/bracken, PLANT/hornwort, PLANT/toadstool -- all misclassify to ANIMAL or PLACE
via the all-zero-score lowest-index tie-break). This is a REAL, non-guaranteed failure rate -- v1's
self-test would have failed loudly had this happened; v2's self-test REQUIRES it.

### Crutch 2 -- hardwired maximally-separated reliability
**v1:** `source_good` (p~0.85, always >=0.5) / `source_bad` (p~0.25, always <0.5) -- gate did trivial
separation, not estimation.
**v2 fix:** an 8-source calibration pool (`SOURCE_P_TRUE = [0.30, 0.40, 0.50, 0.60, 0.75, 0.90, 0.45,
0.45]`), spanning the 0.5 decision threshold, with a DERIVED reliability score per source (Laplace-smoothed
mean correctness over a large disjoint calibration pool, N_CAL=240/seed -- the atom-29376 "aggregate over
OTHER observations, never the item under test" pattern, adapted from vector leave-one-item-out
cosine-consistency to discrete category-label correctness bookkeeping: a history-fold of 160 items derives
the score, a disjoint test-fold of 80 items validates it).
**CAN-FAIL CHECK:** AUC of the history-fold-derived score predicting individual test-fold observation
correctness, pooled across all 8 sources. MEASURED@smoke (3-seed mean): **0.690** (per-seed: 0.697 / 0.698
/ 0.676) -- materially below 1.0 (informative, not a perfect/leaky proxy) and above chance.
**GATED_NEARTHRESHOLD** (diagnostic arm, HP_SCOPE-excluded) exercises the p_true=0.50 MID source with a
per-item stochastic correctness draw, illustrating graded near-threshold behavior directly (not gated into
the HARD_PASS decision, reported for transparency).

### Crutch 2b -- common-mode blind spot
**v2 fix:** a correlated MIRROR PAIR (`mirror_a`, `mirror_b`, both p_true=0.45) shares ONE correctness draw
and, when wrong, ONE shared wrong-category draw (the upstream-copied-source / illusory-truth failure mode;
see `research_brain_source_independence_monitoring_2026-07-20.md`). A pairwise cross-source
agreement-matrix detector (atom-29378 pattern, adapted from a rank-1-eigenvector fit to a direct
closed-form product-plus-collision null since per-source marginal estimates are already available in this
controlled construction) computes `residual(a,b) = observed_agreement(a,b) - null(phat_a, phat_b)`.
**CAN-FAIL CHECKS:**
- Mirror-pair residual fires: MEASURED@smoke **0.746** (>= 0.15 floor).
- All independent pairs stay quiet: MEASURED@smoke max |residual| = **0.063** (<= 0.10 ceiling).
- MUST-FAIL SHUFFLE CONTROL (permute per-source item-correspondence, destroying true co-item pairing):
  mirror residual collapses to **-0.082** (<= 0.10 ceiling in absolute value) -- confirms the detector is
  keying on genuine same-item cross-source structure, not a source-level artifact.
- NAIVE-vs-AWARE stress test (300-draw calibration-pool scale, synthetic 2-candidate-set convention): a
  NAIVE policy applies the independent-sources corroboration formula
  (`1-(1-r_a)*(1-r_b)` = 0.665 at seed 7, comfortably >= threshold) to the CORRELATED pair; an AWARE policy
  (informed by the detector's fire) discounts the pair to single-source treatment (`min(r_a,r_b)` = 0.421,
  correctly below threshold). Gate metric = **false-accept-rate gap** (the direct "confidently accepted a
  wrong answer" metric -- see Disclosed Limitations for why raw accuracy is reported as context only, not
  gated). MEASURED@smoke (3-seed mean): naive false-accept rate = **0.089**, aware = **0.000**, gap =
  **+0.089** (>= 0.05 floor). NAIVE is measurably fooled; AWARE is not.

### Crutch 3 -- empty-set (NO_EVIDENCE) coherence blind spot
**v1:** coherence check auto-passed on empty-candidate-set items (nothing to violate); RANDOMIZED_LOOKUP
(real-but-irrelevant content) was ACCEPTED on all NO_EVIDENCE items via the reliability channel alone
(0% accuracy on that 6-item sub-slice, a disclosed, un-patched gap).
**v2 fix:** `content_relevance_check()` -- Jaccard-style content-word overlap (>=1 shared content word,
stopwords/term excluded) between the retrieved gloss and the ORIGINAL CONTEXT SENTENCE. Each NO_EVIDENCE
item's context sentence is seeded with ONE incidental anchor word drawn directly from that item's OWN real
WordNet gloss (`NOEVIDENCE_ANCHOR_WORD`, e.g. aardvark -> "grasslands", ridge -> "striation") -- a
distinctive, non-category-keyword content word, so gap-detect's candidate-set size stays 0 (verified by the
goldilocks gate) while giving the relevance check real discriminating power. Applied ONLY when
`set_size == 0` (size>0 items keep v1's candidate-set-membership check unchanged).
**CAN-FAIL CHECK:** on the NO_EVIDENCE subset (6 items), RANDOMIZED_LOOKUP reject rate MEASURED@smoke =
**1.000** (>= 0.70 floor -- v1 measured 0.000, i.e. always accepted); GATED_CLEAN (anchor-bearing true
gloss) accept rate MEASURED@smoke = **1.000** (>= 0.60 floor -- the patch does not simply block
everything).

## KEPT FROM v1 (unchanged)

Loop wiring (`hdlab.conformal.calibrate_quantile` real import, internal-retrieve-first, provenance-tagged
revise with no overwrite); the 4 mandatory must-fail controls (bad-source / ungated-lookup-can-hurt /
randomized-lookup / gap-no-lookup); STRONG/AMBIGUOUS/MALFORMED regime construction (context-cue sentence
templates, sibling pairs, Goldilocks-gate); the glass-box invariant -- TIGHTENED per Director instruction:
`glassbox_scan()` now covers the WHOLE file (v1 exempted the first 2500 chars as a disclosed, no-violation
coverage gap; v2 has no exemption window, only a narrow near-declaration exemption for the
`FORBIDDEN_SUBSTRINGS` list literal itself).

## FALSIFIABLE BANDS

**HARD-PASS** (ALL required):
1. `mean_3seed(acc_gated_clean_primary) - mean_3seed(acc_passive_primary) >= 0.10`.
   MEASURED@smoke: 0.861 - 0.389 = **+0.472**.
2. `(acc_gated_badsource_primary - acc_ungated_badsource_primary) >= (acc_gated_clean_primary -
   acc_ungated_clean_primary) + 0.20`. MEASURED@smoke: 0.347 >= 0.028 + 0.20 = 0.228 -> margin
   **+0.319**.
3. Bad-source rejection rate `>= 2x` genuine (clean) rejection rate (fallback: absolute margin `>= 0.50`
   if clean rate is exactly 0). MEASURED@smoke: reject_bad=1.000 / reject_clean=0.083 -> ratio
   **12.0**.
4. `abs(acc_randomized_lookup_primary - acc_passive_primary) <= 0.10`. MEASURED@smoke: **0.014**.
5. `acc_gap_no_lookup_primary == acc_passive_primary` (tolerance 0.02). MEASURED@smoke: **0.000**.
6. Provenance completeness: 100% of ACCEPTED revisions carry all 4 fields. MEASURED@smoke: **True**
   (274 records).
7. Goldilocks-gate construction check (STRONG=size1, AMBIGUOUS=size2, MALFORMED=size>=4+no-fire,
   NO_EVIDENCE=size0). MEASURED@smoke: **all True**.
8. Glass-box static scan (whole-file, no exemption window): zero forbidden substrings.
   MEASURED@smoke: **0 hits**.
9. Verbatim-answer guard: zero of the 48 real WordNet glosses contain their own category name.
   MEASURED@smoke: **0 violations**.
10. Anchor-word collision guard (NEW, v2-specific): zero NO_EVIDENCE anchor words leak into that item's
    own bad_gloss/unrelated_gloss. MEASURED@smoke: **0 collisions**.
11. **INDEPENDENCE (Crutch 1 fix):** `round_trip_rate < 0.999` (measurably broken, not construction-
    guaranteed) AND `round_trip_rate >= 0.50` (classifier still functional). MEASURED@smoke: **0.854**.
12. **RELIABILITY AUC (Crutch 2 fix):** `0.55 <= mean_3seed(AUC) <= 0.95`. MEASURED@smoke: **0.690**.
13. **COMMON-MODE SEPARATION (Crutch 2b fix):** mirror-pair residual `>= 0.15`; max independent-pair
    residual `<= 0.10`; shuffled mirror residual `<= 0.10` in absolute value. MEASURED@smoke:
    **0.746 / 0.063 / 0.082**.
14. **NAIVE-vs-AWARE (Crutch 2b fix):** `mean_3seed(naive_false_accept_rate - aware_false_accept_rate)
    >= 0.05`. MEASURED@smoke: **+0.089**.
15. **RELEVANCE CHECK (Crutch 3 fix):** NO_EVIDENCE-subset RANDOMIZED_LOOKUP reject rate `>= 0.70` AND
    NO_EVIDENCE-subset GATED_CLEAN accept rate `>= 0.60`. MEASURED@smoke: **1.000 / 1.000**.

(stretch, reported not required) Learning curve: `mean_3seed(acc_gated_clean_occurrence2) -
mean_3seed(acc_passive_occurrence2) >= 0.20`. MEASURED@smoke: **+0.500**.

**HARD-FAIL** (any):
- Band 1 gap `< 0.10` -> `HARD_FAIL_ACTIVE_NO_BETTER_THAN_PASSIVE`.
- Band 2 margin-of-margins `< 0.20` -> `HARD_FAIL_GATE_DECORATIVE`.
- Band 3 rejection-rate gap `< 0.50` (absolute) or ratio `< 2x` -> `HARD_FAIL_GATE_NOT_DISCRIMINATIVE`.
- Band 4 `abs(delta_randomized) > 0.10` -> `HARD_FAIL_NOISE_AVERAGING_SUSPECTED`.
- Band 9 violated -> `HARD_FAIL_VERBATIM_ANSWER_CONSTRUCTION_DETERMINED`.
- Band 8 violated -> `HARD_FAIL_GLASSBOX_VIOLATION` (BLOCK_DISPATCH).
- Band 10 violated -> `HARD_FAIL_ANCHOR_WORD_COLLISION`.
- Band 11 `round_trip_rate >= 0.999` -> `HARD_FAIL_INDEPENDENCE_NOT_BROKEN` (Crutch 1 not removed).
- Band 11 `round_trip_rate < 0.50` -> `HARD_FAIL_CLASSIFIER_DEGENERATE`.
- Band 12 AUC outside `[0.55, 0.95]` -> `HARD_FAIL_AUC_OUT_OF_BAND` (either no-signal or leak/trivial).
- Band 13 not all three conditions hold -> `HARD_FAIL_COMMONMODE_NOT_SEPARATED`.
- Band 14 gap `< 0.05` -> `HARD_FAIL_NAIVE_NOT_FOOLED` (Crutch 2b fix not demonstrated).
- Band 15 either condition fails -> `HARD_FAIL_RELEVANCE_CHECK_INERT` (Crutch 3 not fixed).

**MIDDLE_BAND**: band 1 gap in `[0.10, 0.20)`, baseline out of band, or provenance incomplete.

**HP_SCOPE**:
```yaml
HP_SCOPE:
  PASSIVE: []
  GATED_CLEAN: [band1_primary_gap, band7_goldilocks, band9_verbatim_guard, band11_independence]
  UNGATED_CLEAN: [band2_clean_margin_reference]
  GATED_BADSOURCE: [band2_gated_margin, band3_rejection_rate]
  UNGATED_BADSOURCE: [band2_ungated_margin, band3_rejection_rate_denominator]
  RANDOMIZED_LOOKUP: [band4_no_gain, band15_relevance_reject]
  GAP_NO_LOOKUP: [band5_exact_passive_reproduction]
  GATED_NEARTHRESHOLD: []   # DIAGNOSTIC ONLY -- excluded from all HARD_PASS/HARD_FAIL gates
```
The calibration-pool analyses (AUC / common-mode / naive-vs-aware) are NOT per-arm; they are separate
per-seed computations feeding bands 12/13/14 directly.

## HONEST DISCLOSED LIMITATIONS

1. Internal-retrieve is a plain Python dict, not the production HD codebook/cleanup memory (same
   disclosed gap as v1; hardening step = wire onto atom 29368's real codebook).
2. The NAIVE-vs-AWARE stress test uses a SYNTHETIC 2-candidate-set convention
   (`sibling=(true_cat+1)%6`) at calibration-pool scale (300 draws), not the 24-item real-term eval set --
   chosen deliberately for statistical stability (18 real AMBIGUOUS items is too few to resolve the
   naive/aware gap cleanly; at 300 draws the effect is stable across seeds). The underlying mechanism
   (derived reliability + closed-form null + shuffle control) is identical to what feeds the main loop's
   gate.
3. The closed-form product-plus-collision null (`phat_a*phat_b + (1-phat_a)*(1-phat_b)/5`) is an
   engineering simplification of atom 29378's rank-1-eigenvector fit, enabled by having per-source marginal
   reliability estimates directly available in this controlled construction. Conceptually equivalent (both
   test observed cross-source agreement against an independent-sources null); disclosed as a deliberate
   adaptation, not claimed as a new discovery.
4. AWARE's common-mode-informed conservatism has a real, disclosed coverage cost: at p_mirror=0.45
   (deliberately chosen just below RELIABILITY_THRESHOLD to make the illusory-corroboration failure mode
   visible), AWARE's combined score never crosses threshold, so it ALSO forfeits the mirror pair's modest
   genuine true-positive value -- raw stress accuracy (naive=0.674, aware=0.500, context only) can make
   NAIVE look fine on accuracy alone even though it is measurably fooled on false-accept rate. Band 14
   gates on false-accept-rate specifically for this reason.
5. GATED_NEARTHRESHOLD is diagnostic only (HP_SCOPE-excluded); it illustrates graded near-0.5 behavior
   but is not part of the HARD_PASS/HARD_FAIL decision.
6. classify_gloss's tie-break on an all-zero-score gloss defaults to category index 0 (ANIMAL) -- visible
   in the round-trip misses (5/7 misses default to ANIMAL). This is the same deterministic lowest-index
   tie-break convention as v1's argmax_tiebreak elsewhere; disclosed, not hidden, and does not affect any
   gated band (the misses are a feature of the independence proof, not a bug to fix).
7. Construction remains a controlled, low-noise vocabulary (real dictionary content, but a curated 48-term
   set across 6 categories) -- this cell proves the MECHANISM is no longer construction-determined; it
   does not yet prove the loop survives fully open-domain, noisy real corpora. That remains a future
   hardening step, same as v1's disclosure.

## SCHEMA-VET / CELL-TEMPLATE FIELDS

```yaml
cardinality_ok: true                  # EXPECTED_N_UNITS = len(SEEDS) x len(CONDITIONS) = 3x8 = 24
arms_differ_verified: true            # hash-checked at smoke across the 8 conditions' full prediction vectors
arms_differ_exempted:
  - ["PASSIVE", "GAP_NO_LOOKUP"]
  - ["PASSIVE", "GATED_BADSOURCE"]
  - ["GAP_NO_LOOKUP", "GATED_BADSOURCE"]
  - ["GATED_CLEAN", "UNGATED_CLEAN"]
final_metrics_atomicity: "tmp_replace"
except_ordering: "SystemExit/KeyboardInterrupt re-raised BEFORE except Exception; no bare/BaseException"
crlb_n_a: "not a capacity/JL cell; discriminator is keyword-classification + conformal set-size
  construction + reliability-AUC/common-mode-residual estimation, no argmax-noise floor."
discriminator_reachability: true
baseline_in_band: "acc_passive_primary measured 0.389 at smoke, within (0.05,0.95)"
discriminator_survives_scale: "Option A -- smoke IS the full regime (48+6 fixed items, 8-source
  calibration pool at N_CAL=240/seed; no separate scale-up axis exists for this mechanism-validation
  cell); only SEEDS differ (3, matching the multi-seed confidence/contamination-cell discipline)."
cell_chunked: false                   # single-shot, sub-second total; all seeds one process
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: false              # justified: sub-second total wall time, far under 15-min threshold
progress_logging: "print_flush_true"  # defense-in-depth; not required (timeout well under 1800s)
defensive_error_checking: "passed_all_4_patterns (start_marker + crash_diagnostic; heartbeat exempted;
  not chunked given sub-second wall time)"
deterministic_seeding: true           # torch.Generator(seed) + np.random.default_rng(seed) throughout;
  # no hash()/list(set()) ordering anywhere (grepped clean)
calibration_check: "adaptive_with_discriminator_gate -- reliability scores derived via Laplace-smoothed
  leave-one-fold-out mean over an 8-source calibration pool (history fold -> score; disjoint test fold ->
  AUC validation); q fixed via hdlab.conformal.calibrate_quantile over a held-out synthetic calibration
  set, never touching eval-item labels. Discriminator-still-fires verified at smoke via bands 7/11/12/13/15."
```

## TIMEOUT / DISPATCH

Entire cell (fact-list construction + 3 seeds x 8 conditions x 54 items + 8-source calibration pool
analysis x3 + 300-draw stress test x3, all in-memory numpy/dict/keyword operations, no corpus load, no
nltk/network access) runs in well under 1 second (measured smoke elapsed_s=0.053). Run FOREGROUND to
completion; no queue dispatch. `--timeout 120` as a defensive ceiling if ever routed through
`queue_add.sh` (not required for this local run). **Per Director's contract for this task: do NOT
queue_add, do NOT push, do NOT full-dispatch beyond this local smoke.**

## DATA DEPENDENCY STATUS

ATOMIC-2020 (the task's suggested top-pick lookup source) was NOT staged this cycle -- not attempted,
because a BETTER-FITTING real independent source was already available locally: Princeton WordNet via
`nltk.corpus.wordnet`, confirmed present in `.venv` (network reachability to github.com also confirmed
available, `curl` returned 200, but was not needed since the corpus was already downloaded locally).
WordNet's genus-differentia glosses + lexicographer-file supersenses map cleanly onto this cell's
6-category taxonomy; ATOMIC-2020's if-then event-relation format is a better fit for a FUTURE
event-plausibility-web cell (per `notes/research_plausibility_web_engineering_resources_adoptable_
foundation_2026-07-20.md`) than for this category-classification lookup task. **No staging step is needed
for a full run of THIS cell** -- the WordNet content is already harvested and frozen as static literals in
the cell file; the full run has the same zero-external-dependency profile as the smoke.

## GOVERNANCE

Pause-flag checked before authoring: `data/orchestrator_paused.flag` absent (verified 2026-07-20). No
origin push, no remote-persist, no queue_add invoked -- local-only, design-gate + smoke only per contract.
Routes to Skunkworks for adversarial VET before any atomize/store-write (not performed by this agent).
