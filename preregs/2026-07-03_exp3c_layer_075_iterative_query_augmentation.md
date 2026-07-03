# PREREG 2026-07-03 — Experiment 3c: Layer 0.75 Stage 3 REDESIGN via iterative query-augmentation

## Anchor
`substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03`

## Cell path
`experiments/exp_substrate_stage1_apply_exp3c_layer075_iterative_query_augmentation_smoke_2026_07_03.py`

## Motivation (cite chain)
- Skunkworks task `af07b1e11bdf9d322` verified the Exp 3B HF diagnosis: query-only cosine
  rescore is **architecturally bridge-blind** — bridge entity is by definition not in the
  user query text for a multi-hop question, so `cos(Q_0, fact)` cannot up-rank chunks
  that share only the bridge with the query.
- Skunkworks recommended path (b): iterative query-augmentation via bridge-entity
  extraction from the candidate pool (LLM-free, substrate-native). CITED@Skunkworks VET
  af07b1e11bdf9d322 MM_TENTATIVE atom on Director-side abstraction-lossy failure
  ((query, bridge, candidate) collapsed to (query, candidate) silently drops the bridge).
- Path (b) is CHEAPER than path (a) BridgeRAG tripartite `s(q,b,c)` (no new scoring
  primitive; reuses BGE + candidate-pool statistics) — so path (b) is tried first per
  cost ordering. If (b) also HFs, path (a) is next.
- Memory rule reference: `feedback_concept_query_before_dispatch_would_have_predicted_
  substrate_content_HF_2026-07-02.md` — Director-side abstraction-lossy failure is a
  general class; this pre-reg operationalizes the fix for the retrieval-arc instance.

## Load-bearing question
Does **iterative query-augmentation** (bridge-entity discovery from candidate pool +
per-bridge query re-encoding + aggregated rescore) close the interface gap from Exp 3
(MAIN=0.411 vs ORACLE=0.822)? Or is the abstraction-lossy failure mode fundamental
to LLM-free retrieval, escalating to path (a) BridgeRAG tripartite?

## Precedent numbers (MEASURED@ tagged)
- ORACLE at hub-bridge scope = 0.8533  MEASURED@d:/AI/hd-instrument/data/exp_exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_ORACLE_COMPOSITION_SANITY
- Exp 3B EXP3_BASELINE = 0.4133  MEASURED@ same file:per_arm_mean_accuracy.ARM_EXP3_BASELINE_REPRODUCTION
- Exp 3B MAIN (v1 with query-only Stage 3) = 0.0267  MEASURED@ same file:per_arm_mean_accuracy.ARM_MAIN_LAYER075_STACKED
- Exp 3B STAGE3_ONLY (v1 query-only rescore) = 0.0133  MEASURED@ same file:per_arm_mean_accuracy.ARM_STAGE3_ONLY
- Exp 3B STAGE1_ONLY = 0.3933  MEASURED@ same file
- Exp 3B STAGE2_ONLY = 0.4067  MEASURED@ same file
- Frady-Sommer SNR at (K=5, N=4096) = 28.6  THEORETICAL@sqrt(N/K)=sqrt(4096/5) — deep in safe argmax zone; failure is not argmax noise.

**Diagnosis carried forward from Exp 3B VET:** query-only cosine rescore drops ~60% of
GT chunks because `cos(Q_0, gt_hop2_fact)` is low when the hop-2 fact only shares the
bridge (not any query token) with Q_0. Query-only Stage 3 REMOVED true GT chunks that
Layer 0.5 had correctly surfaced in the 30-chunk PPR union — Stage 3 v1 was strictly
destructive.

## Layer 0.75 v2 primitive

Stages 1 and 2 UNCHANGED from Exp 3B (verified null-effect but not net-negative;
STAGE1_ONLY 0.393, STAGE2_ONLY 0.407 vs baseline 0.413 — noise-level shift). Only
Stage 3 is replaced.

### Stage 3 v2: iterative query-augmentation via bridge-entity discovery

Substrate-native, LLM-free. Sub-primitive is candidate-pool entity co-occurrence
counting + BGE re-encoding + score aggregation. Per Skunkworks tolerance (Principle
11): no new abstraction — reuses BGE encoder + existing entity vocabulary
(`ENTITIES` list) already loaded in the cell for the KG-walk stage.

**Algorithm:**
```
Input: candidate_indices P_1 (up to 30 facts from PPR union), query_text Q_0,
       facts, ENTITIES vocabulary, fact_bge (BGE embeddings), query_bge Q0_emb.
Output: K_FINAL=5 fact indices.

# Step A: bridge-entity discovery from P_1
entity_count = {}                                    # entity_idx -> {distinct fact_i}
for i in P_1:
    e, r, v, _ = facts[i]
    entity_count.setdefault(ENTITIES.index(e), set()).add(i)
    entity_count.setdefault(ENTITIES.index(v), set()).add(i)
# Bridge candidates = entities appearing in >=2 distinct facts in P_1
bridge_candidates = [e for e, fs in entity_count.items() if len(fs) >= 2]
# Rank by pool-frequency and drop entities already in query text (would be trivial)
q_lower = Q_0.lower()
bridge_candidates = [e for e in bridge_candidates
                     if ENTITIES[e].lower() not in q_lower]
bridge_candidates.sort(key=lambda e: -len(entity_count[e]))
bridge_candidates = bridge_candidates[:B_BRIDGES]    # B_BRIDGES=5

# Step B: build augmented queries + encode
aug_texts = [Q_0 + " " + ENTITIES[b] for b in bridge_candidates]
aug_emb = bge_encode(aug_texts)                       # (B, D)

# Step C: score each candidate in P_1 vs Q_0 + each Q_aug_i
cand_emb = fact_bge[P_1]                              # (K_p1, D)
cos_q0 = cand_emb @ Q0_emb                            # (K_p1,)
cos_aug = aug_emb @ cand_emb.T                        # (B, K_p1)

# Step D: score aggregation (soft-OR over bridges; Q_0 anchored)
w0 = W_QUERY_ANCHOR = 1.0
aug_agg = cos_aug.max(axis=0) if len(bridge_candidates) > 0 else 0
scores = w0 * cos_q0 + W_AUG * aug_agg                # W_AUG = 1.0
# Top K_FINAL by score
selected_local = argsort(scores)[::-1][:K_FINAL]
selected = [P_1[i] for i in selected_local]
```

**Hyperparameters (drill-A-informed; not tuned per-arm):**
- `B_BRIDGES = 5` (top-5 bridge candidates by pool-frequency)
- `W_QUERY_ANCHOR = 1.0`, `W_AUG = 1.0` (equal weight; softest possible aggregation)
- `K_FINAL = 5` (identical to Exp 3B)
- Aggregation = `max` over bridges (each bridge acts as its own hypothesis; best
  match wins). Alternative `sum` deferred (more sensitive to bridge-count).
- Fallback: if `len(bridge_candidates) == 0` (rare), Stage 3 v2 reduces to
  query-only cosine top-K over P_1 (equivalent to Exp 3B Stage 3 v1 sans MMR).

## Composition primitive
**Identical** to Exp 3 / Exp 3B `composition_primitive` (FHRR bind/unbind 2-hop chain).
NOT re-tuned; NOT modified. ORACLE arm reproduces 0.853 hub-bridge scope
(within +/- 0.10 tolerance) or halt via HALT_ORACLE_DRIFT.

## Corpus & regime (SMOKE — same as Exp 3B for direct comparison)
- Identical hub-and-spoke synthetic corpus (N_ENTITIES=40, N_RELATIONS=5,
  N_FACTS=200, HUB_INDICES=[0,1,2], HUB_OVER_SAMPLE=3.0).
- SMOKE regime: N_DIM=4096, N_QUERIES_TARGET=50/seed, SEEDS=[11,17,23], ~150 queries.
  (Note: Director spawn says "30 diagnostic queries × 3 seeds" — matching Exp 3B's
  N_QUERIES_TARGET=50 which yielded ~50 hub-bridge queries per seed post-scope-filter.
  Field of ~150 queries pooled across seeds is the direct-comparison unit.)
- Hub-concept-bridge scope filter (identical to Exp 3B): `mid in hub_set`.

## Arms (8)
1. `ARM_ORACLE_COMPOSITION_SANITY` — ground-truth 2 gt_chunks -> composition.
   Reproduction gate: drift <= 0.10 vs 0.853.
2. `ARM_EXP3_BASELINE_REPRODUCTION` — Exp 3 MAIN pipeline (BGE hop-1 -> PPR union
   up to 30 -> composition). Reproduction gate: drift <= 0.10 vs 0.413.
3. `ARM_MAIN_LAYER075_STACKED_V2` — Stage 1 seed-reweight + Stage 2 hub-dampened PPR
   + Stage 3 v2 iterative query-augmentation -> composition. **Discriminator arm.**
4. `ARM_STAGE1_ONLY` — Stage 1 only (rest = Exp 3 pipeline).
5. `ARM_STAGE2_ONLY` — Stage 2 only.
6. `ARM_STAGE3_V1_QUERY_ONLY_RESCORE` — Exp 3B Stage 3 v1 (query-only cosine + MMR),
   reproduced for HF confirmation. Reproduction gate: drift <= 0.10 vs 0.013.
7. `ARM_STAGE3_V2_ITERATIVE_QUERY_AUG_ONLY` — Stage 3 v2 iterative query-augmentation
   ISOLATED (no Stage 1, no Stage 2; normal Exp 3 PPR union -> Stage 3 v2 -> composition).
   Isolates Stage 3 v2 contribution.
8. `ARM_RANDOM_CANDIDATES_CONTROL` — 5 random facts -> composition. Chance floor ~0.05.

## Bands (per META_RULE_L strict-above-floor; dual HP bar per Director spawn)
Auto-scaled to ORACLE_measured at runtime (identical scaling to Exp 3B):

**HARD_PASS_FULL_CLOSURE:** `MAIN_V2 >= 0.90 * ORACLE_measured` (~0.77 given
ORACLE=0.853). Retrieval-architecture arc CLOSES.

**HARD_PASS_INTERFACE_POSITIVE:** `MAIN_V2 >= Exp3_baseline_precedent = 0.413`
**AND** `STAGE3_V2_ONLY > 0.413`. Proves iterative-query-augmentation is at least
non-destructive at the interface (Stage 3 v1 was strictly destructive, dropping
MAIN from 0.413 to 0.027).

**MIDDLE_BAND:** `0.413 <= MAIN_V2 < 0.77` and INTERFACE_POSITIVE gate not fully met
(e.g., MAIN_V2 clears 0.413 but STAGE3_V2_ONLY doesn't).

**HARD_FAIL:** `MAIN_V2 < 0.413` **AND** `STAGE3_V2_ONLY < 0.20`. Iterative query-
augmentation is architecturally dead too. **Escalate to path (a) BridgeRAG tripartite.**

- HP_SCOPE: HARD_PASS_FULL_CLOSURE + HARD_PASS_INTERFACE_POSITIVE apply only to
  `ARM_MAIN_LAYER075_STACKED_V2`. Reproduction gates apply to ORACLE (drift <= 0.10
  vs 0.853), EXP3_BASELINE (drift <= 0.10 vs 0.413), STAGE3_V1_QUERY_ONLY (drift <=
  0.10 vs 0.013). Ablation arms + RANDOM exempt from HP threshold.
- Additional strict gates:
  - HALT_ORACLE_DRIFT: `abs(ORACLE_arm - 0.853) < 0.10` else HARD_FAIL
    (composition primitive changed since Exp 3B).
  - FLAG_BASELINE_DRIFT: `abs(EXP3_BASELINE_arm - 0.413) < 0.10` else soft flag.
  - FLAG_V1_HF_DRIFT: `abs(STAGE3_V1_QUERY_ONLY_arm - 0.013) < 0.10` else soft flag
    (Fix#28 confidence check — must reproduce the HF for the Skunkworks diagnosis
    to be trusted).

## Cardinality (META_RULE_H)
`EXPECTED_N_UNITS = 8 arms x 3 seeds = 24`. `cardinality_ok = True` requires
actual == expected. `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch.

## Compute architecture
- Storage strategy: **sharded** (each fact = one FHRR triple HD; META_STORAGE_STRATEGY_
  COMPOSITION_DEPTH_PHYSICS_LAW 2026-07-02 compliance).
- Class: **sequential-CPU** with justification: (a) per-query PPR sparse matvec on 40x40
  adjacency (< 1ms), (b) FHRR composition chain-dependent (unbind step N depends on step
  N-1), (c) BGE re-encoding of augmented queries adds up to 5 texts per query per seed
  (~750 short-text BGE encodes per seed, ~30s), (d) total wall time projected ~90-180s
  for 3 seeds x 8 arms x ~50 queries. Not batching-eligible at this regime.
- Progress logging: `print_flush_true` (per §17; wall projected 90-180s is under 15min
  threshold but flush-true is defense-in-depth).

## Bias / discipline compliance
- CARDINALITY_OK: field mandatory (see above).
- Concept-query-before-dispatch: DONE 2026-07-03 pre-authoring. Top substrate hit
  cosine=0.315 was HippoRAG PPR iterative random walks (graph-spreading mechanism);
  cosine=0.303 was hybrid substrate architecture. NEITHER is candidate-pool bridge
  extraction + query re-encoding. Genuinely novel operationalization.
- ORACLE reproduction gate: drift <= 0.10 from 0.853.
- Exp 3 baseline reproduction gate: drift <= 0.10 from 0.413.
- **Fix#28 confidence-check reproduction gate: drift <= 0.10 from 0.013 for
  STAGE3_V1_QUERY_ONLY** (must reproduce the HF for the diagnosis to be trusted).
- Full smoke code path exercises same branches as FULL (smoke IS the full regime per
  USER-locked 2026-07-01 SMOKE-only-local policy).
- Fix#28 discipline: metrics.json per-arm scores verified off-disk in completion
  report, not by re-summarizing verdict_msg.
- Per-query GT-coverage tracking mid-cell (same tool cell-author added in Exp 3B):
  for first 10 queries per seed, record `gt_in_p1_pool` (pre-Stage-3-v2),
  `gt_in_p2_selected` (post-Stage-3-v2), `bridge_candidates_extracted`. If Stage 3 v2
  STILL drops most GT chunks, the abstraction is dead — escalate.
- Local_cpu only per USER-locked 2026-07-01.

## SCHEMA-VET checklist
- arms_differ_verified: sha256 of per-arm prediction sequences per seed.
  STAGE3_V1 vs STAGE3_V2 must differ (they're the point of comparison).
  RANDOM vs low-scoring arms may legitimately share on very-hard queries; declare
  exempt post-hoc if convergence is genuine chance-level.
- final_metrics_atomicity: `tmp_replace`
- except SystemExit: raise BEFORE except Exception (NOT BaseException)
- crlb_floor_computed: 0.035 THEORETICAL@sqrt(K_final/N_dim)=sqrt(5/4096)
- discriminator_reachability: True (HP target ~0.77 well above CRLB 0.035; interface-
  positive gate 0.413 also feasible per Exp 3 baseline achievement)
- baseline_in_band: EXP3_BASELINE expected ~0.41 (in band 0.05..0.95); verify in smoke
- discriminator survives scale: SMOKE regime IS discriminator regime (matches Exp 3B)
- cell_chunked: False (single-cell; 3 seeds inline; wall < 5min projected)
- start_marker_written: True
- crash_diagnostic_present: True
- heartbeat_present: False (wall < 15min threshold)
- progress_logging: `print_flush_true`
- calibration_check: `default_ok_for_this_regime` — reuses chain-grade FHRR + Exp 2C
  PPR + Exp 3B hyperparams unchanged (HUB_DEG_THRESH=8, HUB_DAMPEN=0.30, K_FINAL=5)
  + new Stage 3 v2 hyperparams (B_BRIDGES=5, W_QUERY_ANCHOR=1.0, W_AUG=1.0).

## Test-design gates (§15)
- sweep_alignment_verdict: `ALIGNED` — no sweep axis; single regime; ablations
  isolate stages.
- discriminating_fraction: N/A (no sweep). Discriminator = arm-vs-arm comparison
  vs measured precedents.
- composition_edges:
  - BGE dense (hop-1 top-K facts) -> seed entities: SHAPE_MATCH
  - seed_entities -> stage1_reweighted_seed_vec: SHAPE_MATCH
  - reweighted_seed + hub_dampened_A -> PPR_dist: SHAPE_MATCH (Exp 2C primitive)
  - PPR_top_K -> candidate_facts P_1 (up to 30): SHAPE_MATCH
  - **P_1 -> bridge_entity_extraction (co-occurrence counting): SHAPE_MATCH
    (integer indexing over ENTITIES vocabulary; no new abstraction)**
  - **bridge_candidates + BGE(query + " " + bridge_name) -> B x D augmented embeddings:
    SHAPE_MATCH (BGE is the same encoder; text-input, dense-vector-output signature)**
  - **augmented_emb + query_emb + fact_bge[P_1] -> aggregated cos scores: SHAPE_MATCH
    (matmul + max-pool over bridges; standard batched dot-product)**
  - top-K by aggregated score -> K_FINAL=5 facts: SHAPE_MATCH
  - K_FINAL=5 facts -> FHRR_composition_primitive: SHAPE_MATCH (identical to Exp 3B)
- positive_control_arms:
  - `ARM_ORACLE_COMPOSITION_SANITY` reproduces 0.853 within 0.10 (composition intact
    positive control; HARD_FAIL_ORACLE_DRIFT if outside).
  - `ARM_EXP3_BASELINE_REPRODUCTION` reproduces 0.413 within 0.10 (Exp 3 MAIN intact
    positive control; FLAG_BASELINE_DRIFT if outside — soft).
  - `ARM_STAGE3_V1_QUERY_ONLY_RESCORE` reproduces 0.013 within 0.10 (Exp 3B Stage 3
    v1 HF reproduction; FLAG_V1_HF_DRIFT if outside — soft; Fix#28 confidence check).
- functional_requirements:
  - FR1 "seed PPR with query-specific bias" -> stage 1 (node-spec IDF re-weight; unchanged)
  - FR2 "prevent hub-collapse of PPR mass" -> stage 2 (hub-dampened adjacency; unchanged)
  - FR3 "surface bridge-relevant candidates that lack query-token overlap" -> stage 3 v2
    (iterative query-augmentation via bridge-entity discovery + re-encoding)
  - FR4 "compose 2-hop chain into predicted answer" -> composition primitive (Exp 3 ORACLE)
  - FR5 "prove v2 non-destructive vs v1 destructive" -> STAGE3_V1 arm HF-reproduces
    (0.013); STAGE3_V2_ONLY arm > 0.413 (non-destructive; interface-positive gate)

## Pause gate
Local_cpu_queue only. USER-locked 2026-07-01 SMOKE-only-local policy. No FULL
dispatch from this cell without explicit USER authorization.

## Decision-point closure conditions

**Arc CLOSES (HARD_PASS_FULL_CLOSURE) iff ALL:**
1. ORACLE_arm reproduces 0.853 +/- 0.10 (composition primitive intact)
2. EXP3_BASELINE_arm reproduces 0.413 +/- 0.10 (Exp 3 regime intact)
3. STAGE3_V1_arm reproduces 0.013 +/- 0.10 (Fix#28 diagnosis confirmed)
4. MAIN_V2_arm >= 0.90 * ORACLE_measured (HARD_PASS_FULL_CLOSURE)

**Arc PARTIALLY CLOSES (HARD_PASS_INTERFACE_POSITIVE) iff ALL:**
1-3 above AND MAIN_V2 >= 0.413 AND STAGE3_V2_ONLY > 0.413. Iterative query-
augmentation validated as non-destructive; interface primitive proven; deeper
retrieval improvement deferred to Layer 0.75.v3 or scale escalation.

**Arc DOES NOT CLOSE (HARD_FAIL) iff:**
MAIN_V2 < 0.413 AND STAGE3_V2_ONLY < 0.20. Iterative query-augmentation
architecturally dead; escalate to **path (a) BridgeRAG tripartite** `s(q,b,c)`.
