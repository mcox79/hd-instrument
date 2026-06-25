# Pre-registration: substrate_refuse_gate_nonlinear_readout_v2_full

**Date:** 2026-06-25
**Anchor:** substrate_refuse_gate_nonlinear_readout_v2_full
**Queue:** local_cpu_queue
**Seeds:** [11, 13, 19] (cross-cell consistent with today's batch)
**N_DIM:** 256, **N_PRESENT:** 60, **N_QUERY:** 120, **PARAPHRASE_NOISE:** 0.10
**BETA_GRID:** [10.0, 20.0, 40.0, 80.0, 160.0]
**C_GRID:** 0.10..0.95 step 0.05
**ALPHA:** 1.0 (softmax)

## Promotion context

USER 2026-06-25: the v1 smoke (`substrate_refuse_gate_nonlinear_readout_v1`) HARD_PASS'd synthetic with gap_refuse=1.000,
accept_drop=0.000 @ (beta=10, c=0.15), n_seeds=1 -> cannot tier-rule chain-grade per BIAS-14. v2 re-runs synthetic with
n_seeds=3, prospective bands locked + per-seed cv discipline. The v1 "real bge held-out q54-q65" full path is NOT
re-dispatched here -- that's a separate question (real-data envelope vs synthetic-mechanism); v2 closes the chain-grade
question on the synthetic-mechanism arm so substrate has a 4th refuse-gate primitive in the basis.

## Strategic significance

If chain-grade: substrate basis gains a 4th refuse-gate primitive (alongside audit-based + graph-health + CSP). The
mechanism is reusable for ANY retrieval pipeline: max-softmax-weight over candidate scores is the refuse signal; threshold
the concentration. Composes with intent-classifier + audit-device + KV-store.

## Mechanism (unchanged from v1; per `_spread_attention_harness`)

- present = N_PRESENT cluster centroids (bipolar; cluster_size=1 = i.i.d.)
- paraphrased queries (in-coverage) = centroid + 10% bit-flips (near-duplicate; should retrieve)
- absent queries (gap) = novel bipolar (should be refused)
- per (beta, c):
  - softmax(beta * cosine_scores) yields W; max-weight is the concentration signal
  - gap_refuse = fraction of absent with max-weight < c (correctly refused)
  - accept_drop = 1 - fraction of paraphrased with max-weight >= c (correctly accepted)
- per seed (synthetic harness uses np.random.default_rng(seed)), per (beta,c) -> {gap_refuse, accept_drop, absent_spreads}.

DISCRIMINATING REGIME (verify-the-referent at runtime): absent must SPREAD (median max-weight < 0.9 AND verify_spread
returns spreads=True). NON-discriminating regime = NON_TEST.

## Pre-registered bands (LOCKED at module init via assert)

### HARD_PASS_CHAIN_GRADE
- gap_refuse mean >= 0.95 (across 3 seeds at best (beta,c))
- accept_drop mean <= 0.05
- gap_refuse cv <= 0.05 (across 3 seeds at SAME (beta,c))
- all 3 seeds must satisfy discriminating regime at this (beta,c)

### HARD_PASS_PARTIAL (= MIDDLE_BAND)
- gap_refuse mean 0.80 - 0.95 AT a discriminating (beta,c)
- OR gap_refuse cv 0.05 - 0.10 with mean >= 0.95
- accept_drop mean <= 0.10

### HARD_FAIL
- no (beta,c) reaches gap_refuse >= 0.80 AND accept_drop <= 0.10 across all 3 seeds discriminating

## Q-discipline

v1 reported gap_refuse=1.000 / accept_drop=0.000 -- both at the Q-saturation rail. With 3 seeds + per-seed noise, expect:
- Some seeds may hit 1.000 (small N_QUERY/2=60 absent + favorable noise realization)
- Some may hit 0.97-0.99 (typical synthetic discrimination at beta=10-40)
- cv should be tight (synthetic absent = i.i.d. random; well-separated from clustered paraphrased)

If ALL 3 seeds report exactly 1.000 at the same (beta,c), the synthetic regime is too easy -- still chain-grade by bands
but tier-owner (Skunkworks) may demote to MEASURED_MECHANISM (synthetic absent = i.i.d.-random easy regime; "real bge
held-out" remains the harder question).

## Smoke-vs-full discipline

Smoke (1 seed, seed=11) vs full (3 seeds [11,13,19]) match on EVERY capacity-sensitive dimension:
- N_DIM = 256 (both)
- N_PRESENT = 60 (both)
- N_QUERY = 120 (both)
- PARAPHRASE_NOISE = 0.10 (both)
- BETA_GRID = same (both)
- C_GRID = same (both)
- ALPHA = 1.0 (both)

Only difference: number of seeds aggregated. No regime sign-flip possible.

## Timeout estimate

Smoke wall: ~1s (per v1 timing; pure numpy, n=256 / 60 present / 60 absent / 5 beta x 18 c = 90 ops).
formula: timeout_s = ceil(1.5 * 1 * 1^1.5 * 3) = 4.5s
Plus harness + checkpoint overhead: **timeout_s = 300** (5min; very conservative).

## PROT compliance

- PROT-018: anchor has no `_n<N>` suffix; rule does not apply.
- PROT-019: same.
- PROT-020: routed to local_cpu_queue; rule does not apply.
- PROT-021: timeout 300s < 14400s; rule does not apply (but cell imports `_seed_checkpoint` anyway).

## Symmetric verify rail

Verdict reports:
- per-seed best (beta,c) + gap_refuse + accept_drop
- per-(beta,c) aggregate mean + cv across seeds
- spread_report (absent median max-weight per beta — the discriminating regime ground-truth)
- all_discriminating flag per operating point (all 3 seeds must discriminate)

## Cross-cell discipline

Same as Cell 1: ASCII; substrate-only (no LLM forward calls); per-arm metrics in verdict_msg per Fix #28; bands at module
init; seeds [11,13,19]; META_M6 (NAIVE baseline = "linear cosine-tau M1 already HARD_FAIL'd at gap_refuse >= 0.95" =
DERIVED from V1 6th-module M1 historical result, NOT copied from a different regime).
