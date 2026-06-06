# Prereg: pp49_hrc_protocol_artifact_nscale_v1_n8192

**Date:** 2026-06-03
**Anchor:** pp49_hrc_protocol_artifact_nscale_v1_n8192
**Script:** experiments/exp_pp49_hrc_protocol_artifact_nscale_v1_n8192.py
**Queue:** remote_cpu_queue (CPU)
**Cap_map row:** PP-49 counterfactual abduction / heteroassociative chains

## Hypothesis

The protocol-artifact boundary (rank-1 ceiling at predecessor-start) holds at N=8192.
Theory: rank-1 ceiling is a geometric property of the substitution algebra, NOT N-dependent.
Expected: predecessor-start cf_cos <= 0.50 for d >= 3 at N=8192 (same as N=4096).
           root-start cf_cos >= 0.90 for d >= 2 at N=8192 (same as N=4096).

## Prior results

- pp49_hrc_depth_parity_discriminator_sweep_v1_n4096: pending (N=4096, depths 1-8, both protocols).
- Research (PP-49 routing v359): depth-5 HARD_FAIL is a MEASUREMENT PROTOCOL ARTIFACT.
  Root-start bypasses rank-1 ceiling: cf_cos >= 0.95 smooth monotone.

## Pre-registered bands

Calibration probe; no prior empirical anchor at N=8192; bands +-50% per policy.

- **HARD-PASS:** predecessor-start cf_cos <= 0.55 for d>=3 (within 10% of rank-1 ceiling 0.50)
               AND root-start cf_cos >= 0.80 for d>=2 at N=8192.
               => N-scale independence of protocol-artifact boundary confirmed.
- **MIDDLE:** pred-start cf_cos in (0.50, 0.70) for d>=3 (partial N-scale dependence).
- **HARD-FAIL:** pred-start cf_cos > 0.70 for d>=3 (rank-1 ceiling absent at N=8192)
               OR root-start cf_cos < 0.50 for d>=2 (root-start also broken at N=8192).

Note: both HARD_PASS or MIDDLE leave PP-49 product narrative intact.
HARD_FAIL would indicate the protocol artifact disappears at N=8192 (unexpected).

## Middle-band outcome plan

MIDDLE: file exp_dev_to_strategy noting partial N-scale dependence; characterize transition range.
HARD_FAIL: characterization complete; protocol artifact is N-dependent; file routing note.

## PROT-018

Anchor _n8192; script N=8192. Verified: `grep "^N = " -> N = 8192`.

## PROT-021

run_mode=full, n_seeds=5. Seed checkpoints keyed with run_mode + max_depth.

## Timeout estimate

Smoke wall: <1s for 2 seeds at N=512.
FULL: N=8192, 5 seeds, 5 depths, N_CHAINS=5, N_BG=M_ACT=409.
Matrix ops: W_cf = N x N float32 = 268 MB; chunked Hopfield (no materialized W).
Estimate: 1.5 * 60 * (8192/4096)^1.5 * (5/2) = 1.5 * 60 * 2.83 * 2.5 = ceil(637.5) = 900s -> 1200s.

**timeout_s = 1200**

## Dependency check

No upstream data dependencies. Script is self-contained (pure numpy).

## Ship rationale

RESUME: script existed but queue_add failed mid-cycle due to API ConnectionRefused.
N-scale validation of PP-49 protocol artifact boundary; establishes N-independence for product narrative.
