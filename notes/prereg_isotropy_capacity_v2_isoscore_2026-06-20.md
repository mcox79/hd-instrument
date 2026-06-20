# PRE-REG: isotropy_capacity_v2_gpu_v1 (#6) -- substrate Hebbian capacity across encoders predicted by INDEPENDENT IsoScore (non-circular), beating SVD d_eff

**Anchor:** `isotropy_capacity_v2_gpu_v1`  **cell:** experiments/exp_isotropy_capacity_v2_gpu_v1.py (committed 7a883fe1)
**Tier:** TIER-2 substrate-capability cert candidate. **Compute:** GPU (encode 6 encoders) + CPU (IsoScore/capacity).

## Hypothesis (pre-registered, symmetric)
Substrate Hebbian auto-associative CAPACITY (M_crit) across encoders is predicted by embedding ISOTROPY -- measured by an
INDEPENDENT IsoScore (covariance-eigenvalue spectral-uniformity in [0,1], 1=uniform spectrum, 0=rank-1-collapse) -- and
isotropy predicts capacity BETTER than SVD d_eff (participation ratio). Resolves the effrank d_eff honest-negative
(capacity ~ d_eff REFUTED) by identifying isotropy as the distinctive axis.

## Pre-flag-B fix (the load-bearing non-circularity)
isotropy = INDEPENDENT IsoScore (covariance-EIGENVALUE measure), NOT `1-mean_pairwise_cos` (which IS the Hebbian crosstalk
-> "isotropy predicts capacity" would be near-tautological). IsoScore depends on the covariance eigenvalue SPECTRUM, not
pairwise cosines -> genuinely independent predictor. My impl in-cell; Testbed's independent IsoScore (b2479cc8,
Skunkworks-verified-correct) is the 2nd-witness -> per-encoder cross-check at landed-VET (defense-in-depth vs an impl bug
silently reducing to crosstalk).

## Pre-registered bands (sacrosanct both ways)
- **HARD_PASS:** Pearson(IsoScore, log M_crit) > 0.80 across >=5 encoders AND Pearson(IsoScore,cap) > Pearson(d_eff,cap)
  (isotropy beats d_eff) AND c-per-encoder spread (max/min) <= 5 (no cleanup-boost-artifact) AND worst seed-CV < 0.5.
- **MIDDLE_BAND:** Pearson(IsoScore, log M_crit) in [0.5, 0.8] OR c-spread in (5,10].
- **HARD_FAIL:** Pearson < 0.5 (isotropy doesn't predict -> a 3rd axis needed) OR Pearson(d_eff,cap) >= Pearson(iso,cap)
  (d_eff predicts as well -> isotropy NOT the distinctive axis) OR c-spread > 10 (cleanup-boost artifact dominates).
- **UP-GUARD (negativity-bias symmetric):** Pearson > 0.99 -> FLAG, verify IsoScore/capacity are not metric-overlapping.
- **CAN-FAIL regime (discriminating):** a SHUFFLED IsoScore-vs-capacity pairing MUST give |Pearson| < 0.5 (else the
  high-Pearson is an artifact of the fit, not a real predictor). [Reported in detail; the live gate is the un-shuffled Pearson.]

## Disciplines applied (the 3 new + standing)
1. capacity-RELATIVE: gate on Pearson over M_crit, never a fixed arbitrary recall@M.
2. run's-OWN-moments: E[<ki,kj>^2] computed per-encoder via D x D gram closed-form (no reference value, no M x M).
3. same-distribution: keys are RAW per-encoder embeddings (no projection here -> the split-discipline is N/A; encoders
   naturally SPAN isotropy: MiniLM/bge high, pythia low). [The projected within-encoder case is the v2 causal anchor below.]
4. c-per-encoder = M_crit_obs / (1/E[<>^2]) REPORTED per encoder (cleanup-boost; flags a c-artifact correlation).

## v2 within-encoder causal anchor (folded, REPORTED)
Correlational (cross-encoder Pearson) + CAUSAL (the #7 finding: pythia-2.8b raw keys [low-iso] -> #7-projected [high-iso]
de-crowds and capacity rises ~125x within a SINGLE encoder). Same axis (isotropy), two independent lines.

## SCHEMA-VET
metrics.json REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, run_mode, detail.pearson_isoscore_vs_logMcrit,
detail.pearson_deff_vs_logMcrit, detail.c_spread_max_over_min, detail.per_encoder, elapsed_s, per_unit.
Per-(encoder,seed) checkpoint (write_partial_key) -> restart-from-checkpoint. import torch first; CUDA-required for full.

## Version-marker
FULL run: 6 encoders (MiniLM, mpnet, bge-large, sentence-t5-base, pythia-160m, pythia-2.8b), M_keys=8000, seeds=1..5.
The EXPECTED run has n_enc>=5 in detail.per_encoder + pythia-2.8b present. Verify-the-referent: data dir + this marker.
