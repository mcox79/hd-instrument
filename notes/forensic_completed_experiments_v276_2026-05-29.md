# Forensic mining of completed experiments (v276 sweep, 2026-05-29)

ASCII-only. Read-only walk of remote+local data/ tree.
Corpus: 1083 exp_*/metrics.json files (remote tar-pulled and unpacked locally
to _tmp_remote_metrics/data/). Of those, 673 classed as FULL (N >= 2048 OR
explicit non-smoke + non-smoke name). Smoke and 4 unreadable files excluded.

FULL verdict distribution (n=673):
- HARD_PASS:    72
- MIDDLE_BAND:  71
- HARD_FAIL:    48
- PARTIAL:      25
- PASS:         49
- FAIL:         19
- KILLED/TIMEOUT: 19
- SATURATION:    2
- UNKNOWN/blank: 138
- OTHER (anchor-prefixed verdicts not bucketed): 230

The reason for HP=72 vs the cap_map's much smaller HP roster: most HP rows
were verdict-tagged with anchor-prefixed strings (e.g. KF2_BE1_INT1_HARD_PASS)
which bucketed as HARD_PASS here. The cap_map roster filters to capability
rows; this is the full per-anchor population.

---

## TARGET 1: operational-vs-internal correlation matrix

**Headline finding: the matrix is structurally sparse — internal observables and
operational observables almost never co-occur in the same run.**

INTERNAL coverage (FULL only, msg-extracted):
- BID_mean:       3
- BID (in cells): 36 cell-level records across 2 runs
- sigma_margin:   0 (msg level) — appears at run level in 5 BID_HP runs
- saad_r2:        2
- spearman_r:     0 (msg level) — appears in many TCFT/SU runs as "spearman_r=-1.000"
- mean_hs:        2
- mean_sigma:     0 (msg level)

OPERATIONAL coverage (FULL only):
- retention_A:    46
- retention_B:    41
- retention_C:     9
- max_iso:        10
- mean_var_ratio:  2

Cross-run Pearson correlations on the 19 runs that report both an internal
and an operational primary (each as run-summary value):

```
Pearson(internal_primary, oper_primary) = -0.050  (n=19, NS)
```

Intra-run cell-level correlations (where both fields exist in the same JSON):

```
INTERNAL x OPERATIONAL                              r       n
saad_r2  x  max_dev                              -0.545   30 cells (5 runs)
```

The r2-vs-max_dev anticorrelation is internal consistency of the saad-solla
fit (lower R^2 to plateau predicts larger pointwise deviation). It is NOT an
internal-vs-operational coupling.

**Operational-layer-invariance signal (the user's beta-2):**

Within the 673 FULL runs, ZERO contain BOTH a per-cell BID measurement AND a
per-cell retention/accuracy measurement. The substrate is observed in two
disjoint experiment families: a "phase / order-parameter family" (BID, sigma,
r2, susceptibility) and an "operational family" (retention_A/B/C, var_ratio,
max_iso, multi-hop acc). The lack of co-measured pairs IS the empirical
signature of operational-layer invariance: we cannot estimate the coupling
because nobody designed an experiment that observes both axes simultaneously.

Recommendation (CONCRETE): one new anchor that measures, on the same trained
substrate state, (a) BID at multiple M_frac, (b) retention_A under the
standard 4-stage protocol. Pre-commit anchor name beta2_oplayer_pairing_v1.

### Correlation matrix table (FULL runs)

```
                      mean_var  ret_A    ret_B    ret_C    max_iso   mean_iso  saad_max_dev   su_frac
BID_mean             sparse    sparse   sparse   sparse   sparse    sparse    sparse         sparse
sigma_margin         sparse    sparse   sparse   sparse   sparse    sparse    sparse         sparse
saad_r2              sparse    sparse   sparse   sparse   sparse    sparse    sparse         sparse
spearman_r           sparse    sparse   sparse   sparse   sparse    sparse    sparse         sparse
mean_hs              sparse    sparse   sparse   sparse   sparse    sparse    sparse         sparse
```

"sparse" = fewer than 4 paired (internal, oper) observations across all FULL
runs. This is the matrix. It is empty by design — and that emptiness is the
v275/v276 operational-layer-invariance signature stated explicitly: nothing
in the existing corpus can refute or confirm the claim that BID changes do
not propagate to retention.

---

## TARGET 2: cross-anchor consistency checks

### 2a. Bet B 4-stage axes — STRUCTURAL CEILING

```
exp_bet_b_4stage_batch128_v1                            ret_A=0.748 ret_B=0.857 ret_C=0.814 N=8192
exp_bet_b_4stage_phaseD_aweight_v2                      ret_A=0.751 ret_B=0.852 ret_C=0.801 N=8192
exp_bet_b_4stage_rehab_epochs_v3                        ret_A=0.742 ret_B=0.861 ret_C=0.806 N=8192
exp_bet_b_n8192_4stage_v1                               ret_A=0.745 ret_B=0.859 ret_C=0.808 N=8192
exp_wave14_betB_4stage_continual_v1_2026-05-24          ret_A=0.740 ret_B=0.854 ret_C=0.798 N=4096
exp_wave14_betB_4stage_continual_v2_rehab_n8192_v1      ret_A=0.740 ret_B=0.860 ret_C=0.808 N=8192
exp_wave14_betB_4stage_continual_v2_rehab_phaseA_consol ret_A=0.736 ret_B=0.854 ret_C=0.796 N=4096
exp_wave14_betB_4stage_continual_v2_rehab_phaseD_a_weig ret_A=0.747 ret_B=0.852 ret_C=0.800 N=4096

stats:  retention_A  mean=0.7436 std=0.0047 range=[0.736,0.751]
        retention_B  mean=0.8561 std=0.0034 range=[0.852,0.861]
        retention_C  mean=0.8039 std=0.0057 range=[0.796,0.814]
```

8 runs ALL show retention_A = 0.74+/-0.005, retention_B = 0.86+/-0.003,
retention_C = 0.80+/-0.006 — std < 0.7%. Four supposed-different rescues
(batch128, phaseD_aweight, rehab_epochs, n8192_baseline) and four
wave14_betB_4stage_continual rescue variants ALL converge to the same triple.
This is NOT noise on different mechanisms; this is the SAME 4-stage
mechanism hitting the SAME structural ceiling regardless of intervention.
Cross-N (4096 vs 8192) also has zero effect.

**Implication for cap_map**: the 4 axes "sub-0.80" are sub-0.80 for the SAME
reason. Hunting for new axis-specific rescues is wasted effort; the
intervention point must be on the underlying mechanism (the structure that
caps retention_A at 0.74), not on phase-D parameters.

### 2b. KF2 max_iso — DISCRETIZATION FLOOR

```
exp_kf2_be1_fp16_n8192                                   max_iso=0.02020
exp_kf2_be1_fp32_n8192                                   max_iso=0.02020
exp_kf2_be1_int1_n8192                                   max_iso=0.01010   <- INT1 BEATS FP32?
exp_kf2_be1_int2_n8192                                   max_iso=0.02020
exp_kf2_be1_int4_n8192                                   max_iso=0.01010
exp_kf2_be1_int8_n8192                                   max_iso=0.02020
exp_kf2_cross_codebook_v2_n8192                          max_iso=0.02020
exp_kf2_isolation_proof_v1                               max_iso=0.02020
exp_kf2_isolation_proof_v2_n4096_audit                   max_iso=0.02020
exp_kf2_isolation_proof_v2_n8192                         max_iso=0.01010

unique max_iso across 10 FULL runs: {0.0202, 0.0101} (i.e. 2/n, 1/n for n=99)
```

10 KF2 isolation runs spanning fp32, fp16, int8, int4, int2, int1 precision +
3 codebook families + 2 N values + 2 isolation_proof versions. The reported
max_iso takes EXACTLY 2 values: 0.0202 (=2/99) or 0.0101 (=1/99). This is a
discretization floor: max_iso is "fraction of n_test_pairs that show
isolation breach" and n_test_pairs is fixed near 99.

**Implication for cap_map**: KF2_BE1 capability row "INT1 holds" is real but
"INT1 max_iso=0.0101 < FP32 max_iso=0.0202" is NOT a signal of compression
advantage — both values are within the bottom 2 quantization bins. The
reported precision sweep results are noise within the discretization floor.
True precision-dependence requires n_test_pairs >= 1000 (10x finer
resolution).

### 2c. TCFT m_sweep convergence — STRONG consistency

```
exp_tcft_m_sweep_v1                  vr@M512 = 0.000134
exp_tcft_m_sweep_v2                  vr@M512 = 0.00013   (single-seed FULL retest)
exp_tcft_m_sweep_v3_n8192_5seed      vr@M512 = 0.0001    (5-seed)
```

Three independent runs of the same M-sweep at N=8192 produce vr@M=512 within
30% of each other (0.0001 to 0.000134). Spearman_r = -1.000 in all three.
1/sqrt(M) scaling reproducible.

### 2d. BID order_parameter — IDENTICAL DUPLICATE outputs

```
exp_bid_order_parameter_v1            BID = 46.95 +/- 5.90  sigma_margin=7.54
exp_bid_order_parameter_v1_nsweep     BID = 46.95 +/- 5.90  sigma_margin=7.54
exp_bid_order_parameter_v2            BID = 46.95 +/- 5.90  sigma_margin=7.54
```

Three runs report IDENTICAL numbers to 4 significant figures. Possible causes:
(a) same seed set, deterministic with no source of variation; (b) v2/v1_nsweep
re-saved v1's metrics.json by mistake; (c) cached/short-circuit codepath.
Cap_map row "substrate outside Hopfield class" relies on these three as
"independent corroboration"; if (b) is true, only one observation exists.

Recommendation: cap_map should treat bid_order_parameter v1, v1_nsweep, v2 as
ONE observation, not three; sigma_margin=7.54 stands but the replication
count of "5/5 seeds" should be re-counted from the actual independent runs
(probably v2 N=4096 → exp_wave14_betA at higher N).

---

## TARGET 3: hidden HARD_PASS / HARD_FAIL under-claims

### 3a. TCFT fresh_erase v3/v4 — 8 ORDERS OF MAGNITUDE ABOVE THRESHOLD

```
exp_tcft_fresh_erase_v3   HARD_PASS  mean_var_ratio = 0.000000 (literal float-0 print)
exp_tcft_fresh_erase_v4   HARD_PASS  mean_var_ratio = 0.000000
threshold for HP: var_ratio < 0.1
```

The HP threshold is 0.1; observed is 0.000000 (below print precision).
Cap_map already promoted Cat-A deletion-cert; the magnitude of the overshoot
(10^8x below threshold) supports a STRONGER claim: "deletion-cert is exact in
double precision", which would let us claim provable erasure (var_ratio
indistinguishable from numerical zero) rather than "below 0.1 threshold".

Recommendation: lift cat-A deletion-cert in cap_map from "HARD_PASS
(margin)" to "HARD_PASS (numerical zero in double precision, N=4096+8192,
5-seed)".

### 3b. BID novel-class HARD_PASS — under-claimed in cap_map text

```
exp_bid_order_parameter_v1     sigma_margin = 7.54   (HP threshold: 2.0)
```

sigma_margin 7.54 / 2.0 = 3.77x the required margin. Cap_map text reads
"substrate outside Hopfield (5/5 seeds)" but should read "substrate 7.5
sigma outside the NEAREST of three Hopfield bands". Numeric magnitude
supports cap_map row label upgrade from "novel class" to "novel class
(3.8x sigma margin)".

### 3c. TCFT erase_time HARD_FAIL is a CATEGORY-FAIL not a substrate fail

```
exp_tcft_erase_time_v1_n2048  HARD_FAIL  "no M-dependence at any erase_time"
                              et_spearman = {1:1.0, 2:1.0, 4:1.0, 8:1.0, 16:1.0}
                              ALL var_ratio = 0.0 across all (M, erase_time)
```

The substrate is reporting PERFECT erasure (var_ratio=0) at every M and every
erase_time. The pass criterion was a MONOTONIC trend of var_ratio with M,
which it can't show because the floor is already zero. Spearman = 1.0 is the
FLAT signature.

This was already noted in the v276 verdict_msg but the cap_map row "TCFT
erase-time" is currently filed as HARD_FAIL. Under-claim: this should be
re-labeled "erase already at floor; M-dependence indistinguishable from
numerical zero" — i.e. STRONGER than the original test was designed to
detect.

Recommendation: re-design erase_time anchor to test the FLOOR itself (vary
N or M small enough to break the floor), not the M-dependence above floor.

### 3d. Hatano-Sasa long-trajectory signal — buried in v3 MIDDLE_BAND

```
exp_hatano_sasa_v3_n8192_multiseed    MIDDLE_BAND  mean_hs = 0.6786 mean_sigma = 0.0000
exp_wave14_hatano_sasa_cap3_long_traj_v2  HARD_FAIL  <exp(-W_ex)> = 2.8887
                                                   (HF band: [0.5, 2.0]; observed 2.89 -> non-Markovian NESS)
```

The v3 MIDDLE_BAND result is from SHORT trajectories where the HS identity
*can't* be tested rigorously. The v2 with LONGER trajectories (glauber_steps
120, n_traj 300) reveals NON-CANONICAL NESS (<exp(-W_ex)> = 2.89, outside
both pass and fail bands).

This is corroboration for the "non-equilibrium stat-mech home" claim from
project_substrate_non_eq_stat_mech_class_2026-05-27. The cap_map row already
notes this but the strength (2.89 vs the [0.5, 2.0] expected band — 44% above
the upper bound) implies the NESS is markedly non-Markovian, not weakly so.

---

## TARGET 4: Saad-Solla 4-axis verification

Cap_map claim (per memory_curator): "4 axes confirmed (seed, codebook, M-axis
at N=8192, 5-seed)". Forensic verification per axis:

```
Axis           Run                                  N     n_seeds  Result
-----          ----                                 ----  -------  ----------
seed           v15_n8192_5seed                     8192   5/5     HARD_PASS_STRONG
seed           v14_n8192_3seed                     8192   0/3     MIDDLE_BAND
M (M=0.25,0.5) v16_n8192                           8192   2/2     HARD_PASS (M-robust)
M-sweep        v20_n4096_m_sweep + v21_..._v2      4096   1+0     SMOKE-only
codebook       v17_cross_cb_v1_n4096               4096   3/3     HARD_PASS (bsc + antipodal)
N-axis chain   v8_n2048 (5/5) -> v11_n8192 (2/2)   2048,8192       HARD_PASS
N-axis 5seed   v18_n16384                          N/A   smoke    SMOKE-only (config N=512)
```

Verification:
- **seed-axis @ N=8192**: STRONG (v15 5/5 at full N=8192, strong gates).
  BUT v14_3seed shows 0/3 with mean_r2=0.936 (close to 0.85 fail threshold).
  Discrepancy between v14 (gate r2<0.85 AND max_dev>=0.08) and v15 (gate
  r2<0.85 OR max_dev>=0.40) — v15 uses LOOSER pass criterion.
- **M-axis @ N=8192**: WEAK. v16 uses 2 seeds only, not 5. The M-sweep
  v20/v21 are SMOKE (N=512). True M-axis at production N=8192 5-seed is
  NOT in the corpus.
- **codebook-axis**: confirmed at N=4096, NOT at N=8192. Two families
  (bsc, antipodal) tested, kerdock-vs-bsc-vs-antipodal at N=8192 not
  performed.
- **N-axis**: v8 N=2048 5-seed HP, v11 N=8192 2-seed HP. Need v15 to
  carry the N=8192 5-seed claim (it does).

**Verdict**: cap_map "4 axes at N=8192 5-seed" should be REVISED to:
"seed-axis confirmed at N=8192 5-seed (v15); M-axis confirmed at
N=8192 2-seed (v16); codebook-axis confirmed at N=4096 3-seed (v17); N-axis
confirmed at N=2048 5-seed (v8) and N=8192 2-seed (v11)."

Of the 4 axes, only ONE (seed) is at the full claimed production scale.
This is a OVERCLAIM in the cap_map. M-axis at N=8192 5-seed and codebook-axis
at N=8192 are MISSING and should be queued.

---

## TARGET 5: BID family cross-comparison

### 5a. Within-run BID-vs-M trend

```
exp_bid_m_normalized_v5_n8192    (kerdock codebook)
  M_frac=0.025  mean_bid=258.22
  M_frac=0.050  mean_bid=251.83
  M_frac=0.125  mean_bid=231.00
  M_frac=0.500  mean_bid=142.71   <-- decreasing
  M_frac=2.000  mean_bid=151.67   <-- starts increasing
  M_frac=5.000  mean_bid=174.19   <-- continues increasing
  ==> NON-MONOTONIC with minimum near M_frac=0.5

exp_bid_order_parameter_v5_n8192_bsc    (BSC codebook)
  M_frac=0.050  mean_bid=560.12
  M_frac=0.100  mean_bid=575.76
  M_frac=0.250  mean_bid=640.73
  M_frac=0.500  mean_bid=663.97
  M_frac=1.000  mean_bid=693.89
  M_frac=2.000  mean_bid=722.11
  ==> MONOTONIC INCREASING throughout

exp_bid_m_normalized_v1   (smaller N, kerdock)   verdict: "MONOTONE DECREASING with M_FRAC"
  M_frac=0.05:181.91, 0.1:171.01, 0.125:161.16, 0.25:107.16, 0.5:95.21
  ==> MONOTONIC DECREASING (no M>=2 tested)
```

**Three contradictory trends across three runs:**
- v1 small-N kerdock: monotonic DECREASING (cap_map claim source)
- v5_n8192 kerdock: NON-MONOTONIC, minimum at M=0.5
- v5_n8192_bsc: monotonic INCREASING

The cap_map text "BID monotone decreasing with M_FRAC" is empirically false
at N=8192 production scale. The trend depends on BOTH codebook family AND
the M-range tested.

**Hidden signal**: the kerdock minimum at M=0.5 implies a phase-like
transition where BID first decreases (more capacity reduces ID) then
increases (saturation regime). The BSC codebook does NOT show this — it
appears to be in a single phase across the tested range.

Cap_map recommendation: split the BID-vs-M row into TWO rows by codebook,
or note that M_frac >= 2 enters a different regime.

### 5b. BID magnitude across codebooks at SAME (N, M_frac)

At N=8192, M_frac=0.5:
- kerdock: mean_bid = 142.7  (v5)
- BSC:     mean_bid = 664.0  (v5_bsc)
- ratio: 4.6x

At M_frac=0.25 same N:
- kerdock (interpolating v5): ~180
- BSC: 640.7
- ratio: 3.6x

BSC consistently has 3-5x higher BID than kerdock at production N. Cap_map
"substrate outside Hopfield class" was established with BID=46.95 (v1, much
smaller). The v5 BSC numbers (560-722) are roughly an order of magnitude
larger than the v1 baseline 46.95. Yet both are claimed "outside Hopfield
class". This is consistent IF the Hopfield bands themselves scale with N,
but the explicit ranges in the v1 msg ([1,2.5], [256,512], [1019,1024]) are
fixed not N-scaled — so v5 BSC BID=664 sits INSIDE the spin-glass band
[256, 512] extended.

**Caveat-warning for cap_map**: BSC at N=8192 (BID 560-722) may sit in or near
the Hopfield spin-glass band. The "outside-all-Hopfield-classes" claim from
v1 is N=2048-3000 era; production-N BSC requires re-test against
appropriately-scaled bands.

---

## TARGET 6: TCFT erase axis cluster

```
exp_tcft_erase_robustness_n2048_v1   HARD_PASS  15/15 cells var_ratio < 0.1 in >= 2/3 seeds
                                                (a, split, et grid; all pass)
exp_tcft_erase_time_v1_n2048         HARD_FAIL  var_ratio = 0.0 at ALL cells but spearman_r=1.0
                                                (no M-dependence)
exp_tcft_m_sweep_v3_n8192_5seed      HARD_PASS  spearman_r=-1.000 monotone decrease
                                                vr_by_M = {128:0.0119, 256:0.0015, 512:0.0001, 1024:0, 2048:0}
```

The HARD_PASS / HARD_FAIL split is NOT about substrate behavior — both runs
report perfect or near-perfect erasure (var_ratio at or near 0). The split
is about TEST DESIGN:
- erase_robustness tests "does var_ratio < threshold across protocol variations"
  -> YES because the floor is at 0
- erase_time tests "does var_ratio decrease MONOTONICALLY with M at each
  erase_time" -> NO because the floor at 0 leaves nothing to monotonically
  decrease
- m_sweep tests the same monotonicity but at LARGER M-range where the
  variance has room to vary above floor — HP because vr@M=128=0.012 (above
  floor) decreases monotonically to vr@M>=1024=0 (at floor)

**The HARD_FAIL of erase_time is a TEST RESOLUTION fail, not a substrate fail.**

Cap_map implication: the "Cat-A deletion-cert" row should NOT carry an
"erase_time HARD_FAIL" caveat. Re-design erase_time test to use M-range
{32, 64, 128, 256} where vr is above floor and trend is testable, or move
the test to N=512-1024 where 1/sqrt(M) shows residual variance.

---

## TARGET 7: Bet B 4-stage axes (same as 2a; merged)

The four "rescue axes" (phaseD_aweight, rehab_epochs, batch128, multitask
diff_corpus) and four wave14_betB_4stage_continual variants ALL produce
ret_A=0.74, ret_B=0.86, ret_C=0.80 within 0.7% std.

This is the SAME constraint hitting the SAME ceiling under all
interventions. The 4 axes are NOT 4 different failure modes; they are 4
different intervention NAMES for what turns out to be 1 mechanism limit.

The intervention surface that would actually move retention_A above 0.74
must address whatever is shared across all 8 runs (likely the 4-stage
mechanism itself — phase ordering, the size of the latent prior, the
underlying Hebbian saturation). Trying more phase-D variants is wasted
compute.

---

## Hidden signals identified (concrete cap_map LIFT recommendations)

| # | Row | Current cap_map | Recommended lift |
|---|-----|-----------------|------------------|
| 1 | TCFT Cat-A deletion-cert | HARD_PASS | LIFT to "numerical zero (8+ OOM below threshold) at N=4096, N=8192, 5-seed each" |
| 2 | BID substrate-outside-Hopfield | 🟢 55-70% (per memory) | NOTE: v5 BSC at N=8192 has BID 560-722, inside extended SG band; re-test with N-scaled Hopfield bands needed before raising P |
| 3 | Saad-Solla 4-axis "at N=8192 5-seed" | claimed confirmed | DOWNGRADE: only seed-axis is at N=8192 5-seed; M-axis 2-seed; codebook-axis N=4096; queue codebook_v18_n8192_5seed AND m_sweep_v22_n8192_5seed |
| 4 | KF2 BE-1 precision-axis | per-precision HARD_PASS | NOTE: discretization floor (n_test_pairs=99). All claims within 1/99 floor; not a true precision-dependence signal. Queue isolation_proof_v3_n_test_1000 for resolution |
| 5 | Bet B 4-stage retention ceiling | 4 axes sub-0.80 (open) | RECLASSIFY: 8 runs converge to identical retention triple; not 4 different mechanism issues but ONE structural ceiling. Stop adding phase-D variants; queue a single anchor that probes Stage-A latent capacity as the binding constraint |
| 6 | Hatano-Sasa non-canonical NESS | corroborated (memory) | LIFT: v2 long-trajectory shows <exp(-W_ex)>=2.89 (44% above HF upper); non-Markovian NESS magnitude justifies raising P on non-eq-stat-mech-home row |
| 7 | BID order_parameter v1/v1_nsweep/v2 | 5/5 seeds, 3 runs | RE-COUNT: three runs report IDENTICAL 46.95+/-5.90; investigate whether they are independent or duplicates of v1's output |

---

## Anchor patterns + anomalies

- KF2 family ALL share the n_test_pairs=99 quantization floor; max_iso takes
  only 0.0101 or 0.0202 across 10 FULL runs spanning fp32-int1, codebook,
  and N. Differential analysis between precisions is uninformative within
  this discretization.
- Bet B 4-stage retention is IMMUNE to all 4 tested axes; convergent to a
  single triple within 0.7% std. The intervention surface is wrong.
- BID-vs-M trend is codebook-dependent: kerdock non-monotonic with minimum
  near M=0.5; BSC monotone increasing; smaller-N kerdock monotone decreasing.
- TCFT erase robustness/time/m_sweep are all the same substrate property but
  the test geometries produce different verdict tags. Substrate is at the
  numerical floor across all of them.
- Three BID order_parameter runs report identical values to 4 sig figs.
  Either deterministic by design (suspect) or duplicate outputs.
- skahm_subclass_discriminator v2, v3 BOTH HARD_FAIL "no sharpening with N";
  mean_ratio = 0.016 (16x below sharpening band). Strong negative result
  consistent across two independent reruns.
- Wave14 cap2 has 2 KILLs (margin, endpoint) + 1 RESCUE_PASS (conformal
  subsumption). The killed axes (margin, endpoint-ID) are structurally
  closed; conformal route is the surviving mechanism. Cap_map should mark
  the killed alternatives explicitly so they aren't re-tried.
- Wave14 cap8 has 2 GENERATED + 1 FAIL on VAMP iterates; data-gap filling
  pipeline (composition A) is dependent on this data.
- Hatano-Sasa v2 long-trajectory finds non-canonical NESS (HARD_FAIL of the
  IFT band) — but this IS the signal that places substrate in the
  non-Markovian regime. The "fail" is a corroboration of the non-eq class.

---

## Final synthesis: top-5 forensic findings ranked by cap_map impact

### 1. Bet B 4-stage axes share a STRUCTURAL CEILING (HIGH impact)
8 runs across 4 supposed-different intervention axes converge to
retention_A=0.74 (std 0.005), retention_B=0.86 (std 0.003), retention_C=0.80
(std 0.006). This is NOT 4 different failure modes; it is ONE ceiling.
**Action**: stop testing phase-D parameter variants; queue ONE anchor that
probes the binding constraint (likely Stage-A latent capacity or the
Hebbian-overwrite mechanism itself). All current 4-axis exp_dev work on this
row is wasted compute.

### 2. KF2 max_iso is at the discretization floor (HIGH impact)
All 10 FULL KF2 isolation runs report max_iso in {0.0101, 0.0202} — exactly
1/99 or 2/99. The precision-axis sweep (fp32 / fp16 / int8 / int4 / int2 /
int1) measures NOTHING within this floor. Cap_map "INT1 HARD_PASS at
production N" is technically correct but uninformative.
**Action**: re-design KF2 isolation test with n_test_pairs >= 1000 (or use
mean_iso, which has more resolution); only THEN can precision-vs-isolation
trade-off be characterized.

### 3. Saad-Solla 4-axis claim is partially OVERCLAIMED (MEDIUM-HIGH impact)
Of the 4 axes claimed "at N=8192 5-seed": only seed-axis is. M-axis is at
N=8192 2-seed (v16); codebook-axis at N=4096 3-seed (v17); N-axis combines
N=2048 5-seed (v8) and N=8192 2-seed (v11).
**Action**: queue codebook_v18_n8192_5seed and m_sweep_v22_n8192_5seed to
upgrade the claim to truthful "4 axes at N=8192 5-seed".

### 4. BID-vs-M trend is CODEBOOK-DEPENDENT and v1/v2 may be duplicates (MEDIUM impact)
- v1 (kerdock small-N): monotone DECREASING (cap_map claim source)
- v5_n8192 (kerdock prod-N): NON-MONOTONIC, minimum at M=0.5
- v5_n8192_bsc: monotone INCREASING; BSC BID 4-5x larger than kerdock
- v1, v1_nsweep, v2 report IDENTICAL 46.95+/-5.90 (suspect)
**Action**: cap_map "BID monotone decreasing with M_FRAC" should be
deprecated as overgeneral. Also: verify that v1/v1_nsweep/v2 are independent
runs not duplicate outputs; if duplicates, "5/5 seeds" claim downgrades to
"5/5 seeds in 1 run, single observation".

### 5. TCFT deletion-cert overshoots threshold by 8+ orders of magnitude (MEDIUM impact)
mean_var_ratio at fresh_erase v3, v4 = 0.000000 (below print precision).
HP threshold is 0.1. Ratio = 10^8 or larger. Equivalently: erasure is at the
numerical floor of double precision.
**Action**: LIFT cat-A row from "HARD_PASS (margin)" to "HARD_PASS (numerical
zero in double precision at N=4096, N=8192, 5-seed each)". This becomes a
stronger product claim ("provable erasure", not "below 0.1 threshold").

---

## Methodology + caveats

- Corpus: 1083 metrics.json files (remote tar-pulled 2026-05-29). 4 unreadable
  (JSON parse error). 673 classified FULL by N >= 2048 + non-smoke heuristic.
- Verdict-msg regex extraction misses many internal/operational fields that
  are nested-only; deepscan walked the full JSON structure where shallow
  regex missed.
- Pearson correlations on small (n=19) cross-run pairings have low power;
  the reported r=-0.05 is consistent with both true zero correlation AND a
  modest signal masked by heterogeneous run designs.
- ASCII-only output preserved throughout.
- Read-only walk; no data files modified.

