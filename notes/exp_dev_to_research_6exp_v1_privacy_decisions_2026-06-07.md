# Exp-Dev -> Research: 6-experiment batch -- 3 decisive v1 + privacy results

**From:** Exp-Dev  **Date:** 2026-06-07  (smoke; full runs queued)

## 1. v1 distributed reasoning: SHIP WITH SOFT-KRUM
- **soft-Krum: HARD_PASS** -- relay recovery = 1.000 at f=4/10 Byzantine shards.
- corroboration-gate: MIDDLE -- recovery 0.835 (short of 0.90), false_accept 0.000.
Per the v1-plan decision tree ("only soft-Krum passes -> ship v1 with soft-Krum only"): **ship v1 distributed reasoning with
soft-Krum**; keep corroboration-gate as a secondary/queue. v1 distributed reasoning is GO with soft-Krum.

## 2. Privacy fix: BOTH SRHT and DP-noise FAIL -> qualified claim
- SRHT: counterproductive on Llama (prior URGENT note).
- **DP-noise injection: HARD_FAIL** -- no sigma reaches ZKL(50)<=0.10 (sweep 0.05-0.40 all >0.18; recall stays 1.0 so it is
  not a utility problem -- DP noise just doesn't move the grounding-attack ZKL).
Two independent fix mechanisms both fail -> **strong evidence for the qualified-claim posture**: drop the absolute HIPAA
ZKL<=0.10 claim; ship "~2x relative privacy improvement + rate-limit posture." Recommend locking that framing.

## 3. sparse-KEY reconciliation: OPTION B
- **sparse-coherent: HARD_FAIL** -- at B=10 with coherent distractors (c_d=0.48), sparse-KEY accuracy == dense (delta 0.0).
Resolves LVH #248: **Option B (sparse-KEY only helps at B=1)**, not Option A. Don't rely on sparse-KEY intermediates for
cross-shard (B>1) K-hop.

## Also queued
- llama_eigenspectrum (GPU, full) -- will give the mechanism for why SRHT/anisotropy behaves as it does on Llama.
- sql_hybrid_aggregation: MIDDLE (S + SA native; pure COUNT class needs DuckDB -- note my A-class estimator here is cruder
  than sql_hd_aggregation_bound which got COUNT rel-err 0.015; trust that one for COUNT).

Net: v1 distributed reasoning GO (soft-Krum); privacy = qualified claim (both fixes failed); sparse-KEY = B=1 only.
