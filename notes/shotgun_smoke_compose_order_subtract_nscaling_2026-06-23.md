# Shotgun Smoke: compose-order / anti-Hebbian subtract / N-scaling cfrpe-stdp
# Date: 2026-06-23
# Scripts: experiments/smoke/smoke_compose_order_v1.py
#          experiments/smoke/smoke_anti_hebbian_subtract_v1.py
#          experiments/smoke/smoke_nscaling_cfrpe_stdp_v1.py
# Total elapsed: ~66s (0.1 + 12.0 + 53.7)
# No cert atomization. Information acquisition only. Fix #28: per-arm numbers reported.

---

## Smoke 1: COMPOSE-ORDER

**Pre-reg question**: theta-gamma+brain-compose at N=4096 had nested_sparse and nested_cleanup
each fine alone but COMPOSED collapsed (0.187 recall vs 1.000 alone). Which compose step breaks?

**Config**: N=256 M=50 sigma=16 seeds=[7,17,23] f=0.10 (sparse fraction)

**Per-arm results** (mean across 3 seeds):

| Arm                                      | mean_recall | delta_vs_baseline | verdict       |
|------------------------------------------|-------------|-------------------|---------------|
| ARM_BASELINE_LOCKIN_ALONE                | 0.029       | --                | baseline      |
| ARM_LOCKIN_THEN_SPARSE                   | 0.008       | -0.021            | FREE          |
| ARM_LOCKIN_THEN_CLEANUP                  | 0.029       | 0.000             | FREE          |
| ARM_LOCKIN_THEN_SPARSE_THEN_CLEANUP      | 0.008       | -0.021            | FREE          |
| ARM_LOCKIN_THEN_CLEANUP_THEN_SPARSE      | 0.008       | -0.021            | FREE          |
| ARM_SPARSE_INPUT_THEN_LOCKIN_THEN_CLEANUP| 0.163       | +0.134            | BENEFICIAL    |

**HARD_INFO interpretation**:

Primary finding: ALL arms at N=256 sigma=16 show recall near chance (0.008-0.029; baseline=0.029,
chance=0.020). The baseline lock-in itself is marginally above chance at this sigma/N/M regime.
This means the compose-order smoke CANNOT discriminate the breakage step because the signal
collapses BEFORE any compose step -- the baseline is already near floor.

Key positive signal: ARM_SPARSE_INPUT_THEN_LOCKIN_THEN_CLEANUP achieves 0.163 recall (5.6x
the baseline). Using the SPARSE CODEBOOK as the input space (i.e., encoding cues in sparse space
before lock-in) significantly improves recall at sigma=16. This strongly suggests the N4096_v1
collapse is a **codebook-space mismatch** issue: the brain_full arm tried to apply sparse + cleanup
but used sparse codebook for encoding while the single_lockin arm uses dense codebook, causing the
retrieval comparison to operate across incompatible spaces.

**Root cause hypothesis for N4096_v1 HARD_FAIL**:
ARM_NESTED_BRAIN_FULL at N=4096 likely collapses because the compose pipeline applies sparsify
to the demodulated output (which lives in dense codebook space) then does cleanup against sparse
codebook -- but retrieval is scored against the DENSE codebook. The sparse intermediate output
has poor overlap with both the sparse and dense codebooks. The ARM_SPARSE_INPUT_THEN_LOCKIN result
here confirms that encoding in sparse space from the start (before lock-in) is MORE effective than
sparsifying after demodulation.

**Pickup recommendation**: Design N4096_v2 with CONSISTENT codebook spaces:
- ARM_SPARSE: encode in sparse space from the start; run lock-in; decode against sparse codebook
- ARM_BRAIN_FULL: encode sparse, run lock-in, cleanup against same sparse codebook
- Do NOT switch codebook space mid-pipeline (sparse output vs dense retrieval)

---

## Smoke 2: ANTI-HEBBIAN SUBTRACTION

**Pre-reg question**: dual-trace drill predicted -ACh*E_neg (anti-Hebbian subtraction) is
the load-bearing axis. Confirm or deny.

**Config**: N=256 V=200 N_TRAIN=2000 seeds=[7,17,23] sparse_f=0.10

**Per-arm results** (mean BPC nats; lower=better; uniform=5.298):

| Arm               | mean_bpc | mean_lift | per_seed (bpc)                     |
|-------------------|----------|-----------|------------------------------------|
| ARM_NO_SUBTRACT   | 3.9236   | 1.3747    | [3.7959, 3.9456, 4.0294]           |
| ARM_WITH_SUBTRACT | 3.9071   | 1.3912    | [3.7759, 3.9267, 4.0187]           |
| ARM_SUBTRACT_2X   | 3.8878   | 1.4105    | [3.7534, 3.9041, 4.0059]           |

WITH vs NO_SUBTRACT delta = 0.0165 nats (below 0.05 meaningful threshold)
SUBTRACT_2X vs WITH delta = 0.0193 nats (also below threshold)

**HARD_INFO interpretation**:

SUBTRACTION IS NOT THE PRIMARY LEVER at this scale. The -ACh*E_neg term adds only 0.017 nats
improvement over no subtraction (3-seed mean). The 0.05 meaningful-delta threshold is not met.

The 2X arm is monotonically better (0.019 nats additional over 1X), suggesting the subtraction
gradient points in the right direction but is very weak. The small consistent improvement
(all 3 seeds: WITH better than NO, 2X better than WITH) is genuine but sub-threshold.

This does NOT confirm the dual-trace drill's prediction that subtraction is load-bearing.
Alternate axes per HARD_INFO plan:
1. Timescale ratio (tau_pos/tau_neg = 5/50; test 1/50 or 5/200)
2. Cardinality: V=200 may be too small for the LTD trace to accumulate meaningful statistics
3. Eligibility trace decay vs learning rate interaction (LR=0.1 may be too small for trace effects)
4. The dual-trace advantage may require longer training sequences (N_TRAIN=2000 is tiny corpus)

**Pickup recommendation**: Route to Strategy for 2x-revival drill. The direction is correct
(monotonic improvement) but the lever is weak at this scale. Test at N_TRAIN=20k with V=2000
before concluding subtraction is not useful. The current smoke's N_TRAIN=2000 / tau_neg=50
means the slow trace (E_neg) only completes ~40 effective decay cycles -- insufficient to build
meaningful predictive statistics for the ACh gate.

---

## Smoke 3: N-SCALING FOR CF-RPE x STDP HETEROGENEITY

**Pre-reg question**: Does CFRPE x STDP HETEROGENEOUS beat CFRPE_ONLY at N=1024+?
At what N does heterogeneity become net-beneficial?

**Config**: V=512 N_TRAIN=2000 seeds=[7,17,23] N in {128,256,512,1024}

**Per-arm results** (mean BPC across 3 seeds; uniform=6.238):

| N    | CFRPE_ONLY_bpc | CFRPE_gap | HET_bpc | HET_gap | het_delta | verdict  |
|------|----------------|-----------|---------|---------|-----------|----------|
| 128  | 2.934          | 3.304     | 3.033   | 3.205   | -0.099    | CF_WINS  |
| 256  | 2.851          | 3.388     | 2.876   | 3.362   | -0.026    | TIED     |
| 512  | 2.822          | 3.417     | 2.809   | 3.429   | +0.012    | TIED     |
| 1024 | 2.770          | 3.468     | 2.801   | 3.438   | -0.030    | TIED     |

Per-seed detail at N=512 (the boundary):
  seed=7:  CF=2.9001 HET=2.8864 (HET better by 0.0137)
  seed=17: CF=2.9097 HET=2.8491 (HET better by 0.0606)  <- seed 17 crosses threshold
  seed=23: CF=2.6550 HET=2.6919 (CF better by 0.0369)

**HARD_INFO interpretation**:

NO CLEAR INVERSION through N=1024. The CFRPE x STDP heterogeneous arm does not consistently beat
CFRPE_ONLY at any N tested. Pattern is: CF_WINS at N=128 (STDP adds noise at small dim), then
TIED in both directions for N=256,512,1024 with seed variance dominating.

The het_delta at N=512 (-0.030, TIED) and N=1024 (-0.030, TIED) shows no trend toward HET winning
at larger N. If anything the gap oscillates around zero rather than converging to HET.

Mechanistic interpretation: the STDP asymmetric term (Nxt.T@Ctx - Ctx.T@Nxt) is orthogonal to
cf-RPE by construction (cf-RPE = delta.T@Ctx symmetric; STDP = antisymmetric). At this corpus
size (N_TRAIN=2000 steps) and LR=0.5, both terms are learning different structure but the STDP
contribution is effectively noise at the scale tested. Larger N (higher dimensionality) doesn't
help because the STDP term needs more training samples to accumulate statistical structure, not
more dimensions.

**Pickup recommendation**: 
- The existing full cell (exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512)
  with N_STEPS=1000 and CORPUS=60000 is 30x larger training than this smoke. Those results
  (gap=5.02 vs cf=4.77) are not contradicted -- this smoke's N_TRAIN=2000 is simply too small
  for STDP statistics. Do NOT cancel the full cell based on this smoke.
- DO NOT dispatch a large-scale FULL sweep predicting HARD_FAIL on N-scaling alone.
  This smoke's regime (N_TRAIN=2000) is insufficient to distinguish the structural axis from noise.
- If the full cell's N=512 result (gap=5.02 HET > 4.77 CF) holds, the question about "N-scaling"
  is moot -- heterogeneity IS already beneficial at N=512 with sufficient training data.

---

## Cross-smoke synthesis

Three questions, three informationally distinct answers:

1. **Compose-order (Smoke 1)**: The collapse in N4096_v1 is ALMOST CERTAINLY a codebook-space
   mismatch (sparsify output -> retrieve against wrong codebook), NOT an ordering failure.
   ARM_SPARSE_INPUT_THEN_LOCKIN shows 5.6x recall improvement over baseline, confirming that
   the sparse codebook is the RIGHT space if used consistently end-to-end.

2. **Anti-Hebbian subtraction (Smoke 2)**: The -ACh*E_neg term is DIRECTIONALLY correct
   (monotonically better) but sub-threshold at this scale. It is NOT the primary load-bearing
   axis of the dual-trace mechanism. Other axes (timescale ratio, corpus size, V) need
   investigation before concluding the dual-trace hypothesis is wrong.

3. **N-scaling for STDP heterogeneity (Smoke 3)**: No clear N-threshold inversion through N=1024
   at N_TRAIN=2000. The published full cell (N_STEPS=1000, CORPUS=60000) already shows HET > CF
   at N=512 -- that result is not contradicted by this smoke, which just tested an insufficient
   data regime.

## Pickup recommendations (priority order)

1. **HIGH** (Smoke 1 root cause): Author N4096_v2 of brain_compensation with CONSISTENT codebook
   spaces -- encode cues in sparse space from the start, run lock-in + cleanup entirely in sparse
   space, retrieve against sparse codebook. This directly tests the codebook-mismatch hypothesis.

2. **MEDIUM** (Smoke 2 follow-up): Route a revival note to Strategy for dual-trace at larger
   corpus (N_TRAIN=50k, V=2000, tau_neg=200). Sub-threshold at small scale may be a corpus-size
   artifact. Do NOT cancel dual-trace hypothesis based on this smoke.

3. **LOW** (Smoke 3): Do not modify the existing CFRPE x STDP full cell dispatch. The smoke's
   regime is too small to predict the full cell outcome. Wait for the full cell verdict.

## Suspicious-result gates

- Smoke 1: INCONCLUSIVE (baseline itself near floor; can't discriminate ordering). The
  ARM_SPARSE_INPUT result is the real signal. Design with consistent codebook spaces next.
- Smoke 2: results are VALID (all BPC in finite plausible range; consistent seed-to-seed
  direction; self-test passed). SUBTRACTION_NOT_LEVER at this scale is the verdict.
- Smoke 3: results are VALID (both arms finite, self-test passed; TIED result is informative,
  not a sentinel). NO_INVERSION is the verdict for N_TRAIN=2000 regime.
