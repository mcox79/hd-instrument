# WM readout architectural bug: `vals_corr` unused in readout (deferred to v5)

**Filed:** 2026-07-01
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** v3 cell-author Option D recommendation while authoring v4_pc_only cell

## Bug

**File:** `experiments/_sparsity_free_axis_v2_core.py` (also inherited by `_sparsity_free_axis_v3_core.py`)
**Function:** `_eval_wm_point`

At line 419:
```python
vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)
```

`vals_corr` is computed correctly (Gaussian noise added to `vals` s.t. `E[cos(vals_corr, vals)] ~ 1 - 2*CORRUPTION_WM`).

**But `vals_corr` is only referenced at lines 443-445 (calibration cosine diagnostic):**
```python
Qn = torch.linalg.norm(vals_corr[:cal_sample], dim=1).clamp(min=1e-12)
Xn = torch.linalg.norm(vals[:cal_sample], dim=1).clamp(min=1e-12)
cd = (vals_corr[:cal_sample] * vals[:cal_sample]).sum(dim=1)
```

Then `del vals_corr` at line 448.

The actual WM readout path:
```python
# Line ~412
traces = _bind_hadamard(keys, vals)              # uses raw vals
bank_trace = traces.sum(dim=0, keepdim=True)      # sum-of-raw-bindings

# Line ~421
readouts = keys * bank_trace                      # unbind with keys, get vals estimates
combined_mask = k_mask & v_mask
readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)

# Line ~425
cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, BETA, active_mask=v_mask)
top1_bank = _top1_recall(cleaned, vals, target_idx)
```

**Corruption never reaches the readout.** WM top1 is INSENSITIVE to CORRUPTION_WM by construction.

## Empirical confirmation

Three matching WM top1 values at v2 c=0.40 vs v3 c=0.55:
- 0.9526, 0.9626, 0.8228 — IDENTICAL at both c values

If the readout used `vals_corr` correctly, c=0.55 should degrade top1 significantly below c=0.40 (higher corruption -> lower cleanup recall). Zero delta confirms the bug.

## Implication

Skunkworks' Wave 7 v3 revival criterion (raise WM c to 0.55) is architecturally UNACHIEVABLE at the current WM readout design. Any attempt to escalate CORRUPTION_WM will produce identical results.

## v5 scope (deferred WM regime fix)

**Required fix:** rewrite `_eval_wm_point` so the corrupted state actually enters the retrieval pathway. Two candidate designs, in order of increasing bio-plausibility:

**Option A (KEYS_CORR unbind — SIMPLEST):**
```python
keys_corr = _corrupt_hrr_real(keys, CORRUPTION_WM, sub_seed)
readouts = keys_corr * bank_trace         # unbind with CORRUPTED keys
```
Semantics: retrieval-time key is noisy (query recall corrupted). Matches typical HRR bind-unbind corruption model.

**Option B (VALS_CORR readback via cleanup):**
```python
readouts = keys * bank_trace              # ideal unbind
readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)
# Corrupt readout BEFORE cleanup — represents post-unbind noise
readouts_noisy = _corrupt_hrr_real(readouts_normed, CORRUPTION_WM, sub_seed)
cleaned = _hopfield_cleanup(readouts_noisy, vals, T_WM, BETA, active_mask=v_mask)
```
Semantics: post-unbind decoded value is noisy; cleanup denoises. Matches "storage-noise" model.

**Author decision for v5:** Option A is simpler + matches the closer analog to PC regime (query is corrupted; storage is clean). Option B is more physically motivated for continuous readouts. Both are defensible; v5 cell-author picks per Research direction.

**Cross-arm calibration required for v5:** the calibration cosine line at 443-445 currently measures `cos(vals_corr, vals) ~ 1 - 2c`. Under Option A that would become `cos(keys_corr, keys)`; the target calibration stays the same but the diagnostic must switch to the actually-used corrupted variable so the diagnostic reflects what the readout sees.

## v5 pre-reg design skeleton (for future reference)

- Grid: same PC + WM (v2 shape); c_WM in {0.30, 0.40, 0.50} sweep (verify corruption-recovery gradient)
- Positive-control: bank-avg WM top1 at K=2000 alpha=0.10 c_WM=0.40 in [0.20, 0.80]
- New HP gate: WM_CORRUPTION_LEVER (Spearman rho(c_WM, top1_wm) <= -0.60) — proves corruption reaches readout
- Regression gate: reproduce v2 PC data at MEASURED tolerance 0.05 per point

## Blast radius

This bug affects v2 + v3 shared core; both cells' WM verdicts should be treated as "no-signal" on the WM axis, NOT "WM has poor corruption recovery." No downstream framing that relies on WM sensitivity to c should cite v2 or v3 as evidence.

The PC axis in v2/v3 core is unaffected — PC pathway uses `_corrupt_hrr_real` correctly at line 330 (`Q_sub_0 = _corrupt_hrr_real(X, CORRUPTION_PC, sub_seed)`) and cleans FROM that corrupted state. PC data at v2 is MEASURED-clean.

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; found while authoring v4 pc-only cell per prior cell-author Option D recommendation)
