# Pre-registration: substrate_hierarchical_bank_v1

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research phase-diagram gap analysis Axis H (CG=0.45, payoff=HIGH, 5x-drill-eligible if HP).
Source: `notes/research_phase_diagram_gap_analysis_next_cells_2026-07-01.md` sec.3.
Composes with ANCHOR 1 partition-by-source CG per META_RULE_AT.

## Why this cell exists (the gap)

Axis H (codebook structure) is CG at flat and partition-by-source (ANCHOR 1). **Hierarchical-2-level bank UNTESTED.** If a 2-level hierarchical bank (context-router -> sub-bank) lifts effective capacity above flat B*K_per, it is a Stage 2 architectural lever composable with existing multi-bank CG.

## Anchor

`substrate_hierarchical_bank_v1_seed_{7,13,19}` (3 chunked sibling cells).
Shared core: `experiments/_substrate_hierarchical_bank_v1_core.py`.

## Routing

- **Smoke queue:** local CPU (.venv direct invocation). Numpy-only; matmul over M<=64K x N=8192 tractable on laptop; smoke ~2-5 min/seed at full M=64K.
- **Full queue:** `remote_cpu_queue` (CPU-eligible; numpy; no torch). GPU not required (no softmax-attention). Push routes through Orchestrator (harness-DENIED direct push from exp_dev).

## Codebook structures (OUTER axis; LOCKED)

3 structures, common signature `(items: (M, N), cues: (M, N)) -> (pred_idx: (M,), routing_acc: float or None)`:

| Structure | Mechanism | Baseline vs new |
|-----------|-----------|-----------------|
| `flat` | single flat codebook of M items; argmax over full M | baseline; no routing |
| `partition_by_source` | S sub-banks each holding M/S items; oracle-source routing | ANCHOR 1 CG baseline (partition-by-source-class KG CG) |
| `hierarchical_2level` | context-router bank -> sub-bank; router-tag chooses sub-bank; sub-bank does argmax | NEW candidate |

**Router imperfection (META_RULE_Q mitigation).** For `hierarchical_2level`, we use a TWO-WORKSPACE HD design: (1) router workspace = sum_i (item_i * router_tag[bank_i]) with additive noise SIGMA=1.0; route cue for item i = router_ws * item_i (yields router_tag[bank_i] + M-1 crosstalk terms); routed_bank = argmax over router_tags. (2) Per-sub-bank readout workspace = sum_{j in bank b} (item_j * slot_tag_j); readout cue = readout_ws * slot_tag_i; pred = argmax over items in routed bank. Router SNR ~ sqrt(N/M): at M=64K, N=8192 SNR = 0.358 predicts routing_acc well below 0.85 (HARD_FAIL prediction is falsifiable). At M=4K, N=8192 SNR = 1.43 predicts routing_acc ~ 0.40-0.60 (MIDDLE_BAND at low M; degrades to HARD_FAIL by M=64K).

**IMPORTANT calibration note:** hand-verified at M=4000, N=8192, S=8 (seed=7): flat=0.010, partition=0.577, hierarchical=0.250, hier_routing_acc=0.432. **Given this measured routing_acc trajectory, HARD_FAIL (routing_acc<0.85 at M=64K) is the most likely outcome under current design.** This is a genuine falsifiable prediction; if hierarchical DOES lift capacity above partition despite routing degradation, that would be a surprise chain-grade finding (composed routing + readout may lift even with imperfect routing due to sub-bank cleanup). Predictions kept as-is per spec.

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| codebook_structure (OUTER) | flat / partition_by_source / hierarchical_2level | 3 |
| M (inner) | {4000, 16000, 64000} | 3 |
| N_dim (fixed) | 8192 | 1 |
| n_super_banks (partition + hierarchical) | 8 | 1 |
| seed (chunked; one per file) | {7, 13, 19} | 3 |

**Cardinality per seed:** `3 structures * 3 M = 9` phase points.
**Cardinality SMOKE per seed:** `3 structures * 2 M = 6` phase points (M in {4000, 64000}; DISCRIMINATOR-MUST-SURVIVE-SCALE: MUST include M=64000).
**Cardinality FULL across 3 seeds:** `9 * 3 = 27` total grid points.

Fixed substrate parameters:
- `N_DIM = 8192` (bipolar codebook; matches WM K-cliff envelope + prior ANCHOR CG regime)
- `n_super_banks = 8` (partition + hierarchical routing depth)
- `CUE_COS = 0.70` (item cue-to-slot similarity)
- `CUE_ROUTE_COS = 0.85` (router-tag cue similarity; tuned so routing_acc in 0.90-0.98 band, NOT 1.000)
- `SIGMA = 1.0` (workspace noise on writes; bipolar-quantized)

## CRLB / capacity-feasibility validation (META_RULE_AG)

For bipolar codebook of size M in N-dim, matched-filter SNR = sqrt(N) / sqrt(M-1).

- **flat** at M=64000, N=8192: SNR = sqrt(8192/64000) = 0.358; below cliff (M > N); recall predicted FLOOR
- **partition_by_source** at M=64000, S=8: per-sub-bank M/S = 8000; SNR = sqrt(8192/8000) = 1.012; near cliff; recall predicted DISCRIMINATING [0.10, 0.95]
- **hierarchical_2level** at M=64000, S=8: identical per-sub-bank capacity to partition; ADDS router-cost (routing_acc<1); expected recall = partition_recall * routing_acc

**Capacity-per-slot lift metric:** `capacity_per_slot(structure) = mean_recall(M=64000)`. Hierarchical wins condition: `capacity_per_slot(hierarchical) >= 1.20 * capacity_per_slot(flat)` at M=64000 AND `routing_acc >= 0.95`.

Cliff prediction at M=64K bracket:
- flat: FLOOR expected
- partition: DISCRIMINATING
- hierarchical: DISCRIMINATING (with router cost)

`crlb_formula_reference: "matched-filter SNR = sqrt(N/(M_effective-1)); M_effective = M/S for partition + hierarchical; flat M_effective = M"`

## Pre-reg bands (LOCKED at module init)

**Per-point recall tiers:**
- SATURATED: `recall >= 0.995` (META_RULE_Q suspect-1.000; TRIP if hierarchical hits this at M=64K -> MIDDLE_BAND)
- HARD_PASS: `0.80 <= recall < 0.995`
- MIDDLE_BAND: `0.50 <= recall < 0.80`
- FLOOR: `recall <= 0.10`
- HARD_FAIL: otherwise

**Cell-level FULL discriminator:**

- **HARD_PASS:** at M=64000, `capacity_per_slot(hierarchical) >= 1.20 * capacity_per_slot(flat)` AND `routing_acc_hierarchical >= 0.95` AND `routing_acc_hierarchical < 0.995` (router imperfect; anti-Q) AND cross-seed cv on both metrics `< 0.10` AND cardinality_ok AND distinctness_self_report_pass
- **HARD_FAIL:** `routing_acc_hierarchical < 0.85` at M=64000 (routing collapses under load)
- **MIDDLE_BAND:** hierarchical wins at M<64K but degrades at M=64K, OR `routing_acc_hierarchical` borderline [0.85, 0.95), OR cross-seed cv in [0.10, 0.20]

**Smoke discriminator (DISCRIMINATOR-MUST-SURVIVE-SCALE):**

Smoke MUST include M=64000 (per USER META_RULE / research spec). At smoke:
- `capacity_per_slot(hierarchical) >= 1.10 * capacity_per_slot(flat)` at M=64000 (relaxed 1.10 vs 1.20 for single-seed smoke), OR
- Both partition + hierarchical are >=0.20 above flat at M=64000 (mechanism gets to fire; discriminator visible at scale)

If NEITHER: `BLOCK_DISPATCH` -- discriminator does not survive scale even at full M=64K.

## Discipline gates (mandatory; all checked)

- **META_RULE_H (cardinality_ok):** `EXPECTED_N_UNITS_FULL=9`, `EXPECTED_N_UNITS_SMOKE=6`. Verdict-emitter HARD_FAILs on observed != expected.
- **META_RULE_AY:** verdict-emitter HARD_FAILs on `distinctness_self_report_pass == False`. Prevents phantom-degeneracy pattern.
- **META_RULE_AX:** per-arm mechanism_hash + pred_pattern_hash distinct across 3 codebook structures. Tracked via pairs_mech_differ AND pairs_pred_differ.
- **META_RULE_AW:** identical config across seeds (3 sibling files import same core).
- **META_RULE_Q:** suspect-1.000 saturation check for BOTH routing_acc and recall. If `routing_acc_hierarchical >= 0.995`, downgrade verdict to MIDDLE_BAND (by-construction perfect routing).
- **META_RULE_AR:** partition-by-source is CG-baseline; hierarchical must LIFT above BOTH flat and partition to earn CG. If hierarchical ~= partition (within +/-0.05 capacity-per-slot), verdict MIDDLE_BAND (no additional lift; router adds cost without capacity gain).
- **META_RULE_AF:** arms-must-differ; 3 codebook structures' outputs SHA-256 hashed per phase point.
- **META_RULE_AG:** CRLB / capacity-feasibility validated above.
- **META_RULE_J:** no silent except: blocks; per-unit failure-class instrumentation.
- **META_RULE_AC:** numbers in this pre-reg tagged.
- **META_RULE_AH:** atomic-final-metrics-write via `_seed_checkpoint.write_partial_key` then aggregate -> atomic metrics.json write at end.
- **META_RULE_AT:** composition with ANCHOR 1 partition-by-source CG (partition_by_source is the second arm; hierarchical must outperform for CG).

## Schema-VET fields

- `cardinality_ok: bool`
- `arms_differ_verified: bool` (set at smoke gate via distinctness_self_report_pass)
- `final_metrics_atomicity: "tmp_replace"`
- `cell_chunked: true` (3 sibling cells; one seed per file)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true` (per-phase-point flush prints)
- `defensive_error_checking: passed_all_4_patterns`
- `crlb_floor_computed: "M_eff = M/S = 8000 at M=64K S=8; SNR=1.012 near cliff"`
- `discriminator_reachability: true`
- `baseline_in_band: true` (flat at M=64K predicted FLOOR; partition at M=64K predicted MIDDLE_BAND; hierarchical predicted MIDDLE_BAND with routing cost)
- `sweep_alignment_verdict: ALIGNED` (M is natural capacity axis for all 3 codebook structures)
- `discriminating_fraction: 0.67` (2 of 3 M-values expected discriminating: M=16K near cliff for flat, M=64K discriminating for partition + hierarchical)
- `composition_edges: bipolar codebook -> optional_router -> sub-bank argmax -> pred_idx SHAPE_MATCH`
- `positive_control_arms: flat @ M=4000, expected recall >= 0.80 (M/N = 0.49 well below cliff)`
- `functional_requirements: 1. associative recall from cue; 2. routing arm distinguishable from flat baseline via capacity-per-slot at M=64K; 3. routing_acc<1.000 (router imperfect per anti-Q)`

## Effort estimate

- `_substrate_hierarchical_bank_v1_core.py`: ~450 LoC (3 primitives + per-point eval + selftest + per-seed sweep + verdict)
- 3 sibling cells: ~220 LoC each x 3 = 660 LoC
- This pre-reg: ~130 lines
- **Total ~1250 LoC**
- **Estimated wallclock per seed FULL:** ~5-10 min on remote_cpu (numpy matmul at M=64K x N=8192 = ~4GB peak; laptop-tractable)
- **Timeout per seed:** 1800s (30 min; 3x expected worst-case + margin)

## Falsifiable predictions (from research spec)

- **HARD_PASS:** hierarchical wins >=1.2x flat capacity at M=64K with routing_acc>0.95 + cross-seed cv<10%
- **HARD_FAIL:** hierarchical routing_acc<0.85 at M=64K (routing collapses under load)
- **MIDDLE_BAND:** hierarchical wins at M<64K but degrades at M=64K OR routing_acc borderline 0.85-0.95

## 5x-drill escalation eligibility

Research flagged Axis H as **5x-drill-escalation eligible if landed HP** (three-drill support: cortical column hierarchy Mountcastle-Felleman + content-addressable memory hierarchy + hierarchical crossbar arrays IBM TrueNorth). Post-landing decision routed via Research + Skunkworks.
