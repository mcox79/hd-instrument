# PREREG 2026-07-03 — Experiment 3: composition recovery vs ORACLE (hub-concept-bridge scope)

## Anchor
`substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03`

## Cell path
`experiments/exp_substrate_stage1_apply_exp3_composition_recovery_hub_bridge_smoke_2026_07_03.py`

## Scope (Skunkworks Exp 2C VET tier ruling)
**Hub-concept 2-hop bridge queries ONLY.** Per today's Skunkworks Exp 2C tier ruling: PPR-walk mechanism validated at MEASURED_MECHANISM tier, scope constrained to queries where the bridging entity is a HUB concept (deg >= HUB_DEG_MIN). We do NOT smuggle non-hub-bridge queries in — filter is enforced at query-synthesis + reported in metrics.

## Load-bearing question
Does end-to-end pipeline (hop-1 BGE dense → PPR-walk over KG → composition) recover composition F1 approaching the ORACLE=0.783 baseline established by `exp_substrate_rag_with_substrate_composition_smoke_2026_07_03`, thereby closing the retrieval-architecture arc (composition works; retrieval was the bottleneck; graph-walk fixes retrieval within hub-concept-bridge scope)?

## Precedent numbers (MEASURED@ tagged)
- ORACLE arm = 0.7833  MEASURED@d:/AI/hd-instrument/data/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03_smoke/metrics.json:per_arm_mean_accuracy.ARM_TANDEM_SUBSTRATE_ORACLE
- BGE-composition arm = 0.0833  MEASURED@d:/AI/hd-instrument/data/exp_substrate_rag_with_substrate_composition_smoke_2026_07_03_smoke/metrics.json:per_arm_mean_accuracy.ARM_TANDEM_RAG_SUBSTRATE_COMPOSITION
- Exp 2C PPR-recovery = 0.993  MEASURED@d:/AI/hd-instrument/data/exp_exp2c_smoke_local/metrics.json:per_arm_mean_recall_at_k.ARM_MAIN_PPR_RECOVERED
- Exp 2C baseline trigram = 0.347  MEASURED@ same file:per_arm_mean_recall_at_k.ARM_HOP1_TRIGRAM_ALONE_BASELINE

## Composition primitive
Identical to `arm_tandem_rag_substrate_composition` from RAG-composition SMOKE. FHRR bind/unbind 2-hop chain over a codebook of entity/relation phase vectors. NOT re-tuned; NOT modified. Pre-flight sanity: ORACLE arm on ground-truth chunks must reproduce ~0.783 or halt (composition primitive drifted since 2026-07-03 morning).

## Corpus (SMOKE)
Hub-and-spoke synthetic corpus derived from RAG-composition SMOKE + hub injection:
- `N_ENTITIES = 40`, `N_RELATIONS = 5`, `N_FACTS = 200`
- 3 hub entities (indices 0,1,2) chosen as fact VALUE with probability 3x higher than non-hubs.
- Result: hub entities have in-degree ~15-30; non-hub in-degree ~1-4. Matches Exp 2C's Wikidata hub-and-spoke topology qualitatively.
- Query set: 30 chain queries "What is r1 of r2 of e0?" filtered to `mid ∈ hub_set` (hub-concept-bridge scope). If synthesizer under-produces (< 10 queries), verdict = MIDDLE_BAND_VACUOUS_SUBSET.

## Compute architecture
- Storage strategy: **sharded** (each fact = one FHRR triple HD; no bundling; matches Skunkworks 2026-07-02 META_STORAGE_STRATEGY_COMPOSITION_DEPTH_PHYSICS_LAW).
- Class: **sequential-CPU** with justification: (a) per-query PPR is a sparse mat-vec on a 40x40 adjacency (< 1 ms), (b) FHRR composition is a chain-dependent operation (unbind step N depends on step N-1), (c) total wall time < 10s for 30 queries × 3 seeds. Not batching-eligible.

## Arms (4)
1. `ARM_BGE_ONLY_COMPOSITION_BASELINE` — hop-1 BGE dense top-K candidates → composition primitive. Reproduces RAG-composition SMOKE HF regime; expected ~0.083.
2. `ARM_PPR_UNION_HOP1_COMPOSITION_MAIN` — union of {BGE hop-1 top-K} + {PPR-walk top-K entities seeded from BGE hop-1's entities → all facts involving those entities} → composition primitive. Target: near ORACLE.
3. `ARM_ORACLE_COMPOSITION_SANITY` — ground-truth 2 chain facts → composition primitive. Sanity check for 0.783 reproduction.
4. `ARM_RANDOM_CANDIDATES_CONTROL` — 5 random facts → composition primitive. Chance floor (~0.05 = 1/20 answer alphabet).

## Bands (per META_RULE_L strict-above-floor)
- HARD_PASS: MAIN composition F1 >= 0.90 * ORACLE_measured (i.e. >= 0.70 target when ORACLE reproduces 0.783). Threshold auto-scales with measured ORACLE at smoke time.
- HARD_FAIL: MAIN composition F1 < 0.60 * ORACLE_measured (~0.47 when ORACLE = 0.783).
- MIDDLE_BAND: 0.60..0.90 * ORACLE_measured.
- Additional strict gates:
  - ORACLE sanity: `abs(ORACLE_arm - 0.783) < 0.10` else HALT_ORACLE_DRIFT (composition primitive changed since 2026-07-03 morning).
  - Baseline reproduction: `abs(BASELINE_arm - 0.083) < 0.10` else FLAG_BASELINE_DRIFT (dense retrieval regime changed).
- HP_SCOPE: HARD_PASS gate applies only to `ARM_PPR_UNION_HOP1_COMPOSITION_MAIN`. ORACLE gate applies to `ARM_ORACLE_COMPOSITION_SANITY`. RANDOM/BASELINE arms exempted from HP threshold; they carry reproduction gates instead.

## Cardinality (META_RULE_H)
`EXPECTED_N_UNITS = 4 arms x 3 seeds = 12`. `cardinality_ok = True` requires actual == expected. `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` on mismatch.

## SCHEMA-VET checklist
- arms_differ_verified: sha256 of per-arm prediction sequences per seed; RANDOM vs BASELINE may legitimately share on all-wrong regime (declare arms_differ_exempted with rationale).
- final_metrics_atomicity: `tmp_replace`
- except SystemExit: raise BEFORE except Exception (NOT BaseException)
- crlb_floor_computed: 0.016 THEORETICAL@sqrt(K/N)=sqrt(5/4096) per Plate 1995 FHRR unbind noise floor (inherited from ORACLE cell)
- crlb_formula_reference: `sqrt(K_chunks/N_dim)` per Plate 1995
- discriminator_reachability: True (HP target 0.70 well above CRLB 0.016)
- baseline_in_band: expect 0.05 < BASELINE < 0.30 (BGE-composition HF regime); verify in smoke
- discriminator survives scale: SMOKE regime IS the discriminator regime; N_DIM=4096, N_ENTITIES=40 close enough to RAG-composition SMOKE precedent (N_DIM=4096, N=20). Composition primitive identical.
- CARDINALITY_OK: mandatory field (see above).
- calibration_check: `default_ok_for_this_regime` — reusing chain-grade FHRR primitives at same regime as ORACLE precedent; PPR alpha=0.15 iters=5 matches Exp 2C field-std.
- start_marker_written: True
- crash_diagnostic_present: True
- heartbeat_present: False (SMOKE wall time < 30s per seed; below 15min threshold)
- cell_chunked: False (single-cell; 3 seeds inline)
- progress_logging: `print_flush_true`

## Test-design gates (§15)
- sweep_alignment_verdict: `ALIGNED` — no sweep axis; single regime.
- discriminating_fraction: N/A (no sweep). Discriminator = arm-vs-arm comparison.
- composition_edges:
  - BGE_dense → entity_extraction (top-K fact entities): SHAPE_MATCH (bijection: fact idx → entity set)
  - entity set → PPR_seed_vec: SHAPE_MATCH (uniform mass over indices)
  - PPR_top_K entities → candidate_facts: SHAPE_MATCH (union of facts with entity or value in top-K)
  - candidate_facts → FHRR_composition_primitive: SHAPE_MATCH (identical signature to ORACLE arm's input)
- positive_control_arms: ORACLE arm reproduces ORACLE=0.783 within +/- 0.10 tolerance at test regime. HARD_FAIL_ORACLE_DRIFT if outside.
- functional_requirements:
  - FR1 "retrieve candidates covering the mid-entity for hub-bridge queries" → PPR-walk over KG (Exp 2C primitive)
  - FR2 "compose 2-hop chain into predicted answer entity" → FHRR bind/unbind chain (ORACLE-cell primitive)
  - FR3 "produce discriminator vs BGE-only baseline" → BASELINE arm at same corpus/queries

## Pause gate
Cell dispatched to `local_cpu_queue` for smoke ONLY. USER-locked 2026-07-01: SMOKE only on local_cpu_queue. Full run (if warranted post-smoke) routes via Orchestrator to remote_cpu_queue.

## Decision-point closure conditions
Retrieval-architecture arc CLOSES if AND ONLY IF:
1. ORACLE_arm reproduces 0.783 +/- 0.10 (composition primitive intact)
2. BASELINE_arm reproduces 0.083 +/- 0.10 (failure regime intact)
3. MAIN_arm >= 0.90 * ORACLE (HARD_PASS)

If any condition fails, arc does NOT close — surface failure mode for USER decision.

## Bias controls
- Query set: hub-concept-bridge ONLY. Non-hub-bridge queries FILTERED at synthesis; scope declared in metrics `n_hub_bridge_queries` field.
- ORACLE sanity check: composition primitive must not have drifted; enforced via strict reproduction gate.
- Baseline reproduction: dense-retrieval-only regime must reproduce the ~0.083 failure; enforced via reproduction gate.
- PPR params: alpha=0.15 iters=5 top_k=5 — INHERITED from Exp 2C (MEASURED_MECHANISM tier). Not re-tuned.
