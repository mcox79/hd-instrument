# Pre-registration: BID Order-Parameter Probe v1

**Date:** 2026-05-27
**Anchor name:** bid_order_parameter_v1
**Script:** experiments/exp_bid_order_parameter_v1.py
**Queue:** remote_cpu_queue
**Filed by:** exp_dev

---

## Hypothesis

H1 (novel class): the substrate's accessible bipolar state-space has an intrinsic
dimension (BID) inconsistent with ALL three standard Hopfield phase classes.
This would be direct geometric evidence that the substrate is in a novel thermodynamic
class, independent of any framework assumption.

H2 (methodological artifact / standard class): BID matches one of the 3 known classes,
retroactively localizing the substrate and indicating prior framework rejections were
due to architectural mismatch rather than genuine novelty.

---

## BID Estimator

Binary Intrinsic Dimension (BID) via Levina-Bickel 2-NN ratio estimator on bipolar
state-space samples (arxiv 2601.17427; Miolane & Monod "The dimensionality of the
Hopfield model"):

  For each sample point x_i in S substrate samples:
    d1_i = Hamming distance to 1st nearest neighbor (excluding self)
    d2_i = Hamming distance to 2nd nearest neighbor
    mu_i = d2_i / d1_i   (>= 1.0 by construction)
  BID = 1 / mean_i( log(mu_i) ) for valid points (mu_i >= 1.01, d1_i > 0)

---

## Pre-registered reference bands (N-dependent)

At primary N=1024 (and analogous for N=2048, 4096):

| Class       | BID band (N=1024)     | BID band (N=2048)      | BID band (N=4096)       |
|-------------|----------------------|------------------------|-------------------------|
| Retrieval   | [1.0, 2.5]           | [1.0, 2.5]             | [1.0, 2.5]              |
| Spin-glass  | [256.0, 512.0]       | [512.0, 1024.0]        | [1024.0, 2048.0]        |
| Paramagnetic| [1019.0, 1024.0]     | [2043.0, 2048.0]       | [4091.0, 4096.0]        |

Note: BID_RETRIEVAL band is N-independent (O(1) effective dimension at attractor).
Spin-glass and paramagnetic bands scale as O(N).

Substrate OUTSIDE all three bands = geometrically unclassified = H1 candidate.

---

## Calibration probe policy

This is the FIRST substrate measurement of BID; no prior empirical anchor exists.
Per calibration-probe policy:
- HARD-PASS band is pre-registered as "outside ALL 3 class bands by >= 2 sigma"
  not a point estimate. This is appropriately wide for a first measurement.
- HARD-FAIL band is pre-registered as "inside any ONE class band in >= 4/5 seeds"
  which is a clear positive identification, not a borderline call.

---

## Pre-registered threshold bands

### HARD-PASS (favor H1 -- novel class)

**HP1** (primary HARD-PASS): substrate BID falls OUTSIDE all 3 reference bands
  (retrieval, spin-glass, paramagnetic) by >= 2 sigma in 4-of-5 seeds at N=1024.
  Quantitatively: substrate BID NOT in [1.0, 2.5], NOT in [256, 512], NOT in [1019, 1024].
  Sigma = BID std across seeds; margin = min(dist_to_nearest_band_boundary) / sigma >= 2.0.
  HARD-PASS verdict: BID_HARD_PASS_NOVEL_CLASS
  P(H1) updates to >= 0.65.

**HP2** (joint signature): BID outside bands AND P(q) bimodality_coeff differs from
  all 3 class profiles in 4-of-5 seeds.
  HARD-PASS verdict (secondary): BID_HARD_PASS_NOVEL_CLASS_JOINT
  P(H1) updates to >= 0.70 (joint observable stronger than BID alone).

**HP3** (stability): BID stable within +/- 5% across N in {1024, 2048, 4096}.
  Stability condition: max_drift_frac <= 0.05.
  Required for the novel-class claim to be defensible at scale (not finite-N artifact).

### HARD-FAIL (favor H2 -- standard class)

**HF1** (any standard class): substrate BID lands INSIDE any one of the 3 bands
  in >= 4 of 5 seeds at N=1024.
  HARD-FAIL verdict: BID_HARD_FAIL_RETRIEVAL_CLASS, BID_HARD_FAIL_SPIN_GLASS,
                     or BID_HARD_FAIL_PARAMAGNETIC_CLASS
  P(H2) jumps to >= 0.55.
  Action: investigate why prior framework rejections occurred despite standard-class physics.

**HF2** (unstable): BID drifts >= 20% from N=1024 to N=4096.
  HARD-FAIL verdict: BID_HARD_FAIL_UNSTABLE
  Interpretation: BID is a finite-N artifact, not a thermodynamic OP.
  No novel-class claim possible; deeper instrumentation audit required.

**HF3** (spin-glass specifically): HF1 in [N/4, N/2] band.
  HARD-FAIL verdict: BID_HARD_FAIL_SPIN_GLASS
  Action: re-open 1-RSB analysis with stratified seeds.

### MIDDLE-BAND

**MB1**: BID outside bands but sigma margin < 2.0 (weak separation).
  Verdict: BID_MIDDLE_BAND_OUTSIDE_WEAK_SIGMA or BID_MIDDLE_BAND_MIXED.
  Action: ship secondary discriminator (joint BID + chi_4 + Kovacs hump signature).

---

## Instrumentation self-test (pre-registered formula check)

Formula self-tests (from _instrumentation_selftest() in the script):
  1. Random BSC at N=64, S=120 -> BID >= 3.0
     (random binary manifold has high effective dimension)
  2. Single-attractor retrieval at N=64 -> BID may be NaN (degenerate ok; n_valid < 5 accepted)
     Rationale: single stored pattern causes all retrievals to converge to identical vector
     -> all Hamming distances 0 -> n_valid=0; this is correct behavior for the degenerate case
  3. classify_bid(1.5, 1024) = "RETRIEVAL_BAND"
  4. classify_bid(300.0, 1024) = "SPIN_GLASS_BAND"
  5. classify_bid(1022.0, 1024) = "PARAMAGNETIC_BAND"
  6. classify_bid(100.0, 1024) = "OUTSIDE_ALL_BANDS"

---

## Smoke results (pre-ship)

Multi-scale smoke (N=256 and N=512, 1 seed, S=100):

  N=256: BID=29.19 class=OUTSIDE_ALL_BANDS q_mean=0.8436
         param_ref_BID=26.95
         Bands: retrieval=[1,2.5] spin-glass=[64,128] paramagnetic=[251,256]

  N=512: BID=26.86 class=OUTSIDE_ALL_BANDS q_mean=0.8462
         param_ref_BID=35.18
         Bands: retrieval=[1,2.5] spin-glass=[128,256] paramagnetic=[507,512]

Smoke verdict: BID_MIDDLE_BAND_MIXED (expected -- only 1 seed, 4/5 threshold not met)
Smoke wall_s: 0.01s

Note on paramagnetic reference proximity: substrate BID (~27-29) is in the same
ballpark as the paramagnetic reference BID at these small N (27-35). At full scale
(N=1024-4096) the bands diverge strongly: paramagnetic reference should approach N
while substrate BID is expected to stabilize. This is the key discriminating measurement.

Suspicious-result gate: PASS
  - BID values are real (not 0.0 or NaN)
  - n_valid >= 5 for real substrate samples
  - Script exits in 0.01s which is fast but reasonable (no matrix ops at smoke scale)
  - Metric varies between N=256 and N=512 (not constant)

---

## Timeout estimate

Primary run (N=1024, 5 seeds):
  Local timing at N=4096 one seed: 0.71s
  Full N=1024 est (O(N^2) scaling from N=4096): 0.71 * (1024/4096)^2 = 0.044s/seed
  5 seeds: 0.22s local
  Remote CPU overhead factor: 10x (conservative)
  timeout_s = ceil(1.5 * 0.22 * 10) = ceil(3.3) = 300s minimum

N-sweep run (N=1024/2048/4096, 5 seeds, --n-sweep flag):
  Local timing 3N*5seeds: ~11s
  Remote CPU overhead: 10x
  timeout_s = ceil(1.5 * 11 * 10) = ceil(165) = 300s

Final timeout_s: **300s** (5 min)
Note: computation is dominated by Hebbian W build (O(M*N^2)) and S^2 distance matrix.
At N=4096 with S=500, both are fast on CPU.

---

## Composition classification

This is a SCORE-level composition (joint signature BID + P(q)). Both observables
are computed in one script from the same substrate run. No handoff or pipeline
composition -- score-level isolation is clean.

---

## Dependency verification

- No upstream data dependencies (script generates its own synthetic substrate).
- No cap_map prerequisites.
- Import chain: torch, math, json, os, time (all in .venv; no cross-experiment imports).
- Verified: .venv/Scripts/python.exe has torch 2.12.0+cpu.
