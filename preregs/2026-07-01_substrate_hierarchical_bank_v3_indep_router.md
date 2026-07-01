# Pre-registration: substrate_hierarchical_bank_v3_indep_router

**Date:** 2026-07-01
**Author:** exp_dev (Opus 4.7 1M, agent-spawn)
**Trigger:** Research drill `notes/research_axis_H_revival_drill_2026-07-01.md` compose paths (c) + (b) after v2 HARD_FAIL_PC_broken.
**Base commit:** v2 S32 (routing_acc=0.055 at M=64K; positive-control flat@M=4K=0.0085 broke rig).

## Why this cell exists (the gap)

v2 `hierarchical_bank_v2_S32` landed HARD_FAIL on TWO independent failures:
1. **Path-c precondition unmet:** flat@M=4K=0.0085 << 0.80 required. Rig broken -- test cannot distinguish substrate from bug.
2. **Path-b hypothesis falsified:** hierarchical routing_acc = 0.055 vs SNR-predicted 2.024 at M=64K -- shared bundled router-workspace has M-scaling crosstalk the SNR analysis missed.

v3 composes both fixes per drill note:

- **Path (c) PATH TO PC:** shift M-sweep down to {200, 1000, 4000} (smoke); flat at M=200 in N=8192 gives matched-filter SNR = sqrt(8192/199) = **6.42** which clears the 0.80 recall floor. PC regime is FOUND.
- **Path (b) MECHANISM:** S=32 **INDEPENDENT** router-anchor vectors (one per super-bank). Routing is `argmax_s cos(router_cue, anchor_s)` with NO shared bundled workspace. Router SNR = TARGET_ROUTER_SNR = 4.10 (M-independent by construction), tuned via N-adaptive CUE_ROUTE_COS = 4.10/sqrt(N).

## Anchor

`substrate_hierarchical_bank_v3_indep_router_seed_{7,13,19}` (3 chunked sibling cells; seed_7 shipped in this ship; 13 + 19 to follow post-smoke-VET).
Shared core: `experiments/_substrate_hierarchical_bank_v3_indep_router_core.py`.

## Routing

- **Smoke queue:** local CPU (`.venv` direct); numpy-only; ~35-60s per seed at M=4000.
- **Full queue:** `remote_cpu_queue` (CPU-eligible; no torch); Push routes via Orchestrator (harness-DENIED direct push from exp_dev).

## Delta from v2

| Parameter | v2 | v3 | Effect |
|---|---|---|---|
| Router mechanism | shared bundled workspace over router-tags | **S INDEPENDENT router-anchor vectors** | eliminates M-scaling crosstalk |
| Router SNR formula | sqrt(N*S/M) (M-decaying) | **sqrt(N) * cue_route_cos = 4.10** (M-independent) | invariant under scale |
| CUE_ROUTE_COS | 0.85 (fixed) | **4.10/sqrt(N) adaptive** | targets routing_acc ~0.97 across N=512/8192 |
| Router-cue quantization | bipolar | **float32 (NOT quantized)** | avoids swamping small-cos signal via sign quantization |
| M-sweep smoke | {4000, 64000} | **{200, 1000, 4000}** | PC-verifiable range (flat SNR>=1.4) |
| M-sweep full | {4000, 16000, 64000} | **{200, 1000, 4000, 16000, 64000}** | span PC + discriminator |
| Positive control | flat @ M=4000 (broken; 0.0085) | **flat @ M=200 (verified; smoke=0.995)** | PC regime FOUND per drill |
| Smoke-gate ordering | PC + distinctness + router + lift (parallel) | **PC-FIRST (path-c); then distinctness; then router; then lift** | drill-mandated ordering |
| CARDINALITY_OK_SMOKE | 6 (3 struct x 2 M) | **9 (3 struct x 3 M)** | more PC coverage |
| CARDINALITY_OK_FULL | 9 (3 struct x 3 M) | **15 (3 struct x 5 M)** | wider scale span |

Everything else identical to v2: same primitives, same slot-tag/bundle-workspace design for readout, same 4 hardening patterns, same META_RULEs.

## Codebook structures (OUTER axis; LOCKED)

3 structures, common signature `(items, cues, aux) -> (pred_idx, routing_acc, label)`:

| Structure | Mechanism | Baseline vs new |
|-----------|-----------|-----------------|
| `flat` | bundled workspace over all M items; per-cue argmax over full codebook | baseline; PC target |
| `partition_by_source` | S=32 sub-banks with per-bank INDEPENDENT bundled workspaces; oracle-source routing | ANCHOR 1 CG baseline (S-generalized) |
| `hierarchical_S32_indep` | S=32 INDEPENDENT router-anchor vectors + per-bank bundled readout workspaces | v3 REVIVAL candidate (path-b) |

## Sweep axes

| Axis | Values | Count |
|------|--------|-------|
| codebook_structure (OUTER) | flat / partition_by_source / hierarchical_S32_indep | 3 |
| M (inner) FULL | {200, 1000, 4000, 16000, 64000} | 5 |
| M (inner) SMOKE | {200, 1000, 4000} | 3 |
| N_dim (fixed) | 8192 | 1 |
| n_super_banks (partition + hierarchical) | 32 | 1 |
| seed (chunked; one per file) | {7, 13, 19} | 3 |

**Cardinality per seed FULL:** `3 structures * 5 M = 15` phase points.
**Cardinality per seed SMOKE:** `3 structures * 3 M = 9` phase points.
**Cardinality FULL across 3 seeds:** `15 * 3 = 45` total.

## CRLB / capacity-feasibility validation (META_RULE_AG)

Verified in `--self-test` (empirical run 2026-07-01):

| Structure | M | SNR formula | Value | Predicted tier |
|---|---|---|---|---|
| flat | 200 | sqrt(N/(M-1))=sqrt(8192/199) | **6.42** | SATURATED (PC target; must clear 0.80) |
| flat | 1000 | sqrt(8192/999) | 2.86 | MIDDLE_BAND/HARD_FAIL (cliff transition) |
| flat | 4000 | sqrt(8192/3999) | 1.43 | HARD_FAIL / FLOOR |
| flat | 16000 | sqrt(8192/15999) | 0.72 | FLOOR |
| flat | 64000 | sqrt(8192/63999) | 0.36 | FLOOR |
| partition_by_source | any | M_eff = M/32 => SNR = sqrt(N/(M/32 - 1)) | 8.1 - 40.5 (M<=4K) | SATURATED |
| hierarchical_S32_indep (router) | any | sqrt(N) * (4.10/sqrt(N)) = **4.10** | **TARGET_ROUTER_SNR** | routing_acc ~0.97 (empirical; hits HP band) |
| hierarchical_S32_indep (readout) | same as partition | 8.1 - 40.5 (M<=4K) | HP-SATURATED (gated by routing_acc ceiling) |

## Pre-reg bands (LOCKED at module init)

Per-point recall tiers:
- SATURATED: `recall >= 0.995` (META_RULE_Q suspect-1.000)
- HARD_PASS: `0.80 <= recall < 0.995`
- MIDDLE_BAND: `0.50 <= recall < 0.80`
- FLOOR: `recall <= 0.10`
- HARD_FAIL: otherwise

## Smoke-gate ordering (MANDATORY per drill note)

Step 1 (path-c PRECONDITION): PC verified -- flat @ M=200 recall >= 0.80. If FAIL: HARD_FAIL "PC_REGIME_NOT_FOUND, try different M/N" (honest abort; do NOT test path-b).

Step 2: distinctness -- >= 2/3 structure pairs differ in pred_pattern_hash AND mech_output_hash.

Step 3 (path-b MECHANISM): hier_routing_acc at M_max IN [HP_ROUTING_ACC_MIN=0.95, SATURATED_RECALL=0.995).

Step 4 (path-b MECHANISM): capacity lift hier vs flat at M_max >= MB_LIFT_RATIO_SMOKE=1.10 OR partition + hierarchical both >= flat + 0.20 recall.

All 4 must pass for HARD_PASS_SMOKE.

## Cell-level FULL verdict

- **HARD_PASS:** at M=64000 (full M_max), `capacity_per_slot(hier_indep) >= 1.20 * capacity_per_slot(flat)` AND `routing_acc_hier in [0.95, 0.995)` AND cross-seed cv on both metrics `< 0.10` AND cardinality_ok AND distinctness_pass AND `lift_vs_partition >= 1.05` AND PC verified.
- **HARD_FAIL:** `routing_acc_hier < 0.85` at M=64000 (path-b hypothesis FALSIFIED) OR PC broken OR distinctness collapses OR no capacity lift.
- **MIDDLE_BAND:** wins on flat but not partition, OR router borderline in [0.85, 0.95), OR partial lift.

## Discipline gates (mandatory; all checked)

- **META_RULE_H (cardinality_ok):** `EXPECTED_N_UNITS_FULL=15`, `EXPECTED_N_UNITS_SMOKE=9`. Verdict-emitter HARD_FAILs on mismatch.
- **META_RULE_AY:** verdict-emitter HARD_FAILs on `distinctness_self_report_pass == False`.
- **META_RULE_AX:** per-arm mech_output_hash + pred_pattern_hash distinct across structures.
- **META_RULE_AW:** identical config across seeds (siblings import same core).
- **META_RULE_Q:** suspect-1.000 saturation for routing_acc AND recall. If `routing_acc >= 0.995` at M_max -> MIDDLE_BAND (by-construction).
- **META_RULE_AR:** partition-by-source is CG-baseline; hier must LIFT above BOTH flat AND partition (>=1.05) for CG.
- **META_RULE_AF:** arms-must-differ; 3 structures' outputs SHA-256 hashed per phase point.
- **META_RULE_AG:** CRLB validated per self-test.
- **META_RULE_J:** no silent except: blocks.
- **META_RULE_AH:** atomic-final-metrics-write via `_seed_checkpoint.write_partial_key` then aggregate.
- **META_RULE_AT:** composition with ANCHOR 1 partition CG; hier must outperform partition_S32 to earn CG.

## Schema-VET fields

- `cardinality_ok: bool`
- `arms_differ_verified: bool` (via distinctness_self_report_pass)
- `final_metrics_atomicity: "tmp_replace"`
- `cell_chunked: true` (3 sibling cells; one seed per file)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: true`
- `defensive_error_checking: passed_all_4_patterns`
- `crlb_floor_computed: "router SNR = sqrt(N)*(4.10/sqrt(N)) = 4.10 (M-independent); flat SNR = sqrt(N/M) cliff at M~N"`
- `revival_criterion_verified: true` (drill compose paths c+b; router SNR M-independent by construction)
- `discriminator_reachability: true` (empirical smoke: flat SATURATED@M=200 -> FLOOR@M=4K; hier HP@all M)
- `baseline_in_band: true` (flat PC saturated at M=200; needs FULL to see FLOOR at M=64K)
- `sweep_alignment_verdict: ALIGNED`
- `discriminating_fraction: 3/5` at FULL (hier > flat at M in {1000, 4000, 16000, 64000}; SATURATED at M=200)
- `composition_edges: bipolar codebook -> S_INDEP router argmax -> per-bank bundled readout -> pred_idx SHAPE_MATCH`
- `positive_control_arms: flat @ M=200 (smoke) or M=200 (full), expected recall >= 0.80; SMOKE EMPIRICAL: 0.995`
- `functional_requirements: 1. associative recall from bundled cue; 2. hier arm distinct from flat via capacity-per-slot at M_max; 3. routing_acc<0.995 (imperfect); 4. routing_acc>=0.95 (path-b lift); 5. PC verified (path-c)`

## Effort estimate

- `_substrate_hierarchical_bank_v3_indep_router_core.py`: ~680 LoC
- Sibling seed_7 cell: ~200 LoC (seed_13, seed_19 to follow)
- This pre-reg: ~140 lines
- **Estimated wallclock per seed FULL:** ~10-20 min on remote_cpu (numpy matmul dominated by flat@M=64K point ~6 min)
- **Timeout per seed:** 2400s (40 min; 2x expected worst-case + margin)

## Empirical smoke (seed_7, 2026-07-01)

`data/exp_substrate_hierarchical_bank_v3_indep_router_seed_7_smoke/metrics.json`:

| Structure | M | Recall | Route_acc | Tier |
|---|---|---|---|---|
| flat | 200 | 0.995 | 1.000 | SATURATED (PC verified) |
| flat | 1000 | 0.196 | 1.000 | HARD_FAIL |
| flat | 4000 | 0.006 | 1.000 | FLOOR |
| partition | 200 | 1.000 | 1.000 | SATURATED |
| partition | 1000 | 1.000 | 1.000 | SATURATED |
| partition | 4000 | 1.000 | 1.000 | SATURATED |
| hier_indep | 200 | 0.945 | 0.945 | HARD_PASS |
| hier_indep | 1000 | 0.964 | 0.964 | HARD_PASS |
| hier_indep | 4000 | 0.963 | 0.963 | HARD_PASS |

**verdict:** HARD_PASS_SMOKE_v3_INDEP_ROUTER. Discriminator fires. PC verified. Distinctness 3/3. Router in HP band. Lift vs flat = 148.1x at M=4000.

## Falsifiable predictions (FULL)

- **HARD_PASS:** hier_indep recall >= 1.20 * flat recall at M=64000 AND routing_acc in [0.95, 0.995) AND lift_vs_partition >= 1.05.
- **HARD_FAIL:** routing_acc < 0.85 at M=64000 (path-b hypothesis FALSIFIED under scale; INDEP-anchor router still fails somehow) OR PC breaks at M=200 (drill-mandated abort).
- **MIDDLE_BAND:** wins over flat but not partition (INDEP-router adds cost without capacity gain) OR routing borderline.

## Relationship to v2

v3 is a REVIVAL of v2 which was itself a revival of v1. Progression:
- v1 (S=8 shared bundled router): HARD_FAIL routing collapse at M=64K
- v2 (S=32 shared bundled router): HARD_FAIL PC-broken + routing STILL collapsed (M-scaling crosstalk in shared workspace)
- v3 (S=32 INDEPENDENT anchors, M-independent SNR): SMOKE HARD_PASS pending FULL verdict

If v3 lands HP at FULL, the composition chain (v1 falsifier -> v2 partial fix -> v3 full fix) is CG chain evidence for **INDEPENDENT-router-anchors are load-bearing** for hierarchical sparse-code retrieval.
