# PRE-REG: substrate_adaptive_cfrpe_x_k2_compose_v1

**Filed:** 2026-06-24
**Cell:** experiments/exp_substrate_adaptive_cfrpe_x_k2_compose_v1.py
**Routing:** overnight_queue (GPU, marsh@home)
**Author:** exp_dev
**Strategic context:** A1 joint compose HARD_FAILed with UNIFORM cf-RPE
(K=2 x cf-RPE 7.2690 vs cf-RPE alone 7.1540 -- sub-additive). A3 per-token
ADAPTIVE cf-RPE produced 6.9920 BPC (substrate-as-LM single-arm record).
This cell asks: **does ADAPTIVE cf-RPE compose with K=2 routing where UNIFORM
cf-RPE did not?**

## Hypothesis

UNIFORM cf-RPE applies the same global LR to every batch sample regardless
of prediction error. In a K=2 multi-bank architecture, this drives BOTH banks
toward the SAME features at the SAME rate, causing destructive interference
where one bank's bias bleeds into the other. The result: composition is
sub-additive (K=2 worse than K=1).

PER-TOKEN ADAPTIVE cf-RPE routes plasticity to high-prediction-error samples
(median-normalized clamp [0.25, 4.0]). HYPOTHESIS: this differential weighting
may make compose-with-K=2 non-interfering, because each bank ends up focusing
on its own "high-error" sample subset (which the gate-routing has already
softly partitioned).

If TRUE: substrate has a path to break the bigram floor via adaptive primitives.
If FALSE: the K=2 compose-collapse is mechanistic, not LR-specific -- and
adaptive composition is also blocked.

## Four arms (3 seeds each, full N_DIM_TOTAL=8192, text8 N_TRAIN=100k)

1. **ARM_BASELINE_RANK1_K1_HEBBIAN** -- single bank rank-1 Hebbian
   - sanity rail vs fair_harness reference 7.3065
2. **ARM_ADAPTIVE_CFRPE_K1** -- per-token adaptive cf-RPE @ K=1
   - provenance check vs A3 reference 6.9920 (single-arm best)
3. **ARM_K2_RANK1_HEBBIAN** -- K=2 multi-bank rank-1 Hebbian
   - provenance check vs prior K=2 Hebbian 7.3325
4. **ARM_K2_ADAPTIVE_CFRPE** -- K=2 multi-bank x per-token adaptive cf-RPE
   - **THE TEST ARM**

## Pre-reg HARD bands

### Sanity rails (Fix #28 per-arm; full mode only)

| Arm | Reference BPC | Tolerance |
|-----|---------------|-----------|
| ARM_BASELINE_RANK1_K1_HEBBIAN | 7.3065 | +/- 0.05 |
| ARM_ADAPTIVE_CFRPE_K1 | 6.9920 | +/- 0.05 |
| ARM_K2_RANK1_HEBBIAN | 7.3325 | +/- 0.05 |

If any rail drifts beyond tolerance: **HARD_FAIL_PROVENANCE** (encoder /
methodology mismatch, result not comparable to A3 / K2_v2 references).

### Primary verdict bands on ARM_K2_ADAPTIVE_CFRPE

| Verdict | Condition |
|---------|-----------|
| HARD_PASS (chain-grade-eligible) | BPC <= 6.80 AND beats ARM_ADAPTIVE_CFRPE_K1 by >= +0.10 |
| MIDDLE_BAND | BPC in [6.80, 6.95] (additive but not super-additive) |
| HARD_FAIL | BPC >= 6.99 (no compose benefit; K=2 collapses adaptive too) |
| All arms | cv <= 0.05 across seeds |

### Discriminator regime

The HARD_PASS bar (6.80) is +0.19 BPC below the best known cf-RPE single-arm
(6.9920 from A3) and +0.16 below the prior cf-RPE chain-grade reference 7.0552.
The HARD_FAIL floor (6.99) is just below A3 to ensure that "K=2 brings nothing"
is unambiguous.

## Method discipline

- **Encoding:** word2vec-google-news-300 -> Gaussian-project to N_DIM=8192
  -> sparse-bipolar f=0.05 -> L2 normalize (EXACT match to fair_harness
  chain-grade pipeline).
- **Plasticity rules:**
  - Hebbian (K=1, K=2): one-pass rank-1 outer-product.
  - Adaptive cf-RPE (K=1): EXACT A3 rule (median-normalized clamp [0.25, 4.0])
    at N_STEPS=5000 batch=64 LR=0.5.
  - Adaptive cf-RPE (K=2): per-bank adaptive cf-RPE step with gate-weighted
    routing (probs = softmax(E_banks[0] @ W_gate.T / GATE_TEMP=0.5)). Each
    bank's update is gate-weighted AND per-token-LR-weighted.
- **Inference:** joint (T, lambda) sweep, LAMBDA_GRID excludes 0.0 (META C7).
- **Per-seed checkpoint:** experiments/_seed_checkpoint.py (PROT-021 satisfied).
- **GPU:** torch.cuda matmul; PROT-020 satisfied (literal `import torch`).
- **Substrate-only:** LLM_CALL_COUNTER asserted == 0.

## Resource budget

- **N_DIM_TOTAL=8192 (4096/bank); N_TRAIN=100k; 3 seeds.**
- Estimated wall (per K2_v2 ~ 1300s/seed full): ~4000s for 3 seeds. Buffered
  to 5400s (1.5x ratio); below PROT-021 4h checkpoint floor but cell uses
  `_seed_checkpoint` anyway (best practice).
- Smoke: N_DIM=1024, N_TRAIN=2k, 1 seed, ~30-60s laptop CPU.

## What this DOES NOT show

- Does not test K > 2 (only K=2 vs K=1 contrast)
- Does not test composition with STDP / cleanup / k-WTA
- Soft gate is not end-to-end trained; gate W is fixed random projection
- N_DIM_PER_BANK=4096 in K=2 vs N_DIM=8192 in K=1 = explicit resolution
  tradeoff that the architecture imposes
- Result at text8 V=4000 may not generalize to other corpora
- Adaptive LR floor/ceil [0.25, 4.0] is the A3-inherited setting; not swept

## Cites

- preregs/2026-06-24_substrate_cfrpe_per_token_adaptive_lr_v1.md (A3 prereg)
- preregs/2026-06-24_substrate_K2_x_cfrpe_compose_word2vec_v2.md (K=2 rescue prereg)
- experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (A3 cell; 6.9920)
- experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (K2_v2 cell)
- experiments/exp_fair_harness_substrate_as_lm_v1.py (encoder chain-grade)
- data/exp_fair_harness_substrate_as_lm_v1/metrics.json (7.3065 baseline)

## Cell discipline compliance

- [x] Fix #14: ONE cell
- [x] Fix #24: GPU dispatch with torch.cuda + matmul (overnight_queue eligible)
- [x] Fix #26: predispatch_check PROCEED (zero prior landings / atoms)
- [x] Fix #28: per-arm metrics propagation; verdict reads bpc_best per arm
- [x] A5: path-scoped commit (cell + prereg only)
- [x] ASCII-only
- [x] LAMBDA_GRID excludes 0.0 (META C7)
- [x] HDLAB_EXP_NAME-driven output dir
- [x] REQUIRED_FIELDS: verdict + verdict_msg + elapsed_s + summary
- [x] `--self-test` writes NOTHING (no stale-metrics masquerade)
- [x] Per-seed checkpoint (PROT-021 best-practice; not gated)
