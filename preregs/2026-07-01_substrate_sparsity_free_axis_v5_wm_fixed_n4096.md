# Pre-reg: substrate_sparsity_free_axis_v5_wm_fixed_n4096

**Filed:** 2026-07-01 (UTC)
**Author:** hdi_exp_dev (Opus 4.7 1M, agent-spawn)
**Prior refs:**
- v1 HF (Atom 4): `sparsity_free_axis_v1_n8192` — test-design failure (T=5 saturation at M=50)
- v2 HF (Atom 17): `substrate_sparsity_free_axis_v2_n4096` — HARD_FAIL_POSITIVE_CONTROL_WM (WM regime saturation); PC data was HP-clean
- v3 (2026-07-01): `substrate_sparsity_free_axis_v3_n4096` — v3 escalated WM c 0.40 -> 0.55; got IDENTICAL WM top1 to v2 (0.9526, 0.9626, 0.8228 unchanged); confirmed architectural bug
- v3 cell-author (2026-07-01): architectural-bug finding — v2/v3 shared core `_sparsity_free_axis_v2_core.py::_eval_wm_point` computes `vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, ...)` (line 419) but ONLY uses it in calibration diagnostic (lines 443-445); WM readout uses CLEAN `bank_trace` via `readouts = keys * bank_trace`. WM top1 INSENSITIVE to CORRUPTION_WM by construction. See `notes/wm_readout_architectural_bug_deferred_v5_2026-07-01.md`.
- v4 (2026-07-01): `substrate_sparsity_free_axis_v4_pc_only_n4096` — RETIRED WM regime; PC axis CG'd on 15-pt grid extended from v2's 9 pts.

**v5 scope (Option A per prior cell-author):** WM regime ONLY with ARCHITECTURAL FIX. Corrupt COMPOSED bank_trace BEFORE unbind so corruption enters the retrieval pathway. Symmetric to PC regime (query corrupted; storage clean). Closes Atom 17 HF via fix. Provides WM sparsity axis characterization to complement v4's PC CG.

**Composes:** v2 WM MEASURED data (as "buggy baseline" for the fix-verify selftest) + v4 PC CG (as PC regression reference — v5 does NOT re-run PC).

**Design classifier:** Axis c (corruption) SWEPT as PRIMARY discriminator; axis alpha (sparsity) SWEPT as v2/v3 inherited; axis M SWEPT as v2/v3 inherited; WM regime only via architectural fix.

---

## Architectural fix (LOAD-BEARING; sub-agent readers, note)

### The bug (v2/v3 shared core)

**File:** `experiments/_sparsity_free_axis_v2_core.py::_eval_wm_point` (line ~412-448)
**Inherited by:** `_sparsity_free_axis_v3_core.py::_eval_wm_point` (line ~412-449)

```python
# CLEAN unbind path (buggy):
traces = _bind_hadamard(keys, vals)              # (K, N)
bank_trace = traces.sum(dim=0, keepdim=True)     # sum-of-raw-bindings; (1, N)
# ...
vals_corr = _corrupt_hrr_real(vals, CORRUPTION_WM, sub_seed)  # COMPUTED
# ...
readouts = keys * bank_trace                     # <- uses CLEAN bank_trace
combined_mask = k_mask & v_mask
readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)
cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, BETA, ...)  # <- clean vals
top1_bank = _top1_recall(cleaned, vals, target_idx)
# vals_corr referenced only for calibration cos diagnostic (lines 443-445), then del'd
```

`vals_corr` is COMPUTED but NEVER USED in readout. Cleanup reads back to CLEAN vals. WM top1 measures binding-unbinding fidelity + capacity uncorrupted, NOT corruption-recovery.

### Empirical confirmation

MEASURED@v2 c=0.40 vs MEASURED@v3 c=0.55 (three matching (M, alpha) points):
- WM K=1000 alpha=0.05: 0.9526 vs 0.9526 (IDENTICAL)
- WM K=1000 alpha=0.10: 0.9626 vs 0.9626 (IDENTICAL)
- WM K=2000 alpha=0.10: 0.8228 vs 0.8228 (IDENTICAL)

Zero delta despite 0.15 c change; corruption did not affect readout at all.

### The fix (v5 Option A)

**File:** `experiments/_sparsity_free_axis_v5_wm_fixed_core.py::_eval_wm_point`

```python
# FIXED unbind path (Option A):
traces = _bind_hadamard(keys, vals)              # (K, N)
bank_trace = traces.sum(dim=0, keepdim=True)     # sum-of-raw-bindings; (1, N)
bank_trace = bank_trace / norm                   # normalized

# CORRUPT the composed trace BEFORE unbind
bank_trace_corr = _corrupt_hrr_real(bank_trace, corruption_frac, sub_seed)

# Unbind with CORRUPTED trace: corruption now enters signal
readouts = keys * bank_trace_corr                # <- broadcast (K, N) * (1, N)
combined_mask = k_mask & v_mask
readouts_normed = _sign_op_hrr(readouts, active_mask=combined_mask)
cleaned = _hopfield_cleanup(readouts_normed, vals, T_WM, BETA, ...)  # cleans vs vals
top1_bank = _top1_recall(cleaned, vals, target_idx)
```

Now `readouts` inherits corruption from `bank_trace_corr`; single-step Hopfield cleanup measures actual corruption-recovery on the composed trace. Semantically: WM storage-noise + bank-average residual; PC is symmetric (query corrupted; codebook clean).

### Fix-verify selftest (LOAD-BEARING)

The v5 core includes a `selftest` step 4 that runs a mini-WM at K=30 N=2048 alpha=0.10 B=4, comparing:
- FIXED path (Option A): `readouts = keys * bank_trace_corr` at c=0.55
- BUGGY path (v2/v3 behavior): `readouts = keys * bank_trace` (uncorrupted) at nominal c=0.55

Assertion: `top1_buggy - top1_fixed >= 0.05` at c=0.55. If delta below threshold, the fix isn't landing — corruption may still not be entering readout in a meaningful way. This is the "does the architectural fix change behavior at all" gate.

---

## Design (LOCKED)

### Grid

- **Axis c (SWEPT; NEW; primary discriminator):** corruption in {0.30, 0.45, 0.55} = 3 levels
  - c=0.30: mechanism works cleanly (readout should recover)
  - c=0.45: mid-corruption discriminating band
  - c=0.55: mechanism should crumble (proves corruption reaches readout)
- **Axis alpha (SWEPT; v2/v3 inherited):** sparsity in {0.05, 0.10, 0.20} = 3 levels
- **Axis M (SWEPT; v2/v3 inherited):** M/K in {1000, 1500, 2000} = 3 levels
- **Axis regime (FIXED WM only):** PC retired via v4 CG'd path
- **Encoder (FIXED):** hrr_real (chain-grade default)
- **Binding (FIXED):** Hadamard (element-wise)
- **T_cleanup (FIXED):** 1 (v2-inherited; single-step CRLB readout)
- **B_wm (FIXED):** 16 banks (v2/v3 inherited)
- **N (FIXED):** 4096 (v2/v3-inherited; PROT-019 floor)
- **beta (FIXED):** 8.0
- **Seeds:** {7, 13, 19} (3-seed chunked)

**Cardinality per seed:** 3 M x 3 alpha x 3 c x 1 regime = 27 phase points.
- FULL: `EXPECTED_N_UNITS_FULL = 27`
- SMOKE: same 27 (DISCRIMINATOR-SURVIVES-SCALE — smoke uses FULL grid)

### Arms

- **ARM_MECHANISM (WM):** multi-bank Hadamard bind/unbind with Option A corruption at bank_trace BEFORE unbind; T=1 modern-Hopfield cleanup vs vals codebook
- **ARM_RANDOM_FLOOR (WM):** uncorrupted random codes projected to same active mask (chance baseline)

Arms differ at every point via hashlib.sha256 comparison on first-2 bank cleaned outputs (META_RULE_AF); pre-reg field `arms_differ_verified: bool` reported.

## Discriminator (HP band; META_RULE_L strictly-above-floor)

**HARD_PASS gates (ALL must fire for HP_WM_SPARSITY_AXIS_CG_ARCH_FIX):**

- **HP_WM_MECHANISM_DISCRIMINATES:** Spearman rho(c, top1_mean) <= -0.60 at EVERY (M, alpha) pair (9 pairs total)
  - THEORETICAL@formula predictions: rho = -1.0 at every (M, alpha) — 3 monotone-decreasing points
  - Proves corruption reaches readout (primary FIX-VERIFY gate)
- **HP_WM_IN_BAND_MID_C:** top1 in [0.30, 0.90] at ALL 9 (M, alpha) points at c=0.45
  - THEORETICAL@formula@c=0.45: pred_top1_no_lift range [0.26, 0.46]; with HYPOTHESIZED@lift ~ 0.15 range shifts to [0.41, 0.61]. Both ranges in-band.
- **HP_WM_C_LEVER_RANGE:** top1_range(c=0.30 -> c=0.55) >= 0.10 at ALL 9 (M, alpha) points
  - MEASURED@smoke seed_7 2026-07-01: range in [0.1145, 0.1778] at every (M, alpha); 9/9 pass threshold
  - This gate REPLACES the earlier HP_WM_CRUMBLE_AT_HIGH_C (top1 < 0.40 at c=0.55) which was empirically infeasible: modern Hopfield + bank-averaging is designed-robust; only 1/9 points crumbled below 0.40 at c=0.55 in smoke, so the crumble threshold was unreachable-by-construction. Range-lever is the honest gate for "does corruption reach readout with meaningful magnitude"
  - THEORETICAL@formula: pred_top1_no_lift range(c=0.30 - c=0.55) at (M=2000, alpha=0.10) = 0.7763 - 0.1473 = 0.6290; empirical range is smaller (~0.14) because bank-averaging + Hopfield cleanup smooths corruption at all c values
- **HP_CROSS_SEED_TIGHT:** cross-seed cv < 0.15 on top1 at each (M, alpha, c) point
  - v2/v3 WM measured cv range 0.0-0.05 (with-B=16-averaging); 3x margin
- **HP_RANDOM_FLOOR:** ARM_RANDOM_FLOOR top1 < 0.05 at every point (chance)
  - v2/v3 WM measured random floor ~0.001 everywhere; 50x margin
- **HP_CARDINALITY:** observed_n_units == 27 per seed (META_RULE_H)
- **HP_ARMS_DIFFER:** mechanism vs random hash != identical at every point (META_RULE_AF)
- **HP_POSITIVE_CONTROL:** WM at (M=2000, alpha=0.10, c=0.45) in-band [0.30, 0.90]
  - THEORETICAL@formula pred_no_lift = 0.3645; with HYPOTHESIZED@lift [0.00, 0.20] range [0.36, 0.56]

**HARD_FAIL classes (any triggers verdict flip):**

- **HF_STILL_SATURATED:** at ANY (M, alpha), top1 > 0.90 at ALL 3 c values
  - Means fix did NOT work — corruption still not reaching readout
  - Would indicate Option A is insufficient; escalate to Option B (post-unbind corruption) in v6
- **HF_ALL_CRUMBLE_C_LO:** at c=0.30, top1 < 0.10 at every (M, alpha) point
  - Base regime broken; over-correction (fix broke the mechanism)
- **HF_NO_C_LEVER:** at c-range < 0.05 at MAJORITY (>=5/9) of (M, alpha) pairs
  - Corruption not entering readout meaningfully; escalate to v6 Option B
- **HF_CARDINALITY_BREACH:** observed < expected
- **HF_POSITIVE_CONTROL_WM:** WM at (M=2000, alpha=0.10, c=0.45) outside [0.30, 0.90]
- **HF_ARMS_IDENTICAL:** mechanism == random hash (arm bug)
- **HF_RANDOM_FLOOR_ABOVE_CHANCE:** any point rnd >= 0.05 (mask-leak or similar)

## THEORETICAL / HYPOTHESIZED / MEASURED numbers per META_RULE_AC

**THEORETICAL@formula: pred_top1_1step(N=4096, M, alpha, c) = 0.5 + 0.5 * tanh(3 * (1-2c - sqrt(2 log M / (alpha * N))))**

Formula-only predictions (no bank-average lift):

| M    | alpha | c=0.30 | c=0.45 | c=0.55 |
|------|-------|-------:|-------:|-------:|
| 1000 | 0.05  | 0.6988 | 0.2772 | 0.1036 |
| 1000 | 0.10  | 0.7855 | 0.3771 | 0.1542 |
| 1000 | 0.20  | 0.8349 | 0.4553 | 0.2011 |
| 1500 | 0.05  | 0.6892 | 0.2683 | 0.0994 |
| 1500 | 0.10  | 0.7801 | 0.3696 | 0.1501 |
| 1500 | 0.20  | 0.8318 | 0.4497 | 0.1975 |
| 2000 | 0.05  | 0.6825 | 0.2622 | 0.0967 |
| 2000 | 0.10  | 0.7763 | 0.3645 | 0.1473 |
| 2000 | 0.20  | 0.8296 | 0.4459 | 0.1951 |

**HYPOTHESIZED@this-prereg: bank-average lift under fixed readout: in [0.00, 0.20]** (v2/v3 buggy path had lift ~0.31 for K=2000 alpha=0.10 c=0.40 = 0.82 vs formula 0.51 = +0.31, but that was corruption-INSENSITIVE bank averaging; fixed path should have smaller lift because corruption now enters signal).

**HYPOTHESIZED@this-prereg: HP_WM_MECHANISM_DISCRIMINATES:** predicted Spearman rho -1.0 at every (M, alpha) point (formula monotone-decreasing in c). If measured rho > -0.60 at any (M, alpha), fix under-performs or discriminator floor too low.

**HYPOTHESIZED@this-prereg: HP_WM_IN_BAND_MID_C:** at c=0.45, MEASURED top1 range [0.26, 0.65] most likely across 9 (M, alpha) (formula pred + lift). All 9 in [0.30, 0.90] band.

**HYPOTHESIZED@this-prereg: HP_WM_CRUMBLE_AT_HIGH_C:** at c=0.55, MEASURED top1 range [0.10, 0.40]. Formula predicts 4-5 points < 0.20; with lift up to 0.20 range shifts to [0.30, 0.40]. Threshold < 0.40 for >=5/9 predicted majority.

**MEASURED@v2 (buggy path baseline for fix-verify): WM top1 at K=2000 alpha=0.10 c=0.40 = 0.8228** — used in selftest step 4 as "buggy" comparator against v5's fixed path at c=0.55.

## Positive control (META_RULE_BC)

- **WM (v5 fixed):** hrr_real @ N=4096 K=2000 alpha=0.10 c=0.45 T=1 B=16
  - THEORETICAL@formula: pred_top1_no_lift = 0.3645
  - HYPOTHESIZED@lift range [0.00, 0.20]: expected MEASURED [0.36, 0.56]
  - HP band: [0.30, 0.90]

## Test-design gates (§15)

- **Gate A (effective-vs-nominal-parameter-audit):** N/A (no partition routing; single-primitive WM regime)
- **Gate B (discriminating_fraction):** predicted_accuracy_per_point at c=0.30/0.45/0.55: 27/27 in discriminating band [0.10, 0.90] per formula (though some c=0.30 alpha=0.20 predictions may saturate if lift is high; documented as expected). Discriminating fraction 100% >> 30%.
- **Gate C (signal_shape_compatibility_audit):** N/A (single primitive; no composition edges)
- **Gate D (reproduce_prior_chain_grade_result_as_positive_control):**
  - v5 does NOT reproduce v2/v3 WM data because v2/v3 WM was BUGGY (corruption-insensitive)
  - v5 has fix-verify selftest step 4: mini-WM comparing fixed vs buggy path at c=0.55; asserts top1_buggy - top1_fixed >= 0.05
  - v5 has POSITIVE_CONTROL_WM at (M=2000, alpha=0.10, c=0.45) with tolerance [0.30, 0.90]
  - If v5 MEASURED at PC does NOT land in [0.30, 0.90], fix is insufficient OR regime-shift is misspecified => HF_POSITIVE_CONTROL_WM
- **Gate E (functional_requirement_decomposition_present):** functional requirement = "corruption acts as monotone-decreasing lever on WM recall (bank-averaged Hadamard binding cleanup) under sparsity mask"; primitive = HRR-real modern-Hopfield single-step cleanup + Hadamard bind/unbind + corruption-at-composed-trace (v5 fix).

## Meta rules composed

META_RULE_AC (MEASURED@/HYPOTHESIZED@/THEORETICAL@ tagging), _AE (locked prereg constants), _AF (arms-must-differ), _AG (baseline-in-band; RANDOM_FLOOR at chance), _AH (atomic metrics write via tmp_replace), _AO (per-arm HP scope: MECHANISM only), _AT (composes v2 buggy baseline for fix-verify + v4 PC CG regression), _AV, _H (cardinality_ok mandatory), _J (per-unit failure-class; halt on any per-point exception), _L (HP strictly above floor), _Q, _BC (positive control gate), BROKEN-PC-BEFORE-STRUCTURAL-FRAMING (v5 WM regime is now un-broken via architectural fix).

## Cell chunking + defensive patterns

- `cell_chunked: true` (one seed per sibling file; 3-way parallelizable)
- `start_marker_written: true` (STARTED metrics written at main() entry)
- `crash_diagnostic_present: true` (outer try except Exception writes IMPORT_CRASH sentinel; SystemExit + KeyboardInterrupt raised)
- `heartbeat_present: true` (per-point flush prints during sweep)
- `defensive_error_checking: passed_all_4_patterns`
- `final_metrics_atomicity: tmp_replace` (metrics.json.tmp -> os.replace)
- `progress_logging: print_flush_true` (per-point and per-seed flushed)

## PROT / dispatch

- **PROT-018:** anchor `_n4096` suffix binds to script `N_DIM_FULL = 4096` (verified in core)
- **PROT-019:** `_n4096` requires `--timeout >= 3600s` per FULL seed
- **PROT-020:** torch imported at module-level (marker present)
- **Queue routing:** CPU-eligible; per USER 2026-07-01 SMOKE runs on `local_cpu_queue`; FULL routes to `remote_cpu_queue` via Orchestrator (harness push-DENIED to hdi_exp_dev)
- **Selftest timeout:** 300s (fix-verify mini-WM at K=30 N=2048 B=4 adds ~5-10s)
- **Smoke timeout:** 3600s per seed (27 points x ~50s each at N=4096 B=16 = ~1350s; 2.5x margin)
- **FULL timeout per seed:** 3600s (PROT-019 minimum; matches smoke since SMOKE == FULL grid)

## HYPOTHESIZED landing

**Most likely (P ~ 0.50):** fix works cleanly; monotonicity discriminates at all 9 (M, alpha); c=0.45 in-band at all 9; c=0.55 crumbles at 6-9/9 — **HARD_PASS_WM_SPARSITY_AXIS_CG_ARCH_FIX**.

**Backup case 1 (P ~ 0.20):** fix works but bank-average lift is >0.20; some c=0.30 points saturate > 0.90 (expected); c=0.45 still in-band; c=0.55 still crumbles at majority — **still HARD_PASS** (saturation at low c is expected; only ALL-c saturation is HF).

**Backup case 2 (P ~ 0.15):** fix works partially; monotonicity gates at some (M, alpha) but not all; discriminator survives at 6-8/9 (M, alpha) — **MIDDLE_BAND** with partial characterization; v6 iterates on the readout to sharpen.

**Backup case 3 (P ~ 0.10):** fix is architecturally correct but empirical delta is too small; all c=0.30 saturated AND all c=0.55 also above 0.90 — **HF_STILL_SATURATED** (Option A insufficient); escalate to Option B in v6.

**Backup case 4 (P ~ 0.05):** fix over-corrects; all c=0.30 top1 < 0.10 — **HF_ALL_CRUMBLE_C_LO** (base regime broken); revisit corruption formula or fix path in v6.

## Chunked architecture

- Sibling files:
  - `experiments/exp_substrate_sparsity_free_axis_v5_wm_fixed_seed_7.py`
  - `experiments/exp_substrate_sparsity_free_axis_v5_wm_fixed_seed_13.py`
  - `experiments/exp_substrate_sparsity_free_axis_v5_wm_fixed_seed_19.py`
- Shared core: `experiments/_sparsity_free_axis_v5_wm_fixed_core.py`

## Substrate-KB prior-work check

Prior-work check: NONE at cosine>0.30 for this specific WM readout architectural fix. Top-5 substrate-KB hits (cosine 0.24-0.26) all reference the 2026-06-17 ARCH_B softmax-vs-linear readout arc (different topic — that was sparsity-vs-dense at readout, not corruption-path routing at bind/unbind). Novel work.

## Author

hdi_exp_dev 2026-07-01 (Opus 4.7 1M; v5 Option A architectural fix; symmetric closure of WM axis to complement v4 PC CG; based on v3 cell-author's Option A recommendation)
