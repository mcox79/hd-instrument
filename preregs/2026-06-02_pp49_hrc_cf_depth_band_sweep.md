# Pre-registration: PP-49 HRC counterfactual depth-band sweep

**Date:** 2026-06-02
**Anchor:** `pp49_hrc_cf_depth_band_sweep_v1_n4096`
**Queue:** remote_cpu_queue
**Trigger:** Item 4 (I-15 carryover); PP-49 depth-5 HARD_FAIL showing cf_cos=0.028 (expected >= 0.60).
**Priority:** Candidate B from v349 REFILL.

## Capability question

Does counterfactual abduction over heteroassociative chains work at ANY depth {1,2,3,4,5}? Where does the substitution mechanism break down?

## Prior results

- Depth-5 HARD_FAIL: cf_cos=0.028 (expected >= 0.60); cert_rate=1.0, audit_rate=1.0 (certificate passes; retrieval fails)
- Depth-10 FAST_FAIL: exit_code=3221226505 (Windows OOM/stack overrun)

## Pre-registered bands (calibration probe; no prior depth-sweep anchor)

Bands widened to +/-50% per calibration-probe policy (no prior depth-sweep result).

### HARD-PASS
depth-1 cf_cos >= 0.70 (substitution at single hop retrieves the substituted pattern)
AND at least one depth in {1,2,3} achieves cf_cos >= 0.50.

### MIDDLE
depth-1 cf_cos in [0.20, 0.70) -- substitution works at single hop but weakly.
OR depth-1 fails but some deeper depth works (unusual pattern).

### HARD-FAIL
depth-1 cf_cos < 0.20 -- substitution fails even at single hop.
This means the counterfactual abduction mechanism is fundamentally broken at N=4096.
Characterization result: PP-49 counterfactual abduction not viable at production N.

## Middle-band outcome plan

MIDDLE: file exp_dev_to_strategy note identifying what the effective substitution cosine range implies for PP-49 redesign.
HARD_FAIL: characterization complete; PP-49 counterfactual abduction requires architectural redesign; file routing note.

## Smoke gate

Smoke at N=256 showed HARD_FAIL (cf_cos ~ 0.13 at depth-1, ranging from -0.18 to +0.26 across depths).
Multi-scale check at N=1024 also near-zero.
Result is consistent and not a sentinel (cert_rate=1.0, values vary across depths).
FULL run at N=4096 5-seed confirms characterization at production scale.

## N-suffix note (PROT-018)

No `_nN` suffix in anchor name. Production N = 4096. Stated here per PROT-018 note in script header.

## Timeout estimate

Smoke wall: <1s for 2 seeds at N=256.
FULL: N_ACTIVE=4096, 5 seeds, 5 depths, N_CHAINS=8.
Matrix ops: H = N x N float32 = 67 MB; 5 Hopfield retrieve steps per trial.
Estimate: ceil(1.5 * 2 * (4096/256)^1.5 * (5/2)) = ceil(1.5 * 2 * 128 * 2.5) = ceil(960) = 960s -> **1200s**

## Dependency verification

No data dependencies. Pure numpy CPU. Self-contained.
