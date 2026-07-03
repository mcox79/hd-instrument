# Pre-reg: Layer 0.5 Production Wiring Skeleton — ARC-CLOSED integration end-to-end

- date_authored: 2026-07-03
- cell_author: hdi_exp_dev (spawn)
- cell_path: `experiments/exp_layer_05_production_wiring_skeleton_smoke_2026_07_03.py`
- scope: `hub_concept_bridge_only` (identical corpus to Exp 3B/3C/3D/3E)
- role: production wiring **skeleton** — validates the ARC-CLOSED pipeline end-to-end at the substrate-native integration boundary (char-trigram Layer 0 replaces BGE; PPR Layer 0.5 + v3-clean Layer 0.75 + FHRR Layer 1 unchanged)

## Motivation

Exp 3E FULL HARD_PASS_FULL_ARC_CLOSURE_V3_CLEAN 2026-07-03T17:11Z
CITED@Director spawn prompt 2026-07-03; MEASURED@`data/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_MAIN_V3_CLEAN`
= 0.833 (SMOKE landed on disk 2026-07-03) closes the retrieval-architecture arc on hub-concept-bridge scope.

The Exp 3E cell used **BGE-small** at Layer 0. The production wiring skeleton **substitutes CharTrigramEncoder** (substrate-native, zero-external-model) at Layer 0 — the boundary where a real Director-KB / KGStore composition would attach. Everything downstream (PPR union, v3-clean structural filter, FHRR unbind-and-cleanup) is unchanged.

This cell exercises the INTEGRATION SEAM: does the ARC-CLOSED pipeline survive replacing the semantic-retrieval Layer 0 with a substrate-native trigram encoder? If yes → production wiring path validated. If no → integration seam breaks something that individual arms cannot detect.

## Concept-query-before-dispatch

`bash tools/substrate_query.sh "Layer 0.5 production wiring skeleton integration end-to-end pipeline arc closure"` (2026-07-03).
Top cosine=0.3369 (`entity=production_line`, wordnet), and `pb_production_recipe_integration_v1` HARD_PASS atom at 0.3213 — different domain (production-recipe scheduling, not retrieval-architecture). Below 0.30 relevance threshold for prior-arc cell hit. No prior "Layer 0.5 production wiring skeleton" cell exists. Genuinely novel operationalization.

## Primitives composed (source-signature verbatim per MM_STANDARD)

Composes ONLY existing chain-grade primitives. Zero new abstractions.

1. **Layer 0 (dense retrieval; substrate-native)** — `hdlab.char_trigram_encoder.CharTrigramEncoder.encode` / `.encode_batch` (bag-of-char-trigrams bipolar bundling; deterministic per-trigram HD; sign-bundle). CITED@`hdlab/char_trigram_encoder.py:50`.
2. **Layer 0.5 (PPR-union)** — reuses Exp 3E cell's `build_entity_kg` + `ppr_iterate_sparse` + `seed_vec_from_indices` + `ppr_pipeline_union` (uniform seed, NO Stage 1 IDF-reweight, NO Stage 2 hub-dampen). CITED@`experiments/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py:287,311,326,554`. Same PPR mechanism as Exp 2C smoke cell.
3. **Layer 0.75 (structural KG-slot filter)** — `hdlab.layer_075_structural_slot_filter.layer_075_v3_clean_filter`. CITED@`hdlab/layer_075_structural_slot_filter.py:51`.
4. **Layer 1 (FHRR unbind-and-cleanup composition)** — reuses Exp 3E cell's `bind_phase` + `unbind_phase` + `phase_cos_batch` + `composition_primitive`. CITED@`experiments/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py:175,180,189,490`. ORACLE reproduces MAIN_V3_CLEAN=0.833 SMOKE on Exp 3E at N=4096 24q 1seed with BGE Layer 0.
5. Stage 1 IDF reweight (`stage1_reweight_seed`) + Stage 2 hub-dampen (`stage2_hub_dampen_adjacency`) — reused only for the S1S2_INSERTED_REGRESSION arm which validates the S1+S2-SUBTRACT discipline at the production seam.

Corpus construction (hub-and-spoke synthetic; identical to Exp 3B/3C/3D/3E): `build_corpus`, `ENTITIES` (40), `RELATIONS` (5), `HUB_INDICES=[0,1,2]`, `HUB_OVER_SAMPLE=3.0`. CITED@`experiments/exp_substrate_stage1_apply_exp3e_layer075_v3_clean_arc_closure_2026_07_03.py:112,120,194`.

## Arms (6)

1. `ARM_ORACLE_INTEGRATION` — GT chunks fed to composition primitive; sanity check the composition primitive is intact after char-trigram substitution.
2. `ARM_LAYER0_ONLY` — char-trigram hop-1 top-5 directly to composition (no PPR, no v3 filter).
3. `ARM_LAYER_05_ONLY` — char-trigram Layer 0 → PPR uniform union → composition (no v3 filter).
4. `ARM_LAYER_075_INSERTED` — char-trigram Layer 0 → PPR uniform union → v3-clean filter → composition (integration MAIN pipeline). **MAIN DISCRIMINATOR.**
5. `ARM_S1S2_INSERTED_REGRESSION` — char-trigram Layer 0 → PPR **with S1 reweight + S2 hub-dampen** → v3-clean filter → composition. Validates S1+S2-SUBTRACT discipline at production seam.
6. `ARM_INTEGRATION_END_TO_END` — alias of ARM_LAYER_075_INSERTED (declared as separate arm name for reporting clarity per Director spec; SUCCESS-MODE EXEMPT from ARMS-MUST-DIFFER against arm 4).

**Cardinality:** `EXPECTED_N_UNITS = 6 arms x n_seeds`. SMOKE: 6 * 1 = 6.

## Reproduction gates (soft; char-trigram vs BGE encoder mismatch expected)

Encoder is substituted (char-trigram replaces BGE); soft flags only. HARD_PASS logic uses ARM_INTEGRATION_END_TO_END absolute threshold, not encoder-drift.

| Metric | Precedent | Precedent source | Soft-flag gate |
|---|---|---|---|
| ARM_ORACLE_INTEGRATION | 0.833 | MEASURED@Exp 3E SMOKE 2026-07-03 (should reproduce; composition primitive intact) | drift &lt;= 0.10 |
| ARM_LAYER_05_ONLY | ~0.41 | HYPOTHESIZED@Director spawn (Exp 3 EXP3_BASELINE with BGE was 0.4111; char-trigram expected similar range 0.30-0.50) | drift &lt;= 0.20 |
| ARM_LAYER_075_INSERTED | ~0.77 | HYPOTHESIZED@Director spawn (Exp 3E STAGE3_V3_ONLY with BGE was 0.767; char-trigram may drift more) | drift &lt;= 0.20 |
| ARM_S1S2_INSERTED_REGRESSION | ~0.51 | HYPOTHESIZED@Director spawn (Exp 3D MAIN with BGE was 0.5111; validates S1+S2-SUBTRACT holds at production seam) | drift &lt;= 0.20 |
| ARM_LAYER0_ONLY | 0.35-0.44 | HYPOTHESIZED@Director spawn (char-trigram Wikipedia baseline r@5=0.854 from separate cell today; hub-and-spoke shape different — expected lower) | soft (informational) |

## Bands

- `HARD_PASS_PRODUCTION_WIRING_VALIDATED`:
  ARM_INTEGRATION_END_TO_END &gt;= 0.60
  AND ARM_ORACLE_INTEGRATION drift &lt;= 0.10 (composition primitive intact)
  AND ARM_S1S2_INSERTED_REGRESSION &lt; ARM_LAYER_075_INSERTED (S1+S2-SUBTRACT preserved at seam)
  → substrate-native production wiring path validated end-to-end.
- `MIDDLE_BAND`:
  0.30 &lt;= ARM_INTEGRATION_END_TO_END &lt; 0.60 → partial integration; investigate; present to Director.
- `HARD_FAIL`:
  ARM_INTEGRATION_END_TO_END &lt; 0.30 → integration seam breaks something not captured in individual arms; deep-dive per HF-deep-dive policy.
- `HALT_ORACLE_DRIFT`: |ARM_ORACLE_INTEGRATION - 0.833| &gt;= 0.10 → composition primitive broken by import path or encoder substitution side effect; do NOT trust integration verdict.

## SCHEMA-VET pre-dispatch checklist

- **1. cardinality_ok (META_RULE_H):** EXPECTED_N_UNITS = 6 * n_seeds. Verdict counts per_arm keys; HARD_FAIL_CARDINALITY_BREACH on mismatch.
- **2. Per-unit failure-class instrumentation (META_RULE_J):** `except Exception:` only (no bare / no BaseException); `_write_crash_metrics` diag on Exception; specific propagation.
- **3. Discriminator-fires gate (META_RULE_K):** v3 slot-fire count logged per-seed. If v3 fallback rate &gt; 50% across seeds, emit FLAG_V3_MOSTLY_FALLBACK. Char-trigram may cause more fallback due to weaker Layer 0 coverage — expected behavior; not auto-fail.
- **4. Strictly-above-floor target (META_RULE_L):** HP absolute floor 0.60 (Director spec); band = 0.60 to ORACLE(~0.83); 5% band-width = 0.011 → HP metric &gt;= 0.611.
- **5. HP_SCOPE:** HP applies ONLY to ARM_INTEGRATION_END_TO_END. Reproduction arms subject to soft drift flags only.
- **5b. Calibration-check (META_RULE_M):** `calibration_check: default_ok_for_this_regime` — v3 filter has no tunable thresholds; char-trigram n_dim=4096 SMOKE / 8192 FULL matches Exp 3E scale.
- **6. ARMS-MUST-DIFFER (META_RULE_AF):** Per-arm prediction-array SHA256 verified. EXEMPT pairs: (ARM_INTEGRATION_END_TO_END, ARM_LAYER_075_INSERTED) — declared alias per Director spec; SUCCESS-MODE EXEMPT (ARM_LAYER_075_INSERTED, ARM_ORACLE_INTEGRATION) at 100% GT-pool coverage per Exp 3E precedent.
- **7. ATOMIC-FINAL-METRICS-WRITE (META_RULE_AH):** `final_metrics_atomicity: tmp_replace`.
- **8. `except SystemExit: raise` BEFORE `except Exception`:** present at outer try/except; no BaseException handler.
- **9. CRLB / capacity-feasibility:** `crlb_floor_computed=0.025` THEORETICAL@sqrt(K_final/N_dim)=sqrt(5/8192)~0.025 per Plate 1995; HP=0.60 &gt;&gt; 0.025; `discriminator_reachability: True`.
- **10. baseline_in_band (META_RULE_AG):** ARM_LAYER_05_ONLY expected ~0.30-0.50; in-band. ARM_LAYER0_ONLY expected ~0.20-0.50; in-band.
- **11. All numbers tagged (META_RULE_AC):** see Reproduction gates table above.
- **13. Cell hardening:**
  - `cell_chunked: False` (single-cell single-seed for SMOKE; SMOKE ~30s wall).
  - `start_marker_written: True`.
  - `crash_diagnostic_present: True`.
  - `heartbeat_present: False` (SMOKE too short; FULL will add).
  - `defensive_error_checking: passed_all_4_patterns`.
- **15. TEST-DESIGN gates:**
  - A) `sweep_alignment_verdict: ALIGNED` — no sweep axis.
  - B) `discriminating_fraction: 1.0` — 1/1 point in band (MAIN target 0.60-0.90 predicted).
  - C) `composition_edges`:
    - `char_trigram_encode -> bge_top_k_analog SHAPE_MATCH` (both output List[int] of top-k fact indices via cosine argsort).
    - `bge_top_k -> ppr_pipeline_union SHAPE_MATCH` (list of fact indices).
    - `ppr_union -> layer_075_v3_clean_filter SHAPE_MATCH` (list of fact indices).
    - `v3_filter -> composition_primitive SHAPE_MATCH` (list of fact indices).
  - D) `positive_control_arms`:
    - ARM_ORACLE_INTEGRATION (composition primitive reproduce; tolerance 0.10 vs 0.833 MEASURED@Exp 3E SMOKE).
    - ARM_LAYER_075_INSERTED (Exp 3E ARM_MAIN_V3_CLEAN analog under encoder substitution; tolerance 0.20 soft; regime_extension_audit: SHAPE_DRIFT_char_trigram_vs_bge).
    - ARM_S1S2_INSERTED_REGRESSION (Exp 3D S1S2-inserted analog; tolerance 0.20 soft).
  - E) `functional_requirements`:
    - "encode text to HD without external model" → CharTrigramEncoder.encode
    - "seed PPR from Layer 0 top-k entities" → ppr_pipeline_union.
    - "narrow union to hop-1 + hop-2 slot matches" → layer_075_v3_clean_filter.
    - "compose hop-1 + hop-2 to answer" → composition_primitive (FHRR unbind + cleanup).
- **16. RUN_MODE VERIFICATION:** cell reads argv `--full` / `--smoke` / `--self-test`; writes `run_mode` to metrics.json.
- **17. PRINT-PROGRESS FLUSHING:** `sys.stdout.reconfigure(line_buffering=True)` + `flush=True` on progress lines; SMOKE ~30s wall so `progress_logging: line_buffered_stdout`.

## Compute architecture

- **class: sequential-CPU with justification** — SMOKE at N_DIM=4096 24 queries × 6 arms. CharTrigramEncoder is Python-loop over trigrams per text but caches HD lookups → amortized fast (~ms per text). PPR + KG traversal + FHRR composition per query is sequential (chained retrieval where each hop depends on prior; genuine sequential dependency per META rule). Total SMOKE wall estimated ~30-60s. Well under 10s / phase-point threshold that would trigger GPU-batching justification.
- **storage: sharded** — each fact HD is its own vector (`fact_hds[i]` per index); no bundled composition storage. Complies with META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW.

## Regime

| Field | SMOKE (local_cpu) | FULL (remote) |
|---|---|---|
| N_DIM | 4096 | 8192 |
| N_QUERIES_TARGET | 24 | 100 |
| SEEDS | [11] | [11, 17, 23] |
| top_k (Layer 0) | 5 | 5 |
| PPR alpha / iters | 0.15 / 5 | 0.15 / 5 |
| K_FINAL | 5 | 5 |
| B_BRIDGES | 5 | 5 |
| target wall | ~30-60s | ~15-30 min |

## Timeout estimation

SMOKE: 1 seed × 24 queries × 6 arms at N_DIM=4096. Extrapolate from Exp 3E SMOKE (7 arms × 24q × 1 seed ~30s including BGE encoder load): char-trigram Layer 0 is FASTER than BGE (no torch load, no transformer forward), and 6 arms vs 7 → ~15-30s wall. **SMOKE timeout_s = 180** (6x buffer).

FULL: 3 seeds × 100 queries × 6 arms at N_DIM=8192. Extrapolate ~140s per seed × 3 seeds = 420s = 7min. **FULL timeout_s = 1800** (30 min; 4x buffer).

## Verdict logic

- HP: ARM_INTEGRATION_END_TO_END >= 0.60 AND ORACLE drift <= 0.10 AND S1S2 < LAYER_075_INSERTED → production wiring path validated.
- MB: 0.30 <= ARM_INTEGRATION_END_TO_END < 0.60 → partial; present to Director.
- HF: ARM_INTEGRATION_END_TO_END < 0.30 → integration seam breaks; HF-deep-dive.
- HALT_ORACLE_DRIFT: |ORACLE - 0.833| >= 0.10 → composition primitive broken; halt.

## Rollback and iteration policy

- SMOKE HF: deep-dive per USER HF-deep-dive policy. Likely: char-trigram Layer 0 coverage collapses; investigate whether PPR-expansion still recovers GT chunks.
- SMOKE MB: present to Director (per Director spec).
- SMOKE HP: propose remote FULL at N=8192 100q × 3 seeds; if Director-KB scale wiring needed, discuss extension to real corpus at FULL.

## Explicit self-reference note (USER-locked)

I authored this cell as the exp_dev agent per Director spawn 2026-07-03. Not "Director dispatched" — I am doing the authoring.
