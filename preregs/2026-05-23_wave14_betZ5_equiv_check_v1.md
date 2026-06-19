# Pre-registration: wave14_betZ5_equiv_check_v1

**Date**: 2026-05-23
**Experiment**: Bet Z.5 absorbing-diffusion ensemble smoother vs VAMP-on-chain structural equivalence
**Script**: experiments/exp_wave14_betZ5_equiv_check_v1.py
**Queue**: local_cpu_queue
**Expected wall time**: 20-40 min CPU (N=4096, K_ent=200, 3 seeds, 40 trials, K_ensemble=50)

---

## Hypothesis

Bet Z.5 (Absorbing Diffusion Ensemble Smoother, v144 candidate row, 13 versions stale) is either:

1. **Structurally equivalent to VAMP-on-chain** (same output distribution up to reparameterisation):
   Pearson r(VAMP_sims, Z5_posterior_mean) >= 0.99 across all test chains. Consequence: close
   Bet Z.5 candidate row as duplicate-of-existing; VAMP-on-chain is already the implementation.

2. **Strictly stronger than VAMP-on-chain**:
   r < 0.99 (distributions differ) AND mean per-codeword variance certificate > 0.01.
   Consequence: Bet Z.5 produces a readout primitive VAMP cannot -- per-codeword posterior variance
   over the K diffusion ensemble members. VAMP is deterministic (single-pass); variance is trivially
   zero. Confirms a substrate-novel capability; justifies 4-6 hr GPU impl.

---

## Method

- Test grid: same substrate factbase construction as exp_wave14r_multihop_K100.py
  (bipolar BSC codebook, bound triple-store M = sign(sum of triples)).
- VAMP forward pass: forward-only deterministic single pass matching vamp_chain_forward_backward
  forward component; output: similarity vector over entity_atoms at final hop.
- Absorbing-diffusion ensemble: K_ensemble=50 independent noisy forward passes from
  noise_level=3.0 (Gaussian std) at the start entity, each absorbed to bipolar via sign_quantize
  at each hop; ensemble mean = posterior mean logits; ensemble std = per-codeword variance cert.
- Structural equivalence metric: Pearson r(VAMP_sims, Z5_posterior_mean) over all trials.
- Variance certificate: mean(std(per-entity similarity across K ensemble members)) per trial.

---

## Falsifiable predictions (pre-registered)

**P1 (equivalence)**: If Bet Z.5 == VAMP up to framing, expect r >= 0.99.
  Hard fail threshold: r < 0.95 in all 3 seeds (rules out equivalence with high confidence).

**P2 (variance cert distinguishability)**: If Z.5 is strictly stronger, expect mean_var_cert > 0.01.
  Hard fail threshold: mean_var_cert < 0.001 (ensemble collapses; diffusion adds no information).

**P3 (accuracy parity at full N)**: At noise_level=3.0, Z5 accuracy should be within +/- 15% of
  VAMP accuracy (same chain, same factbase). If Z5_acc < 0.5 * VAMP_acc, diffusion is pathological.

---

## Memory budget

- Dominant tensors: entity_atoms (K_ent x N float32) + M (N float32) + ensemble stack (K_ens x K_ent float32)
- FULL: K_ent=200, N=4096, K_ens=50 -> ~3.3 MB; well under any CPU limit.
- Peak estimated: < 50 MB CPU.

---

## Verdicts

- **BETZ5_EQUIVALENT_TO_VAMP**: r >= 0.99. Close candidate row. VAMP-on-chain IS the Z.5 algorithm.
- **BETZ5_STRICTLY_STRONGER**: r < 0.99 AND var_cert > 0.01. Confirm new substrate primitive.
- **BETZ5_INCONCLUSIVE**: r or var_cert degenerate (both near 0 or all outputs collapsed).

---

## Notes

Noise regime: at nl <= 1.0, all K ensemble trajectories collapse to the same sign-quantize
absorbing state (var_cert=0, r=1.0 trivially). nl=3.0 is the calibration point where ~8-15 of
20 ensemble members take distinct paths (smoke: distinct_paths=9/20 at N=512).
The FULL run at N=4096 with deeper chains and more distractors will show the stable-regime result.
