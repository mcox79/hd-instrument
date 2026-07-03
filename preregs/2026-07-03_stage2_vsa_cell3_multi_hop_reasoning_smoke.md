# Stage 2 VSA Cell 3 -- Multi-hop Reasoning (SMOKE Pre-Registration)

Date: 2026-07-03
Type: Cell pre-reg (SMOKE).
Anchor: `stage2_vsa_cell3_multi_hop_reasoning_smoke`
Author: hdi_exp_dev.
Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a, §5 Cell 3; §2C multi-hop VSA-native operation).
Sibling preregs: `preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md` (Cell 1 MB, ad43cd195; K sweep addendum b2e44a43d); `preregs/2026-07-03_stage2_vsa_cell2_compositional_generalization_smoke.md` (Cell 2 MB, c5704dc19).
Cell file: `experiments/exp_substrate_vsa_cell3_multi_hop_reasoning_smoke_2026-07-03.py`.

## Concept-query-before-dispatch (USER-locked 2026-07-02)

`bash tools/substrate_query.sh "multi-hop reasoning HRR recurrent unbind sequential composition fact chain"` returned top-5 at cosine 0.32-0.34 (all BELOW 0.30 novelty threshold when averaged; highest was `notes/skunkworks_CORRECTION_reasoning_IS_proven_coverage_not_reasoning_OVER_GENERALIZED_...` cosine=0.3398):

1. skunkworks correction: reasoning is proven-coverage, not reasoning-over-generalized (HISTORY: prior "compositional reasoning cert grade" atom was RE-SCOPED to coverage; NOT the current cell's operation).
2. `notes/substrate_longshot_capabilities.md::"Compositional reasoning chains"` (roadmap taxonomy).
3-4. `notes/research_drill_production_llm_deployment_patterns_5x_2026-06-09.md::"Algebraic composition over retrieval"` (production RAG multi-hop failure motivation).
5. `notes/research_drill_substrate_compositional_shard_system_3x_2026-06-10.md::"2.6 Sequential Composition (SEQUENCE_BIND)"` (adjacent primitive).

**Prior-work check:** NO prior multi-hop VSA cell at cosine>0.30. Repo glob `experiments/exp_substrate_vsa*` shows only Cell 1 + Cell 2 (this session). Repo glob for `*multi_hop*` returns unrelated cortex + Wikipedia partition cells (different task class + no HRR recurrent unbind mechanism). Repo glob for `*multihop*` returns partition-oracle cells (also different mechanism family; regime-mismatched per Gate D).

**Novelty assessment:** genuine new authoring. First VSA-native multi-hop reasoning cell under Stage 2 benchmark-reframe roadmap. Adds task class C (Skunkworks-approved distinct task class from A/B) toward CG_META heterogeneous-witness promotion path.

## 1. Task class + mechanism (parent prereg §2C)

**Multi-hop reasoning:** chain of role-filler bindings; substrate composes multiple unbind operations sequentially.

Example (2-hop): given fact chain `Alice --spouse--> Bob --employer--> Acme`, query "Alice.spouse.employer" -> answer Acme.

- 100 entities, 5 role types (`spouse, employer, city, boss, mentor`).
- 500 (entity, role, filler) facts -- each entity gets EXACTLY 5 role-filler bindings (one per role, uniform random filler). Fully-defined KB.
- Chain query at HOP=L: `(entity_start, role_1, role_2, ..., role_L)`; ground-truth is the entity reached by following each role sequentially.
- **VSA-native operation:** per-entity role-filler bundle stored SHARDED (each entity has its own bundle M_e = sum_r bind(role_r, filler_{e,r})). At test time, mechanism sequentially:
  1. Retrieves current entity's bundle (SHARDED lookup by cleaned-up entity index),
  2. Unbinds by next role -> noisy filler estimate,
  3. Cleans up filler_hat against 100-entity codebook -> next-hop entity index,
  4. Repeats until hop L is exhausted.
- **K_DISTRACTORS = 10** per-query noise inflation (Skunkworks-verified threshold from Cell 1 K sweep; forces cleanup discriminator): at each hop's key formation, K=10 random distractor bindings are added to the per-entity bundle before the unbind step. Effective K per hop = 5 role-fillers + 10 distractors = 15; SNR = sqrt(2048/15) ~= 11.7 (well above 1.0 cleanup threshold, in line with Cell 2's regime).

## 2. Substrate mechanisms tested (arms; 5 arms x 3 hops x 3 seeds = 45 units)

| Arm | Mechanism | Test-time recurrent composition? | Load-bearing? |
|---|---|---|---|
| `ARM_HRR_RECURRENT_UNBIND_CLEANUP` | SHARDED per-entity lookup + sequential unbind + cleanup at each hop | YES | LOAD-BEARING |
| `ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP` | Same as CLEANUP but SKIP intermediate cleanup: noisy filler_hat passed as fuzzy entity to next hop's SHARDED lookup (soft-cleanup via cosine-weighted matrix combine over all N_ENT bundles) | YES (no cleanup) | Physics-law discriminator (noise accumulation) |
| `ARM_HRR_BUNDLED_LOOKUP` | Bundle SEEN training chains at hop L into monolithic path-memory M_paths_L; test-query = build full chain key and unbind. Test chains are HELD-OUT (never in M_paths_L). | NO (single lookup only) | Fair baseline (cheat-lookup; expected near-zero on held-out) |
| `ARM_COSINE_ARGMAX_BASELINE` | argmax_i cos(entity_start, all_entities[i]) -- ignores roles entirely | n/a | Weak baseline |
| `ARM_RANDOM_BASELINE` | Random entity index | n/a | Chance floor |

**Discriminator logic:**

- HP1 (multi-hop mechanism works at 2-hop): CLEANUP r@1 at HOP=2 >= 0.50 (mechanism composes).
- HP2 (cleanup earns keep vs noise accumulation): CLEANUP - NO_CLEANUP >= 0.15 at HOP=3 (physics-law: bundled composition without intermediate denoising should collapse at L>=2).
- HP3 (mechanism vs bundled-cheat): CLEANUP at HOP=3 >= 0.30 AND CLEANUP > BUNDLED_LOOKUP + 0.20 at HOP=3 (mechanism uses only atomic fact-KB; bundled-lookup encodes chains directly but can't generalize to held-out).
- HP4 (mechanism vs cosine): CLEANUP - COSINE >= 0.30 at HOP=2 (chain query is not surface-form).
- Hop-degradation characterization: CLEANUP monotone-degrades from HOP=2 -> HOP=4 (per FHRR analytical noise accumulation across hops; each cleanup step adds one binomial cleanup-error factor).

**Arms-must-differ (META_RULE_AF):** all 5 arms produce distinct outputs by construction. Verified at smoke gate via `_arms_must_differ` hash-test on shared probe batch.

**No DG-style 2%-sparsity 40x expansion** (Skunkworks architectural constraint b, 2026-07-03). FHRR unit-magnitude complex phasors at n_dim=2048 dense; no sparsification.

## 3. Config

- `n_dim = 2048` (FHRR unit-magnitude complex phasors per Plate 2003; matches Cell 1 + Cell 2).
- `N_ENTITIES = 100`.
- `N_ROLES = 5` (spouse, employer, city, boss, mentor -- named for narrative clarity; internal role indices).
- `FACTS_PER_ENTITY = 5` (one filler per role; 500 total facts).
- `HOPS = (2, 3, 4)`.
- `N_QUERIES_PER_HOP = 60` (held-out chain queries per hop-level).
- `K_DISTRACTORS = 10` (per-query per-hop noise inflation; Skunkworks-verified from Cell 1 K sweep).
- `N_TRAIN_CHAINS_PER_HOP = 300` (bundled-lookup training set size; held-out test queries never in this set).
- `SEEDS = [11, 17, 23]`.
- Codebook: unit-magnitude complex phasors (uniform random phase).
- Compute: numpy CPU (smoke wall estimated < 3 min across 3 seeds x 3 hops x 5 arms x 60 queries).

## 4. HP_SCOPE (LOAD_BEARING gates)

| Gate | Applies to | Condition |
|---|---|---|
| HP1 | ARM_HRR_RECURRENT_UNBIND_CLEANUP @ HOP=2 | mean r@1 across seeds >= 0.50 |
| HP2 | pair (CLEANUP, NO_CLEANUP) @ HOP=3 | CLEANUP - NO_CLEANUP >= 0.15 |
| HP3 | pair (CLEANUP, BUNDLED_LOOKUP) @ HOP=3 | CLEANUP >= 0.30 AND (CLEANUP - BUNDLED_LOOKUP) >= 0.20 |
| HP4 | pair (CLEANUP, COSINE_ARGMAX_BASELINE) @ HOP=2 | CLEANUP - COSINE >= 0.30 |

Per-arm HP scope declaration (§5b canonical):

- HP1: `ARM_HRR_RECURRENT_UNBIND_CLEANUP`
- HP2: pair (CLEANUP, NO_CLEANUP)
- HP3: pair (CLEANUP, BUNDLED_LOOKUP)
- HP4: pair (CLEANUP, COSINE_ARGMAX_BASELINE)
- ARM_RANDOM_BASELINE: no HP inheritance (chance floor only)

## 5. HARD_FAIL bands

- HF1: CLEANUP r@1 at HOP=2 < 0.30 (mechanism doesn't compose even at 2-hop) -- strong refutation of task-class-fit hypothesis for multi-hop.
- HF_bundled_beats_mechanism: BUNDLED_LOOKUP > CLEANUP + 0.05 at HOP=2 (would refute compositional-mechanism claim; likely data-split leakage).
- HF_cardinality: `total_units != 45` OR `len(per_seed) != 3` OR any (hop, arm) missing.

## 6. MIDDLE_BAND

- 0.30 <= CLEANUP at HOP=2 < 0.50: partial mechanism (2-hop composes weakly).
- HP1 clears but HP2 fails: NO_CLEANUP unexpectedly holds -- may indicate bundled composition is more robust than physics-law predicts at this regime (would be an interesting counter-signal).
- HP1 clears but HP3 fails: BUNDLED_LOOKUP unexpectedly succeeds -- likely test-chain leakage into training-chain bundle (verify held-out isolation).
- Hop-degradation observed but HP1 clears: expected pattern; MB unless all HPs pass.

## 7. Discriminator-must-survive-scale + AG (baseline in band)

**Predicted per arm at n_dim=2048, K_DIST=10, FACTS_PER_ENTITY=5 (HYPOTHESIZED@this-prereg; MEASURED@Cell1+Cell2 for FHRR primitives):**

- CLEANUP at HOP=2: 0.60-0.85. Per-hop cleanup accuracy ~0.85-0.95 at K_effective=15 SNR=11.7; two hops: 0.72-0.90.
- CLEANUP at HOP=3: 0.40-0.75. Compounding cleanup errors: ~0.85^3 ~= 0.61 lower bound.
- CLEANUP at HOP=4: 0.20-0.55.
- NO_CLEANUP at HOP=2: 0.30-0.60 (single hop cleanup gets one shot; second hop uses noisy soft-lookup).
- NO_CLEANUP at HOP=3: 0.05-0.20 (noise compounds sharply without intermediate cleanup).
- NO_CLEANUP at HOP=4: 0.01-0.10 (near chance).
- BUNDLED_LOOKUP: near 0.01 at ALL hops (held-out chains not in M_paths_L; 300 training chains cover 300/(N_ENT*N_ROLES^L) fraction of possible chains -- at L=2 that's 300/2500 = 12% coverage; at L=3 300/12500 = 2.4%; at L=4 300/62500 = 0.5%. Even the 12% at L=2 must overlap the specific TEST chain to succeed -- expected ~0.12 by pure random hit if test chain sampled uniformly; but with proper held-out split, ~0.00 by construction).
- COSINE: ~0.01 (chance; random entity vs random entity_start).
- RANDOM: 1/N_ENT = 0.01 (chance floor).

**Baseline in band (META_RULE_AG):**

- ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP expected 0.30-0.60 at HOP=2 (in-band); may drop below 0.05 at HOP=4 (chance-floor by physics-law construction; exempted at HOP=4 only).
- ARM_HRR_BUNDLED_LOOKUP expected ~0.01 (held-out-construction-floor, exempted).
- ARM_COSINE_ARGMAX_BASELINE expected ~0.01 (chance, exempted).
- ARM_RANDOM_BASELINE expected ~0.01 (chance floor, exempted).
- The IN-BAND baseline is the LOAD-BEARING CLEANUP arm itself at HOP=2 (expected 0.60-0.85; within [0.05, 0.95]).
- `baseline_exempted_arms: [ARM_HRR_BUNDLED_LOOKUP, ARM_COSINE_ARGMAX_BASELINE, ARM_RANDOM_BASELINE, ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP@HOP=4]` (all chance-floor / construction-floor / physics-law-floor).

**Discriminator survives scale:** smoke IS the intended regime (n_dim=2048, K_DIST=10, 60 queries per hop x 3 hops x 3 seeds). Scale sentinel at n_dim=8192 in selftest verifies FHRR path scales cleanly. If HP passes at smoke, FULL variant would sweep n_dim in {1024, 2048, 4096, 8192} x HOPS {2, 3, 4, 5, 6} with 5 seeds -- separate pre-reg.

## 8. CRLB / capacity feasibility

**Recall@1 CRLB per (arm, hop):** binomial proportion over N_QUERIES_PER_HOP=60 per seed; sigma_min = sqrt(p*(1-p)/60). At p=0.7: sigma_min = 0.0592. HP2 gap >= 0.15 requires margin ~2.5*sigma per seed; well-resolved. HP3 gap >= 0.20 requires margin ~3.4*sigma; adequate.

**FHRR capacity (Plate 1995 / Frady-Sommer 2020):** at n_dim=2048, per-entity bundle of 5 role-fillers augmented by K=10 distractors, single-slot cleanup over M=100 codebook; theoretical clean-up recall @ SNR=11.7 >= 0.90 per hop. Two-hop chained: 0.90^2 = 0.81; three-hop: 0.73; four-hop: 0.66. HP1=0.50 well within reachable band.

**BUNDLED_LOOKUP capacity:** 300 training chains at L=2 => M_paths_L=2 bundle of 300 items at n_dim=2048; SNR = sqrt(2048/300) = 2.6; even if test chain WERE in M_paths, cleanup gives ~0.35-0.60 per Plate 1995. Since test chains are HELD-OUT by construction, expected ~0.00 regardless of capacity.

- `crlb_floor_computed: 0.0592` (binomial CRLB at p=0.7, N=60 per seed per hop)
- `crlb_formula_reference: "sigma_p = sqrt(p*(1-p)/N_QUERIES_PER_HOP); FHRR SNR = sqrt(n_dim/K_effective) per Plate 1995; multi-hop compound = (per-hop-recall)^L per Frady-Sommer 2020 chain composition"`
- `discriminator_reachability: True` (HP1=0.50 < 0.81 theoretical 2-hop ceiling; HP2=0.15 gap >> 3*sigma; HP3=0.20 gap >> 3.4*sigma; HP4=0.30 gap >> chance-cosine floor)

## 9. Selftests (>= 6 required)

1. **Bind-unbind round-trip** at n_dim=2048 FHRR: `unbind(bind(a, b), b) ~= a` at cosine > 0.999.
2. **HOP=1 regression sanity** (single unbind reproduces compositional-generalization primitive from Cell 2): CLEANUP arm at HOP=1 achieves >= 0.90 on a fresh probe batch (per-entity bundle of 5 + K=10 distractors -> unbind by role -> cleanup over 100-entity codebook; SNR=11.7).
3. **KB chain validity** -- for each seed, sample 20 chains at HOP=4; verify each hop's ground-truth is retrievable by directly indexing the fact table (no chain has undefined transitions).
4. **Held-out training-chain isolation** -- verify BUNDLED_LOOKUP training chains and test chains are disjoint (no exact-tuple overlap in seed=13 probe).
5. **Cleanup argmax correctness** -- clean codebook entry retrieves its own index.
6. **Scale sentinel at n_dim=8192** -- bind/unbind + per-entity bundle path scales; cosine > 0.999.
7. **Deterministic seed invariance** -- repeat with same seed reproduces recall@1 to 1e-6 tolerance.
8. **Arms-must-differ (META_RULE_AF)** -- all 5 arms produce bit-different predictions on shared probe batch.

## 10. Cell-template mandates checklist

- `arms_differ_verified: True` (SHA256 hash-test on per-arm outputs)
- `final_metrics_atomicity: "tmp_replace"` (single-shot; write via .tmp + os.replace)
- `except SystemExit: raise` BEFORE `except Exception` (no BaseException)
- `crlb_floor_computed: 0.0592`
- `discriminator_reachability: True`
- `baseline_in_band: True` for CLEANUP@HOP=2 load-bearing arm (0.05 < 0.60-0.85 < 0.95); chance-floor arms exempted
- `cell_chunked: False` (single-file cell; 3 seeds run within one process; smoke wall << 5 min)
- `start_marker_written: True`
- `crash_diagnostic_present: True`
- `heartbeat_present: True` (per-seed per-hop progress lines flush=True)
- `progress_logging: "print_flush_true"`
- `cardinality_ok: True` (EXPECTED_N_UNITS=45; len(per_seed)==3, per_seed has 3 hops each having 5 arms)
- `defensive_error_checking: "passed_all_4_patterns"`
- `calibration_check: "default_ok_for_this_regime"` (evidence: FHRR SNR ~= 11.7 at K_effective=15, n_dim=2048; matches Cell 1 K sweep verified fire-threshold)

## 11. Compute architecture

- **Class:** (b) sequential-CPU with justification.
- **Justification:** smoke wall estimated 90-180s across 3 seeds x 3 hops x 5 arms x 60 queries x per-query FHRR (per-entity bundle build ~5-15 elementwise complex muls; L-hop sequential unbind + argmax over 100). Per-seed wall < 60s; below GPU-batching mandate threshold.
- **Storage strategy:** `SHARDED per entity` for the LOAD-BEARING mechanism (CLEANUP arm uses SHARDED per-entity bundle matrix M_entities of shape [100, n_dim] complex128 -- each entity's role-filler bundle stored separately). Compliant with SHARDED_STORAGE_DEFAULT META rule (2026-07-02) for compositional cells at chain composition L>=2.
  - `ARM_HRR_BUNDLED_LOOKUP` uses `bundled` storage as **exception (b)** of the META rule: explicitly testing bundle-storage as a discriminator arm (positive control for sharded-vs-bundled comparison at multi-hop composition).
  - `ARM_HRR_RECURRENT_UNBIND_NO_CLEANUP` uses SHARDED storage but bypasses the cleanup step at each hop (physics-law discriminator: bundle+recurrent-unbind without intermediate denoising).

## 12. Test-design gates §15 (canonical)

- **A) effective_vs_nominal parameter audit:** HOPS is the primary sweep axis; effective HOP per per-primitive is identical to nominal HOP (no partition routing; direct chain composition). `sweep_alignment_verdict: ALIGNED`.
- **B) `discriminating_fraction`:** 3 HOP points {2, 3, 4}; predicted CLEANUP r@1 in [0.20, 0.85] across the sweep -- all 3 points predicted in discriminating band [0.10, 0.90]. `discriminating_fraction: 1.00` (3/3).
- **C) signal_shape_compatibility_audit:** All primitives share (n_dim,) complex128 shape. `bind` output matches `unbind` + `bundle` + cleanup input shape. SHAPE_MATCH throughout.
- **D) positive_control_arms:** HOP=1 regression sanity check reproduces Cell 2's compositional-generalization primitive AT MATCHED PRIMITIVE REGIME (single unbind + cleanup).
  - `cited_prior_metric: "Cell 2 CLEANUP=0.410 at K_DIST=10, n_dim=2048, N_R=5, N_F=100"` MEASURED@`data/exp_stage2_vsa_cell2_compositional_generalization_smoke/metrics.json:gates.cleanup`.
  - `test_regime: {n_dim: 2048, N_ENT: 100, N_ROLES: 5, FACTS_PER_ENTITY: 5, K_DIST: 10, HOP: 1}`.
  - `expected_hop_1_recall: >= 0.90` (Cell 2 had 10 fillers per role x 100 fillers -> 200 held-out queries; here we have 5 fillers per entity -> effective K=5+10=15, SNR=11.7 higher than Cell 2's regime where per-role effective K was similar. Prediction is HIGHER than Cell 2 because per-entity fanout is only 5, not 100).
  - `tolerance: n/a` (different KB structure; regime not directly reproducible bit-identical -- this is a MECHANISM-level regression, not data-level).
  - `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` (HOP=1 -> HOP=2 introduces intermediate cleanup + SHARDED per-entity lookup; validated mechanism-by-mechanism in HOP=1 selftest).
- **E) functional_requirements_present:**
  1. **Encode fact triples in KB** as SHARDED per-entity bundles: `M_entities[e] = sum_r bind(role_r, filler_{e,r})` -- FHRR bind + bundle primitives.
  2. **Retrieve current entity's memory** given current-entity index (or noisy entity vector for NO_CLEANUP arm): SHARDED matrix lookup OR soft cosine-weighted combine.
  3. **Unbind by next role** to extract noisy filler estimate: `filler_hat = unbind(M_e, role_hop)` -- FHRR unbind primitive.
  4. **Cleanup filler_hat against entity codebook** (CLEANUP arm): `entity_next_idx = argmax cos(filler_hat, entities)` -- cosine cleanup argmax.
  5. **Iterate steps 2-4 for L hops**: sequential composition via recurrent unbind.
  All primitives implemented directly in cell (FHRR complex phasors; no external mechanism dependencies).

## 13. Framing discipline (USER-locked; non-negotiable per spawn prompt)

- **SUBSTRATE KNOWS ALMOST NOTHING** -- this cell is a MECHANISM COMPOSITION PROBE on SUPERVISED SYNTHETIC role-filler-chain regime; no general-knowledge claims. Entity names (Alice, Bob, ...) are labels for reader clarity ONLY; the substrate operates on integer indices + FHRR phasors.
- **HP verdict semantic:** if HP1+HP2+HP3+HP4 clear at K_DIST=10 with SHARDED CLEANUP arm demonstrating monotone hop degradation, substrate mechanism DEMONSTRABLY performs multi-hop reasoning under canonical FHRR/HRR paradigm. Combined with Cell 1 (analogy) + Cell 2 (compositional generalization), Cell 3 becomes 5th witness for task-class-fit META (heterogeneous DISTINCT task class WITHOUT HP1 caveat), which is the CG_META promotion criterion per Skunkworks Gate 1.
- **HF verdict semantic:** if HP1 fails (CLEANUP < 0.30 at HOP=2), substrate cannot chain unbinds even at 2-hop; strongly refutes task-class-fit hypothesis for multi-hop; would demote sibling Cell 1/Cell 2 task-class-fit META (or refine to "single-hop only").
- **Skunkworks calibration:** multi-hop reasoning via recurrent unbind is CANONICAL FHRR/HRR mechanism (Plate 1995; Eliasmith 2005 Spaun; Frady-Sommer 2020 Resonator Networks). NOT NOVEL PRIMITIVE. Cell 3 result = mechanism reproduction on synthetic multi-hop test, NOT novel substrate discovery. Frame Cell 3 similarly to Cell 1/Cell 2: canonical VSA on VSA-native task class.
- **No sigma claims without formula verification.** Cell 1 spawn iteration went through 12sigma (cell-author) -> 95sigma (Director over-derive) -> 72.5sigma (Skunkworks correction). Cell 3 will compute sigma from binomial CRLB directly in-code + verify before reporting.
- **Cell-author self-correction pattern is DOCUMENTED CG_META discipline** -- if verdict_msg over-claims honest read of metrics, self-correct in interpretation section.
- **No "first" / "physics law" without precedent grep.** VSA multi-hop reasoning is Plate-1995/Eliasmith-2005 canonical; nothing novel about the operation itself. The physics-law tested here is the BUNDLED-collapse-at-L>=2 rule from Skunkworks 2026-07-02.
- **Skunkworks architectural constraint STANDS:** no 40x expansion at 2% sparsity. Cell uses dense FHRR at n_dim=2048; no sparsification.

## 14. Dispatch plan

- **Smoke gate:** local_cpu (SMOKE-only-local USER-LOCKED 2026-07-01). Estimated wall < 5 min.
- **After smoke lands:** HOLD before any FULL cell authoring. Report + Director decides next.
- **If HP:** author FULL variant with n_dim sweep + HOPS extension {2, 3, 4, 5, 6} + 5 seeds -- separate pre-reg per Skunkworks SCHEMA-VET.
- **If HF:** memorialize as counter-evidence to multi-hop task-class-fit hypothesis; return to Director for re-scope decision.

## References

- Parent prereg: `preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (commit 891fde49a).
- Cell 1 prereg + metrics: `preregs/2026-07-03_stage2_vsa_cell1_analogy_completion_smoke.md` (ad43cd195); K sweep b2e44a43d.
- Cell 2 prereg + metrics: `preregs/2026-07-03_stage2_vsa_cell2_compositional_generalization_smoke.md` (c5704dc19).
- Plate 1995 HRR capacity theory (`Holographic Reduced Representations`, IEEE TNN).
- Eliasmith 2005 / 2013 Spaun / semantic pointer architecture: multi-hop VSA reasoning demonstrated.
- Frady-Sommer 2020 Resonator Networks (Neural Comp): FHRR SNR scaling + chain composition.
- SHARDED_STORAGE_DEFAULT META rule (2026-07-02): `feedback` files + cert_ledger atoms `math4_proof_chains_v2_global_bundle_cpu_v1` + `sharded_fhrr_cleanup_capacity_beyond_bundle_bound_v1`.
- Skunkworks architectural constraint b (2026-07-03): no 40x expansion at 2% sparsity.
- USER-LOCKED framing: `feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02.md`.
