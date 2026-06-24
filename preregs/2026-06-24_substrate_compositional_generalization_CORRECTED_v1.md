# prereg: substrate_compositional_generalization_CORRECTED_v1

Date: 2026-06-24
Author: exp_dev
Cell: `experiments/exp_substrate_compositional_generalization_CORRECTED_v1.py`
Routing: local_cpu_queue (pure numpy + HRR primitives; fast)
Driver: USER 2026-06-24 compositional reasoner product story; replaces broken ARM 2 from `substrate_brain_aligned_aliveness_shotgun_v1` (HARD_FAIL holdout=0.000).

## Strategic rationale

Brain-aligned shotgun ARM 2 HARD_FAILED holdout top-1=0.000, but the fact-finder drill (notes/director_compositional_failure_USER_test_wrong_VSA_modality_inventory_2026-06-24.md) identified the root cause as a MECHANISM CONFIG BUG, not a substrate-aliveness failure:

- HRR circular convolution operates well only on DENSE random unit-norm vectors (Plate 1995).
- Brain-aligned shotgun fed circ-conv with sparse-bipolar (f=0.05) + NO per-bind normalization + raw-sum bank.
- Result: in_distribution_top1 = 0.10 (essentially chance 0.05); TRAIN-pair recall itself broken.
- Provenance: `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/partial_metrics_s7.json` -> `in_distribution_top1=0.10`, `mean_cosine_correct_holdout=-0.0008`.

Counter-evidence that substrate IS compositionally alive when configured right:
- `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/metrics.json` ARM_BIND_RECENT_5 lift=+0.212 on heldout contexts (MIDDLE_BAND but compositional).
- `data/exp_fhrr_rs_parity_cpu_v1/metrics.json` HARD_PASS (FHRR phase-domain works).
- `data/exp_hrr_depth_budget_sparse_bipolar_v2/metrics.json` HARD_PASS (sparse-bipolar HARD_PASS in autoassociative regime; NOT under HRR circ-conv bind).
- `data/exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1/metrics.json` HARD_PASS (VSA-partition routing 10M).

This cell re-runs the EXACT brain-aligned ARM 2 protocol with CORRECT mechanism configurations to disambiguate "compositional alive" from "mechanism broken".

## Mechanism

Pure NumPy. No learning, no plasticity, no cf-RPE. N_DIM=4096 (matched to contextual_encoding_hrr_PRODUCTION_held_out_v1 winning config; reduce crosstalk at the M=200 superposition level). 4 arms, 3 seeds.

### ARMS

**ARM_BROKEN_SPARSE_NO_NORM** (control / provenance arm; reproduces brain-aligned shotgun ARM 2 bug)
- Codebook: sparse-bipolar f=0.05.
- Bind: `_bind_circ(a, b)` = real(ifft(fft(a) * fft(b))).
- Bank: raw `bank += bind_circ(subj[i], obj[j])` (NO normalization).
- Expected: in_distribution_top1 < 0.20 (provenance for the diagnosis).

**ARM_DENSE_HRR_NORMALIZED** (Plate's canonical HRR config)
- Codebook: dense Gaussian with unit-L2 norm per vector.
- Bind: `_bind_circ(a, b)`.
- Bank: `bank += _l2_normalize(bind_circ(subj[i], obj[j]))` (per-bind L2 normalization).
- Final cleanup query also L2-normalized before cosine.

**ARM_FHRR_NORMALIZED** (frequency-domain HRR; phase-only)
- Codebook: random unit-modulus phase vectors of length N_DIM in complex64 (`exp(i * theta)`).
- Bind: element-wise complex multiply (`a * b`).
- Unbind: element-wise complex multiply with conjugate (`c * conj(b)`).
- Bank: complex sum, per-bind unit-modulus re-projection (`v / abs(v)` per coordinate after each addition is too costly; instead bundle then L2-normalize the real and imag parts after the sum -- standard FHRR bundling).
- Cosine in complex space: `real(<a, conj(b)>) / (||a|| * ||b||)`.

**ARM_SPARSE_HRR_NORMALIZED** (sparse-bipolar bind WITH per-bind L2 normalization)
- Codebook: sparse-bipolar f=0.05.
- Bind: `_bind_circ(a, b)` (same FFT circular convolution).
- Bank: `bank += _l2_normalize(bind_circ(subj[i], obj[j]))` (the fix the broken arm lacks).

## Test protocol (identical to brain-aligned shotgun ARM 2)

- 20 subjects x 20 objects = 400 possible pairs.
- Coverage = 0.50; 200 random pairs become TRAIN bindings, 200 are HELDOUT.
- Each TRAIN pair binds as `bank += unit_norm(bind_circ(subj[i], obj[j]))` (arm-dependent).
- For each TRAIN (i, j): `unbind(bank, subj[i])`, argmax cosine over the 20-entry OBJ codebook. Aggregate -> `in_distribution_top1`.
- For each HELDOUT (i, k) where the pair is unseen: same unbind+argmax. Aggregate -> `holdout_top1`.
- Chance = 1/20 = 0.05.

## Sanity floor (Fix per fact-finder)

**MANDATORY**: `in_distribution_top1 > 0.70` for an arm's holdout result to count as a generalization claim. If in_dist <= 0.70, that arm is METHODOLOGY-CONFOUND (mechanism doesn't even recall TRAIN), not a generalization signal. Both metrics are reported per arm.

## Pre-reg HARD bands (sacrosanct both directions)

### Sanity check (arm-1 control)
- Pass-band-for-broken-arm-provenance: `ARM_BROKEN_SPARSE_NO_NORM.in_distribution_top1 < 0.20`.
- If this arm UNEXPECTEDLY clears 0.70, the fact-finder diagnosis is wrong and the cell raises a flag for re-analysis.

### Cell-level verdicts (cell verdict driven by best normalized arm)

- **HARD_PASS_COMPOSITIONAL_ALIVE**: ANY normalized arm (DENSE / FHRR / SPARSE_NORMALIZED) achieves `in_distribution_top1 > 0.70` AND `holdout_top1 > 0.50`. Substrate compositionally generalizes when configured right.

- **MIDDLE_BAND_PARTIAL_GENERALIZATION**: best normalized arm clears `in_distribution_top1 > 0.70` but holdout in [0.20, 0.50].

- **HARD_FAIL_DEEPER_ISSUE**: NO arm (including normalized) clears `in_distribution_top1 > 0.70`. Substrate's HRR-family fundamentally broken at this scale; not just the broken arm.

- **HARD_FAIL_PROPER_RETEST**: normalized arms clear `in_distribution_top1 > 0.70` but ALL of them have `holdout_top1 < 0.20`. Genuine compositional-generalization failure (substrate-product implication: would need attention-based recombination or hierarchical compose).

## Seeds & config

- Full: seeds = [7, 17, 23] (n=3).
- Smoke: seed = [0] with reduced grid (n_subj=n_obj=8, coverage=0.50 -> 32 train / 32 heldout, N_DIM=1024).
- Per-seed checkpointed via `experiments/_seed_checkpoint.py`.
- CONFIG_VERSION includes every result-affecting param.

## Timeout estimation

Smoke target ~30-60s (1 seed; 4 arms; small grid; N=1024). Full estimate per seed: 4 arms x (200 train binds + 400 unbind/cosine queries) at N_DIM=4096 -> dominated by FFT pairs (M=200 train binds + M=200 holdout + M=200 in_dist = 600 FFT pairs * 4 arms ~= 2400 FFTs per seed; each ~0.5ms at N=4096; <2s per seed for the FFT work). Codebook cosine matmul: 20x4096 -> negligible. Total per-seed estimate <30s; 3 seeds <100s. Add I/O and FHRR complex overhead -> <300s total. Budget **timeout=1800s** (30min) for headroom.

## Pre-flight gates passed before dispatch

- [ ] `--self-test` exits 0 (HRR involutive + per-arm tiny configs + normalization-not-no-op all pass).
- [ ] `--smoke` produces valid metrics.json with REQUIRED_FIELDS (verdict, verdict_msg, elapsed_s, summary).
- [ ] Cell file + prereg path-scoped commit BEFORE queue_add.
- [ ] queue_add gate clears (no PROT-018 since anchor has no `_n<N>` suffix; PROT-021 N/A timeout<14400s).
- [ ] predispatch_check: PROCEED (anchor brand-new; no prior landings).

## WHAT_THIS_DOES_NOT_SHOW

This cell tests COMPOSITIONAL GENERALIZATION on subject-object role-binding under SUPERPOSITION at a single M scale. It does NOT show:
- Language-task performance (no text corpus involved).
- Learning / plasticity (no cf-RPE, no gradient updates).
- That any specific downstream task will benefit.
- Capacity scaling (only one M value).
- Robustness to noisy / sparse keys (subjects are clean codebook entries).
- That FHRR will win or lose vs DENSE / SPARSE_NORMALIZED (different arms are different points in the design space).

A HARD_PASS_COMPOSITIONAL_ALIVE verdict is a MECHANISM characterization at M=200/D=4096 on role-bind / unbind under superposition, with TRAIN/HELDOUT generalization gap as the discriminator.

By-construction notes:
- TRAIN-pair "generalization" is misleading -- the SAME pair was bound; unbind is recall, not generalization. We report it as `in_distribution_top1` (sanity floor) and use HELDOUT for the real test.
- ARM_BROKEN_SPARSE_NO_NORM is a CONTROL meant to reproduce the broken-mechanism failure; if it accidentally HARD_PASSes the diagnosis would be revisited.
- All arms use the same 20-subject 20-object task topology; only the mechanism (codebook + bind + normalization) varies.

## Cites

- USER compositional reasoner product story 2026-06-24.
- Fact-finder note: `notes/director_compositional_failure_USER_test_wrong_VSA_modality_inventory_2026-06-24.md`.
- Broken-mechanism evidence: `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/partial_metrics_s7.json` `in_distribution_top1=0.10`.
- HRR-can-generalize counter: `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/metrics.json` ARM_BIND_RECENT_5 lift=+0.212.
- FHRR-RS-parity HARD_PASS: `data/exp_fhrr_rs_parity_cpu_v1/metrics.json`.
- Sparse-bipolar HARD_PASS (autoassociative regime; not HRR-bind): `data/exp_hrr_depth_budget_sparse_bipolar_v2/`.
- VSA-partition routing 10M HARD_PASS: `data/exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1/metrics.json`.
- Plate 1995 (HRR canonical dense unit-norm).
