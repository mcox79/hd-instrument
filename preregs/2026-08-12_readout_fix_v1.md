# PRE-REG -- readout_fix_v1: three measured read-out defects, implemented and ABLATED

Filed BEFORE any measurement run of `experiments/exp_readout_fix_v1.py`.
Author: hdi_exp_dev. ASCII-only.

Upstream evidence (all MEASURED, verified off disk before this pre-reg was written):
* `data/exp_context_vector_signal_v1/metrics.json` (commit 59479cf82, run_mode=full, 216.9s):
  per-encounter flip REAL **0.782962** CI95 [0.764563, 0.800267]; SCRAMBLE_SENT 0.998427;
  informative_rate REAL 0.416687 vs SCRAMBLE_SENT 0.416808; sense_thresh_rate 0.107220 both;
  best_cos_mean 0.311343 vs 0.311344; trace-sum sense-match REAL 0.221625 vs SCRAMBLE 0.285400
  (`trace_sum_separation` -0.063775); space_drift REAL fixed 0.782962 -> segment-snapshot
  **0.856881**; per-encounter argmax concentration REAL top1_share 0.014851, n_distinct 884,
  norm_entropy 0.959808; n_encounters 8282, n_lemmas 4467, n_anchors_eligible 898, d=256.
* `data/exp_pbv_hypothesis_v1_smoke/metrics.json:arms.B_PBV.trajectory`: n_confirm 788,
  n_disconfirm 7048 -> confirm rate **788/7836 = 0.100561**; informative_encounter_rate 0.393912.
* `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md` (a28cf3b45): the revival gate is
  "the confirm rate must move well above 0.101".

Prior-work check (`tools/substrate_query.sh "readout margin z-score anchor frequency correction
frozen anchor space argmax stability flip rate"`): top hit cosine 0.3232 is a 2026-06-08 dispatch-
ordering note (`notes/exp_dev_handoff_research_substrate_only_language_model_5x_2026-06-08.md`),
lexically matched on "anchor"/"dispatch", topically unrelated; hits 3-4 are the bare token
`anchor`/`Anchor`. NO substantive prior arc on read-out margin/hubness/frozen-pool at
cosine > 0.30. Reported as: **Prior-work check: NONE substantive at cosine>0.30** (the 0.3232 and
0.3096 hits are token collisions on the word "anchor", not prior work on this question).

---

## 1. Question

The per-encounter context vector carries a large, replicated signal (D = +0.2155, CI
[+0.1982, +0.2332], 100% of bootstrap above zero). The READ-OUT buries it: REAL's argmax flips on
78.3% of adjacent encounters, so an identity-matching verifier (`encounter_best == hypothesis.obj`)
cannot function. Three causes were MEASURED. Do they fix the read-out, and **which one carries the
effect**?

FIX 1 -- MAGNITUDE GATE IS BLIND. `cos >= PBV_INFORMATIVE_MIN` admits scrambled context at
0.416808 and real context at 0.416687: enrichment **1.0000x**. All lemma-specific information is
in argmax IDENTITY, none in the score. Replace the magnitude test with a FIELD-RELATIVE test (how
far the winner stands above the rest of the field), threshold DERIVED from the measured
distribution, not guessed.

FIX 2 -- FREQUENCY-BIASED POOL. Anchors are themselves accumulated context sums, so the pool is
biased to the corpus frequency backbone; a lemma's OWN summed contexts clear SENSE_MATCH_THRESH
LESS often (0.221625) than scrambled ones (0.285400). Frequency-correct the comparison pool by
per-anchor background standardization (hubness correction).

FIX 3 -- GROWING ANCHOR SPACE. Re-scoring against each encounter's own segment snapshot raises
flip 0.782962 -> 0.856881 (+0.0739). Freeze the field within a verification episode.

## 2. Compute architecture

Class **(b) sequential-CPU, justified**: the whole measurement is one dense
(8282 x 256) @ (256 x <=898) matmul per condition-arm (~1.9 GFLOP total across all 40 scorings)
plus a 2000x cluster bootstrap over 4467 lemmas. Wall time estimated < 5 min; GPU batching would
be pure overhead. Storage strategy: `no_storage` (re-scoring cached vectors; no bundling, no
composition). INLINE-LOCAL, foreground-to-completion, `timeout: 600000`. No remote dispatch, no
push.

## 3. Harness reuse (mandatory; no new harness)

The cell IMPORTS from `experiments/exp_context_vector_signal_v1.py`: `load_pass_cache`,
`build_arm_contexts`, `bundle_words`, `_eligible_anchor_view`, `score_argmax`,
`_per_lemma_flip_counts`, `_flip_rate_ci`, `_boot_indices`, `_agreement`, `_concentration`,
`_seed_from`, `_atomic_json`. It re-uses that cell's OWN pass cache
(`data/exp_context_vector_signal_v1/_pass_cache.npz` + `_pass_encounters.json`, written by the
FULL run at 2026-08-12 18:53), so the corpus, the encounter set (8282 encounters / 4467 lemmas,
`trace_alignment_ok` proven bit-identical to the loop's stored traces), the anchor space (898
eligible), the SCRAMBLE_SENT null construction, the cluster-bootstrap and the CI convention are
IDENTICAL and the numbers are directly comparable. `verified_baseline_reproduces` gate: the
cell's own BASELINE condition must reproduce flip 0.782962 to within 1e-6, else BLOCK.

## 4. The three fixes as implemented (substrate-level, DEFAULT OFF)

All three land in `hdlab/reading_grounding_loop.py` as ADDITIVE, keyword-only, default-None
options. `readout=None` takes the identical pre-existing code path -- backward compatibility is a
BLOCKING gate (sec 9), not an aspiration.

**F1 `margin_z_min` + `margin_stat`.** Per encounter, over the ELIGIBLE anchor field
`s_1..s_k` (k = 898) with winner `s_(1)`:
 - `z_top  = (s_(1) - mean(s)) / sd(s)`
 - `margin = s_(1) - s_(2)`
The FORM is selected by AUC (real vs SCRAMBLE_SENT) on a SELECTION half of lemmas (deterministic
sha256 split), and the THRESHOLD is a quantile of a MEASURED distribution, in two pre-registered
variants:
 - **G-MATCH (primary)**: threshold = the quantile of the REAL statistic that retains exactly
   0.416687 of encounters -- i.e. RETENTION-MATCHED to the legacy gate. Same retained count, same
   pair count, no subsetting confound; the only difference is WHICH encounters are selected. The
   headline F1 number is then the NULL ADMISSION RATE at matched real retention (legacy = 0.4168).
 - **G-FPR (secondary)**: threshold = 95th percentile of the NULL statistic (false-informative rate
   fixed at 0.05 by construction); the reported quantity is REAL retention (enrichment over 0.05).
Selection of form and both thresholds are computed on the SELECTION half only; every headline
number is reported BOTH over all lemmas and over the EVALUATION half alone.

**F2 `anchor_center` / `anchor_scale`.** Per anchor `a`, background mean `mu_a` and sd `sd_a` of
`cos(x, a)` over the SELECTION-half encounter contexts; calibrated score
`s'(x,a) = (cos(x,a) - mu_a) / max(sd_a, 1e-6)`. A hub anchor that scores high against everything
is penalised. This CHANGES the argmax (where the signal lives).

**Integrity property, measured in the cell.** SCRAMBLE_SENT borrows a DIFFERENT encounter's real
window and re-masks it for this target, so its window multiset is a permutation of the real one up
to that re-masking -- NOT bit-identical. The background statistics are therefore near-invariant,
not exactly invariant, and the cell MEASURES the discrepancy
(`f2_calibration_arm_delta_max` = max over anchors of |mu_real - mu_null|, and the same for sd)
rather than asserting an equality that the construction does not support. Blocker at > 0.05; the
measured value is reported either way. Rationale for keeping the check: if the calibration were
materially different under the two arms it could in principle manufacture a real-vs-null gap, so
its near-invariance is what licenses reading F2's real-vs-null separation as signal.
*(PRE-RUN CORRECTION, filed before any measurement of this cell: the first draft of this section
asserted exact floating-point invariance with a 1e-9 blocker. That was wrong on inspection of
`build_arm_contexts`'s re-masking step -- caught by reading the construction, not by seeing a
result. Corrected here rather than silently at verdict time.)*

**F3 `ConceptSpace.freeze()` -> `FrozenAnchorSpace`.** A snapshot object that duck-types the only
method `canonicalize_fast` reads (`anchor_matrix`), so a verification episode compares every
encounter of one hypothesis against ONE stable field. `make_pbv_fns(..., freeze_episode=True)`
snapshots at PROPOSE and releases at ABANDON.

## 5. Ablation matrix

Eight conditions (2^3): `BASE`, `F1`, `F2`, `F3`, `F1F2`, `F1F3`, `F2F3`, `ALL`.
Leave-one-out is read off directly: `F2F3` = ALL minus F1, `F1F3` = ALL minus F2,
`F1F2` = ALL minus F3.

Two regimes:
* **FIXED** (final anchor space; the regime the 0.782962 baseline was measured in) -- directly
  comparable to the primary baseline. **F3 IS A NO-OP HERE BY CONSTRUCTION** (the space is already
  frozen): the four F3-ON rows are NOT run and NOT reported as results (sec 8, removed band #2).
* **GROWING** (each encounter scored against its own curriculum-segment snapshot; baseline
  0.856881) -- the only regime in which F3 has bite. All eight conditions run here.

Every condition is scored for BOTH arms (REAL, SCRAMBLE_SENT).
`EXPECTED_N_UNITS = 4 (FIXED) * 2 arms + 8 (GROWING) * 2 arms = 24`; `cardinality_ok` counts them
and HARD_FAILs on a shortfall (META_RULE_H).

## 6. Metrics

PRIMARY: **per-encounter flip rate**, cluster-bootstrapped over lemmas (2000x), same harness.
 - `flip_all`: over ALL adjacent same-lemma encounter pairs. Directly comparable to 0.782962.
 - `flip_gated`: over adjacent pairs of RETAINED encounters (legacy `cos>=0.30` gate when F1 is
   OFF, the F1 gate when ON). This is what the verifier actually experiences.
SECONDARY: **projected confirm rate** vs the observed 0.100561 (sec 7).
Reported per condition: retention, null admission, argmax concentration (top1_share,
n_distinct, norm_entropy), D = flip(NULL) - flip(REAL), and paired leave-one-out deltas with CIs.

## 7. Confirm-rate projection (NOT a PBV re-run)

PBV is NOT re-run. The confirm rate is PROJECTED by replaying the EXACT `Library.flag` PBV state
machine (`hdlab/grounding_acquisition_loop.py:236-321`: PROPOSE at init_strength 0.5; CONFIRM iff
`argmax == h.obj` -> Bush-Mosteller gamma 0.5; else DISCONFIRM; ABANDON+REPROPOSE from THIS
encounter when strength <= 0.2) over each lemma's re-scored, gated encounter sequence in recorded
order. Reported as `confirm_rate_projected`, always labelled PROJECTED.
**Calibration gate (can fail):** the BASELINE condition's projection must land within 0.05 of the
observed 0.100561. Outside that, `projection_calibrated=false` and every confirm-rate number is
demoted to WITHIN-CELL RELATIVE ONLY with no claim against the 0.101 revival gate. (Exact equality
is not expected: this population is 8282 arm-A encounters, arm B's was 31045.)

## 8. Bands -- and the bands that CANNOT FAIL, named and REMOVED

### Bands that cannot fail -> REMOVED from the verdict (four PBV non-failable bands are not to be repeated)
1. **F1's effect on `flip_all` is EXACTLY ZERO by construction** -- a gate selects encounters, it
   does not move an argmax. The F1/F1F2/F1F3/ALL rows of the `flip_all` column are therefore NOT
   evidence for F1 and are excluded from F1's verdict. F1 is judged ONLY on (a) null admission at
   matched retention, (b) `flip_gated`, (c) the projected confirm rate.
2. **F3 in the FIXED regime is a no-op by construction** -- not run, not reported (sec 5).
3. **"The gated flip rate is lower than the ungated one"** -- a smaller retained set changes the
   pair population on its own, so this comparison cannot fail informatively. REMOVED; replaced by
   the RETENTION-MATCHED RANDOM-SUBSET control arm (`R-CTRL`, same retained count, encounters drawn
   at random with a fixed seed). Any F1 claim must beat R-CTRL, not merely beat the ungated rate.
4. **"Some metric moved"** -- not a band. Every verdict below names its metric, its direction, its
   effect size and its CI.
5. **`verified_baseline_reproduces`** is a HARNESS gate, not a result: it can only BLOCK, and it is
   reported with zero verdict weight.

### Verdict bands (pre-committed, all failable)
PRIMARY (FIXED regime unless stated):
* **READOUT_FIX_WORKS (HARD_PASS)**: the ALL condition's `flip_gated` is at least **0.15** below
  the BASE condition's `flip_gated`, the 95% CI of the paired difference excludes 0, AND the ALL
  condition beats `R-CTRL` by >= 0.10.
* **READOUT_FIX_PARTIAL (MIDDLE_BAND)**: reduction in [0.05, 0.15) with a CI excluding 0, or a
  reduction >= 0.15 whose CI covers 0, or an R-CTRL margin in [0.02, 0.10).
* **READOUT_FIX_INEFFECTIVE (HARD_FAIL)**: reduction < 0.05, or CI covers 0, or the R-CTRL margin
  < 0.02 (the improvement is subsetting, not selection).

PER-FIX ATTRIBUTION (this is the point of the cell):
* A fix is **LOAD_BEARING** iff its LEAVE-ONE-OUT removal from ALL degrades the operative flip rate
  by >= 0.05 with a paired-bootstrap CI excluding 0.
* A fix is **NOT_JUSTIFIED** iff its alone-effect is < 0.02 AND its leave-one-out CI covers 0.
  Explicitly reported as "not yet justified", not silently bundled.
* F1-specific: **F1_SELECTIVE** iff null admission at matched real retention <= 0.20 (vs the legacy
  gate's 0.4168); **F1_BLIND (fail)** iff >= 0.35; MIDDLE in between. Under G-FPR, F1_ENRICHED iff
  real retention >= 0.15 at null 0.05 (>= 3x); F1_BLIND iff <= 0.075.
* F2-specific: **F2_HELPS** iff `flip_all` drops >= 0.05 with CI excluding 0 AND the trace-sum
  separation turns non-negative (>= 0.00 vs the measured -0.063775); **F2_NULL** iff |delta| < 0.02.
* F3-specific (GROWING regime only): **F3_HELPS** iff growing-regime flip drops >= 0.05.
  Feasibility: the entire measured space-growth contribution is 0.856881 - 0.782962 = 0.0739, so
  F3's maximum attainable effect is ~0.074 -- the band is reachable but tight, and F3 CANNOT be
  the whole fix. Stated up front so a small F3 number is not later spun as a failure of the cell.

SECONDARY: **CONFIRM_RATE_CLEARS_GATE** iff the ALL condition's projected confirm rate > 0.20
(double the observed 0.100561) with the projection calibrated; **CONFIRM_RATE_MOVES** iff in
(0.1206, 0.20] (a >= 0.02 absolute rise); **CONFIRM_RATE_FLAT (fail)** iff <= 0.1206.

INTEGRITY BLOCKERS (any -> verdict VOID): `verified_baseline_reproduces` false;
`readout_fidelity_mismatches` != 0 (batched scorer vs the ORGAN's `canonicalize_fast` with the same
ReadoutConfig, 200 sampled encounters per condition family); `f2_calibration_arm_delta_max` > 0.05;
`cardinality_ok` false; `arms_differ_verified` false; `no_leak_violations` != 0;
`backward_compat_ok` false.

### Degenerate-collapse guard (can fail, and would invalidate an apparent win)
A read-out can trivially lower its flip rate by collapsing onto one generic anchor. Baseline REAL
argmax: top1_share 0.014851, n_distinct 884, norm_entropy 0.959808. Any condition with
**top1_share >= 0.10** (6.7x baseline) or **n_distinct < 100** is flagged
`DEGENERATE_COLLAPSE` and its flip-rate improvement is REFUSED (reported, never credited).

## 9. Backward compatibility (BLOCKING)

* `readout=None` must take a code path byte-identical to the current one. Asserted in the cell's
  self-test: 200 random encounters scored through `canonicalize_fast` with and without an
  all-None `ReadoutConfig` must return identical (obj, cos).
* `pytest verification/` must stay at 269 passed / 3 skipped.
* An EXISTING foundation snapshot must still load: the cell loads
  `data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl` and the
  `data/exp_context_vector_signal_v1/_pass_cache.npz` ConceptSpace rebuild, and asserts both.
  Recorded as `backward_compat_ok`.

## 10. Scope limits, stated before the run

* **A better read-out is NOT better meanings.** Nothing in this cell measures grounding QUALITY,
  correctness, or whether the anchors mean anything. Flip rate and confirm rate are STABILITY
  measures. The director hand-scores quality separately. No quality claim may be quoted from here.
* PBV is not re-run; the confirm rate is a PROJECTION (sec 7).
* The encounter population is the arm-A (`revive_terminal=False`) reading path, as in the upstream
  cell -- 8282 encounters vs arm B's 31045. Same organs, same corpus, same stream, same construction
  of the context vector and the read-out; different encounter POPULATION.
* WIRE STATUS: **VET_PENDING**. No capability-registry entry, no promotion, no `git add -A`.

## 11. SCHEMA-VET fields

```yaml
cardinality_ok: true                 # EXPECTED_N_UNITS = 24, counted in metrics
sweep_alignment_verdict: ALIGNED     # each fix flag is experienced by the primitive it names
discriminating_fraction: 1.00        # baseline flip 0.7830 sits mid-band [0.05,0.95]; all 8
                                     # conditions predicted in [0.30,0.90] (no floor/ceiling point)
baseline_in_band: true               # BASE flip_all = 0.7830, inside (0.05, 0.95) (META_RULE_AG)
composition_edges: []                # no primitive-to-primitive composition; single read-out
positive_control_arms:
  - arm: BASELINE_REPRODUCES_UPSTREAM
    cited_prior_metric: 0.782962      # MEASURED@data/exp_context_vector_signal_v1/metrics.json
    tolerance: 0.000001
    if_outside_tolerance: BLOCK (harness drift; no verdict)
  - arm: CONFIRM_RATE_PROJECTION_CALIBRATION
    cited_prior_metric: 0.100561      # MEASURED@data/exp_pbv_hypothesis_v1_smoke/metrics.json
    tolerance: 0.05
    if_outside_tolerance: confirm-rate results demoted to within-cell relative only
functional_requirements:
  - "select encounters whose winner is lemma-specific" -> F1 field-relative gate (NEW mechanism;
    the existing magnitude gate is measured blind at 1.0000x enrichment)
  - "compare against a pool not dominated by the frequency backbone" -> F2 per-anchor background
    standardization (hubness correction; NEW, no prior organ)
  - "hold the comparison field still across one hypothesis" -> F3 ConceptSpace.freeze()
real_code_path_exercised: [ConceptSpace, canonicalize_fast, ReadoutConfig, FrozenAnchorSpace,
                           make_pbv_fns, HDFactStore, load_pass_cache]
substrate_signature_checked: [canonicalize_fast, make_pbv_fns, ConceptSpace.freeze, HDFactStore]
guard_baseline_validated: [DEGENERATE_COLLAPSE]   # baseline top1_share 0.0149 is far from the 0.10
                                                  # guard edge, so the guard is not at the floor
deterministic_seeding: true          # fixed ints + hashlib only; no builtin hash(), no list(set())
calibration_check: "adaptive_with_discriminator_gate"   # F1/F2 thresholds are DERIVED from measured
                                  # distributions on a SELECTION half; the discriminator (null
                                  # admission at matched retention) is re-verified on the
                                  # EVALUATION half and reported separately
crlb_n/a: "primary statistic is a paired difference of rates with a cluster bootstrap, not an
           estimator against a noise floor; the reachability constraint that matters (F3 <= 0.074)
           is stated explicitly in sec 8"
cell_chunked: false                  # single deterministic pass, no seed axis
start_marker_written: true
crash_diagnostic_present: true
heartbeat_present: true
defensive_error_checking: "passed_all_4_patterns"
final_metrics_atomicity: "tmp_replace"
arms_differ_verified: true           # sha256 over each condition's argmax vector
progress_logging: "print_flush_true" # (timeout_s < 1800, declared anyway)
HP_SCOPE:
  BASE: [verified_baseline_reproduces]       # the baseline inherits NO fix gate
  R-CTRL: []                                 # control arm, no HP gate
  F1: [F1_SELECTIVE]
  F2: [F2_HELPS]
  F3: [F3_HELPS]
  ALL: [READOUT_FIX_WORKS, CONFIRM_RATE_CLEARS_GATE, DEGENERATE_COLLAPSE]
```

## 12. What falsifies each fix (plain statement)

* **F1 is falsified** if, at retention matched to the legacy gate, the field-relative gate admits
  scrambled context at >= 0.35 (the legacy gate admits 0.4168) -- i.e. standing above the field is
  no more lemma-specific than raw cosine -- or if `flip_gated` under F1 fails to beat the
  retention-matched RANDOM subset by >= 0.02.
* **F2 is falsified** if calibrating the anchor pool moves `flip_all` by < 0.02, or if it leaves
  the trace-sum separation negative, or if it wins only by collapsing the argmax distribution
  (`DEGENERATE_COLLAPSE`).
* **F3 is falsified** if freezing the field within an episode moves the GROWING-regime flip rate by
  < 0.05 (its ceiling is 0.074, so this is a narrow but genuine window).
* **The whole bundle is falsified** if `ALL` fails to beat `BASE` by 0.05 on the operative flip
  rate. A flat result is the reportable outcome, not a reason to re-tune: any post-hoc threshold
  change would be filed as a disclosed AMENDMENT with the unamended outcome preserved in metrics
  (`prereg_literal_primary`), exactly as the upstream cell did.
