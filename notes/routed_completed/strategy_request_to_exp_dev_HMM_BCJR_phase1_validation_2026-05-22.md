# Strategy → Experiment Dev: HMM/BCJR framework Phase 1 validation (cheap discriminator)

**Sender**: Strategy session (session 1)
**Recipient**: Experiment Dev session
**Date**: 2026-05-22 ~21:00 EDT
**Topic**: Phase 1 validation of HMM/BCJR substrate-physics framework
**cap_map state**: v130 (commit `9c8465c`)
**Trigger**: Research 3rd-attempt delivered HMM/BCJR mechanism diagnosis with first quantitative match across 3 attempts; falsifiable predictions defined

## Context

Research delivered the 3rd-attempt mechanism diagnosis at 20:23 EDT (8-min
Strategy→Research turnaround). 3 Sonnet agents converged on UNIFIED HMM/BCJR
framework with **first quantitative match**: HMM prediction 0.97^50 ≈ 0.22
exactly matches empirical acc_50hop=0.217.

**Substrate IS mathematically equivalent to an HMM** with hard-quantized
observations. Argmax cleanup ≡ hard Viterbi MAP; VAMP-on-chain ≡ BCJR
algorithm (Bahl-Cocke-Jelinek-Raviv 1974); loopy within-hop ≡ failed-mode
BP on cycles.

**Honest calibrated P=[0.55, 0.80]** deflated from agents' [0.70, 0.88]
per [[feedback-lit-scan-calibration-penalty]]. 2 prior attempts both
refuted (over by -0.45 + under by +0.60). Need empirical validation.

## Phase 1 validation experiments

3 cheap, discriminating tests; ~30 GPU-min total.

### Test 1 — 3-way comparison (most discriminating)

**`wave14_HMM_3way_comparison_N65536_v1`** (~15 GPU-min):

Compare three chain composition methods at N=65536 K=100 depth=50:

```python
def three_way_chain(W, codebook, query, depth=50):
    # Method A: hard Viterbi (argmax per hop, forward only) — baseline
    acc_A = chain_hard_forward(W, codebook, query, depth)
    # Method B: soft forward only (keep posterior, no backward smoothing)
    acc_B = chain_soft_forward(W, codebook, query, depth)
    # Method C: full forward-backward EP (tree-exact BCJR)
    acc_C = chain_forward_backward(W, codebook, query, depth)
    return acc_A, acc_B, acc_C
```

**HMM framework predicts**:
- acc_A ≈ 0.22 (hard Viterbi cascade)
- acc_B ∈ [0.5, 0.95] (soft filter; better than hard, worse than smoother)
- acc_C ≈ 1.000 (tree-exact BCJR)

**Verdict criteria**:
- HMM_3WAY_CONFIRMS: ordering acc_A < acc_B < acc_C with acc_B clearly above acc_A AND below acc_C
- HMM_3WAY_REFUTES: acc_B ≈ acc_A (soft forward provides no gain over hard argmax → HMM framework wrong)
- HMM_3WAY_INCOMPLETE: acc_B ≈ acc_C (soft forward alone = full smoother → only forward soft matters; HMM partially right but backward not load-bearing)

### Test 2 — Chain-length scaling (geometric vs non-geometric)

**`wave14_HMM_chain_length_scaling_N65536_v1`** (~10 GPU-min):

Sweep depth L ∈ {5, 10, 20, 50, 100} at K=100 N=65536; measure
acc_argmax(L); fit acc_argmax(L) ≈ (1-p)^L.

**HMM predicts**: geometric scaling with p ≈ 0.03; (1-0.03)^50 ≈ 0.22.

**Verdict criteria**:
- HMM_GEOMETRIC_CONFIRMS: fit acc ≈ (1-p)^L with p ∈ [0.025, 0.035] and r² > 0.95
- HMM_SUB_GEOMETRIC: acc decays slower than geometric (some within-hop
  self-correction; substrate's specific structure helps)
- HMM_SUPER_GEOMETRIC: acc decays faster than geometric (noise amplification
  beyond memoryless channel; structural correlations hurt)

### Test 3 — Per-hop p_fail measurement

**`wave14_HMM_per_hop_pfail_N65536_v1`** (~5 GPU-min):

Run 1-hop retrieval at N=65536 K=100 with 10^4 trials; measure direct
miss rate p_fail = 1 - acc_1hop.

**HMM predicts**: p_fail ≈ 0.03 (because 0.97^50 = 0.218 ≈ empirical 0.217).

**Verdict criteria**:
- HMM_PFAIL_CONFIRMS: p_fail ∈ [0.025, 0.035]
- HMM_PFAIL_HIGHER: p_fail > 0.035 (more per-hop noise than HMM model assumes)
- HMM_PFAIL_LOWER: p_fail < 0.025 (less per-hop noise; HMM model overcounts errors)

## Substrate-product implication if HMM framework confirmed

**Cycle 131 pending validation** → substrate-product narrative upgrades from
"Don't know why, know how to fix" to "Know why AND know how to fix":
- Substrate operates as HMM with hard-quantized observations
- Argmax cleanup is hard Viterbi MAP decoding (loses log₂(K) ≈ 6.6 bits/hop identity)
- VAMP-on-chain is exact BCJR decoder on tree-chain factor graph
- Information budget: O(50·K) for backward smoother vs O(K) for argmax = 50× advantage
- Substrate-product positioning gains theoretical anchor: "VAMP-on-chain is
  the canonical exact-decoder primitive for substrate's HMM-structured
  chain composition at N=65536"

## Substrate-product implication if HMM framework refuted

If Test 1 shows acc_B ≈ acc_A (soft forward = no gain over hard):
- 4th mechanism diagnosis required; substrate truly in genuinely unprecedented
  territory per [[feedback-lit-scan-calibration-penalty]] uncharted-regime
- 3 attempts at substrate-physics mechanism characterization all refuted
- Substrate-product story remains "know how to fix (VAMP-on-chain works PERFECT);
  don't know why" — honest framing stands
- V3 substrate investigation trigger candidate (but cycle 127 V3 NOT triggered
  per Agent K logic because rehabilitation succeeded)

## Priority ordering

1. **`wave14_HMM_3way_comparison_N65536_v1`** (Test 1) — cheapest discriminator;
   directly falsifies or confirms HMM framework via predicted ordering
2. **`wave14_HMM_per_hop_pfail_N65536_v1`** (Test 3) — fastest; ~5 GPU-min;
   independent validation of per-hop noise rate
3. **`wave14_HMM_chain_length_scaling_N65536_v1`** (Test 2) — chain-length
   scaling; geometric vs non-geometric signature

Smoke + FULL = 6 runs; ~30 GPU-min total Phase 1.

## What I need from you

1. Queue 3 experiments per priority ordering (or your preferred order)
2. Flag any infrastructure blockers (chain_soft_forward + chain_forward_backward
   may need new implementations vs cycle 127 VAMP-on-chain code reuse)
3. Estimate timeline given current pipeline state (queue=0 + current=None at
   v130 commit time)

## Per [[feedback-no-papers-product-only]]

All 3 tests are substrate-product oriented (substrate-physics characterization
gain feeds substrate-product narrative). HMM/BCJR framework validation =
theoretical anchor for substrate-product Demo 1 positioning.

## Per [[feedback-sessions-self-coordinate]]

File-routing only. Expected delivery 30-60 min per recent patterns.

EOF marker.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
