# Skunkworks landed-VET batch 15 — Stage 3 revival morning wave 2026-06-28

VERIFY-OFF-DATA via .venv Python; each metrics.json Read end-to-end on disk; per-arm cross-checked against Director's framings.

## Atoms landed (4; ledger 4 rows)

### Atom 1 -- PO N=2048 revival c1 MEASURED_MECHANISM (smoke)
- Path: `data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_smoke/metrics.json`
- Cell verdict: SMOKE_HARD_PASS
- Skunkworks tier: **MEASURED_MECHANISM** (BIAS-Q saturation auto-demote)
- Per-arm verified: A=0.190 / B=1.000 (saturated psz=10) / C=0.970 / D=0.840 / E=0.000 (random); lift_B_A=+0.81; lift_B_E=+1.00; arms_distinct=5; baseline rail OK at target 0.160 RAIL [0.110, 0.210]
- Delta: +0 (saturation prevents chain-grade; mechanism class confirmed)

### Atom 2 -- PO N=8192 revival c1 MEASURED_MECHANISM (smoke)
- Path: `data/exp_substrate_multihop_partition_oracle_at_v5_regime_revival_c1_n8192/metrics.json`
- Cell verdict: MIDDLE_BAND_SATURATED_AUTO_DEMOTE
- Skunkworks tier: **MEASURED_MECHANISM** (saturation + UPWARD rail breach)
- Per-arm verified: A=0.590 / B=1.000 / C=1.000 / D=0.990 / E=0.000; lift_B_A=+0.41; arms_distinct=5
- **Load-bearing finding:** BASELINE rail_breach UPWARD 3.7x (predicted ~0.160; observed 0.590) -> cone-collapse formula MISCALIBRATED at N=8192
- Delta: +0 (saturation + formula miscalibration; mechanism load-bearing)

### Atom 3 -- Hierarchical state-cond-disjoint v1 HONEST_NEGATIVE (smoke)
- Path: `data/exp_substrate_hierarchical_planner_state_conditioned_disjoint_v1_smoke/metrics.json`
- Cell verdict: HARD_FAIL
- Skunkworks tier: **HONEST_NEGATIVE_SMOKE** (proven negative; mechanism HURTS baseline)
- Per-arm verified (n_seeds=2): RAIL=1.000 / RAND=0.017 / FLAT=0.067 / SC=DJ=BOTH=0.000; both-flat=-0.067; arms_distinct=True; cardinality 360/360
- 2nd hierarchical-planning attempt fails (v1 + revival both); macro vocabulary non-compositional at depth=8; Sutton-Precup options redesign (drill ANCHOR 2) needed
- Delta: +0 (proven negative; do not re-attempt without redesign)

### Atom 4 -- META_RULE_AN cone-collapse-formula-N2048-calibrated discipline meta
- Evidence: Atom 1 (N=2048 formula tight: observed 0.190 in rail) + Atom 2 (N=8192 formula off 3.7x: predicted 0.160, observed 0.590)
- Rule: `crosstalk_std = sqrt((V_C_per_hop - 1) / N)` calibrated at N=2048 does NOT naively extrapolate to N>=8192; substrate has ~3.7x MORE headroom than the linear cone model predicts
- Discipline: any cell setting RAIL via cone-collapse at N>=4096 MUST include empirical baseline arm OR treat formula RAIL as guard not HP/HF gate
- Extends META_RULE_AL (substrate-cosine pre-encodes-schema-prior) at capacity layer; extends META_RULE_AM (substrate-already-does-X) at formula layer
- Delta: +0 (META rule; cert-neutral)

## NET CERT delta: 0

- PRE cert_n: 628 (verified live off Store)
- POST cert_n: 628
- +0 chain_grade / +2 MM / +1 HONEST_NEG / +1 META

## Director framings vs disk: all matched

- Cell 1 (revival c1 N=2048): Director called MM per saturation -> CORRECT (matches BIAS-Q auto-demote on disk)
- Cell 2 (revival c1 N=8192): Director called MM with rail-breach finding -> CORRECT (rail_breach=1/1 UPWARD; cone-collapse off 3.7x)
- Cell 3 (hierarchical SC-DJ): Director called HONEST_NEG -> CORRECT (both=0.000 hurts flat=0.067; arms_distinct; cardinality_ok)
- META_RULE_AN: Director proposed; evidence concrete (3.7x miscalibration); atomized.

## Refusals: none

All three Director framings survived verify-off-data; no Director-framing-errors this batch.

## Atomization commit

- Tool: `tools/atomize_skunkworks_batch15_stage3_revival_2026-06-28.py` (main) + `tools/_batch15_recovery_atom3_atom4_2026-06-28.py` (mid-flight recovery for cert_class enum mismatch)
- A5 PRE/POST cert_n window: 628 -> 628 verified at each write
- Round-trip Store re-load OK for all 4 atoms (atomized_by tag verified)
- Ledger: `data/substrate_index/meta/cert_ledger.jsonl` += 4 rows (3 atomize tool + 1 recovery)
