# readout_fix_v1 -- three read-out fixes implemented, ablated, and honestly attributed. 2026-08-12

Cell `experiments/exp_readout_fix_v1.py`; pre-reg `preregs/2026-08-12_readout_fix_v1.md` (filed
BEFORE any run; one PRE-RUN correction and four post-SMOKE amendments C1-C4, all disclosed in sec 9
with the unamended outcomes preserved in metrics).
Substrate: `hdlab/reading_grounding_loop.py` -- `ReadoutConfig`, `ConceptSpace.freeze()`,
`FrozenAnchorSpace`, `canonicalize_fast(..., readout=)`, `make_pbv_fns(..., readout=,
freeze_episode=)`. ALL DEFAULT OFF.
Metrics: `data/exp_readout_fix_v1/metrics.json` (FULL, run_mode=full, 78731 B, elapsed 25.2 s),
`data/exp_readout_fix_v1_smoke/metrics.json` (SMOKE).
Author: hdi_exp_dev. WIRE STATUS: **VET_PENDING**.

Prior-work check (`tools/substrate_query.sh`): NONE substantive at cosine > 0.30. Top hit 0.3232 is
a 2026-06-08 dispatch-ordering note, matched on the token "anchor"; hits 3-4 are the bare tokens
`anchor` / `Anchor`. Not a rediscovery.

## VERDICT: MIDDLE_BAND (READOUT_FIX_PARTIAL). The read-out CAN be fixed, but NOT by the fix the framing put first. F2 and F3 carry the effect; F1 as specified is REFUTED.

## 1. Harness reuse verified bit-exactly (this licenses every comparison below)

The cell re-scores `exp_context_vector_signal_v1`'s OWN cached encounters (8282 encounters, 4467
lemmas, 898 eligible anchors, d=256) with that cell's own flip-count, cluster-bootstrap and CI code.

| gate | measured | upstream | match |
|---|---|---|---|
| fixed-space baseline flip | 0.782962 | 0.782962 | EXACT |
| growing-space baseline flip | 0.856881 | 0.856881 | EXACT |
| trace-sum separation (F2 off) | -0.063801 | -0.063775 | to rounding |
| batched scorer vs ORGAN `canonicalize_fast` under 4 ReadoutConfigs | 0/800 mismatch | -- | pass |
| frozen-space read vs ORGAN | 0/50 mismatch | -- | pass |
| no-leak / cardinality (24/24 units) / F1-gate-never-moved-an-argmax | clean | -- | pass |

`pytest verification/` **269 passed / 3 skipped** before AND after the substrate patch. Existing
foundation snapshot loads (`reading_grounding_v5_termboundary`, 341-row jsonl read back); 200/200
`readout=None` calls byte-identical to the pre-existing path.

## 2. THE ABLATION TABLE -- FIXED regime (directly comparable to flip 0.782962)

Operative metric = **flip rate over adjacent RETAINED encounters** (what an identity-matching
verifier actually sees). `flip_all` is the all-pairs rate; it is reported but is NOT evidence for
F1 (see sec 5). F3 is a no-op in this regime by construction and is not run here.

| condition | flip_all | retention | **flip_gated** | 95% CI | pairs | vs BASE (paired) |
|---|---|---|---|---|---|---|
| BASE (legacy `cos>=0.30`) | 0.782962 | 0.4167 | **0.5018** | [0.4644, 0.5397] | 1088 | -- |
| F1 only | 0.782962 | 0.4195 | 0.4520 | [0.4174, 0.4874] | 1093 | **-0.0499** [-0.0780, -0.0209] |
| F2 only | 0.784010 | 0.3300 | 0.3729 | [0.3337, 0.4114] | 834 | **-0.1289** [-0.1553, -0.1058] |
| F1+F2 (bundle) | 0.784010 | 0.3329 | **0.3685** | [0.3321, 0.4061] | 852 | **-0.1333** [-0.1664, -0.1009] |
| R-CTRL (random subset, retention-matched to the bundle) | 0.782962 | 0.3329 | **0.8206** | [0.7837, 0.8540] | 591 | +0.3188 |

Leave-one-out (positive = removing the fix made it WORSE):
* remove F1 from the bundle: **+0.0044** [-0.0259, +0.0337] -- CI covers 0 -> **NOT load-bearing**
* remove F2 from the bundle: **+0.0834** [+0.0561, +0.1094] -- **LOAD-BEARING**

Out-of-selection (EVALUATION half, thresholds never fitted on it): BASE 0.4905, F1 0.4127,
F2 0.3478, bundle 0.3130 -- the ordering and magnitudes hold, so the derived thresholds are not
overfitted.

## 3. GROWING regime (segment-snapshot space; the only regime where F3 exists)

| condition | flip_all | retention | flip_gated | vs BASE (paired) |
|---|---|---|---|---|
| BASE | 0.856881 | 0.4448 | 0.6822 | -- |
| F1 | 0.856881 | 0.4480 | 0.6285 | -0.0537 [-0.0767, -0.0310] |
| F2 | 0.849541 | 0.3615 | 0.5843 | -0.0979 [-0.1207, -0.0773] |
| **F3** | 0.796592 | 0.4034 | 0.5059 | **-0.1763** [-0.2096, -0.1440] |
| F1F2 (= ALL minus F3) | 0.849541 | 0.3619 | 0.5567 | -0.1255 |
| F1F3 (= ALL minus F2) | 0.796592 | 0.4097 | 0.4692 | -0.2130 |
| F2F3 (= ALL minus F1) | 0.790564 | 0.3206 | **0.3768** | **-0.3054** [-0.3439, -0.2683] |
| ALL | 0.790564 | 0.3236 | 0.3917 | -0.2905 [-0.3308, -0.2498] |
| R-CTRL | -- | 0.3236 | 0.8824 | +0.2002 |

Leave-one-out from ALL: remove F1 **-0.0148** [-0.0515, +0.0189] (covers 0; removing F1 is if
anything a small IMPROVEMENT); remove F2 **+0.0776** [+0.0471, +0.1080]; remove F3 **+0.1650**
[+0.1293, +0.2024]. On `flip_all` F3 alone is -0.0603, inside the +0.0739 ceiling the pre-reg
derived from the upstream space-growth measurement -- i.e. F3 delivers essentially all of the
instability that anchor-space growth was measured to add, and no more.

**LOAD-BEARING: F2 and F3. NOT JUSTIFIED: F1** (in both regimes, at the headline operating point).

## 4. F1 as specified is REFUTED, and the refutation is sharp

The pre-reg asked whether a field-relative criterion (margin, or z of the winner against the rest
of the field) can do what the magnitude gate provably cannot: tell whether the context belongs to
the lemma.

| statistic | AUC(REAL vs SCRAMBLE_SENT), selection half |
|---|---|
| legacy best-cosine | 0.5007 |
| z_top (winner vs field mean/sd) | **0.5067** |
| margin (top1 - top2) | **0.4992** |

At retention matched to the legacy gate, the new gate admits scrambled context at **0.4193** while
admitting real context at 0.4195 -- enrichment **1.0000x**, exactly the legacy gate's 0.4168/0.4167.
**Every statistic of the score field is arm-invariant, not just its maximum.** The upstream cell
showed the winning cosine's distribution is identical for real and scrambled context; this cell
shows the whole field is, so NO function of the scores can recover lemma-specificity. Fix 1 as
framed ("replace the magnitude test with a margin or z-score test") does not repair the defect it
was aimed at. That is a real negative and it closes a route.

**What F1 does do, and it is not nothing.** Standing above the field predicts argmax REPEATABILITY,
which is a different property from lemma-specificity:

| operating point | retention | flip_gated (REAL) | 95% CI | flip_gated (NULL) | pairs |
|---|---|---|---|---|---|
| legacy `cos>=0.30` | 0.4167 | 0.5018 | [0.4644, 0.5397] | 0.9978 | 1088 |
| z_top at 5% null admission | 0.0584 | 0.1667 | [0.1088, 0.2318] | 1.0000 | 150 |
| margin at 5% null admission | 0.0514 | **0.0594** | [0.0187, 0.1134] | 0.9600 | 101 |
| margin at 5%, with F2 | 0.0526 | **0.0385** | [0.0087, 0.0805] | 0.9643 | 104 |

At ~5% retention the retained REAL encounters are nearly argmax-STABLE while the geometry-matched
NULL stays at ~0.96-1.00 (D = +0.90 to +0.93). So the aggressive gate is not selecting
geometrically generic encounters -- it selects encounters on which the read-out genuinely agrees
with itself, and only for real context. The cost is that it discards 95% of encounters and leaves
101-156 scored pairs.

## 5. Bands that could not fail -- named, removed, and the four amendments

Pre-registered as non-failable and REMOVED before the run (prereg sec 8):
1. **F1's effect on `flip_all` is exactly 0 by construction** -- a gate selects encounters, it
   cannot move an argmax. Verified as a POSITIVE invariant instead (`f1_gate_moved_an_argmax: []`),
   which is the failable direction. F1's verdict rests only on admission, gated flip, and confirm.
2. **F3 in the FIXED regime is a no-op** -- not run, not reported.
3. **"gated flip < ungated flip"** -- subsetting alone changes the pair population, so it cannot
   fail informatively. Replaced by R-CTRL, which shows random subsetting moves flip the OTHER way
   (+0.32), i.e. the fixes' gains are selection, not subsetting.
4. **`verified_baseline_reproduces`** -- a harness gate that can only BLOCK; zero verdict weight.

Amendments after SMOKE, before FULL (all disclosed in `metrics.amendments`, unamended outcomes
preserved):
* **C1** the absolute collapse guard (top1_share >= 0.10, calibrated on the FIXED baseline 0.0149)
  fired on the GROWING regime's OWN BASELINE at smoke, so it could only fire vacuously there -- the
  same defect class as the upstream A1 guard and the F.4 "guard must not sit at the floor" rule.
  Amended to a guard relative to each regime's own BASE. At FULL it makes no difference: the
  unamended guard also fires on nothing (`prereg_literal_degenerate_collapse: []`), and no condition
  collapses (top1_share 0.0069-0.0186 across all 12; F2 REDUCES concentration, 0.0149 -> 0.0086).
* **C2** the "all condition digests distinct" arms-differ check fired at smoke on exactly the
  F1-only pairs the pre-reg had already declared identical by construction. Amended to: F2/F3-
  differing conditions must differ (0 collisions), F1-only pairs must be identical (0 violations).
  Declared as `arms_differ_exempted`, per the exemption clause.
* **C3** bug fix: the retention-matched threshold now matches the legacy retention OF THE SAME
  regime (matching everything to the FIXED regime's 0.4167 made the GROWING F1 arms retain 1.000 at
  smoke -- a broken comparison, not a result).
* **C4** both statistic forms are carried through instead of selecting one by AUC, because both
  AUCs came back at chance; a coin-flip selection must not hide behind one number.
* **PRE-RUN correction** (before any measurement): the draft's claim that F2's background stats are
  EXACTLY permutation-invariant was wrong on inspection of the re-masking step; replaced by a
  MEASURED near-invariance check. Measured: max |mu_real - mu_null| = 0.0039, max sd delta = 0.0057,
  far inside the 0.05 blocker -- so F2's calibration cannot be manufacturing the real-vs-null gap.

## 6. SECONDARY -- confirm rate: the projection is NOT calibrated, so NO claim against the 0.101 gate

Pre-registered gate: the BASELINE projection must land within 0.05 of PBV's observed
788/7836 = 0.100561. It does not -- FIXED BASE projects **0.4881**. Per the pre-reg, every
confirm-rate number is therefore **WITHIN-CELL RELATIVE ONLY** and the revival gate in the PBV
landed-VET is **NOT addressed by this cell**.

The direction of the bias is known and worth recording: PBV ran against a space that grew at EVERY
encounter, this cell's coarsest regime has 5 snapshots. Down that gradient the projection falls
monotonically toward the observed value -- FIXED BASE 0.4881, GROWING BASE 0.2936, GROWING R-CTRL
0.1123 (vs observed 0.1006). So these are UPPER BOUNDS. Relative movement, for information only:
FIXED 0.488 -> 0.619 (bundle); GROWING 0.294 -> 0.601 (ALL); GROWING ALL at the 5% margin gate
0.94. A calibrated answer requires running the projection against a live per-encounter space, which
this cell did not do.

## 7. What this does NOT show (stated as plainly as the positives)

* **Nothing about grounding QUALITY.** Flip rate, admission and confirm rate are STABILITY
  measures. A read-out that agrees with itself is not a read-out that is RIGHT; `also`/`people`
  winning consistently would score well here. The director hand-scores meaning separately, and no
  sentence of this note may be quoted as evidence about meaning.
* **PBV was not re-run** and nothing here says PBV would now pass.
* **F2's gain is confounded with a retention change** (0.4167 -> 0.3300): under F2 the calibrated
  winner's RAW cosine is lower, so fewer encounters clear the unchanged `cos>=0.30` gate. R-CTRL
  shows the confound has the OPPOSITE sign (random subsetting to 0.333 raises flip to 0.82), so it
  cannot explain the direction -- but a retention-matched F2 arm was NOT run. Note too that F2
  barely moves `flip_all` (-0.0010): it does not make the argmax globally more stable, it changes
  WHICH encounters are retained and what they agree on (it re-picks 48% of argmaxes, kappa 0.518).
  On the pre-registered F2 band, which was written on `flip_all`, F2 is **F2_NULL**; on the
  operative gated metric it is the load-bearing fix. Both are reported; the band was NOT rewritten
  after seeing the result.
* **F2 does not repair the trace-sum pathology**: separation -0.0638 -> -0.0210. Less negative,
  still negative. The pre-registered F2_HELPS band required >= 0.
* **F3 as measured freezes at the lemma's first-encounter SEGMENT snapshot** (5-snapshot
  granularity), which is the strongest freeze available from the cached pass, not a true
  per-hypothesis episode freeze in a live space. `make_pbv_fns(freeze_episode=True)` implements the
  real thing and is self-tested, but was NOT run inside a live reading pass.
* **Population**: 8282 arm-A encounters, not PBV arm B's 31045.
* Single deterministic pass; no seed axis, so no variance estimate beyond the cluster bootstrap.

## 8. Recommendation (hypothesis, pending VET)

Ship F2 + F3; do not ship F1 as an informativeness gate on the strength of this evidence. Keep F1
only as an optional aggressive STABILITY selector (margin at ~5% retention), where it is the only
setting that produces a near-stable subset -- and price in that it discards 95% of encounters. The
open question this cell raises and does not answer: whether a read-out that is stable at 0.037-0.39
flip is stable ON THE RIGHT ANCHOR. That is a quality measurement, not a stability one.
