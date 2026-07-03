# Pre-reg: Exp 3E — Layer 0.75 v3-clean FULL arc-closure attempt

- date_authored: 2026-07-03
- cell_author: hdi_exp_dev (spawn)
- cell_path: `experiments/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py`
- prior_cells (heavy reuse):
  - `experiments/exp_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_smoke_2026_07_03.py` (Exp 3D — 9-arm structural v3 test; landed HARD_PASS_INTERFACE_POSITIVE 2026-07-03)
  - `experiments/exp_substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03.py` (Exp 3C — regime scale target)
  - `experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py`
- scope: `hub_concept_bridge_only` (identical to Exp 3B/3C/3D)

## Motivation and citation trail

Exp 3D SMOKE (2026-07-03) landed with `ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY = 0.7667`
MEASURED@`data/exp_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY`
= 92% of `ARM_ORACLE_COMPOSITION_SANITY = 0.8222` at N_DIM=4096, 30 queries × 3 seeds.

Skunkworks-verified per-arm decomposition of Exp 3D findings:
- MAIN stacked (S1 + S2 + v3) = 0.5111 MEASURED@same:per_arm_mean_accuracy.ARM_MAIN_LAYER075_STACKED_V3
- v3-only (uniform PPR + v3 filter + composition; NO S1, NO S2) = 0.7667 MEASURED@same
- Gap = 0.2556 = Stage 2 hub-dampen actively DEMOTES hop-2 hub-subject facts
  (mid IS a hub by construction; damp scales its outgoing edges by 0.30 → the
  PPR pool downweights the very facts v3 needs).

Skunkworks-filed discipline `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`:
isolated-component-at-SMOKE (v3 alone 0.767 at SMOKE) is NECESSARY but NOT
SUFFICIENT for arc-closure. Skunkworks recommended path (b): v3-clean FULL at
Exp 3C regime (N=8192, 100q × 3 seeds) with drop-S1S2 pipeline as MAIN arm,
subject to 3-seed CV discipline + all-seeds-above-bar gate.

Concept-query-before-dispatch (2026-07-03, `tools/substrate_query.sh "v3 clean
structural KG slot filter FHRR composition retrieval PPR uniform"`):
top cosine=0.2773 (`entity=structural_formula`, wordnet), below the 0.30 threshold
for prior-arc cell hit. Genuinely novel operationalization; no prior v3-clean cell exists.

## Precedents (MEASURED @ off-disk 2026-07-03)

Averaged 3 seeds (11, 17, 23) at N_DIM=4096:

| Metric | Exp 3D value | Reproduction gate |
|---|---|---|
| ORACLE composition sanity | 0.8222 | drift ≤ 0.10 (HALT if breached) |
| EXP3_BASELINE reproduction | 0.4111 | drift ≤ 0.10 (soft flag) |
| STAGE3_V1 (query-only rescore) | 0.0111 | drift ≤ 0.005 (soft flag) |
| STAGE3_V2 (iterative query-aug) | 0.0333 | drift ≤ 0.005 (soft flag) |
| V3_STACKED_WITH_S1S2 (Exp 3D MAIN) | 0.5111 | drift ≤ 0.05 (validates S1+S2-subtract finding) |
| MAIN_V3_CLEAN (Exp 3D S3V3_ONLY) | 0.7667 | discriminator — no drift gate; measured on THIS cell |
| RANDOM_CONTROL | 0.0556 | drift ≤ 0.10 (soft) |

## Arms (7)

Pruned from Exp 3D's 9 arms (drop stage1_only, stage2_only — v3-clean cell
doesn't need to re-witness those single-stage baselines):

1. `ARM_ORACLE_COMPOSITION_SANITY` — composition primitive on ground-truth chunks; ORACLE
2. `ARM_EXP3_BASELINE_REPRODUCTION` — Exp 3 BGE + PPR-union baseline
3. `ARM_STAGE3_V1_QUERY_ONLY_RESCORE` — Fix#28 confidence check ~0.011
4. `ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY` — Fix#28 confidence check ~0.033
5. `ARM_MAIN_V3_CLEAN` — **uniform PPR → v3 structural filter → composition**  (MAIN discriminator; target ~0.77+)
6. `ARM_V3_STACKED_WITH_S1S2` — Exp 3D MAIN reproduction (~0.511; validates S1+S2-subtract diagnosis)
7. `ARM_RANDOM_CANDIDATES_CONTROL` — chance ~0.05

Cardinality: `expected_n_units = 7 arms × 3 seeds = 21`.

## Bands (Skunkworks-derived arc-closure discipline, per `feedback_arc_continuation_vs_arc_closure_isolated_smoke_not_enough_2026-07-03`)

- `HARD_PASS_FULL_ARC_CLOSURE`:
  MAIN_V3_CLEAN ≥ 0.90 × ORACLE (~0.74)
  AND per-seed coefficient of variation (cv) < 0.10
  AND ALL individual seeds ≥ 0.60
  → retrieval-architecture arc CLOSES on hub-concept-bridge scope with 3-seed stability.

- `HARD_PASS_MEASURED_MECHANISM`:
  MAIN_V3_CLEAN ≥ 0.60 × ORACLE (~0.49) but not-full-closure (either cv breach OR seed-below-0.60)
  → mechanism validated at scale, but arc-closure not yet certified; stability gap surfaced.

- `MIDDLE_BAND`:
  0.413 ≤ MAIN_V3_CLEAN < 0.60 × ORACLE (~0.49)
  → partial signal; not confidently above Exp3 baseline threshold.

- `HARD_FAIL`:
  MAIN_V3_CLEAN < 0.413 (below Exp3 baseline)
  → v3-clean regressed at scale; SMOKE result was regime-artifact.

- `HALT_ORACLE_DRIFT`: |ORACLE - 0.8222| >= 0.10 → composition primitive changed; do NOT trust MAIN interpretation.
- `FLAG_V3_STACKED_S1S2_DRIFT`: |V3_STACKED_WITH_S1S2 - 0.5111| >= 0.05 → cannot validate S1+S2-subtract diagnosis; MEASURED_MECHANISM tier at best.
- `FLAG_V1_HF_DRIFT`: |STAGE3_V1 - 0.0111| >= 0.005 (soft; Fix#28 confidence)
- `FLAG_V2_HF_DRIFT`: |STAGE3_V2 - 0.0333| >= 0.005 (soft; Fix#28 confidence)

**Fix#28-mirror discipline:** verdict must NOT frame as arc-closure unless ALL 4 arc-closure
criteria met simultaneously (`MAIN >= 0.74` AND `cv < 0.10` AND `all seeds >= 0.60` AND
`V3_STACKED_WITH_S1S2` reproduces within 0.05). Any single breach → downgrade to
MEASURED_MECHANISM tier (still HARD_PASS-family) with explicit gap disclosure.

## SCHEMA-VET pre-dispatch checklist

### 1. `cardinality_ok` (META_RULE_H)
`EXPECTED_N_UNITS = 7 arms × 3 seeds = 21`; verdict counts and emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on breach.

### 2. Per-unit failure-class instrumentation (META_RULE_J)
Only `except Exception:` (no bare / no BaseException) with `_write_crash_metrics` diagnostic.

### 3. Discriminator-fires gate (META_RULE_K)
v3 slot-fire count (n_slot_fired vs n_fallback) logged per-seed. If v3-clean fallback rate > 30% across seeds, emit FLAG. Smoke required to have slot-fire > 0 on at least 50% of diag queries.

### 4. Strictly-above-floor target (META_RULE_L)
`HARD_PASS_FULL_ARC_CLOSURE` uses 0.90 × ORACLE (not the raw floor).

### 5. Per-arm HP_SCOPE
`HP_SCOPE: {ARM_MAIN_V3_CLEAN: [HP_FULL_ARC_CLOSURE, HP_MEASURED_MECHANISM]}`.
Reproduction arms (ORACLE, EXP3_BASELINE, V1, V2, V3_STACKED_WITH_S1S2) subject to drift gates ONLY (not HP gates).

### 5b. Calibration-check (META_RULE_M)
`calibration_check: default_ok_for_this_regime` — v3 has NO tunable thresholds (subject/relation slot match is boolean); Exp 3D SMOKE established default_ok at N=4096.

### 6. ARMS-MUST-DIFFER (META_RULE_AF)
Per-arm prediction-array SHA256 verified with SUCCESS-MODE EXEMPTION for ARM_MAIN_V3_CLEAN vs ARM_ORACLE when full GT-coverage achieved (mechanism achieved GT-parity → composition emits identical output by mathematical necessity).

### 7. ATOMIC-FINAL-METRICS-WRITE (META_RULE_AH)
`final_metrics_atomicity: tmp_replace` — write to `metrics.json.tmp` then `os.replace`.

### 8. `except SystemExit: raise` BEFORE `except Exception`
Present at outer try/except; no BaseException handler.

### 9. CRLB / capacity-feasibility
`crlb_floor_computed = 0.035` THEORETICAL@sqrt(K_final/N_dim) = sqrt(5/8192) ≈ 0.025 at FULL N_DIM=8192
HP target 0.74 >> 0.035; discriminator_reachability = True.

### 10. `baseline_in_band` (META_RULE_AG)
EXP3_BASELINE expected ~0.41 (Exp 3D MEASURED); well inside [0.05, 0.95] band.

### 11. All numbers tagged (META_RULE_AC)
See "Precedents" table above; all values MEASURED@.

### 13. CHUNKED cell / start_marker / crash_diagnostic / heartbeat
- `cell_chunked: False` (single cell with in-cell seed loop; 3 seeds acceptable for
  ~7-15 min FULL wall on GPU — chunked overhead not justified. Runner-death risk
  mitigated by short wall + start_marker + heartbeat.)
- `start_marker_written: True`
- `crash_diagnostic_present: True`
- `heartbeat_present: True` (uses `experiments._cell_heartbeat.CellHeartbeat`
  wrapping the per-query loop with total_units = n_seeds × n_queries_target × 7 arms)
- `defensive_error_checking: passed_all_4_patterns`

### 15. TEST-DESIGN gates
- A) `sweep_alignment_verdict: ALIGNED` — no sweep axis; single-point per arm × seed
- B) `discriminating_fraction: 1.0` — 1/1 point in band (MAIN target 0.60-0.90 predicted)
- C) `composition_edges: [ppr_union -> v3_filter -> composition]` all SHAPE_MATCH
  (v3 output = subset of candidate_indices int list; composition input is `List[int]` of fact indices — SHAPE_MATCH proven at Exp 3D)
- D) `positive_control_arms`: ARM_EXP3_BASELINE_REPRODUCTION (chain-grade Exp 3C ORACLE_B analog),
  ARM_ORACLE_COMPOSITION_SANITY (composition primitive reproduce), ARM_V3_STACKED_WITH_S1S2 (Exp 3D MAIN reproduce). Tolerances: 0.10 ORACLE, 0.10 baseline, 0.05 V3_STACKED. `regime_extension_audit: SHAPE_MATCH` (SMOKE→FULL is same corpus family, wider N and query count)
- E) `functional_requirements`: 
  - "retrieve hop-1 fact (subj=e0, rel=r2)" → v3 subject/relation slot match
  - "retrieve hop-2 fact (subj=bridge, rel=r1)" → v3 subject/relation slot match with bridge extraction
  - "compose retrieved hops to answer" → FHRR composition primitive (chain-grade)

### 16. RUN_MODE VERIFICATION POST-DISPATCH
Cell reads `HDLAB_RUN_MODE` env var and argv; `--full` selects FULL, `--smoke` SMOKE, `--self-test` selftest.
FULL regime writes `run_mode: "full"` to metrics.json; caller verifies via runner_status.

### 17. PRINT-PROGRESS FLUSHING
All progress logs use `flush=True` + `sys.stdout.reconfigure(line_buffering=True)` at cell entry.
`progress_logging: print_flush_true`
`progress_cadence_expected_s: ~10` (per-seed heartbeat during BGE encoding + per-query loop)

## Compute architecture

- **class: mixed with justification**. BGE encoding is batched (torch, batch=32). PPR + KG traversal + FHRR composition per query is sequential-CPU (chained retrieval where each hop depends on prior). Sequential dependencies are genuine (hop-2 subject = mid extracted from hop-1 result). Per-query wall < 1s at N=8192 → total wall for 100q × 3 seeds × 7 arms ≈ ~10-15 min. Under 10s / phase-point threshold that would require batching justification.
- **storage: sharded** — each fact is its own vector (`fact_hds[i]` per index); no bundled composition. Composition primitive iterates over retrieved facts (up to K_FINAL=5) and picks best per-hop via argmax. Sharded is correct storage for multi-hop composition per META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW.

## Regime

| Field | SMOKE (local) | FULL (remote GPU / CPU) |
|---|---|---|
| N_DIM | 4096 | 8192 |
| N_QUERIES_TARGET | 24 | 100 |
| SEEDS | [11] | [11, 17, 23] |
| top_k (BGE) | 5 | 5 |
| PPR alpha / iters | 0.15 / 5 | 0.15 / 5 |
| K_FINAL | 5 | 5 |
| B_BRIDGES | 5 | 5 |
| target wall | ~30-60s | ~10-30 min |

## Timeout estimation

SMOKE (1 seed × 24 queries × 7 arms) at N_DIM=4096: extrapolate from Exp 3D per-seed 27-28s at 30 queries × 9 arms → about (24/30) × (7/9) × 28 ≈ 17s per seed at same N → SMOKE ≈ 30-60s wall (with BGE fixed setup ~3-5s + first-query dependency load). Use SMOKE cap 180s.

FULL (3 seeds × 100 queries × 7 arms) at N_DIM=8192: extrapolate from Exp 3D per-seed 28s (30q × 9 arms at N=4096) → ~28 × (100/30) × (7/9) × (8192/4096)^1.0 ≈ 145s per seed × 3 seeds ≈ 435s ≈ 8 min. Buffer 3x = **timeout_s = 1800 (30 min)** conservative.

Per USER-locked 2026-07-01: SMOKE only on local_cpu_queue; FULL routed to remote via hdi_orchestrator.

## Rollback and iteration policy

If SMOKE HARD_FAIL: deep-dive per USER-locked HF-deep-dive policy before pivoting to path (a) BridgeRAG tripartite.
If SMOKE MIDDLE_BAND: present to Director for regime assessment.
If SMOKE HARD_PASS (any tier): hdi_orchestrator dispatches remote FULL to overnight_queue.
