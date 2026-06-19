# Pre-registration: qe2_coherent_multihop_v1_n4096

**Date**: 2026-05-29
**Anchor**: qe2_coherent_multihop_v1_n4096
**Queue**: remote_cpu_queue
**Script**: experiments/exp_qe2_coherent_multihop_v1_n4096.py
**Research source**: notes/research_coherent_multihop_qe2_v278_2026-05-29.md
**Parent**: exp_wave14r_multihop_K100.py (chained-cleanup baseline)

## Hypothesis

Propagating a top-K soft mixture of codewords through multi-hop factbase operations
-- without intermediate argmax until the final depth -- escapes the cluster-trapping
plateau (d=25-50 acc ~0.22 chained-cleanup baseline) by maintaining the cluster as
a superposition rather than committing to one member per hop.

Design: Option 1 top-K soft mixture (research note section c).
  - At each hop: topk(entity_scores, K_MIX=16), softmax(beta=1.0 * topk_vals), form N-dim mix
  - Factbase readout: s_new = sign_quantize(M * (mix * relation_atom))
  - Final argmax ONLY at depth d

## Config

| Parameter | Smoke | Full |
|-----------|-------|------|
| N | 512 | 4096 |
| K_entities | 40 | 100 |
| K_relations | 5 | 20 |
| NUM_FACTS | 30 | 100 |
| K_MIX | 16 | 16 |
| beta | 1.0 | 1.0 |
| depths | [5,10,25,50,100] | [5,10,25,50,100] |
| n_trials | 30 | 50 |
| seeds | [17,23,31] | [17,23,31] |

## Pre-registered envelope-fail-bands (smoke, gating depth d=50)

| Depth | HARD_PASS (>=) | MIDDLE_BAND | HARD_FAIL (<=) |
|-------|----------------|-------------|----------------|
| d=10 | 0.92 | 0.75-0.92 | 0.75 |
| d=25 | 0.80 | 0.50-0.80 | 0.50 |
| d=50 | 0.65 | 0.35-0.65 | 0.35 |
| d=100 | 0.50 | 0.25-0.50 | 0.25 |

**Gating depth**: d=50. Outcome at d=50 determines HARD_PASS / MIDDLE_BAND / HARD_FAIL.

**Coherent must outperform baseline**: non-trivial pass requires coherent d=50 > cleanup d=50 (~0.22).

## Outcome plans

- **HARD_PASS (d=50 acc >= 0.65)**: cluster-trapping escaped. Ship FULL N=8192 5-seed GPU anchor.
  Cap_map row multi-hop cliff: 🔬 -> 🟡 (candidate). Notify via status_log CRITICAL.
- **MIDDLE_BAND (d=50 in 0.35-0.65)**: partial rescue. Sweep K_MIX in {8, 32} and beta in {0.5, 2.0}
  via second smoke. Gate FULL on second smoke result.
- **HARD_FAIL (d=50 acc <= 0.35)**: coherent multi-hop fails cliff. Ship Option 3 spectral
  diagnostic (exp_dev_handoff anchor 3). If spectral also fails, close multi-hop row red.

## Timeout estimate

Smoke wall time: estimated 120-300s (N=512, 3 seeds, 5 depths, 30 trials, no CUDA).
Formula: 1.5 * 300s * (4096/4096)^1.0 * (3/3) = 450s upper bound.
Safety margin x10 for factbase overhead + runner latency + cold start: 4500s.
PROT-019 floor for _n4096 = 14400s.
**timeout_s = 14400**

## N-suffix binding (PROT-018)

Anchor name contains `_n4096`. Production config: N_FULL = 4096. Binding satisfied.

## Formula self-tests (PROT-019)

1. N_FULL == 4096 (asserted at script top).
2. softmax([2.0, 1.0, 0.0])[0] ~ 0.665, sum = 1.0 (tested in _instrumentation_selftest).
3. Coherent K=1 at beta=10 is valid (not crash; result is bool) -- tested.
4. Per-seed runner returns all expected keys including "coherent", "cleanup", depth keys.
5. Verdict logic: HARD_PASS when d=50 >= 0.65; HARD_FAIL when <= 0.35; MIDDLE_BAND otherwise.
   Self-tested with 4 known-good cases (see _selftest_verdict).

## Prior work context

- 5 prior chained-cleanup rescue attempts (Entries 121, 125, 131, 134, 137) all failed (~80% refutation)
- Entry 155: cluster-trapping 8/8 constraint signature at d=50 acc ~0.22
- Entry 156: retraction framework 22% fixed-point fraction
- This is the FIRST attempt that architecturally inverts the per-hop argmax assumption
- P_deflated(smoke HARD_PASS) = 0.40 per calibration penalty (research note section m)
