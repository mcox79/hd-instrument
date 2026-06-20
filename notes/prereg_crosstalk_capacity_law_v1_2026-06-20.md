# PRE-REG: crosstalk_capacity_law_v1_gpu_v1 (REFRAME of isotropy #6) -- direct crosstalk E[<ki,kj>^2] is the DOMINANT cross-encoder predictor of Hebbian capacity; SVD d_eff AND IsoScore are FAILING CONTROLS

**Anchor:** `crosstalk_capacity_law_v1_gpu_v1`  **cell:** experiments/exp_crosstalk_capacity_law_v1_gpu_v1.py (committed efa2c546)
**Tier (Skunkworks RULING 2026-06-20):** MEASURED_MECHANISM (CERT stays 591), NOT chain-grade unless the chain-eligible bar
(below) is met. Supersedes the isotropy #6 draft (reframe = YES; the non-circularity discipline overturned the isotropy hypothesis).

## Background -- why isotropy #6 was reframed (the discipline producing knowledge)
isotropy #6 hypothesized "embedding isotropy predicts Hebbian capacity," with an INDEPENDENT IsoScore (mean-centered
covariance-eigenvalue) as the non-circular predictor (Skunkworks pre-flag-B). The 160m smoke showed IsoScore is FLAT
(0.86-0.92) and ANTI-correlated with capacity (bge highest IsoScore -> near-lowest capacity). So a genuinely-independent
isotropy measure makes the prediction VANISH -> "isotropy predicts capacity" was circular (confirmed empirically). IsoScore
mean-centers away the shared-mean cone -- exactly the RAW-key crowding Hebbian W=sum k k^T is limited by. Capacity IS the crosstalk.

## Hypothesis (pre-registered, symmetric)
The DIRECT crosstalk moment E[<ki,kj>^2] on RAW (un-mean-centered) unit-normed keys is the DOMINANT cross-encoder predictor
of Hebbian auto-associative capacity M_crit. Two independent mean-centered proxies -- SVD d_eff (participation ratio, the
effrank honest-negative) AND IsoScore -- BOTH FAIL to predict M_crit. The 2-failing-controls is the non-trivial content
(NOT "anything predicts capacity"; specifically the direct crosstalk does, and two plausible rank/spectral proxies fail).

## Pre-registered bands (sacrosanct both ways)
- **HARD_FAIL:** NOT (controls both fail) -- i.e. |Pearson(d_eff,logMcrit)| >= 0.5 OR |Pearson(IsoScore,logMcrit)| >= 0.5
  OR crosstalk-Pearson <= max(|control Pearsons|). (If a control predicts, the finding collapses.)
- **MEASURED_MECHANISM (the floor, expected):** controls both fail (|r|<0.5) AND crosstalk dominant (Pearson > both controls).
  CERT stays 591. This is the honest tier (c not yet bounded; capacity ~ crosstalk is near-mechanistic by the SNR definition).
- **HARD_PASS_CHAIN_ELIGIBLE (-> Skunkworks rules 592):** the above AND n_encoders >= 8 AND Spearman(crosstalk, M_crit) > 0.80
  (robust, NOT MiniLM-leveraged) AND c-spread (max/min) <= 3.0 (c BOUNDED -> near-parameter-free LAW). Skunkworks makes the
  final 592 call; the cell only FLAGS eligibility.
- **UP-GUARD (negativity-bias symmetric):** crosstalk-Pearson > 0.99 -> verify it's not metric-overlap with M_crit.

## c-bounding analysis (the chain-grade crux, per Skunkworks)
Report c-per-encoder (c = M_crit * E[<>^2] = cleanup-boost over the raw-SNR floor) + Pearson(c, D) + Pearson(c, IsoScore)
to test if c is predictable from a measurable encoder property + the raw-vs-projected split (v2 projected-pythia c~17 is the
within-encoder anchor, reported as reference). If c is bounded/predictable -> chain-grade path; if c-spread > 3x -> MEASURED_MECHANISM.

## Disciplines (Orchestrator's referent pre-cleared)
- E[<>^2] + Hebbian W on RAW (un-mean-centered) unit-normed keys (e_sq_gram on Kn=emb/||emb||; W via raw sub). LOAD-BEARING.
- Controls (IsoScore, d_eff) mean-center BY DESIGN -- their blindness to the shared-mean cone IS the evidence.
- run's-OWN-moments per encoder (D x D gram closed-form, no M x M). capacity-RELATIVE (gate on cross-encoder rank-corr).
- Spearman alongside Pearson (de-leverage the single high-capacity point). per-encoder name SANITIZED (dots dropped units in agg).

## SCHEMA-VET (Skunkworks pre-dispatch VET focus: claim-matches-tier, c-per-encoder present, n encoders, Spearman, controls-labeled)
metrics.json REQUIRED_FIELDS: anchor_name, verdict, verdict_msg, run_mode, detail.pearson_crosstalk_vs_logMcrit,
detail.spearman_crosstalk_vs_Mcrit, detail.pearson_deff_vs_logMcrit_CONTROL, detail.pearson_isoscore_vs_logMcrit_CONTROL,
detail.c_per_encoder, detail.c_spread_max_over_min, detail.c_bound_pearson_c_vs_D, detail.n_encoders, per_unit, elapsed_s.
Per-(encoder,seed) checkpoint; per-encoder try/except (a failed encoder skips, doesn't abort). import torch first; CUDA-required full.

## Version-marker
FULL: 13 encoders (MiniLM, mpnet, distilroberta, gtr-t5-base, bge-small, bge-large, e5-base-v2, sentence-t5-base,
pythia-160m/410m/1.4b/2.8b, gpt2-medium), M_keys=8000, seeds=1..5. EXPECTED: detail.n_encoders >= 8 + pythia-2.8b present.
Verify-the-referent at dispatch: E[<>^2]-on-raw-keys (pre-cleared) + on-origin + this marker.
