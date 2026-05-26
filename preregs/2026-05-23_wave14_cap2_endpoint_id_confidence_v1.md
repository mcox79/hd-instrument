# Pre-registration: wave14_cap2_endpoint_id_confidence_v1

**Date**: 2026-05-23
**Exp Dev cycle**: post-v160 Cap 2 STRUCTURAL CLOSURE refill
**Queue**: local_cpu_queue (desktop CPU; cpu_runner_local)
**Script**: `experiments/exp_wave14_cap2_endpoint_id_confidence_v1.py`
**Routing source**: `notes/research_cap2_self_monitoring_rehab_2026-05-23.md` Rescue 1
**Strategy routing**: `notes/strategy_request_to_research_cap2_self_monitoring_rehab_2026-05-23.md`

---

## Hypothesis

Cap 2 self-monitoring confidence is CLOSED for margin/tau-based intrinsic signals (v153 + v160 HARD FAIL). Research recommends Rescue 1 as the highest-leverage experimental rescue: the substrate-novel 28-element endpoint partition (W^L fixed-point trajectory; cycles 137/149/152) carries per-query information that margin/tau discard.

Confidence proxy: map each query's W^L terminal state to one of the discovered endpoint clusters, then compute `p(correct | endpoint_k)` empirically. Wrap with Mondrian/PLCP conformal (partition variable = endpoint cluster index) for distribution-free coverage.

This is the PLCP-anchored (Partition Learning Conformal Prediction, arxiv 2404.17487) implementation of endpoint-id confidence.

---

## Substrate

Autoassociative Hopfield: `W = patterns.T @ patterns / N`. W^L dynamics (L=30 synchronous hops) to convergence on noisy queries. Terminal state identifies the basin of attraction = endpoint cluster.

**N=4096 M=100 L=30 hops n_ref_attractors=20 n_trials_per_stratum=200 n_seeds=3**
**Noise strata**: p in {0.0, 0.05, 0.10, 0.20} (bit-flip on query key)
**Cal/test split**: 50/50 within each (stratum, seed) cell

---

## Memory budget

- W: N x N float32 = 4096 x 4096 x 4 = 64 MB (CPU)
- Attractor centers: 20 x N x 4 = 320 KB (negligible)
- Peak: ~64 MB per seed. Sequential seeds. Well under any CPU budget.

---

## Pre-registered predictions

### HARD PASS (all three required)

1. ROC AUC(correct vs incorrect | endpoint partition) >= 0.65 in at least 3/4 noise strata
2. ECE <= 0.10 after Mondrian conformal wrap on calibration split
3. Substrate-novelty check: ablation AUC delta (substrate endpoint vs random-assignment endpoint) >= 0.10

### HARD FAIL (any one triggers)

- AUC < 0.55 in 3/4 noise strata (no signal) → `CAP2_ENDPOINT_KILL`
- ECE > 0.15 after conformal (uncalibratable) → `CAP2_ENDPOINT_UNCALIBRABLE`
- Ablation delta < 0.10 (not substrate-novel) → `CAP2_ENDPOINT_NOT_SUBSTRATE_NOVEL`

### Partial (AUC signal present but not enough strata)

- `CAP2_ENDPOINT_PARTIAL`: AUC >= 0.65 in 1-2/4 strata

---

## Honest framing

Per Research's calibrated P estimate: deflated P = 0.35. Uncharted regime (no direct published precedent for endpoint-id-conditioned conformal on Hopfield attractor basin). Novel-synthesis cap applied. Passing 3/4 strata is a tight criterion at this P.

**The ablation control is load-bearing**: if substrate adds no information over a random partition on the same data, endpoint-id is a data-artifact not a substrate-novel signal. This test is built into the verdict logic.

---

## Verdicts emitted

- `CAP2_ENDPOINT_PASS` — Rescue 1 confirmed; Cap 2 returns to portfolio in refined form
- `CAP2_ENDPOINT_KILL` — no signal; Rescue 1 refuted; try Rescue 2 (VAMP variance)
- `CAP2_ENDPOINT_NOT_SUBSTRATE_NOVEL` — endpoint-id doesn't add substrate info; Rescue 1 refuted
- `CAP2_ENDPOINT_UNCALIBRABLE` — signal present but conformal calibration fails
- `CAP2_ENDPOINT_PARTIAL` — 1-2 strata pass; conditional on whether Research considers partial sufficient
- `CAP2_ENDPOINT_INCONCLUSIVE` — data error

---

## Citations

- PLCP: arxiv 2404.17487 (Partition Learning Conformal Prediction; partition = endpoint cluster)
- Trust Scores: arxiv 2501.10139 (optional Rescue 6 augment if AUC partial)
- Conformal Bayesian Computation: arxiv 2106.06137 (downstream conformal wraps misspecified posteriors)
- Substrate anchors: cycle 152 PQ_DISCRETE_OTHER (15/28 peaks); cycle 150 ORDER_PARAM_SUB_REGION_STABLE
