# Pre-registration: substrate_hierarchical_bank_v2_S32_revival

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Skunkworks 310e1880 REVIVAL criterion for Axis H hierarchical_bank v1 HARD_FAIL closure.
**Base commit:** `bdae076b` (v1 landed HARD_FAIL: router SNR collapsed at M=64K, S=8).

## Why this cell exists (the gap)

v1 `hierarchical_bank` landed HARD_FAIL because router SNR = sqrt(N*S/M) collapsed to 1.012 at M=64K, N=8192, S=8, dropping routing_acc below the 0.85 floor. Skunkworks revival criterion (310e1880): **S >= 32 sub-banks** lifts router SNR to sqrt(N*S/M) = sqrt(4.096) = **2.024** at M=64K -- well above the 0.85 floor.

**Revival hypothesis:** with S=32, the hierarchical 2-level bank's router will NOT collapse under M=64K load, and the sub-bank readout (M_eff = M/S = 2000) will hold high recall (readout SNR = 2.024 identical to router SNR).

## Anchor

`substrate_hierarchical_bank_v2_S32_seed_{7,13,19}` (3 chunked sibling cells).
Shared core: `experiments/_substrate_hierarchical_bank_v2_S32_core.py`.

## Routing

- **Smoke queue:** local CPU (`.venv` direct invocation). Numpy-only; smoke ~2-5 min/seed at full M=64K.
- **Full queue:** `remote_cpu_queue` (CPU-eligible; numpy; no torch). GPU not required. Push routes through Orchestrator (harness-DENIED direct push from exp_dev).

## Delta from v1

| Parameter | v1 | v2 (REVIVAL) | Effect |
|---|---|---|---|
| `N_SUPER_BANKS` (S) | 8 | **32** | Router SNR 4x @ M=64K |
| `hierarchical_2level` arm renamed | `hierarchical_2level` | `hierarchical_S32_2level` | Distinct arm-hash + config-version discriminator |
| Router SNR @ M=64K | 1.012 (collapsed) | **2.024** (safe) | Predicted routing_acc lift from HARD_FAIL band to HP band |
| Readout SNR @ M=64K | 1.012 (marginal) | **2.024** (safe) | M_eff = M/S = 2000 |
| partition_by_source arm S | 8 (v1 CG) | **32** (v2 revival) | Fair-comparison baseline uses same S=32 |
| CRLB flat SNR @ M=64K | 0.358 | 0.358 | Unchanged (flat has no S; expected FLOOR) |

Everything else identical to v1: same primitives, same slot-tag / bundle-workspace design, same 4 hardening patterns, same META_RULEs.

## Codebook structures (OUTER axis; LOCKED)

3 structures, common signature `(items: (M, N), cues: (M, N)) -> (pred_idx: (M,), routing_acc: float, label: str)`:

| Structure | Mechanism | Baseline vs new |
|-----------|-----------|-----------------|
| `flat` | single flat codebook of M items; argmax over full M | baseline; no routing |
| `partition_by_source` | S=32 sub-banks each holding M/S items; oracle-source routing | ANCHOR 1 CG baseline (S-generalized) |
| `hierarchical_S32_2level` | context-router bank -> S=32 sub-banks; router-tag chooses sub-bank; sub-bank argmax | REVIVAL candidate |

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| codebook_structure (OUTER) | flat / partition_by_source / hierarchical_S32_2level | 3 |
| M (inner) | {4000, 16000, 64000} | 3 |
| N_dim (fixed) | 8192 | 1 |
| n_super_banks (partition + hierarchical) | 32 | 1 |
| seed (chunked; one per file) | {7, 13, 19} | 3 |

**Cardinality per seed:** `3 structures * 3 M = 9` phase points.
**Cardinality SMOKE per seed:** `3 structures * 2 M = 6` phase points (M in {4000, 64000}; DISCRIMINATOR-MUST-SURVIVE-SCALE: MUST include M=64000).
**Cardinality FULL across 3 seeds:** `9 * 3 = 27` total grid points.

## CRLB / capacity-feasibility validation (META_RULE_AG)

For bipolar codebook of size M in N-dim, matched-filter SNR = sqrt(N/(M-1)). Router SNR = sqrt(N*S/M).

Verified via `python -c "import math; ..."` on laptop 2026-07-01:

- **flat** at M=64000, N=8192: SNR = sqrt(8192/63999) = **0.358**; below cliff (M > N); recall predicted FLOOR
- **partition_by_source** at M=64000, S=32: per-sub-bank M/S = 2000; SNR = sqrt(8192/1999) = **2.024**; above cliff; recall predicted HP
- **hierarchical_S32_2level** at M=64000, S=32: readout SNR identical to partition (2.024) AND router SNR = sqrt(8192*32/64000) = sqrt(4.096) = **2.024**; well above 0.85 collapse floor
- **v1 comparison** at M=64000, S=8: router SNR = sqrt(8192*8/64000) = sqrt(1.024) = **1.012** (marginal; collapsed in v1 measurement)

**Revival criterion (Skunkworks 310e1880):** router SNR at M=64K, S=32 = 2.024 >= 0.85 floor.

## Pre-reg bands (LOCKED at module init)

**Per-point recall tiers:**
- SATURATED: `recall >= 0.995` (META_RULE_Q suspect-1.000)
- HARD_PASS: `0.80 <= recall < 0.995`
- MIDDLE_BAND: `0.50 <= recall < 0.80`
- FLOOR: `recall <= 0.10`
- HARD_FAIL: otherwise

**Cell-level FULL discriminator:**

- **HARD_PASS:** at M=64000, `capacity_per_slot(hierarchical_S32) >= 1.20 * capacity_per_slot(flat)` AND `routing_acc_hier >= 0.95` AND `routing_acc_hier < 0.995` (router imperfect; anti-Q) AND cross-seed cv on both metrics `< 0.10` AND cardinality_ok AND distinctness_self_report_pass AND `lift_vs_partition >= 1.05`
- **HARD_FAIL:** `routing_acc_hier < 0.85` at M=64000 (REVIVAL_HYPOTHESIS_FALSIFIED: S=32 not enough)
- **MIDDLE_BAND:** hierarchical wins at M<64K but degrades at M=64K, OR `routing_acc_hier` borderline [0.85, 0.95), OR cross-seed cv in [0.10, 0.20], OR lift_vs_flat OK but lift_vs_partition < 1.05

**Smoke discriminator (DISCRIMINATOR-MUST-SURVIVE-SCALE):**

Smoke MUST include M=64000. At smoke seed_7:
- `capacity_per_slot(hierarchical_S32) >= 1.10 * capacity_per_slot(flat)` at M=64000 (relaxed 1.10 vs 1.20 for single-seed smoke), OR
- Both partition + hierarchical are >=0.20 above flat at M=64000, AND
- `routing_acc_hier > 0.85` at M=64000 (revival criterion must fire)

If NEITHER: `BLOCK_DISPATCH` -- revival hypothesis falsified at smoke.

## Discipline gates (mandatory; all checked)

- **META_RULE_H (cardinality_ok):** `EXPECTED_N_UNITS_FULL=9`, `EXPECTED_N_UNITS_SMOKE=6`. Verdict-emitter HARD_FAILs on observed != expected.
- **META_RULE_AY:** verdict-emitter HARD_FAILs on `distinctness_self_report_pass == False`.
- **META_RULE_AX:** per-arm mechanism_hash + pred_pattern_hash distinct across 3 codebook structures.
- **META_RULE_AW:** identical config across seeds (3 sibling files import same core).
- **META_RULE_Q:** suspect-1.000 saturation check for both routing_acc and recall. If `routing_acc_hier >= 0.995`, downgrade verdict to MIDDLE_BAND.
- **META_RULE_AR:** partition-by-source is CG-baseline; hierarchical must LIFT above BOTH flat AND partition (>=1.05) to earn CG.
- **META_RULE_AF:** arms-must-differ; 3 codebook structures' outputs SHA-256 hashed per phase point.
- **META_RULE_AG:** CRLB / capacity-feasibility validated above.
- **META_RULE_J:** no silent except: blocks.
- **META_RULE_AC:** numbers in this pre-reg tagged.
- **META_RULE_AH:** atomic-final-metrics-write via `_seed_checkpoint.write_partial_key` then aggregate.
- **META_RULE_AT:** composition with ANCHOR 1 partition-by-source CG; hierarchical must outperform partition_S32 for CG.

## Schema-VET fields

- `cardinality_ok: bool`
- `arms_differ_verified: bool` (set at smoke gate via distinctness_self_report_pass)
- `final_metrics_atomicity: "tmp_replace"`
- `cell_chunked: true` (3 sibling cells; one seed per file)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true`
- `defensive_error_checking: passed_all_4_patterns`
- `crlb_floor_computed: "router SNR = sqrt(N*S/M) = 2.024 at M=64K S=32; readout M_eff=2000 SNR=2.024"`
- `revival_criterion_verified: true` (Skunkworks 310e1880; router SNR at M=64K S=32 >= 0.85 floor by 2.38x margin)
- `discriminator_reachability: true`
- `baseline_in_band: true` (flat at M=64K predicted FLOOR; partition/hierarchical at M=64K predicted HP)
- `sweep_alignment_verdict: ALIGNED`
- `discriminating_fraction: 1.0` (all 3 M-values expected discriminating for hier vs flat)
- `composition_edges: bipolar codebook -> router_S32 -> sub-bank argmax -> pred_idx SHAPE_MATCH`
- `positive_control_arms: flat @ M=4000, expected recall >= 0.80`
- `functional_requirements: 1. associative recall from cue; 2. routing arm distinguishable from flat via capacity-per-slot at M=64K; 3. routing_acc<1.000 (router imperfect); 4. routing_acc>0.85 (S=32 revival must fire)`

## Effort estimate

- `_substrate_hierarchical_bank_v2_S32_core.py`: ~570 LoC
- 3 sibling cells: ~215 LoC each x 3 = 645 LoC
- This pre-reg: ~140 lines
- **Total ~1350 LoC**
- **Estimated wallclock per seed FULL:** ~5-10 min on remote_cpu (numpy matmul at M=64K x N=8192)
- **Timeout per seed:** 1800s (30 min; 3x expected worst-case + margin)

## Falsifiable predictions

- **HARD_PASS:** hierarchical_S32 wins >=1.2x flat capacity at M=64K with routing_acc>0.95 + cv<10% + lift_vs_partition>=1.05
- **HARD_FAIL:** hierarchical_S32 routing_acc<0.85 at M=64K (REVIVAL FALSIFIED)
- **MIDDLE_BAND:** wins at M<64K but degrades at M=64K OR routing_acc borderline 0.85-0.95 OR lifts flat but not partition

## Relationship to v1

v2 is a REVIVAL, not a supersession. v1 is the falsifier for S=8 router regime; v2 tests S=32 rescue. If v2 lands HP, both cells stand as CG evidence for the S-dependence of router SNR (v1 = below-cliff arm; v2 = above-cliff arm) -- 5x-drill escalation eligible.
