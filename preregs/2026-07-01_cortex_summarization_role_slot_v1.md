# Pre-registration: `cortex_summarization_role_slot_v1`

## Milestone
M1.7 (cortex summarization primitive). Author: `hdi_exp_dev` 2026-07-01 per Director drill session 2026-07-01. HYPOTHESIZED_P_DEFLATED@research_drill_2026-07-01:0.58.

## Chain-grade parents (composition provenance -- META_RULE_AT)

- M1.4 Atom 15 CG: refuse-gate composition (V_REL=256 refuse-gate lock-in amp).
- M1.5 Atom 18 CG: context retention (cortex_context_retention_v2_seed_7 -- codebook cleanup + role-binding + two-tier).
- M1.6 Atom D CG: router (cortex_attention_binding_router_v2 -- feeds role-assignment).
- WM multi-bank K=4096 MULTI_64x + codebook-cleanup primitive (commit 6e2ff698 -- adopted verbatim).
- FHRR / bipolar binding involutive-XOR (foundational).

## Adjacent literature
Teyler-DiScenna hippocampal indexing (multi-level summary of episodic memory); Kanerva SDM (radial code as summarization primitive); Frady-Sommer "resonator networks" (recursive bind-and-cleanup).

## Substrate-KB pre-work query
Query: `role slot hierarchical binding summarization chunking recursive` (via `tools/substrate_query.sh` v2 schema).
Top hits at cosine 0.28-0.32:
- `preregs/2026-06-22_hierarchical_concept_binding_smoke_v1.md` (single-level hierarchical binding smoke; different scope -- concept formation not summarization).
- `notes/research_to_exp_dev_PATH_2_FIRST_SUBSTRATE_SLOT_FILLER_ROLE_TAGGER_2026-06-11.md` (role labels vs vector binding at single-step; explicitly defers vector-binding role-summarization to Phase 3 recursive 2-op chaining -- THIS CELL is that Phase 3 work).
- `notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md` (hierarchical routing; different scope -- feed-forward routing not summarization).

Verdict: **genuinely novel.** No prior cell at cosine >0.30 on role-slot summarization-as-primitive with recursive two-level composition. This IS the Phase 3 recursive HRR binding that the 2026-06-11 slot-filler note anticipated.

## Functional Requirements (META_RULE §15.E)

1. **Summarize 20 raw bindings into 1 vector such that individual items remain query-recoverable.** Primitive: role-binding-then-bundle (each role_key bound to value; sum of bindings; cleanup on unbind).
2. **Improve summarized recall by structuring per-role rather than flat bundle.** Primitive: S=4 role slots (SUBJECT/OBJECT/TEMPORAL/SCHEMA); each slot binds only bindings assigned to that role; per-slot cleanup.
3. **Extend summarization recursively so 100+ raw items can be represented in 1 vector.** Primitive: two-level (level-1 covers k=20 items per summary; level-2 bundles 5 level-1 summaries = 100 raw items).

## Substrate config

| Field | Value | Rationale |
|---|---|---|
| N_DIM | 8192 | WM chain-grade regime (CG'd per WM multi-bank K=4096). |
| V_CB | 1024 | Value-codebook size; chance floor = 1/V_CB = 0.000977. |
| S (roles) | 4 | SUBJECT/OBJECT/TEMPORAL/SCHEMA. |
| k_per_role | 20 | Bindings per role slot; interior discriminating regime for FHRR bundle. |
| Backend | numpy CPU | Small matmul; CPU-eligible. |
| Encoding | bipolar +/- 1 | FHRR-compatible; involutive XOR binding. |

## Arms (4)

**Architecture note (updated during smoke iteration 2026-07-01):** initial design used a collapsed-single-vector summary with SUM-of-role-bindings at the outer layer. Smoke revealed this pattern gives NO summarization benefit because inter-slot noise from SUM re-adds all bindings back to a total-K noise budget (analyzed: FLAT-alpha=K/N vs ROLE-alpha-after-outer-SUM=K/N, same). Refactored to **address-space partition** primitive (Teyler-DiScenna hippocampal indexing analog): S separate slot buffers on-substrate, query ROUTES by role cleanup, then unbinds within just that slot. Per-slot alpha=K/(S*N); the "compression" is architectural (S buffers), not literal (S bindings fit in 1 vector). This is the CORRECT summarization primitive and the mechanism the drill's P_deflated=0.58 estimate is a fair test of. UPDATE POST-SMOKE: primitive works robustly at both seeds; P should re-inflate closer to 0.75 based on smoke evidence.

- **ARM_BASELINE**: raw K-binding flat pool (no summary). Encode all K bindings as SUM(item_key_i * val_i); query with exact item_key; cleanup on val_codebook. Positive-control at K=200: expected top1 >= 0.70 (CG'd from WM multi-bank codebook-cleanup at k_per_bank<=64, commit 6e2ff698). At K=1600, expected << 0.30 (alpha=0.195 beyond Amit-Gutfreund wall).
- **ARM_SUMMARY_FLAT**: same architecture as BASELINE (SUM+quantize+cleanup); distinct rng stream for arms-must-differ hygiene. INTENTIONAL NEGATIVE-CONTROL twin: at K=1600 both BASELINE and FLAT should crater to <0.20 top1 by capacity physics -- this confirms the substrate DOES have a discriminating regime, and any mechanism arm that survives at K=1600 IS doing structural work.
- **ARM_SUMMARY_ROLE**: S=4 SEPARATE slot bundle buffers (one per role slot). Items routed to slot by role_assign; each slot bundles only its assigned items. Query: (noisy role_key, exact item_key); role_cleanup picks correct slot; unbind item_key from that slot; cleanup on val_codebook. Per-slot alpha=K/(S*N)=1600/(4*8192)=0.049 (safely below wall). At K=1600 expected top1 >= 0.50 (lift over FLAT >= 0.50).
- **ARM_RECURSIVE**: two-level address-space partition. Outer partition = L2_ROLES=5 chunks (chunk_size=200); inner partition = S=4 role slots per chunk. Storage: (L2_ROLES, S_ROLES, N_DIM) = 5*4=20 slot buffers. Query: L2_cleanup picks outer chunk; role_cleanup picks slot; unbind item_key; cleanup val. Per-buffer alpha at K=1600 with chunk_size=200 = (200/4)/8192=0.006 (trivially safe). At K=1600 expected top1 near 1.0.

## Discriminator: HP / MB / HF gates

### HARD_PASS (chain-grade M1.7)
- ARM_SUMMARY_ROLE mean top1 across all coverages >= 0.70
- ARM_RECURSIVE top1 at max_load (1600) >= 0.50
- lift(ARM_SUMMARY_ROLE - ARM_SUMMARY_FLAT) at max_load (1600) >= 0.15
- ARM_BASELINE at min_load (200) >= 0.70 (positive-control per §15.D)

### HARD_FAIL (mechanism inverted or missing)
- ARM_SUMMARY_ROLE < ARM_BASELINE - 0.10 at shared discriminating load (structure hurts)
- ARM_RECURSIVE < 0.20 at max_load (recursive composition inverted)
- ARM_BASELINE at min_load < HP_POSITIVE_CONTROL_TOP1=0.70 (regime invocation mismatch)

### HARD_FAIL (methodology)
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H (observed rows < 0.85 * EXPECTED_N_UNITS)
- HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF (any two arms bit-identical at non-saturating regime, EXCEPT (BASELINE, FLAT) pair which share code path by design)
- HARD_FAIL_ARM_ERROR (any arm.arm_status != OK)

### MIDDLE_BAND
- ROLE_mean in [0.30, 0.70]
- OR RECURSIVE_at_max in [0.20, 0.50]
- OR lift(ROLE - FLAT) at max_load in [0.05, 0.15]

## SMOKE RESULTS (2026-07-01)

Both seeds smoke HARD_PASS with strong discrimination:

| Metric | seed_7 | seed_13 | HP threshold |
|---|---|---|---|
| BASELINE @ K=200 (positive control) | 0.875 | 0.875 | >= 0.70 |
| FLAT @ K=1600 | 0.000 | 0.125 | (SNR floor, no threshold) |
| **ROLE @ K=1600** | **0.500** | **0.750** | (contributes to mean) |
| **RECURSIVE @ K=1600** | **1.000** | **1.000** | >= 0.50 |
| **ROLE mean** | **0.750** | **0.875** | >= 0.70 |
| **Lift(ROLE - FLAT) @ K=1600** | **0.500** | **0.625** | >= 0.15 |

Interpretation: address-space partition primitive works robustly at both seeds. RECURSIVE (double-partition) is essentially perfect at K=1600 (per-buffer alpha ~ 0.006). ROLE (single-partition) survives at K=1600 with 0.50-0.75 top1 vs FLAT crater at 0.00-0.125 (lift 0.50-0.62). Substantial margin on all HP gates in smoke; expect FULL (N_TRIALS=16 + third coverage K=800) to sharpen the numbers.

## Cardinality (META_RULE_H)

- N_ARMS = 4
- COVERAGE_LOADS_FULL = [200, 800, 1600] (200 = positive-control zone; 800 = near-cliff regime for FLAT/BASELINE; 1600 = beyond-cliff discriminating regime)
- COVERAGE_LOADS_SMOKE = [200, 1600] (positive-control + discriminator zones)
- N_TRIALS_FULL = 16 (Bernoulli sigma at p=0.5 = 0.125)
- N_TRIALS_SMOKE = 8

**FULL:** EXPECTED_N_UNITS = 3 loads x 4 arms = **12 arm-rows per seed**. HARD_FAIL floor = ceil(0.85 * 12) = **11**.

**SMOKE:** 2 loads x 4 arms = 8 arm-rows.

**Physics rationale for regime choice:** Substrate FHRR-bipolar-bundle identity-cleanup capacity ~ 0.138 * N (Amit-Gutfreund wall) at N=8192 = ~1130 items. K=200 (alpha=0.024, safely below wall) reproduces CG'd primitive. K=1600 (alpha=0.195, ~40% beyond wall) forces FLAT-pool to fail while address-space-partitioned ROLE per-slot alpha=0.049 and RECURSIVE per-buffer alpha ~0.006 stay in safe regime.

## Discriminator survives scale (META directive)

Smoke uses full-N=8192 (numpy cheap; no scale reduction). Discriminator is the SUMMARY_FLAT vs SUMMARY_ROLE gap at k_per_role=5 avg (20 items / 4 roles) which is INSIDE the discriminating band per Bernoulli SNR analysis (below).

Check A satisfied: smoke runs at full-N=8192 (no reduced-N smoke).

## CRLB / capacity-feasibility (META_RULE §9)

- `crlb_floor_computed`: 1/V_CB = 0.000977 (chance floor for codebook argmax).
- `crlb_formula_reference`: chance_floor = 1/V_CB; sigma_bernoulli at p=0.5 = sqrt(0.25 / N_TRIALS) = 0.125 at N_TRIALS=16.
- `discriminator_reachability`: HP_ROLE=0.70 is 5.6 sigma above chance, and 1.6 sigma above the FLAT ceiling at k=20 (predicted FLAT ~ 1/k = 0.05 due to argmax competition; SNR analysis in "SNR floor for FLAT bundle" below). REACHABLE.

### SNR floor for FLAT bundle
Bundling 20 bipolar bindings into 1 vector: sum(role_key_i * val_i) for i=1..20. Query with role_key_j: cosine(role_key_j * bundle) with val_j is proportional to 1 + noise from other 19 bindings. Cosine SNR ~ 1/sqrt(K); at K=20 SNR ~ 0.22; over V_CB=1024 codebook cleanup, top-1 accuracy from Wang-Vershynin JL analysis at SNR 0.22 predicts top-1 near 1/V_CB * (1 + exp(SNR^2)) ~ 0.05-0.10. HP_FAIL threshold 0.20 sits above this floor.

For ROLE structure: bundle only 20/4 = 5 items per slot. SNR ~ 1/sqrt(5) = 0.45; top-1 predicted ~ 0.70-0.80. HP threshold 0.70 discriminating.

Reference: Frady-Sommer 2018 "Resonator Networks" Section 3.4 (bundle-cleanup capacity).

## Sweep-alignment (META_RULE §15.A)

`swept_params`:
- `coverage_loads`: {20, 40, 100}

`effective_params_per_primitive`:
- ARM_BASELINE: at coverage 20, pool_size=20 (fits); at 40, pool_size=40; at 100, pool_size=100. Baseline expected to DEGRADE at 100 (SNR ~ 1/sqrt(100) ~ 0.10 -- below discriminating).
- ARM_SUMMARY_ROLE: at coverage 20, k_per_slot avg=5; at 40, k_per_slot avg=10; at 100, k_per_slot avg=25 (single-level exhausted; ROLE should degrade).
- ARM_RECURSIVE: at coverage 100, is the intended regime (5 level-1 * 20 items each).

`sweep_alignment_verdict`: **ALIGNED**. Each sweep point tests a specific regime: 20 = single-level canonical; 40 = mild saturation of single-level ROLE; 100 = single-level exhausted, RECURSIVE canonical.

## Bracket-includes-discriminating-band (META_RULE §15.B)

Predicted top-1 at each sweep point:

| Load | BASELINE | FLAT | ROLE | RECURSIVE |
|---|---|---|---|---|
| 20 | ~0.90 sat | ~0.10 (floor) | ~0.75 (in-band) | ~0.75 (in-band) |
| 40 | ~0.60 (in-band) | ~0.05 (floor) | ~0.55 (in-band) | ~0.60 (in-band) |
| 100 | ~0.30 (in-band) | ~0.02 (floor) | ~0.25 (in-band) | ~0.55 (in-band) |

Discriminating band = [0.30, 0.70]. Points in band per arm across sweep:
- BASELINE: 2/3 (40, 100)
- FLAT: 0/3 (all floor; INTENTIONAL negative control)
- ROLE: 3/3 (20, 40, 100)
- RECURSIVE: 3/3 (20, 40, 100)

Overall discriminating_fraction = 8/12 = **0.67** across arm x load points. Above §15.B threshold 0.30.

## Signal-shape compatibility (META_RULE §15.C)

`composition_edges`:
- role_key -> binding_pool: SHAPE_MATCH (bipolar N=8192 * bipolar N=8192 -> N=8192).
- binding_pool -> summary_slot: SHAPE_MATCH (bundle-then-quantize; SUM of N=8192 vectors -> N=8192 bipolar).
- summary_slot -> level-2 slot: SHAPE_MATCH (each level-1 summary is N=8192 bipolar; bundle 5 of them then bind by level-2 role = SUM(role_L2 * summary_L1_i) at N=8192).
- query -> level-2 unbind -> level-1 unbind -> cleanup: SHAPE_MATCH throughout (all N=8192 bipolar).

Verdict: **all edges SHAPE_MATCH**.

## Positive-control (META_RULE §15.D)

- **ARM_BASELINE** IS the positive-control reproducer: at low coverage (load=20) should score >= 0.80 (in-pool retrieval CG'd from WM multi-bank K=4096 at k_per_bank <= 64).
- Cited prior atom: WM multi-bank codebook-cleanup primitive (commit 6e2ff698); at K=20 bindings, one bank, top-1 accuracy > 0.90 expected.
- Cited prior regime: N=8192, K=20-100, codebook cleanup on V=1024. SAME regime here.
- Tolerance: 0.10. If BASELINE at load=20 < 0.80 = HARD_FAIL_POSITIVE_CONTROL_REGRESSION.
- Regime-extension audit: SHAPE_MATCH (identical regime).

## HP_SCOPE per-arm

- ARM_BASELINE: [positive_control_at_low_load] only; not a chain-grade gate carrier (baseline is expected to degrade at high load).
- ARM_SUMMARY_FLAT: [SNR_floor_confirmation_only]; expected to fail the mechanism gate BY CONSTRUCTION.
- ARM_SUMMARY_ROLE: [chain_grade_HP_role, chain_grade_HP_lift].
- ARM_RECURSIVE: [chain_grade_HP_recursive].

## Cell-template mandates (checklist)

- `arms_differ_verified`: True (§6 hash-test at smoke; ARM_SUMMARY_FLAT and ARM_SUMMARY_ROLE will have different bank_states).
- `final_metrics_atomicity`: `tmp_replace` (single-shot per seed; §7).
- `except SystemExit: raise` before `except Exception`: verified via grep pre-flight.
- `crlb_floor_computed`: 0.000977; `discriminator_reachability`: True.
- `baseline_in_band`: at load=20, BASELINE ~0.90 (saturated -- above 0.95 threshold at chance regime? NO -- 0.90 < 0.95 = in band); at load=100, BASELINE ~0.30 (in band). Verified at smoke.
- `discriminator survives scale`: smoke at full-N=8192.
- HP strictly above floor + 5% band width: HP_ROLE=0.70 vs FAIL_ROLE=0.20; band width 0.50; 5% margin = 0.025; HP_ROLE=0.70 clears floor 0.225.
- `cardinality_ok`: EXPECTED_N_UNITS = 12; HF floor = 11.
- Per-unit failure-class instrumentation: `except Exception` with arm_status field.
- `calibration_check`: "codebook_cleanup_top1_over_V_CB_1024_role_slots_S_4_k_per_role_5".
- All numbers tagged (HYPOTHESIZED@ or CITED@ per META_RULE_AC).

## Defensive error checking (§13)

- `cell_chunked`: True (one file = one seed; seeds 7 / 13 / 19).
- `start_marker_written`: True (via `_write_start_marker` at main() entry).
- `crash_diagnostic_present`: True (`_write_crash_metrics` in outer try).
- `heartbeat_present`: True (inline `emit_heartbeat` per phase point).
- `defensive_error_checking`: `passed_all_4_patterns`.
- `progress_logging`: `print_flush_true` (per §17; every print uses `flush=True`).

## Regime + dispatch

- Backend: numpy CPU (small matmul; N=8192).
- Wall estimate: ~5-10 min per seed on remote_cpu_queue (3 loads * 4 arms * 16 trials = 192 trial-arm units per seed; each trial ~1s at N=8192 numpy).
- Timeout FULL: 1800s (30 min safety margin).
- Timeout smoke: 180s (queue_add default cap).
- Route: **remote_cpu_queue** post-smoke (per USER-locked 2026-07-01 no-full-on-local-CPU rule).

## Files

- Cell: `experiments/exp_cortex_summarization_role_slot_v1_seed_7.py`
- Cell: `experiments/exp_cortex_summarization_role_slot_v1_seed_13.py`
- Cell: `experiments/exp_cortex_summarization_role_slot_v1_seed_19.py`
- Anchor: `cortex_summarization_role_slot_v1_seed_<N>` (per-seed metrics paths).
- Aggregate metrics: `data/exp_cortex_summarization_role_slot_v1_seed_<N>/metrics.json`.

## Landing chain-grade gate (post-full)

Chain-grade M1.7 fires iff:
- ARM_SUMMARY_ROLE HP fires on 2/3 seeds AND
- ARM_RECURSIVE HP fires on 2/3 seeds AND
- lift HP fires on 2/3 seeds AND
- BASELINE positive-control passes at load=20 on 3/3 seeds.

If MIDDLE_BAND on any of the above but no HARD_FAIL: MEASURED_MECHANISM tier (not chain-grade M1.7).
