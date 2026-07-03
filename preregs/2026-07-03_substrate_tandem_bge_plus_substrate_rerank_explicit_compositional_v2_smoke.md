# Pre-registration: tandem bge + substrate rerank -- EXPLICIT vs NATURAL query regime differentiator (v2 smoke)

**Anchor:** `substrate_tandem_bge_plus_substrate_rerank_explicit_compositional_v2_smoke`
**Date:** 2026-07-03
**Author:** hdi_exp_dev (Director-authorized)
**Cell:** `experiments/exp_substrate_tandem_bge_plus_substrate_rerank_explicit_compositional_v2_smoke_2026-07-03.py`

## Prior-work check (concept-query-before-dispatch, USER-locked)

Substrate query for keywords "tandem retrieval bge substrate rerank explicit compositional structure role filler" surfaced:
- Rank 1 (cos=0.3682): "Substrate compositional depth retrieval (L1-L8)" -- architectural concept, not the same test regime
- Rank 2-3 (cos=0.3486): `research_drill_substrate_value_add_strong_encoders_3x_2026-06-07.md` -- Axis 3 Pattern B: substrate as precision rerank filter on top of bge (empirical state: cycle 153 causal HP passed; bge-small integration NOT yet run)
- Rank 4-5 (cos=0.3408): `substrate_sq3_structured_image_retrieval_v1_n2048` at MIDDLE_BAND
- Prior on-point cell: `exp_bge_substrate_compositional_verify_v1` (in-repo, HotpotQA distractor, +0.027 F1 lift = below +0.05 HP, real positive but marginal)

**v1 halt-on-rediscovery finding:** 7 prior "dense retrieval + rerank" cells found in substrate KB. verify_v1 is the on-point prior; +0.027 lift on natural HotpotQA questions is the fleet-history residual signal after NL semantic-parse loss.

**v2 differentiator (what this cell tests that v1 did NOT):** v1 tested substrate rerank ONLY on natural HotpotQA questions where compositional structure was IMPLICIT and required an NL-parse-into-VSA step before binding operations could apply. v2 tests substrate rerank on TWO query classes SIDE BY SIDE on the SAME corpus:
- Class A NATURAL (regression to v1 pattern): natural-language questions -- expected +0.02 to +0.03 lift (reproduces verify_v1's residual)
- Class B EXPLICIT_STRUCTURE (THE test): queries constructed at generation time as `bind(ROLE_i, filler_i) + bind(ROLE_j, filler_j)` where roles and fillers are known role symbols + entities. Query text is a serialization of the structure for bge; substrate rerank receives the explicit binding structure for full-fidelity VSA match -- no NL-parse loss.

If v2 finds HP2 on explicit but not on natural, we have evidence for the substrate-as-selector architecture in structured-query regimes and a mechanism-level explanation for the fleet-history residual (parse loss).

Genuinely novel vs prior arc: **YES** for the side-by-side explicit/natural regime comparison on shared corpus. Prior work only tested natural regime.

## Hypothesis

- **H1 (regression):** ARM_TANDEM_NATURAL lift over ARM_BGE_ALONE_NATURAL falls in [+0.01, +0.05] -- reproduces verify_v1 fleet pattern.
- **H2 (LOAD_BEARING differentiator):** ARM_TANDEM_EXPLICIT_STRUCTURE lift over ARM_BGE_ALONE_EXPLICIT_STRUCTURE >= +0.05 -- substrate rerank leverages preserved structure the bge encoder flattens.
- **H3 (substrate-only sanity):** ARM_SUBSTRATE_ALONE_EXPLICIT_STRUCTURE lift over random >= +0.20 -- mechanism is real, not artifact.
- **H4 (rerank matters, not the extended candidate list):** ARM_TANDEM_EXPLICIT_STRUCTURE >= ARM_RANDOM_RERANK_EXPLICIT_STRUCTURE + 0.05.

## Bands (envelope-fail)

Primary metric: retrieval recall@1 (r@1) per arm, averaged across 3 seeds x N_QUERIES queries per class.

- **HARD_PASS (HP):** H2 fires: TANDEM_EXPLICIT lift >= +0.05, AND H1 in band, AND H3 satisfied, AND H4 satisfied.
- **MIDDLE_BAND (MB):** TANDEM_EXPLICIT lift in [+0.02, +0.05) -- partial signal below HP; substrate helps but not decisively.
- **HARD_FAIL (HF):** TANDEM_EXPLICIT lift < +0.02 -- differentiator hypothesis refuted; stronger negative than fleet history (even with full structural preservation substrate rerank cannot help).

## Compute architecture

- Class: **(b) sequential-CPU with justification** for smoke gate; substrate rerank is O(N_QUERIES * K * N_dim) elementwise-complex-mul (FHRR bind is per-query on top-K, K=20, N=4096-8192, ~20 * 8192 = 160k complex mul per query -- CPU-fast).
- Storage strategy: **sharded** (each corpus document has its own HD binding; queries score against doc-level HDs). Compositional retrieval, no bundle-all pattern. `storage_strategy: sharded`.
- FULL dispatch (post-smoke) would batch-GPU bge encoding of full Wikipedia 100K KB. This smoke cell operates on 200-500 doc synthetic-Wikipedia subset -- CPU-viable.
- Wall-time expectation: smoke < 10 min per seed (3 seeds sequential = < 30 min total).

## Corpus + query construction

- **Corpus:** 300 synthetic Wikipedia-style paragraphs (smoke; FULL uses `data/datasets/wikipedia_smoke_500.jsonl` + full Wikipedia 100K bge index if available). Each paragraph is CONSTRUCTED with 2 known (ROLE_k, ENTITY_v) bindings baked into content (e.g., ROLE=capital_of, ENTITY=France paired with FILLER=Paris in text). The role-filler tuples are ground truth per paragraph.
- **Class A NATURAL queries:** For each of N_QUERIES=30 paragraphs, generate a natural-language question that requires knowing both roles' fillers (e.g., "Which city is the capital of France?"). Answer = the paragraph containing both role-fillers.
- **Class B EXPLICIT queries:** For each of N_QUERIES=30 paragraphs, construct query as tuple `(role_i, filler_i, role_j, filler_j)`. Text serialization = "ROLE role_i FILLER filler_i ROLE role_j FILLER filler_j" for bge; HD serialization = `bind(role_i_hd, filler_i_hd) + bind(role_j_hd, filler_j_hd)` for substrate.

## Arms (7 x 3 seeds = 21 units)

1. `ARM_BGE_ALONE_NATURAL` -- bge top-1 on natural queries
2. `ARM_TANDEM_NATURAL` -- bge top-K=20 + substrate rerank (using vwfa char-encoding since no explicit query structure)
3. `ARM_BGE_ALONE_EXPLICIT_STRUCTURE` -- bge top-1 on explicit-structure queries
4. `ARM_TANDEM_EXPLICIT_STRUCTURE` (LOAD_BEARING) -- bge top-K=20 + substrate rerank with explicit role-filler binding structure
5. `ARM_SUBSTRATE_ALONE_EXPLICIT_STRUCTURE` -- substrate direct selection over full corpus (no bge)
6. `ARM_RANDOM_RERANK_EXPLICIT_STRUCTURE` -- bge top-K + shuffle (control: proves rerank matters, not extended candidate list)
7. `ARM_RANDOM_BASELINE_EXPLICIT_STRUCTURE` -- chance floor

### HP_SCOPE

- HP2 applies to: `ARM_TANDEM_EXPLICIT_STRUCTURE`
- HP4 applies to: `ARM_TANDEM_EXPLICIT_STRUCTURE` vs `ARM_RANDOM_RERANK_EXPLICIT_STRUCTURE`
- Bare-baseline arms (BGE_ALONE, RANDOM_*) NOT subject to HP; they establish comparison points only

## SCHEMA-VET gates (§15)

**Gate A (effective vs nominal parameters):** SPD (single-parameter design; N_dim swept only via scale sentinel at 8192 vs primary 4096). `sweep_alignment_verdict: ALIGNED` (no partition-routing masking).

**Gate B (bracket includes discriminating band):** Predicted r@1 per arm at smoke-scale N=4096, K=20, corpus=300:
- BGE_ALONE_NATURAL: ~0.40 (bge-small-en semantic overlap on 300-corpus NL queries)
- TANDEM_NATURAL: ~0.42 (verify_v1 +0.02 pattern)
- BGE_ALONE_EXPLICIT: ~0.45 (structured text has richer keyword overlap)
- TANDEM_EXPLICIT: ~0.60 (structure-preserved rerank hypothesis)
- SUBSTRATE_ALONE_EXPLICIT: ~0.50 (substrate has full structure but slower cleanup)
- RANDOM_RERANK_EXPLICIT: 0.05 (1/K=1/20 top-K permutation baseline)
- RANDOM_BASELINE: 1/300 = 0.0033
`points_in_discriminating_band = 5 of 7; discriminating_fraction = 0.71` >= 0.30 -- ALIGNED.

**Gate C (signal shape compatibility):** bge output (unit-norm float32, 384-dim) -> substrate rerank input (FHRR HD, complex64, N_dim=4096); adapter: text pass-through and independent HD encoding of same text via vwfa (SHAPE_MATCH via decoupled encoding paths). Explicit-structure adapter: role-filler tuple -> `bind(role_hd, filler_hd) + ...` -- direct FHRR construction, no adapter needed.
`composition_edges`: bge_top_K -> {substrate_encoder | random | passthrough}; verdicts: SHAPE_MATCH_via_independent_encoding.

**Gate D (positive control):** `ARM_TANDEM_NATURAL` IS the positive-control regression arm: reproduces verify_v1 +0.027 lift within tolerance +/-0.02. If TANDEM_NATURAL lift is outside [+0.01, +0.05], flag REGIME_OR_INVOCATION_MISMATCH and DO NOT trust TANDEM_EXPLICIT downstream.

**Gate E (functional requirements):** decomposed:
1. Semantic top-K candidate selection -> bge encoder (chain-grade CG_BGE)
2. Structural query representation -> FHRR bind (chain-grade CG_FHRR_BIND per hdlab/binding.py)
3. Structural candidate representation -> either vwfa (natural) or explicit-binding (structured)
4. Rerank score -> cosine of HDs (chain-grade)

## Cell-template mandates checklist

- [x] `arms_differ_verified: True` -- SHA256 hash check on per-arm outputs at smoke gate
- [x] `final_metrics_atomicity: "tmp_replace"` -- atomic write via `os.replace`
- [x] `except SystemExit: raise` BEFORE `except Exception` -- no BaseException
- [x] `crlb_floor_computed: 1/CORPUS_SIZE = 0.0033` (random baseline floor); `discriminator_reachability: True` (HP=+0.05 lift is above CRLB by 15x)
- [x] `baseline_in_band: True` (BGE_ALONE_EXPLICIT predicted ~0.45, in [0.05, 0.95])
- [x] Discriminator survives scale: scale sentinel at N_dim=8192 (one seed at N=8192 to confirm no N-scaling saturation)
- [x] `cardinality_ok: True`; EXPECTED_N_UNITS = 7 arms * 3 seeds = 21
- [x] Per-unit failure-class instrumentation (typed `except Exception as e`)
- [x] `calibration_check: "default_ok_for_this_regime"` (chain-grade FHRR + cosine defaults; no adaptive knobs)
- [x] `cell_chunked: False` -- 3 seeds in one cell for smoke gate (short-elapsed); FULL dispatch would use chunked
- [x] `start_marker_written: True`
- [x] `crash_diagnostic_present: True`
- [x] `heartbeat_present: True`
- [x] `defensive_error_checking: "passed_all_4_patterns"`
- [x] `progress_logging: "print_flush_true"` (smoke timeout < 1800s so field non-mandatory, but included)

## Envelope-fail bands (final table)

| Metric | HF | MB | HP |
|---|---|---|---|
| TANDEM_EXPLICIT lift over BGE_ALONE_EXPLICIT | < +0.02 | [+0.02, +0.05) | >= +0.05 |
| TANDEM_NATURAL lift over BGE_ALONE_NATURAL (regression) | outside [+0.01, +0.05] | [+0.01, +0.05] | matches verify_v1 within +/-0.02 |
| SUBSTRATE_ALONE lift over RANDOM_BASELINE | < +0.10 | [+0.10, +0.20) | >= +0.20 |
| TANDEM_EXPLICIT vs RANDOM_RERANK_EXPLICIT gap | < +0.05 | -- | >= +0.05 |

## Predicted verdict (author's honest prior)

Uncertain -- verify_v1's +0.027 residual suggests substrate CAN extract compositional signal but at natural-parse-loss floor. With EXPLICIT structure preserved end-to-end, the theoretical lift should exceed +0.05 (which is the differentiator hypothesis). But we've been surprised before: substrate-as-selector may have been substantially discovered as marginal at these scales. Honest prior for smoke: 40% HP2, 35% MB, 25% HF.

If HF: stronger negative than fleet history -- substrate rerank cannot help even with full structural preservation. Substrate is not the right layer for selection even on structured queries.
If MB: partial evidence for the mechanism; consider FULL scale test with real bge-large + Wikipedia 100K KB before decision.
If HP: substrate-as-selector at compositional-structure regime validated; supports v3 production rerank pipeline.

## Compute + smoke gate

- Smoke queue: `local_cpu_queue` (SMOKE-only-local; per USER 2026-07-01)
- Expected wall time: < 30 min total (3 seeds sequential, 300 docs, N=4096 primary + one seed at N=8192)
- Timeout: 3600s (safety margin)
- Post-smoke: HARD HOLD; report to Director; no FULL dispatch until Director authorizes

## Report items required post-smoke

- Commit hash of cell + pre-reg
- Per-arm r@1 (mean +/- std across seeds)
- H1 (regression natural lift), H2 (differentiator explicit lift), H3 (substrate sanity), H4 (rerank vs extended-list)
- verify_v1 regression sanity: does TANDEM_NATURAL reproduce verify_v1 within tolerance?
- Honest interpretation: did differentiator hypothesis validate? Implications?
- Scale sentinel: N=4096 vs N=8192 confirmation

## Discipline notes

- No sigma claims without formula verification
- No "first" / "physics law" without prior-arc verification (already done above)
- Honest report: TANDEM_EXPLICIT number as MEASURED@ tag; predicted numbers as HYPOTHESIZED@
- USER's claim ("substrate ideal at selection") is a hypothesis being tested, not assumed
