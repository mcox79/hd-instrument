# Pre-registration: primitive_2_hopfield_cleanup_v1

**Date:** 2026-06-16
**Anchor:** primitive_2_hopfield_cleanup_v1
**Queue:** remote_cpu_queue
**N:** 4096, **Seeds:** 7,17,23, **env_bases:** 3,5,7,11 (R=1155); **GATE-F R-sweep:** R=1155..~111M (factored)

## Scientific question
TIER-3 PRIMITIVE 2: the cleanup/decode layer for residue-FPE (P1 deferred efficient decode here). Quad-head over
the residue codebook: HEAD1 naive max-cos / HEAD2 dense modern-Hopfield (closed-form Ramsauer beta) / HEAD3
sparse-Hopfield (sparsemax) / HEAD4 resonator (OLS-Gram + soft + restarts + reconstruction-accept). Honest
distinctness: HEADS 1-3 are a softness spectrum on the SAME flat O(R) cleanup (HEAD1=HEAD2 at beta->inf); HEAD4 is
the only sub-O(R) FACTORED class. INTEGER-residue scope (continuous bounded by P1 GATE-C1). Per DECISION 226 LOCK +
228 R6/R7/R8.

## Pre-registered bands (tune-free; both-verdict-paths)

**GATE-D (closed-form beta fidelity):** HEAD2 dense-Hopfield at beta SET from Ramsauer Theorem-4 (NOT fitted)
retrieves at acc >= 0.90 low-noise. FAIL = formula-beta does not retrieve.

**GATE-E (gerrymander-guarded Delta_min/noise envelope):** all heads on SAME grid + SAME codebooks; report
best-head-per-regime as a FUNCTION vs the PRE-REGISTERED theory-derived selection map (naive at large Delta_min;
sparse>dense>naive at small Delta_min). Divergence from map = honest theory-gap finding (NOT a re-pick).

**GATE-F (resonator log-scaling = WORK-vs-R; HEAD4):**
- HARD-PASS (P2_LOGSCALING_DEMONSTRATED_INTEGER): log-log work-vs-R exponent < 0.5 (sub-linear, ~log R) AND
  iters-vs-R exponent < 0.5 AND restart-count K not growing AND accuracy held >= 0.90 within 95% CI across the
  R-sweep (R=1155 -> ~111M). Work accounting COMPLETE (R6: per-iter corr+recombine + reconstruction-accept verify;
  OLS Gram pinv amortized once per base). Pre-registered hyperparams (beta, K_max, recon-threshold) FIXED across
  the sweep (no per-scale re-tuning).
- HONEST-BOUNDED (P2_HONEST_BOUNDED): work ~O(R) OR per-scale re-tuning required OR accuracy drops at scale.

**HARD-FAIL:** GATE-D fails (beta formula does not retrieve).

## Calibration rationale
GATE-F is a WORK measurement, not accuracy (per HEAD-4 de-risk VET: accuracy != work; the random-restarts +
reconstruction-accept loop is where a hidden O(R) search could live, so K + iterations are first-class metrics, and
the work-vs-R exponent < 1 is the log-scaling signature). INTEGER scope ONLY (CRT base-independence holds; Kymn
applies). Continuous-magnitude multi-base stays bounded by P1 GATE-C1 (err 1.055 structural break) -- NOT claimed
here. P1 atom UNCHANGED. Tune-free bands locked BEFORE the run (Goodhart guard: per-scale re-tuning = honest-bounded).

## N-suffix section
Production N=4096. GATE-E at env R=1155 (bounded codebook). GATE-F resonator is FACTORED (per-base codebooks
sum(m_b); never the R-codebook) -> the R-sweep to ~111M is cheap (no OOM); GATE-E is the heavier (R-codebook) part
but bounded at R=1155.

## Timeout estimate
Smoke ~ 10s (env R=105, F-sweep R=105/1155). FULL: GATE-E (R=1155 codebook, 6 noise levels, 120 tests, 4 heads,
3 seeds) + GATE-F (5 R-points 1155->111M, 200 tests, factored). No NxN heavy matrix (not the C0/laptop-overheater
class); lighter than P1's GATE-C.
timeout_s = 7200
