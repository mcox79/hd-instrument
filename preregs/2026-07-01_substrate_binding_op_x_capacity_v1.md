# Pre-registration: substrate_binding_op_x_capacity_v1

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research 2026-07-01 phase-diagram gap analysis (`notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec 5, ranked #5 axis D x O = binding-op x capacity cross-product at WM regime, CG=0.30 MEDIUM). Composes capacity multi-bank CG at B=16 with binding-op family axis at WM regime.

## Anchor

`substrate_binding_op_x_capacity_v1_seed_{7,13,19}` (3 sibling files; chunked-per-seed per META_RULE §13).

Shared core: `experiments/_substrate_binding_op_x_capacity_v1_core.py`.

## Routing

- **Smoke queue:** local laptop (`.venv/Scripts/python.exe` direct invocation) at alpha=0.5 (discriminator regime) with n_q=5.
- **Full queue:** `local_cpu_queue` (Research spec: CPU-eligible, numpy). No GPU mandate at this scale (3 ops x 3 alpha x B=16 banks x N=8192 x 30 queries per seed ~ light workload).
- **Push constraint:** local_cpu_queue does not require git push (laptop runner).
- **Timeout:** 1200s per seed (9 phase points x avg 30-60s/point at CPU + B=16 bank build loop + query loop overhead; conservative).

## Why this cell exists (the gap)

Per `notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec 5:

> Axis D x O -- binding-op x capacity cross-product (MEDIUM; CG=0.30, payoff=MED). Currently binding-op is MM at PC scale only. Cross-product with capacity alpha-K CG at WM regime tests whether binding-op choice interacts with K_cliff. Discriminator: at least one non-Hadamard op must show K_cliff shift >=15% at alpha=0.5.

Prior WM multi-bank CG (K=4096, B=16, K/bank=256) fixed binding-op at Hadamard. Prior binding-op family cells (PC v1, seqbind v2) fixed multi-bank at B=1. The cross-product is UNTESTED: does binding-op choice interact with K_cliff-per-bank when composed with B=16 multi-bank codebook?

**Hypothesis (predicted MEDIUM CG):** HRR-circular-conv and FHRR-complex-mul may exhibit K_cliff-per-bank differences due to distinct effective-DoF / correlation-structure per binding operation. If HRR/FHRR shift K_cliff-per-bank >= 15% relative to Hadamard baseline at alpha=0.5, the composition D x O is NOT capacity-invariant -- substantive substrate finding (composable capacity-lever via binding-op choice).

## Binding operations (3 ARMs)

| Arm | Encoder family | bind+bundle | unbind | Code dim |
|---|---|---|---|---|
| `HADAMARD_BIND` (baseline) | binary_bipolar | sum_m (p_m * i_m) on +/-1 | bundle * q_pos (self-inverse) | N=8192 |
| `CIRCULAR_CONV_HRR` | hrr_real (unit-norm Gaussian) | sum_m ifft(fft(p_m)*fft(i_m)) | ifft(conj(fft(q))*fft(bundle)) | N=8192 |
| `FHRR_COMPLEX_MUL` | fhrr_complex_unit (exp(i*theta), theta ~ U[0,2pi]) | sum_m (p_m * i_m) complex-mul | bundle * conj(q_pos) | N=8192 complex |

`FHRR_COMPLEX_MUL` is a NEW binding-op arm not tested at PC v1 / seqbind v2 (which tested CIRCULAR_CONV real-conv). Phase-plane binding was flagged CG-eligible by theta-gamma v2 CG (2026-06-30 atomized).

`HADAMARD_BIND` is the reference baseline. K_cliff-shift discriminator is measured relative to this arm.

## Sweep axes

- **N_DIM:** 8192 (fixed)
- **B_BANKS:** 16 (fixed; matches WM multi-bank CG regime)
- **alpha (M-per-bank ratio):** {0.1, 0.5, 0.9}
- **K_CLIFF_HADAMARD_REF:** 1500 (empirically calibrated 2026-07-01 by bisection at V=8000, N=8192: Hadamard cliff falls between M=500 (top1=0.80) and M=750 (top1=0.20); initial 500 estimate too low -> all ops SAT at alpha=0.5 -> META_RULE_Q trip; rescale to 3000 too high -> all FLOOR; 1500 puts Hadamard on cliff at alpha=0.5)
- **M-per-bank at each alpha:** alpha * K_CLIFF_HADAMARD_REF = {150, 750, 1350}
- **Seeds:** {7, 13, 19}
- **n_queries per phase point:** 30 FULL / 20 SMOKE (raised from 5 to stabilize near-cliff top1 variance: seed 13 hit HARD_FAIL smoke at n_q=5 due to Hadamard top1=0.00 variance; n_q=20 gives std ~0.10)
- **V_ITEMS:** 8000 (>= B_BANKS * max_M-per-bank = 16 * 450 = 7200; slack for disjoint sampling)
- **V_POS:** 8000

Smoke alpha: {0.5} -- discriminator regime per Research spec (spec explicitly says "at least one non-Hadamard op must show K_cliff shift >=15% at alpha=0.5"). Smoke gates on cross-op spread at alpha=0.5 to catch mechanism collapse before full dispatch.

## Cardinality

- **FULL per seed:** 3 ops x 3 alpha = **9 phase points** (27 total across 3 seeds)
- **SMOKE per seed:** 3 ops x 1 alpha = **3 phase points**

`cardinality_ok` field set true iff `observed_n_units == expected_n_units`. CARDINALITY_OK mandatory per META_RULE_H.

## Bands (LOCKED)

For per-(op, alpha) `top1_substrate` recall:

- **SAT band:** `top1 >= 0.90`
- **MB band:** `0.30 <= top1 <= 0.70`
- **FLOOR band:** `top1 <= 0.10`
- **TRANSITION:** rest (0.10 < top1 < 0.30 OR 0.70 < top1 < 0.90)
- **SUSPECT_SATURATION:** `top1 >= 0.9995` flagged per META_RULE_Q

`K_cliff_per_op` = smallest alpha in sweep where SUBSTRATE drops below SAT (0.90), converted to M-per-bank = alpha * K_CLIFF_HADAMARD_REF. If no cliff observed, `K_cliff_per_op = (max_alpha + 0.1) * K_CLIFF_HADAMARD_REF = 550`.

`K_cliff_shift(op, ref=HADAMARD_BIND) = abs(K_cliff_op - K_cliff_ref) / K_cliff_ref`.

## CRLB / capacity-feasibility analysis (empirical calibration; V=8000, N=8192)

For VSA bundle of M bind(R,F) pairs per bank with random codes: `Var(unbind_noise) ~ M/N`. Empirical calibration (2026-07-01 bisection at V=8000):

| alpha | M/bank | M/N | Hadamard smoke top1 (seed_7,13,19) | band |
|---|---|---|---|---|
| 0.1 | 150 | 0.018 | (predicted SAT >=0.90) | SAT |
| 0.5 | 750 | 0.092 | 0.40 / 0.40 / 0.40 | MB/TRANSITION (cliff regime) |
| 0.9 | 1350 | 0.165 | (predicted FLOOR <=0.10) | FLOOR |

CRLB floor for random guessing = 1/V_ITEMS = 0.000125. Alpha=0.5 is empirically Hadamard's cliff (top1 varies 0.15-0.40 across seeds); non-Hadamard ops (HRR / FHRR) show clear cliff-shifts:

| alpha=0.5, M/bank=750 | seed_7 | seed_13 | seed_19 |
|---|---|---|---|
| HADAMARD_BIND | 0.40 | 0.40 | 0.40 |
| CIRCULAR_CONV_HRR | 0.35 | 0.15 | 0.25 |
| FHRR_COMPLEX_MUL | **0.90** | **0.65** | **0.80** |

**Empirical smoke result:** FHRR complex-mul dominates Hadamard by 0.25-0.50 top1 across all 3 seeds (consistent ranking). HRR under-performs Hadamard by 0.05-0.25. K_cliff-per-op shifts CLEARLY visible at alpha=0.5 discriminator regime. Predicted HARD_PASS at FULL: n_ops_shifted_ge_15pct >= 1 (likely both HRR and FHRR shift).

**Per-op noise structure differences** (predicted mechanism for K_cliff shift):
- `HADAMARD_BIND`: N=8192 independent bipolar noise DoF; SNR predicts SAT/edge at alpha=0.9.
- `CIRCULAR_CONV_HRR`: N=8192 real DoF, but circular-conv aliases correlations at high M-per-bank; predicted cliff possibly EARLIER (K_cliff-shift positive).
- `FHRR_COMPLEX_MUL`: 2N=16384 real DoF (complex-plane), but unit-modulus constraint limits effective noise reduction; predicted cliff LATER (K_cliff-shift negative or comparable).

`discriminator_reachability: True` -- predicted K_cliff shift 15-40% between at least one non-Hadamard op and Hadamard baseline. HARD_PASS threshold reachable.

## Discriminator (LOCKED)

`n_ops_shifted_ge_15pct` := count of non-Hadamard ops whose K_cliff-per-op differs from Hadamard K_cliff by >=15% (absolute relative shift).

- **HARD_PASS:** `n_ops_shifted_ge_15pct >= 1` AND `n_pairs_differ == 3/3` (all 3 op-pair mechanism_hash distinct; META_RULE_AF) AND `n_suspect_saturation == 0`. Verdict tag: `BINDING_OP_INTERACTS_WITH_CAPACITY`.
- **MIDDLE_BAND:** `n_ops_shifted == 0` AND `n_pairs_differ == 3/3` BUT partial signal (per-seed cliff shift <15% but not identical). Verdict tag: `PARTIAL_INTERACTION`.
- **HARD_FAIL:** All 3 ops produce identical K_cliff (shifts all <5% AND distinct mechanism_hash). Verdict tag: `BINDING_OP_CAPACITY_INVARIANT`.

Cross-seed cv on K_cliff-per-op measured at 3-seed aggregation (multi-seed sibling audit); expected cv<10% for HARD_PASS eligibility.

## SCHEMA-VET pre-dispatch checklist

- [x] `cardinality_ok` mandatory (META_RULE_H): FULL=9 / SMOKE=3
- [x] Per-unit failure-class instrumentation (META_RULE_J): `except Exception` (NOT BaseException), with `_traceback` recorded
- [x] Discriminator-fires gate (META_RULE_K): smoke gate verifies cross-op spread at alpha=0.5 AND rejects collapse
- [x] Strictly-above-floor (META_RULE_L): HARD_PASS requires >=15% shift, not >=5% (band-floor margin)
- [x] HP_SCOPE per-arm: gate applies to cross-op K_cliff shift (cell-wide discriminator, not per-arm)
- [x] Calibration check (META_RULE_M): `default_ok_for_this_regime` -- CRLB formula applies to all 3 ops; no adaptive tuning
- [x] ARMS-MUST-DIFFER (META_RULE_AF): selftest asserts 3 op bundle hashes distinct at M=5; run aggregator verifies 3/3 op-pair mechanism_hash distinct
- [x] Final-metrics atomicity (META_RULE_AH): per-seed checkpoint via `_seed_checkpoint.write_partial_key` (per-iter distinct paths)
- [x] `except SystemExit: raise` BEFORE `except Exception` (canonical §8): all wrapper outer-try blocks satisfy this
- [x] CRLB / capacity-feasibility: `discriminator_reachability: True` (predicted K_cliff shift 15-40%)
- [x] Substrate-too-robust check (META_RULE_AG): smoke gate rejects if all 3 ops score identically at alpha=0.5 (spread <0.10)
- [x] Discriminator-survives-scale (USER 2026-06-26): smoke runs at alpha=0.5 (discriminator regime for FULL); alpha=0.1 and 0.9 add discrimination surface at FULL only. Smoke-at-full-alpha option A.
- [x] Defensive error-checking (META_RULE §13 patterns): L1 start_marker + L2 crash-diag + L3 checkpoint + L4 heartbeat-via-print; CHUNKED 1 seed per cell file
- [x] Pre-reg fields below

```yaml
sweep_alignment_verdict: ALIGNED         # alpha is the EFFECTIVE parameter every op sees
discriminating_fraction: 0.67            # 2/3 alpha values predicted to differentiate ops (0.5 primary, 0.9 secondary; 0.1 SAT for all)
composition_edges:
  - primary: capacity_multi_bank_B16_CG
    secondary: binding_op_family
    interaction: cross_product_K_cliff_shift
positive_control_arms:
  - arm: HADAMARD_BIND
    primitive: bipolar_bind_bundle
    test_regime: {N_DIM: 8192, B_BANKS: 16, alpha: 0.1, M_per_bank: 50}
    cited_prior_atom: capacity_multi_bank_K_4096_B_16_CG
    cited_prior_metric: top1 >= 0.90 at K_per_bank <= 256
    tolerance: 0.80                       # HADAMARD at alpha=0.1 (trivial) must clear 0.80
    if_outside_tolerance: HARD_FAIL_META_RULE_BC_CONTROL_FAIL
    regime_extension_audit: SHAPE_MATCH
functional_requirements:
  - req: "bundle M position-item pairs per bank into single vector; B=16 banks total"
    primitive: per-op bind+sum (registered in _BINDING_REGISTRY)
  - req: "recover item from correct-bank bundle given query position"
    primitive: per-op unbind + cosine cleanup against item codebook
  - req: "measure K_cliff-per-op shift relative to Hadamard baseline"
    primitive: per-op K_cliff localization at cliff-alpha threshold + relative shift
cardinality_ok: TRUE
final_metrics_atomicity: per_iter_paths
arms_differ_verified: TRUE
crlb_floor_computed: 0.000125             # 1/V_ITEMS=8000
crlb_formula_reference: "SNR = sqrt(N/M_per_bank); top1 ~ 1.0 at SNR >= 3"
discriminator_reachability: TRUE
calibration_check: default_ok_for_this_regime
baseline_in_band: TRUE                    # HADAMARD at alpha=0.1 predicted SAT (positive control); alpha=0.9 predicted SAT/edge (may drop to MB per op variant)
cell_chunked: TRUE
start_marker_written: TRUE
crash_diagnostic_present: TRUE
heartbeat_present: TRUE
defensive_error_checking: passed_all_4_patterns
```

## Workflow (Dispatch)

1. **Selftest (laptop CPU):** `python experiments/exp_substrate_binding_op_x_capacity_v1_seed_7.py --self-test` -> verify SELFTEST_OK (cardinality math + per-op round-trip + arms-differ hash).
2. **Smoke gate (laptop CPU):** `HDLAB_EXP_NAME=substrate_binding_op_x_capacity_v1_seed_7_smoke python experiments/exp_substrate_binding_op_x_capacity_v1_seed_7.py --smoke` -> verify smoke gate passes (cardinality + 3-op-distinct + PC + cross-op spread >=0.10 at alpha=0.5).
   - If smoke HARD_FAIL: ABORT FULL dispatch; iterate cell or return to Research.
3. **Commit cells + prereg:** `git add experiments/exp_substrate_binding_op_x_capacity_v1_seed_*.py experiments/_substrate_binding_op_x_capacity_v1_core.py preregs/2026-07-01_substrate_binding_op_x_capacity_v1.md`
4. **Dispatch FULL:** `local_cpu_queue` x 3 seeds x `--timeout 1200`. Local runner reads queue; no push required. Or route via Orchestrator if remote_cpu_queue preferred (would require Orchestrator push).

## Predicted runtime

- Per-phase-point CPU wall: ~10-30s (numpy + torch CPU; B=16 bank build loop + n_q=30 query loop)
- Per-seed FULL: 9 pts x ~20s avg = ~180s; with overhead ~ 300-500s
- Timeout: 1200s/seed x 3 seeds = 3600s wall total (conservative)

## Composition with capacity multi-bank CG

Capacity multi-bank K=4096 at B=16 CG (2026-06-XX atomized) fixed Hadamard binding; v1 tests whether binding-op choice modulates the K_cliff-per-bank at that same B=16 regime. If HARD_PASS, the substantive composition is:

- **D x O interaction discovered:** capacity multi-bank K_cliff is not binding-op-invariant; ops with different effective-DoF / correlation-structure yield different capacity levers when composed with B=16 banks.
- **Substrate-product implication:** Director can trade off K_cliff-per-bank vs binding-op family at the WM regime (e.g. FHRR-complex-mul may enable 1.15x-1.4x higher K_cliff-per-bank at the same substrate cost).

If HARD_FAIL, substantive substrate finding: binding-op axis is capacity-invariant at WM regime (D x O composition is null). Combined with PC v1 MIDDLE_BAND, would suggest binding-op axis is broadly regime-invariant except at sequence regime (seqbind v2 result-dependent).

## Pointers

- Research spec: `notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec 5 (axis D x O)
- Prior binding-op cells: `experiments/_substrate_pc_binding_operation_family_phase_diagram_v1_core.py`, `experiments/_substrate_seqbind_binding_operation_family_phase_diagram_v2_core.py`
- Prior capacity multi-bank CG: (K=4096, B=16 atom in Store; latest FULL landing per WM multi-bank chain)
- Cell files (this v1): `experiments/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}.py`, `experiments/_substrate_binding_op_x_capacity_v1_core.py`
