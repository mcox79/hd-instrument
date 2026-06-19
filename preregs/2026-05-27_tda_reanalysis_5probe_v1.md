# Pre-registration: TDA re-analysis 5-probe on MoE W configurations

**Date:** 2026-05-27
**Script:** experiments/exp_tda_reanalysis_5probe_v1.py
**Queue:** remote_cpu_queue
**Timeout:** 1800s (30 min)
**Source handoff:** notes/exp_dev_handoff_tda_reanalysis_substrate_W_2026-05-27.md

---

## Hypothesis

TDA's b_0-plateau width provides an INDEPENDENT 4th MoE SHIFT-vs-PARTITION diagnostic
alongside: (1) free-additive top-edge ratio, (2) DMPK SVD-bimodality, (3) spectral gap.
P(adds 4th MoE diagnostic) = 0.38.

## Design

- 5 W configurations: SHIFT_K4, SHIFT_K8, PART_K2, PART_K4, AMBIG_K2
- Generated on-the-fly from seeds using same BSC + outer-product-store pattern as v3
- Pure-PyTorch Vietoris-Rips via cosine-similarity filtration + union-find
- No GPU, no new W generation, CPU-only re-analysis

## Pre-registered bands

| Probe | HARD-PASS | HARD-FAIL | MIDDLE |
|-------|-----------|-----------|--------|
| TDA-A b_0(tau) trajectory | Monotone non-increasing AND plateau at b_0 in {3,4} for finite tau-interval | Non-monotone (b_0 spikes) | Single-value or 2-value plateau only |
| TDA-B longest b_1 bar ratio (substrate/random) | ratio >= 1.5 with p<0.05 | ratio <= 1.1 | 1.1 < ratio < 1.5 |
| TDA-C b_0-plateau width SHIFT-vs-PARTITION agreement | Agreement on >=4/5 cases; width monotonic in inter-expert coupling | Agreement on <=2 cases OR non-monotonic width | Agreement on exactly 3 cases |
| TDA-D long-persistence-bar count vs plateau count | count in {3,4} long bars with lifetime > 0.3*max_lifetime AND <=1 short noise | Continuous distribution (no gap) | count in {2,5} |
| TDA-E predicted plateau heights | max |pred-obs| < 0.05 across 3 plateaus | |pred-obs| >= 0.10 on >=2 plateaus | one plateau off by 0.05-0.10 |

## Joint verdict rules

- TDA_OVERLAPPING_USEFUL: TDA-C HARD-PASS (>=4/5 agreement). P=0.38. Ship as cap_map 4th MoE diagnostic.
- TDA_NOVEL_USEFUL: TDA-B AND TDA-D BOTH HARD-PASS. P=0.10. Open new cap_map row.
- TDA_CONSISTENT_REDUNDANT: TDA-C middle-band or consistent with free-additive (not better). P=0.32. Log as confirmation.
- TDA_INCONCLUSIVE: TDA-C HARD-FAIL or TDA-D continuous distribution. P=0.20. Close algebraic-topo direction.

## Self-test cells

- b_0(tau=0) of fully connected K_n graph = 1 (sanity)
- b_0(tau=max(W)+eps) of any graph = n (all-singleton sanity)
- Persistence of N=6 disjoint K_3 + K_3 (intra=0.9, inter=0.1): b_0 trajectory includes b_0=2 (SHIFT/PARTITION discriminator sanity)
- sim_matrix shape and cosine range validity
- longest_b1 is non-negative finite float

## Implementation notes

- ripser/gudhi NOT available on remote runner; using pure-PyTorch union-find VR implementation
- b_1 estimated via Euler characteristic method (lower-bound; sufficient for ratio test)
- N=512 full / N=128 smoke; M=200 full / M=50 smoke; matches v3 smoke scale
- Remote CPU at BELOWNORMAL priority (structural; no explicit flag needed)

## Expected timeline

- Smoke: < 2 min
- Full: 15-25 min (5 cases x 3 seeds x TDA + random control)
