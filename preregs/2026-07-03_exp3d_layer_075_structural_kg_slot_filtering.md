# Pre-reg: Exp 3D — Layer 0.75 Stage 3 v3 structural KG-slot filtering (LLM-free)

- date_authored: 2026-07-03
- cell_author: hdi_exp_dev (spawn)
- cell_path: `experiments/exp_substrate_stage1_apply_exp3d_layer075_structural_kg_slot_filtering_smoke_2026_07_03.py`
- prior_cells:
  - `experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py` (Exp 3B v1 query-only rescore)
  - `experiments/exp_substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03.py` (Exp 3C v2 iterative query-augmentation)
- scope: `hub_concept_bridge_only` (identical to Exp 3B/3C)

## Motivation and citation trail

- Skunkworks-verified HF_STRUCTURAL attribution across Exp 3B/3C:
  - Exp 3B (v1 query-only rescore + MMR): MAIN_LAYER075_STACKED = 0.0267  MEASURED@`data/exp_exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_MAIN_LAYER075_STACKED`
  - Exp 3C (v2 iterative query-augmentation): MAIN_LAYER075_STACKED_V2 = 0.0367  MEASURED@`data/exp_substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_MAIN_LAYER075_STACKED_V2`
  - Both variants score BELOW EXP3_BASELINE_REPRODUCTION (~0.41-0.44) and BELOW RANDOM_CONTROL (~0.03-0.05); mechanism-class is architecturally dead in the pre-fused-augmentation family: `s(q ⊕ b, c)` cannot distinguish hop-1 fact (bridge = object) from hop-2 fact (bridge = subject) from distractor (bridge-mention-only). All three get equal augmentation boost.
- Director spawn cites the MM_STANDARD atom `feedback_mechanism_abstraction_lossy_cite_source_signature_2026-07-03` as the meta-lesson: prior 2 HFs came from silent abstractions of the mechanism away from its source argument signature (BGE cosine over augmented text can't observe subject/object roles that are LITERALLY THE THING that distinguishes hop-1 from hop-2).
- Path-a' insight: the KG already encodes (subject, relation, object) triples. Structural filtering exploits this triple structure DIRECTLY as the discriminator, rather than attempting to relearn it from BGE cosines that failed twice. No new learned model, no new abstraction beyond existing KGStore triple access (Principle 11 compliant).
- Concept-query-before-dispatch performed by Director prior to spawn: no prior cell operationalizes structural role-filtering as a composition layer between PPR union and FHRR composition. Genuinely novel operationalization of existing `KGStore.predict_one_hop_topk(s, p, k)` primitive.

## Precedents (MEASURED @ off-disk 2026-07-03)

Averaged over 3 seeds (11, 17, 23), 30-50 hub-bridge queries per seed:

| Metric | Exp 3B | Exp 3C | Notes |
|---|---|---|---|
| ORACLE composition sanity | 0.8533 | 0.8167 | Composition primitive intact; small seed variance |
| EXP3_BASELINE reproduction | 0.4133 | 0.4400 | Exp 3 MAIN pipeline; on-disk floor |
| STAGE1_ONLY | 0.3933 | 0.4167 | Stage 1 alone (~ baseline) |
| STAGE2_ONLY | 0.4067 | 0.4300 | Stage 2 alone (~ baseline) |
| STAGE3_V1 (query-only rescore + MMR) | 0.0133 | 0.0133 | HF; below random |
| STAGE3_V2 (iterative query-augmentation) | -- | 0.0433 | HF; below random |
| MAIN v1 stacked S1+S2+S3v1 | 0.0267 | -- | HF |
| MAIN v2 stacked S1+S2+S3v2 | -- | 0.0367 | HF |
| RANDOM_CONTROL | 0.0467 | 0.0300 | Chance baseline |

## Design spec — Stage 3 v3 structural KG-slot filtering

Query semantic: `"What is the r1 of the r2 of e0?"`
- Hop-1 fact needed: (e0, r2, mid_entity) — applying r2 to e0
- Hop-2 fact needed: (mid_entity, r1, answer_entity) — applying r1 to mid

Algorithm (LLM-free; operates on KG triples directly):

1. **Input:** candidate pool P_1 = PPR-union output (~30 candidate facts, each a (subject, relation, object, text) tuple).
2. **Bridge extraction (leverage Exp 3C's `extract_bridge_candidates`, already 100% mid-capture in P_1 per Exp 2C):** get top-B bridge candidates by pool co-occurrence, filter out entities that appear in query text.
3. **Structural role filtering** — for each fact f = (s, r, o, text) in P_1, tag with structural role:
   - HOP_1_CANDIDATE if `s == e0 AND r == r2` (fact is exactly "the r2 of e0 is ...", regardless of bridge identity — this is the hop-1 fact the query needs)
   - HOP_2_CANDIDATE_FOR_b if `s == b AND r == r1` where b is any extracted bridge (fact is "the r1 of b is ...")
   - DISTRACTOR if `o == b AND s != e0` (bridge appears as object; mentions bridge but doesn't advance to the answer)
   - OTHER otherwise
4. **v3 output** = union of {all HOP_1_CANDIDATE facts} + {all HOP_2_CANDIDATE_FOR_b facts across all extracted bridges b}, capped at K_FINAL = 5.
5. **Fallback:** if the structural union is empty (extraction under-selected — no fact matches both subject-slot AND relation-slot), fall back to Stage 1+2 pool alone (Exp 3B/3C measured ~0.40 — null-effect but not catastrophic).
6. **Composition:** feed structural-filtered set into unchanged FHRR composition primitive.

Note: Director spawn described "hop-1-candidates ∩ query.r1 relation-match" but query.r1 is the OUTER relation applied to the bridge, so hop-1 (getting mid) uses r2 and hop-2 (getting answer from mid) uses r1. I interpret the intent as "match the correct relation for each hop role" and implement per relation semantics above. Cell comments cite this fix.

## Arms (9)

For direct comparison with Exp 3C + 1 new arm ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY:

1. `ARM_ORACLE_COMPOSITION_SANITY` — composition primitive on ground-truth chunks; sanity floor
2. `ARM_EXP3_BASELINE_REPRODUCTION` — Exp 3 MAIN pipeline (BGE + PPR union hop-1)
3. `ARM_MAIN_LAYER075_STACKED_V3` — S1 + S2 + S3v3 stacked; discriminator arm
4. `ARM_STAGE1_ONLY` — IDF seed re-weight only
5. `ARM_STAGE2_ONLY` — hub-dampened adjacency only
6. `ARM_STAGE3_V1_QUERY_ONLY_RESCORE` — Fix#28 confidence check; expects ~0.013 reproduction
7. `ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY` — Fix#28 confidence check; expects ~0.043 reproduction
8. `ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY` — v3 in isolation (normal pool → v3 filter → composition)
9. `ARM_RANDOM_CANDIDATES_CONTROL` — chance ~0.05

Cardinality: `expected_n_units = 9 arms × 3 seeds = 27`.

## Bands

- `HARD_PASS_FULL_CLOSURE`: MAIN_V3 >= 0.90 × ORACLE (~0.74) — retrieval-architecture arc CLOSES within scope.
- `HARD_PASS_INTERFACE_POSITIVE`: MAIN_V3 >= 0.413 AND STAGE3_V3_ONLY > 0.413 — structural filtering non-destructive at the interface.
- `MIDDLE_BAND`: 0.413 <= MAIN_V3 < 0.74 AND not interface-positive, OR partial signal
- `HARD_FAIL_DEAD`: MAIN_V3 < 0.413 AND STAGE3_V3_ONLY < 0.20 — structural filtering ALSO dead. Escalate to path (a) BridgeRAG tripartite s(q, b, c).
- `HALT_ORACLE_DRIFT`: |ORACLE - 0.8533| >= 0.10 (composition primitive changed; do NOT trust MAIN_V3 interpretation)
- `FLAG_BASELINE_DRIFT` (soft): |EXP3_BASELINE - 0.4133| >= 0.10
- `FLAG_V1_HF_DRIFT` (soft): |STAGE3_V1 - 0.0133| >= 0.10 (Fix#28 confidence check)
- `FLAG_V2_HF_DRIFT` (soft): |STAGE3_V2 - 0.0367| >= 0.10 (Fix#28 confidence check)

## Compute architecture

- class: **sequential-CPU with justification** — chained retrieval (BGE top-K → PPR union → structural filter → composition); each step depends on prior. No batchable matmul opportunity beyond BGE encoding (which IS batched via encode helper). Substrate primitives are numpy phase math, small-N (N=4096). Wall time budget: ~4-8 min per seed.
- storage strategy: **sharded** (each fact stored as its own vector; no bundle collapse; consistent with Exp 3/3B/3C precedents).
- gpu_batching_justified_absent: v3 primitive is graph-structure lookup (fact filtering by triple role) not matmul. BGE encoding is already batched via cell's existing encode helper (identical to Exp 3C, which produced smoke results in ~5 min per seed on CPU).

## SCHEMA-VET fields

- `cardinality_ok`: True (asserts `actual == 9 × n_active_seeds`)
- `arms_differ_verified`: True (sha256 per-arm prediction-array in smoke)
- `final_metrics_atomicity`: `tmp_replace`
- `crlb_floor_computed`: 0.035  THEORETICAL@`sigma_min = sqrt(K_final/N_dim) = sqrt(5/4096) ≈ 0.035` per Plate 1995
- `discriminator_reachability`: True (HP_full 0.74 >> CRLB 0.035; HP_interface 0.413 comfortably above CRLB)
- `baseline_in_band`: verified at smoke — EXP3_BASELINE_REPRODUCTION MUST land in (0.05, 0.95); precedent 0.41 is comfortably in band
- `discriminator_survives_scale`: SMOKE regime IS the test regime (N_DIM=4096, hub-bridge scope, 30-50 queries per seed × 3 seeds); matches Exp 3B/3C config
- `HP_SCOPE`: HP gates apply only to `ARM_MAIN_LAYER075_STACKED_V3`; drift gates apply to ORACLE (drift ≤ 0.10), EXP3_BASELINE (soft), STAGE3_V1 (soft), STAGE3_V2 (soft)
- `calibration_check`: `default_ok_for_this_regime` — Stage 1/2/BGE hyperparameters unchanged; new v3 hyperparameters (B_BRIDGES=5, K_FINAL=5, structural triple predicate) have no thresholds to tune; either the KG triple matches or it doesn't
- `progress_logging`: `print_flush_true`
- `cell_chunked`: False (single cell, all seeds in-process; 3 seeds × ~30 queries per seed, ~5 min budget per seed; not a multi-hour cell that needs chunking)
- `start_marker_written`: True
- `crash_diagnostic_present`: True
- `heartbeat_present`: False (cell wall time ≤ 15 min; per-seed print flush provides progress signal)
- `defensive_error_checking`: `passed_all_4_patterns` (start marker + crash diag + print flush + Exception ordering)

### Functional Requirements (per §15 Gate E)

1. **Filter candidate pool by structural KG-slot role** — needs KG triple access + role predicate.
   Primitive: KG triple filter (novel operationalization; leverages existing KGStore-style triple representation via `corpus["facts"]` list of tuples).
2. **Bridge entity extraction from candidate pool** — needs P_1 co-occurrence counting.
   Primitive: `extract_bridge_candidates` from Exp 3C (VERIFIED via Exp 2C mid-capture 100% in isolation).
3. **Compose retrieval into 2-hop answer via FHRR unbind chain** — needs FHRR composition primitive.
   Primitive: `composition_primitive` from Exp 3/3B/3C (VERIFIED via ORACLE ~0.85).

### §15 Gates

- Gate A (`sweep_alignment_verdict`): ALIGNED (no sweep axis; all arms use same regime; K_FINAL is a filter-cap not a sweep parameter)
- Gate B (`discriminating_fraction`): n/a (no sweep axis)
- Gate C (`composition_edges`): all edges SHAPE_MATCH:
  - PPR union → structural filter: input is List[fact_index]; output is List[fact_index]; SHAPE_MATCH
  - structural filter → composition primitive: input is List[fact_index] (cap K_FINAL); composition unbind loops over up to K; SHAPE_MATCH (identical to Exp 3B/3C)
  - bridge extractor → structural filter: input is List[int] (entity indices); consumed as membership set; SHAPE_MATCH
- Gate D (`positive_control_arms`):
  - `ARM_ORACLE_COMPOSITION_SANITY` reproduces composition primitive at SAME regime (N_DIM=4096, hub-bridge scope); cited prior ORACLE = 0.8533; tolerance 0.10
  - `ARM_EXP3_BASELINE_REPRODUCTION` reproduces Exp 3 baseline at SAME regime; cited prior = 0.4133; tolerance 0.10
  - `ARM_STAGE3_V1_QUERY_ONLY_RESCORE` reproduces Exp 3B v1 HF at SAME regime; cited prior = 0.0133; tolerance 0.10 (Fix#28 confidence check)
  - `ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY` reproduces Exp 3C v2 HF at SAME regime; cited prior = 0.0367; tolerance 0.10 (Fix#28 confidence check)
- Gate E: functional requirements decomposed above; each mapped to existing chain-grade primitive (composition + bridge extraction) or novel triple-filter (v3 primitive introduced).

## Verdict logic (formal predicates)

Let MAIN = ARM_MAIN_LAYER075_STACKED_V3 mean, ORACLE = ARM_ORACLE_COMPOSITION_SANITY mean, BASE = ARM_EXP3_BASELINE_REPRODUCTION mean, S3V3 = ARM_STAGE3_V3_STRUCTURAL_SLOT_ONLY mean, S3V1 = ARM_STAGE3_V1 mean, S3V2 = ARM_STAGE3_V2 mean.

```
if not cardinality_ok:              HARD_FAIL cardinality breach
elif not arms_differ_ok:            HARD_FAIL META_RULE_AF
elif |ORACLE - 0.8533| >= 0.10:     HARD_FAIL HALT_ORACLE_DRIFT
elif MAIN >= 0.90 * ORACLE:         HARD_PASS FULL_CLOSURE_LAYER075_V3 (retrieval-architecture arc CLOSES)
elif MAIN >= 0.413 and S3V3 > 0.413:HARD_PASS INTERFACE_POSITIVE_LAYER075_V3 (v3 non-destructive)
elif MAIN < 0.413 and S3V3 < 0.20:  HARD_FAIL LAYER075_V3_DEAD — escalate to path (a) BridgeRAG tripartite
else:                                MIDDLE_BAND partial
```

Report soft-flag drifts on EXP3_BASELINE, STAGE3_V1, STAGE3_V2 alongside verdict.

## GT-coverage instrumentation

For the first 10 queries per seed, log:
- P_1 pool size (post PPR union)
- GT chunks present in P_1 pool (should be ≥ 1 typically per Exp 2C bridge-capture)
- Structural-filter output facts
- GT chunks present in filter output — **this is the key diagnostic**: if structural filtering STILL drops GT chunks, the mechanism is dead too
- Bridge extraction results (whether mid was captured as a bridge candidate)

## Explicit arc-closure statement

If HARD_PASS_FULL_CLOSURE: retrieval-architecture arc CLOSES on hub-concept-bridge scope; ready for Director-KB scale re-test (170K atoms).

If HARD_PASS_INTERFACE_POSITIVE: structural filtering non-destructive; deeper improvement toward full closure deferred to next iteration OR scale escalation.

If HARD_FAIL_DEAD: structural filtering ALSO dead. Path a' does not solve bridge-role disambiguation at synthetic-opaque-token regime. Escalate to path (a) BridgeRAG tripartite: learn a trainable joint scoring function s(q, b, c) that jointly attends to query, bridge, and candidate — abandoning the pre-fused-augmentation family entirely.

If MIDDLE_BAND: partial signal. Investigate whether hyperparameter tuning (B_BRIDGES, relation-match strictness) recovers signal OR escalate.
