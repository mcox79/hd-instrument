# KG retrieval (d, sigma) phase sweep — pre-spec for envelope extension

**Date:** 2026-06-25 (pre-spec; not yet authored)
**Driver:** Cell B (substrate_KG_capacity_sweep_M_10k_100k_1M_v1) landed MM tier with cliff at M=50k for d=768 sigma=0.1. To extend KG envelope toward M=100k or M=1M, need (d, sigma) phase sweep.
**Status:** Pre-spec only. NOT dispatching unless USER approves. Adds operating-envelope evidence; doesn't change basis story.

## Theory

Capacity in HRR / sparse projected KV scales roughly with d² / (sigma² · structural-overhead). Cliff at M=50k for d=768 sigma=0.1 implies that doubling d quadruples capacity, AND halving sigma quadruples capacity. So:

| d | sigma | Predicted cliff M (rough) |
|---|---|---|
| 768 (Cell B baseline) | 0.10 | 50k (verified) |
| 768 | 0.05 | ~200k |
| 1536 | 0.10 | ~200k |
| 2048 | 0.10 | ~350k |
| 2048 | 0.05 | ~1.4M |
| 4096 | 0.05 | ~5.6M |
| 4096 | 0.02 | ~35M |

These are rough scaling predictions; sweep determines actual.

## Cell spec (when dispatched)

**Anchor:** `substrate_KG_capacity_sweep_d_sigma_phase_v2`
**File:** `experiments/exp_substrate_KG_capacity_sweep_d_sigma_phase_v2.py`
**Routing:** overnight_queue (GPU; per Fix #24 use torch.cuda actively)

### Sweep grid

| d \ sigma | 0.10 | 0.05 | 0.02 |
|---|---|---|---|
| 768 | (verified by Cell B) | TEST | TEST |
| 1536 | TEST | TEST | TEST |
| 2048 | TEST | TEST | TEST |
| 4096 | TEST | TEST | TEST |

12 (d, sigma) combinations. For each, find the M cliff via binary search:
1. Start at M_init = predicted cliff per scaling
2. If r@1 ≥ 0.50 at M_init, double M; else halve
3. Stop when r@1 crosses 0.50 ± 0.05 OR when binary search narrows to ±10% of cliff
4. Report cliff_M, r@1 at cliff, r@1 at cliff/2, r@1 at cliff*2, W storage at cliff

### Bands

- **HARD_PASS_M_1M_envelope_identified**: at least one (d, sigma) combination achieves r@1 ≥ 0.70 at M=1M
- **HARD_PASS_M_100k_envelope_identified**: at least one (d, sigma) combination achieves r@1 ≥ 0.70 at M=100k
- **MEASURED_MECHANISM_envelope_mapped**: cliffs identified across all 12 points; predicted scaling validated/invalidated
- **HARD_FAIL_OOM_GPU_LIMIT**: GPU memory exhausted at some d (likely d=4096 sigma=0.02 with M=10M); report the M-ceiling for each (d, sigma)

### Config

- Same encoder family as Cell B (dense projected KV; M-independent O(d²) superposition)
- 3 seeds [11, 13, 19] for cv
- GPU required (per Fix #24)
- ASCII only; substrate-only

### Expected outcome

Likely findings:
- Predicted scaling (d² / sigma² · constant) probably holds within 2× factor
- Cliff at M=1M is achievable at d=2048 sigma=0.05 OR d=4096 sigma=0.10 (per scaling table)
- GPU memory becomes the constraint at d=4096 sigma=0.02 with M=10M+
- Optimal (d, sigma) for a given M target identifiable

### Strategic significance

Closes the operating-envelope question for KG retrieval: substrate-product can be positioned as "M=10k-class for d=768; M=1M-class for d=2048 or higher" with empirical evidence at every regime. Removes the open question "could the substrate hold a million facts?"

### What this DOESN'T do

- Doesn't extend Stage 3 integrated audit-device demo to M=1M — the demo at M=10k is already chain-grade at this regime; a M=1M integrated demo would need the (d, sigma) operating point this cell finds, plus other primitive envelopes verified at the new (d, sigma)
- Doesn't address Wave D anisotropic encoder question (Cell H' v2b in flight does this)
- Doesn't address Barrier 1 multi-hop reopening via Path C (Cell H' v2b also addresses this)

## When to dispatch

When user approves OR when basis-finalization arc completes (after Cell H' v2b lands + Skunkworks batch tier-rules + capability assessment finalizes) AND user wants KG envelope extension as next major investment.

Estimated compute: 12 (d, sigma) × ~10 M values (binary search) × 3 seeds × GPU time. Probably 1-3 hours wall on RTX 4060 Ti per Cell B timing.

— Research (Director)
