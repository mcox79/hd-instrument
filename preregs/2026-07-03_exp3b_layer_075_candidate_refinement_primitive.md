# PREREG 2026-07-03 — Experiment 3b: Layer 0.75 candidate-refinement primitive (3-stage stacked)

## Anchor
`substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03`

## Cell path
`experiments/exp_substrate_stage1_apply_exp3b_layer075_candidate_refinement_smoke_2026_07_03.py`

## Load-bearing question
Does a **3-stage LLM-free candidate-refinement primitive** placed BETWEEN Layer 0.5
(PPR-walk output ~30 chunks) and Layer 1 (FHRR composition needing ~2-5 clean chunks)
close the interface gap discovered by Exp 3 (MAIN=0.411 vs ORACLE=0.822 on-disk;
same hub-concept-bridge regime)?

**Arc-closure criterion (per Director spawn prompt 2026-07-03):** if MAIN clears
HP gate (>= 0.90 * ORACLE_measured ~ 0.74), the retrieval-architecture arc CLOSES:
encoder-swap DEFERRED validated, Layer 0.5 KG-walk + Layer 0.75 refinement + Layer 1
FHRR composition pipeline validated within hub-concept-bridge scope.

## Precedent numbers (MEASURED@ tagged)
- ORACLE arm at hub-bridge scope = 0.8222  MEASURED@d:/AI/hd-instrument/data/exp_substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03/metrics.json:per_arm_mean_accuracy.ARM_ORACLE_COMPOSITION_SANITY
- Exp 3 MAIN (PPR union ~30 chunks) = 0.4111  MEASURED@ same file:per_arm_mean_accuracy.ARM_PPR_UNION_HOP1_COMPOSITION_MAIN
- Exp 3 BGE-only baseline = 0.000  MEASURED@ same file:per_arm_mean_accuracy.ARM_BGE_ONLY_COMPOSITION_BASELINE
- Exp 3 RANDOM control = 0.0556  MEASURED@ same file:per_arm_mean_accuracy.ARM_RANDOM_CANDIDATES_CONTROL
- Frady-Sommer SNR at (K=5, N=4096) = 28.6  THEORETICAL@sqrt(N/K)=sqrt(4096/5) — deep in safe argmax zone

**Failure diagnosis (post-drill 2026-07-03):** Exp 3 MAIN failure is NOT argmax noise
(SNR is safe). It is **semantic candidate contamination**: 28 wrong chunks in the
30-chunk PPR union are semantically-adjacent hub-adjacent distractors, not iid noise.
Composition primitive can't distinguish query-relevant from query-irrelevant when
28/30 candidates are all plausible. Fix requires SEMANTIC filtering, not more N.

## Layer 0.75 primitive (3 composable stages)

### Stage 1: node-specificity seed re-weighting (HippoRAG IDF)
- Mechanism: each seed node's PPR personalization probability multiplied by
  `1 / passage_count(node)` where `passage_count(node)` = count of facts in which
  the node appears (as entity or value).
- Precedent CITED@HippoRAG NeurIPS 2024 arXiv 2405.14831 (ablation +3pp MuSiQue R@2)
- Substrate-native: cheap, uses signals already in KGStore.

### Stage 2: hub-dampening inside walk step
- Mechanism: for each node with degree > `HUB_DEG_THRESH=8` (on our 40-entity KG),
  scale down its outgoing edge weights by `HUB_DAMPEN_FACTOR=0.30`. Applied to the
  column-stochastic adjacency BEFORE PPR iteration. Relative ordering of a hub's
  neighbors preserved; total mass through hubs capped. PPR renormalizer (already
  present in Exp 2C primitive) absorbs mass leak.
- Precedent CITED@CatRAG arXiv 2602.01965 "Breaking the Static Graph"
- Addresses Exp 2C VET diagnosis: "hub-and-spoke KG concentrates PPR mass on hubs
  regardless of specific query" — hub-dampening breaks the static-graph fallacy.

### Stage 3: query-conditioned rescore + MMR diversity finalizer
- Mechanism: for each candidate fact surviving stages 1+2, compute
  `s_i = cos(BGE(query_text), BGE(fact_text_i))` reusing the BGE encodings from
  hop-1 retrieval. Apply MMR with `MMR_LAMBDA=0.4`:
  `c* = argmax_i [ lambda * s_i - (1 - lambda) * max_{j in selected} cos(fact_i, fact_j) ]`
  until `K_FINAL=5` candidates selected.
- Precedent CITED@Carbonell & Goldstein 1998 MMR
- Substrate-native: cosine + closed-form MMR; no external LLM, no training.

## Composition primitive
**Identical** to Exp 3 `composition_primitive` (FHRR bind/unbind 2-hop chain).
NOT re-tuned; NOT modified. ORACLE arm reproduces 0.822 hub-bridge scope
(within +/- 0.10 tolerance) or halt via HALT_ORACLE_DRIFT.

## Corpus & regime (SMOKE)
- **Identical hub-and-spoke synthetic corpus to Exp 3** (N_ENTITIES=40, N_RELATIONS=5,
  N_FACTS=200, HUB_INDICES=[0,1,2], HUB_OVER_SAMPLE=3.0).
- SMOKE regime: N_DIM=4096, N_QUERIES_TARGET=50/seed, SEEDS=[11,17,23], total ~150 queries.
- FULL regime (deferred; not this smoke): N_DIM=8192, N_QUERIES_TARGET=100/seed.
- Hub-concept-bridge scope filter (identical to Exp 3): `mid ∈ hub_set`.

## Arms (7)
1. `ARM_ORACLE_COMPOSITION_SANITY` — ground-truth 2 gt_chunks → composition.
   Target ~0.822 (drift <= 0.10). Sanity check composition primitive intact.
2. `ARM_EXP3_BASELINE_REPRODUCTION` — Exp 3 MAIN pipeline (BGE hop-1 → PPR union
   up to 30 chunks → composition). Target ~0.411 (drift <= 0.10). Baseline check
   Exp 3 regime intact.
3. `ARM_MAIN_LAYER075_STACKED` — BGE hop-1 → stage1 seed reweight → stage2 hub-
   dampened PPR → union up to 30 → stage3 rescore+MMR to K_FINAL=5 → composition.
   Target: >= 0.90 * ORACLE_measured (~0.74). **This is the discriminator arm.**
4. `ARM_STAGE1_ONLY` — BGE hop-1 → stage1 seed reweight → normal PPR → union up
   to 30 → composition. Ablation: does node-spec IDF alone lift over baseline?
5. `ARM_STAGE2_ONLY` — BGE hop-1 → normal seed → stage2 hub-dampened PPR → union
   up to 30 → composition. Ablation: does hub-dampen alone lift?
6. `ARM_STAGE3_ONLY` — BGE hop-1 → normal seed → normal PPR → union up to 30 →
   stage3 rescore+MMR to K_FINAL=5 → composition. Ablation: does rescore+MMR alone lift?
7. `ARM_RANDOM_CANDIDATES_CONTROL` — 5 random facts → composition. Chance floor ~0.05.

## Bands (per META_RULE_L strict-above-floor)
Auto-scaled to ORACLE_measured at runtime (identical scaling to Exp 3):
- HARD_PASS: `MAIN >= 0.90 * ORACLE_measured` (~ 0.74) **AND** MAIN strictly greater than
  every single-stage ablation (STAGE1_ONLY, STAGE2_ONLY, STAGE3_ONLY) with margin >= 0.02.
  Second clause proves stacking necessary (no single stage suffices).
- HARD_FAIL: `MAIN < 0.60 * ORACLE_measured` (~ 0.493) — no lift over Exp 3 baseline;
  Layer 0.75 does not close the gap.
- MIDDLE_BAND: 0.60..0.90 * ORACLE_measured (~ 0.493..0.74).
- HP_SCOPE: HP applies only to `ARM_MAIN_LAYER075_STACKED`. Reproduction gates apply
  to ARM_ORACLE_COMPOSITION_SANITY (drift <= 0.10) and ARM_EXP3_BASELINE_REPRODUCTION
  (drift <= 0.10). Ablation arms + RANDOM exempt from HP threshold.
- Additional strict gates:
  - HALT_ORACLE_DRIFT: `abs(ORACLE_arm - 0.8222) < 0.10` else HARD_FAIL
    (composition primitive changed since 2026-07-03 morning)
  - FLAG_BASELINE_DRIFT: `abs(EXP3_BASELINE_arm - 0.4111) < 0.10` else soft flag
    (Exp 3 regime changed; MAIN interpretation degraded but not fatal)

## Cardinality (META_RULE_H)
`EXPECTED_N_UNITS = 7 arms x 3 seeds = 21`. `cardinality_ok = True` requires
actual == expected. `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch.

## Compute architecture
- Storage strategy: **sharded** (each fact = one FHRR triple HD; matches
  META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW 2026-07-02).
- Class: **sequential-CPU** with justification: (a) per-query PPR is sparse
  matvec on 40x40 adjacency (< 1 ms), (b) FHRR composition is chain-dependent
  (unbind step N depends on step N-1), (c) MMR is iterative-greedy over ~30 facts,
  (d) total wall time < 60s for 50 queries * 3 seeds * 7 arms. Not batching-eligible.

## Bias / discipline compliance
- CARDINALITY_OK: field mandatory (see above).
- Concept-query-before-dispatch: performed by exp_dev pre-authoring 2026-07-03.
  Top hit cosine=0.29 ("candidate" wordnet) — no prior Layer-0.75-style primitive
  in Store. Genuinely novel operationalization of the hierarchical-cleanup 2026-06-10
  substrate note.
- ORACLE reproduction gate: drift <= 0.10 from 0.822 hub-bridge scope.
- Exp 3 baseline reproduction gate: drift <= 0.10 from 0.411.
- Full smoke code path exercises same branches as FULL (smoke regime IS the full
  regime for this smoke-only dispatch per USER-locked 2026-07-01 SMOKE-only-local policy).
- Fix#28 discipline: metrics.json per-arm scores verified off-disk in completion report,
  not by re-summarizing verdict_msg.
- Local_cpu only per USER-locked 2026-07-01.

## SCHEMA-VET checklist
- arms_differ_verified: sha256 of per-arm prediction sequences per seed.
  RANDOM vs BASELINE may legitimately share on very-hard queries; declare exempt if so.
- final_metrics_atomicity: `tmp_replace`
- except SystemExit: raise BEFORE except Exception (NOT BaseException)
- crlb_floor_computed: 0.016 THEORETICAL@sqrt(K_final/N_dim)=sqrt(5/4096)
- discriminator_reachability: True (HP target ~0.74 well above CRLB 0.016; MAIN
  headroom vs single-stage arms >= 0.02 achievable per drill C literature)
- baseline_in_band: EXP3_BASELINE expected ~0.41 (in band 0.05..0.95); verify in smoke
- discriminator survives scale: SMOKE regime IS discriminator regime (matches Exp 3)
- cell_chunked: False (single-cell; 3 seeds inline; wall time < 60s)
- start_marker_written: True
- crash_diagnostic_present: True
- heartbeat_present: False (wall < 15min threshold)
- progress_logging: `print_flush_true`
- calibration_check: `default_ok_for_this_regime` — reusing chain-grade FHRR + Exp 2C
  PPR + drill-A-informed hyperparams (HUB_DEG_THRESH=8, HUB_DAMPEN=0.30, MMR_LAMBDA=0.4,
  K_FINAL=5).

## Test-design gates (§15)
- sweep_alignment_verdict: `ALIGNED` — no sweep axis; single regime.
- discriminating_fraction: N/A (no sweep). Discriminator = arm-vs-arm comparison.
- composition_edges:
  - BGE_dense (hop-1 top-K facts) → seed_entities (union of entity+value slots): SHAPE_MATCH
  - seed_entities → stage1_reweighted_seed_vec (IDF weights over entity indices): SHAPE_MATCH
  - reweighted_seed + hub_dampened_A → PPR_dist over entities: SHAPE_MATCH (Exp 2C primitive)
  - PPR_top_K entities → candidate_facts (union): SHAPE_MATCH
  - candidate_facts (up to 30) + query_BGE → rescored+MMR K_FINAL=5 facts: SHAPE_MATCH
  - K_FINAL=5 facts → FHRR_composition_primitive: SHAPE_MATCH (identical to Exp 3 ORACLE)
- positive_control_arms:
  - `ARM_ORACLE_COMPOSITION_SANITY` reproduces 0.822 within 0.10 (composition primitive
    intact positive control at test regime; HARD_FAIL_ORACLE_DRIFT if outside)
  - `ARM_EXP3_BASELINE_REPRODUCTION` reproduces 0.411 within 0.10 (Exp 3 MAIN pipeline
    intact positive control at test regime; FLAG_BASELINE_DRIFT if outside — soft)
- functional_requirements:
  - FR1 "seed PPR with query-specific bias" → stage 1 (node-spec IDF re-weight)
  - FR2 "prevent hub-collapse of PPR mass" → stage 2 (hub-dampened adjacency)
  - FR3 "filter semantic distractors before FHRR composition" → stage 3 (rescore + MMR)
  - FR4 "compose 2-hop chain into predicted answer" → composition primitive (Exp 3 ORACLE)
  - FR5 "prove stacking necessary" → stage-ablation arms 4/5/6 must underperform MAIN

## Pause gate
Local_cpu_queue only. USER-locked 2026-07-01 SMOKE-only-local policy. No FULL
dispatch from this cell without explicit USER authorization.

## Decision-point closure conditions
Retrieval-architecture arc CLOSES iff ALL:
1. ORACLE_arm reproduces 0.822 +/- 0.10 (composition primitive intact)
2. EXP3_BASELINE_arm reproduces 0.411 +/- 0.10 (Exp 3 regime intact)
3. MAIN_arm >= 0.90 * ORACLE_measured (HARD_PASS)
4. MAIN > every single-stage ablation with margin >= 0.02 (stacking necessary)

If any condition fails, arc does NOT close — surface failure mode for Director decision.
