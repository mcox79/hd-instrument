# Pre-reg: Encoder Migration Step 3 - 100-query gold-standard A/B verify vs bag-word (v1)

**Date:** 2026-07-04
**Anchor (full):** `encoder_migration_step3_gold_verify_100_queries_A_B_v1`
**Anchor (smoke):** `encoder_migration_step3_gold_verify_100_queries_A_B_v1_smoke`
**Cell:** `experiments/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_core.py`
**Query set:** `data/gold_query_set_step3_v1.jsonl` (100 rows locked at prereg time; NO post-hoc query addition)
**Class:** MM_TENTATIVE at SMOKE (10-query pipeline-fidelity check); MM_STANDARD post-FULL (100-query result); CG only if H1 + H2 + H3 + H4 all fire cleanly with cv < 0.15 on FULL.
**Stage:** 3 (higher-function retrieval-quality claim).

## Purpose

Certify (or refute) that the Step 1 + Step 2 concept-encoded 970K-KB sparse-CSR delivers measurably better retrieval quality than the existing char-trigram bag-word baseline on a **pre-committed** 100-query gold-standard set. This is the retrieval-quality claim gate for the encoder migration (Step 4 = flip the frontend, contingent on this cell HARD_PASS).

Explicit anti-drift: query set is fully specified at prereg-commit time; no post-hoc query addition, deletion, or gold-target editing between SMOKE and FULL.

## Query set composition (locked)

- **Class 1 (Direct-hit atom queries, 25):** query is a short phrase that plausibly matches an atom's name or a name-adjacent field; gold_entity_name is that atom's canonical entity_name from `data/substrate_director_kb_v1/entities.jsonl`.
- **Class 2 (Concept-cluster queries, 25):** query is a thematic phrase spanning a concept cluster; gold_entity_name is the most-representative atom in that cluster (typically the project_ or T3/EXP_ atom for the cluster).
- **Class 3 (Failure-mode queries, 25):** queries USER hit low-cosine on in this session (memory rules `feedback_*` files as target); gold_entity_name is the intended memory rule.
- **Class 4 (Prior-work queries, 25):** queries that mention past experiment results / reference files; gold_entity_name is the corresponding entity (past cell, verdict, reference doc).

Total 100 rows, qid 1..100 sequential, 25 per class verified at commit time.

## Storage strategy

**SHARDED** (concept arm) + **BUNDLED-BAG-WORD** (baseline arm). Concept arm inherits Step 1/2 sharded sparse-bipolar storage; per-entity vector is its own sparse row. Baseline arm inherits KB v1's char-trigram bag-of-features bundled into per-entity 2048-dim dense float32 rows. Cell does not modify storage; it queries + compares.

## Compute architecture

**Class (b): sequential-CPU with justification.**
- Justification: n_queries = 100 x 2 encoder arms = 200 forward passes. Bag-word arm cost per query: 1 x [1, 2048] @ [970069, 2048]^T = 2 GFLOPs float32 CPU matmul (~500-2000 ms wall at N=970069, matches USER-observed dashboard query wall). Concept arm cost per query: sparse bincount over 970069 x 82 = 79.5M ops (~500 ms wall extrapolated from Step 2 SMOKE 10-query benchmark). Total 200 x ~1s = ~200 s wall FULL = well within local_cpu_queue overnight budget.
- No GPU speedup expected: queries are independent, and each per-query matmul is already dominated by memory-bandwidth-bound single dot-product. Batched-GPU on 100 queries at once would be ~2-4x speedup but adds cross-cutting infra risk (device-transfer overhead + fp16 rounding drift vs Step 1/2 float32 pipeline). Not worth it at n=100.
- **SMOKE local_cpu_queue authorized** per USER 2026-07-01 SMOKE-only-local rule.
- **FULL local_cpu_queue** deferred until Step 1 FULL + Step 2 FULL both land + verdicts verified.

## Mechanism (cell core)

For each query row:
1. Encode query with **CharTrigramEncoder(n_dim=2048)** -> normalize -> [2048] float32 unit vector. Cosine top-10 vs `data/substrate_director_kb_v1/E.pt` [970069, 2048] float32 L2-normalized. Record top-1 idx + cosine, cosine at gold_idx, gold rank in top-10.
2. Encode query with **CharPositionalEncoder(n_dim=4096, max_pos=24)** -> apply top-K WTA at K=82 -> sign * mask -> [4096] int8 sparse-bipolar (identical mechanism to Step 1's concept encode for entities). Cosine top-10 vs `data/substrate_concept_encoder_v1[_smoke]/E_concept.pt` sparse-CSR via vectorized bincount accumulation (identical mechanism to Step 2's `_sparse_batched_cosine`). Record top-1 idx + cosine, cosine at gold_idx, gold rank in top-10.
3. Aggregate per-query records into H1-H4 metrics.

**ARMS-MUST-DIFFER hash check (META_RULE_AF):** at end of run, hash-check that ARM_BAG_WORD top-1 sequence differs from ARM_CONCEPT top-1 sequence over the query set. Bit-identical = arm-implementation bug -> raise. Different encoders + different index spaces + different n_dim make this true by construction; the check guards against a wiring bug where both arms accidentally point at the same E.

## Source signature

- Step 1 encoder.npz sha256: MEASURED at cell runtime + stamped in metrics.json.
- Step 2 E_concept.pt sha256: MEASURED at cell runtime + stamped in metrics.json.
- Bag-word E.pt sha256 (baseline): MEASURED at cell runtime + stamped.
- Query set sha256 (deterministic): MEASURED at cell runtime + stamped.
- Bag-word encoder: **char_trigram_v1** CITED@`data/substrate_director_kb_v1/manifest.json:encoder`.
- Concept encoder mechanism: **CharPositionalEncoder + top-K WTA** at N_DIM=4096 K_SPARSITY=0.02, CITED@Spoke1-v3-D-CG (commit 596a8de03; cat/kitten cos_mean=0.492).
- Cell-code commit: HEAD at prereg-file-commit time (will be MEASURED post-commit).

## Functional requirement decomposition (per META_RULE section 15E)

- **FR1:** Given a query text, produce top-10 retrieved entity_names from bag-word encoder. Primitive: CharTrigramEncoder.encode + dense cosine + argpartition. CG at `hdlab.director_kb_query` production use.
- **FR2:** Given a query text, produce top-10 retrieved entity_names from concept encoder. Primitive: CharPositionalEncoder.encode + top-K WTA + sparse-CSR bincount cosine. CG at Spoke1 v3-D (per-entity encoding); this cell extends by using the SAME mechanism for query encoding (regime-extension audit: SHAPE_MATCH -- query is a single-context string, identical to Step 1's single-context fallback path for entities without atoms).
- **FR3:** Given both arms' outputs + a gold_entity_name, compute per-query cosine-at-gold + gold-rank-in-top-10 for both arms. Primitive: dict lookup name -> idx + index lookup.
- **FR4:** Aggregate per-query metrics into H1-H4 verdict + summary. Primitive: numpy mean/argmax + hypothesis-band verdict logic.

## Effective-vs-nominal-parameter audit (per META_RULE section 15A)

- Only swept axis is **query index** (qid 1..100 at FULL; qid subset at SMOKE). No hyperparameter sweep in this cell. Effective params match nominal: no parametric misalignment risk.
- `sweep_alignment_verdict: ALIGNED`.

## Discriminating-fraction audit (per META_RULE section 15B)

- H1 discriminating band: `delta in [0.05, 0.30]` is discriminating (below 0.05 = null; above 0.30 = trivially-solved; H1 HP threshold 0.15 sits mid-band). HYPOTHESIZED bag-word top-1 mean ~0.35 (CITED USER 2026-07-02 note bag-word 0.5381 on H2 test case is arguably ABOVE avg; other queries lower). HYPOTHESIZED concept top-1 mean ~0.50-0.65 (each entity is 82-sparse-bipolar; query concept-encoded should hit tight semantic cluster). Predicted delta ~0.15-0.30 in-band by construction.
- H2 discriminating band: `cosine_at_gold in [0.30, 0.90]` is discriminating (below 0.30 = below noise floor; above 0.90 = trivially-solved). HYPOTHESIZED concept cosine at gold for H2 test case ~0.65-0.85 based on concept-cluster overlap with gold entity's own atoms. HP threshold 0.75 sits mid-band.
- H3 discriminating: any query IS a candidate regression; band is `drop <= 0.10` HP vs `drop > 0.10` HF. HYPOTHESIZED regressions ~0-3 based on class 2 (concept-cluster queries where bag-word already hits gold via literal-substring match).
- H4 discriminating: `mean_rank in [1.5, 5.0]` is discriminating band. HYPOTHESIZED concept mean rank ~1.5-2.5 based on H1 mean top-1 lift.
- `discriminating_fraction: 4/4 = 1.00 >= 0.30`.

## Signal-shape compatibility audit (per META_RULE section 15C)

- Edge 1: `query_text -> CharTrigramEncoder.encode`. A_out shape: string. B_in shape: string. **SHAPE_MATCH**.
- Edge 2: `CharTrigramEncoder.encode -> bag-word cosine top-10`. A_out shape: [2048] float32. B_in shape: [BAGWORD_N_DIM=2048]. **SHAPE_MATCH**.
- Edge 3: `query_text -> CharPositionalEncoder.encode`. A_out shape: string. B_in shape: string. **SHAPE_MATCH**.
- Edge 4: `CharPositionalEncoder.encode -> top-K WTA sparse-bipolar`. A_out shape: [4096] float32. B_in shape: [CONCEPT_N_DIM=4096]. **SHAPE_MATCH**.
- Edge 5: `sparse-bipolar int8 query -> sparse-CSR bincount cosine over E_concept.pt`. A_out shape: [4096] int8. B_in shape: [CONCEPT_N_DIM=4096]. **SHAPE_MATCH**.
- No adapters needed. No SHAPE_MISMATCH edges.

## Positive-control arm (per META_RULE section 15D)

- **PARTIAL positive control via H2 test case:** the USER-cited bag-word cosine on the H2 query "storage strategy sharded bundled scale free topology" is 0.5381 (CITED@USER-session-2026-07-02). The bag-word arm on qid 51 at FULL should reproduce a cosine at gold in [0.45, 0.65] (tolerance 0.10 around cited 0.5381) as a reproducibility check for the baseline pipeline. If bag-word cosine at H2 gold is < 0.30 or > 0.75 the baseline pipeline is broken (encoder change or KB change since USER's observation) and the H1/H2 verdict is INVALIDATED.
- **Concept side has no chain-grade prior at this regime.** Step 1 v3-D CG was cat/kitten cos_mean=0.492 in a categorized synthetic-triplet regime. Extending to natural-language 100-query retrieval over 970K entities is a **SHAPE_DRIFT with documented risk**: query encoding uses the same mechanism as entity encoding (single-context) but query strings are shorter + less-topical than entity contexts (which are atom-summary-text). Concept-arm at H2 test case is a NOVEL_REGIME measurement; H2 HP threshold 0.75 is HYPOTHESIZED not CITED.
- `positive_control_arms:`
  - `arm: BAG_WORD_H2_REPRODUCE; cited_prior_metric: 0.5381; tolerance: 0.10; test_regime: {qid: 51, encoder: char_trigram_v1, n_dim: 2048}; if_outside_tolerance: HARD_FAIL_BAG_WORD_BASELINE_DRIFT`

## Hypotheses + pass bands

### H1: Mean top-1 cosine lift (aggregate)
- **HP:** `mean(concept_top1_cosine) - mean(bag_word_top1_cosine) >= 0.15` over all 100 queries.
- **MB:** delta in [0.05, 0.15) (positive but below threshold).
- **HF:** delta < 0.05 (null or regression).
- Applies to: ARM_CONCEPT vs ARM_BAG_WORD aggregate.

### H2: USER test case cosine at gold
- **HP:** `concept_cosine_at_gold >= 0.75` on qid 51 ("storage strategy sharded bundled scale free topology" -> "META storage_strategy_composition_depth_physics_law_v1").
- **MB:** in [0.60, 0.75).
- **HF:** < 0.60 OR gold-target absent from concept KB.
- Applies to: ARM_CONCEPT only.
- Regime-extension audit: SHAPE_DRIFT with documented risk (per section 15D).

### H3: No regression greater than 0.10
- **HP:** for every query with both arms' gold present, `bag_cosine_at_gold - concept_cosine_at_gold <= 0.10` (concept is not more than 0.10 worse than bag-word).
- **HF:** any single query regresses > 0.10.
- Applies to: ARM_CONCEPT vs ARM_BAG_WORD per-query.

### H4: Concept mean rank in top-10
- **HP:** mean(concept_gold_rank_in_top10) <= 3.0 where gold is present + rank measured (misses counted at rank TOP_K_REPORT=10).
- **MB:** in (3.0, 5.0].
- **HF:** > 5.0.
- Applies to: ARM_CONCEPT only.

**Verdict tier:**
- FULL HARD_PASS iff H1 + H2 + H3 + H4 all HP AND baseline_in_band (bag-word top-1 mean in [0.05, 0.95]).
- FULL HARD_FAIL iff hp_count == 0.
- FULL MIDDLE_BAND otherwise (1 <= hp_count <= 3, or baseline not in band).
- SMOKE HARD_PASS iff pipeline ran + no exceptions + at least one bag-word gold-target lookup succeeded (concept SMOKE only sees 1K-entity slice; most golds absent by construction).

## CRLB / capacity-feasibility

- CRLB not applicable at cell-level (aggregate retrieval-quality metric is not a bounded-capacity primitive; H1 is empirical delta between two encoders).
- H2 HP threshold 0.75 sits within [0, 1] cosine range; achievable in principle (concept encoder was CG at cat/kitten cos_mean=0.492 in an EASIER within-cluster regime; H2 is a HARDER cross-cluster regime but a specific atom's own concept-cluster overlap with the query should be tight if the mechanism works).
- `crlb_n/a: "retrieval-quality aggregate; no formal noise-floor formula. H2 has explicit floor 0.75 justified via 0-1 cosine range + concept-cluster overlap argument (HYPOTHESIZED)."`
- `discriminator_reachability: True`.

## Pre-reg required fields (SCHEMA-VET checklist)

- `cardinality_ok: True` -- EXPECTED_N_UNITS = 100 (FULL) / 10 (SMOKE). Verdict logic asserts `len(per_query) == expected_n_units`; else HARD_FAIL_CARDINALITY_BREACH_META_RULE_H.
- `arms_differ_verified: True` -- ARM_BAG_WORD top-1 hash vs ARM_CONCEPT top-1 hash asserted != at end of run. Fails cell if bit-identical.
- `arms_differ_exempted: []` -- no legitimate arm-output aliasing.
- `final_metrics_atomicity: "tmp_replace"` -- `write_metrics` via tmp+os.replace.
- `crlb_n/a: "retrieval-quality aggregate; H2 explicit floor 0.75 justified"`.
- `discriminator_reachability: True`.
- `baseline_in_band: verified_at_verdict` -- bag_top1_mean asserted in [0.05, 0.95] at verdict-emission; verdict returns MIDDLE_BAND if out of band.
- `calibration_check: "default_ok_for_this_regime"` -- both encoders use their published defaults (bag-word char_trigram_v1 per KB v1 manifest; concept CharPositionalEncoder n_dim=4096 max_pos=24 K_SPARSITY=0.02 per Spoke1 v3-D CG).
- `sweep_alignment_verdict: ALIGNED` -- only sweep axis is query-index; no parametric misalignment.
- `discriminating_fraction: 1.00` -- all 4 hypotheses have discriminating bands per section 15B rationale.
- `composition_edges:` 5 SHAPE_MATCH edges (per section above); no adapters needed.
- `positive_control_arms:` `BAG_WORD_H2_REPRODUCE` with tolerance 0.10 around cited 0.5381.
- `functional_requirements:` FR1/FR2/FR3/FR4 above.
- `cell_chunked: False` -- single-seed artifact + gate cell; no per-seed axis. FULL is deterministic given fixed encoder seeds + query set.
- `start_marker_written: True` -- `_start_marker.json` at main() entry.
- `crash_diagnostic_present: True` -- outer try catches Exception (not BaseException) + writes CELL_CRASHED metrics via `_write_crash_metrics`.
- `heartbeat_present: True` -- `_heartbeat.jsonl` emitted at each stage + every ~5% of queries.
- `defensive_error_checking: "passed_all_4_patterns"`.
- `progress_logging: "line_buffered_stdout"` + explicit `flush=True` on all progress prints. Per-query print every 5% of queries at FULL (every 5 queries); every query at SMOKE (10 queries).
- `run_mode_declared: "smoke_then_full"` -- SMOKE dispatch first (this ship, gates pipeline fidelity); FULL dispatch deferred until Step 1 FULL + Step 2 FULL land + verdicts verified.
- `HP_SCOPE:` `{ARM_CONCEPT: [H1_HP, H2_HP, H4_HP], ARM_BAG_WORD: [] (baseline; no HP claim), COMPARISON: [H1_HP, H3_HP]}`.

## Wall-time estimates + timeouts

- SMOKE (10 queries x 1K-entity encoders): bag-word arm ~5 ms per query; concept arm ~1 ms per query; total ~60 ms wall + encoder load overhead (~5 s bag-word, ~1 s concept). Total ~10-30 s wall. `--timeout 180` local dispatch (fits 180 s smoke gate cap).
- FULL (100 queries x 970K-entity encoders): bag-word arm ~500-2000 ms per query (matmul dominated); concept arm ~500 ms per query; total ~200-300 s wall + encoder load (~15 s bag-word 7.9 GB E.pt load, ~5 s concept). Total ~5-10 min wall. `--timeout 1800` local dispatch (30 min defense margin).

## Off-disk verify (post-SMOKE gates)

- `data/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1_smoke/metrics.json` exists with:
  - `verdict = HARD_PASS` (SMOKE tier: pipeline ran without exceptions).
  - `run_mode = smoke`.
  - `n_queries = 10`.
  - `per_query` length 10.
  - `arms_differ_verified = True`.
  - `bagword_e_pt_sha256`, `concept_pt_sha256`, `query_set_sha256` all non-empty.
  - `summary_h1_h4.n_bag_gold_missing < 10` (at least one bag-word gold-target present).
- Advisory (not gates): H1/H2/H3/H4 fields populated but interpretation deferred to FULL. Concept arm at SMOKE only sees 1K-entity slice; gold-targets outside first 1K are absent by construction and correctly reported as `concept_gold_present: False`.

## Off-disk verify (post-FULL gates)

- `data/exp_encoder_migration_step3_gold_verify_100_queries_A_B_v1/metrics.json` exists with:
  - `run_mode = full` + `n_queries = 100`.
  - `verdict in {HARD_PASS, MIDDLE_BAND, HARD_FAIL}` per section above.
  - `summary_h1_h4.h1_delta` populated.
  - `summary_h1_h4.h2_concept_cosine_at_gold` populated.
  - `summary_h1_h4.h3_regressions` (list; may be empty).
  - `summary_h1_h4.h4_concept_mean_rank` populated.
  - `arms_differ_verified = True`.

## Post-FULL Skunkworks landed-VET (surfaced in report; NOT Step 3's job)

- Verify per-query records match expected structure + gold-target lookups.
- Re-compute H1-H4 aggregates from per_query field off-disk (independent-of-cell recompute per Fix#28 verify-referent).
- Tier decision: CG only if H1 + H2 + H3 + H4 all HP AND positive_control BAG_WORD_H2_REPRODUCE within tolerance AND cv < 0.15 across per-query classes (Class 1 / Class 2 / Class 3 / Class 4).
- If BAG_WORD_H2_REPRODUCE fails tolerance: invalidate H1/H2/H3/H4 and file baseline-drift audit (probable KB re-ingest changed E.pt since USER's session note).

## Framing at SMOKE

Advisory pipeline-fidelity check. Nothing about retrieval quality is claimed at SMOKE. The concept arm at SMOKE only sees a 1K-entity slice, so most Class 1-4 gold-targets are absent; SMOKE only certifies:
- Both encoders load without error.
- Query encoding works on real query text.
- Cosine + top-K computation works.
- A/B comparison logic works.
- Per-query metrics.json writes.
- ARMS-MUST-DIFFER hash-check fires.

## References

- Migration plan: `notes/design_substrate_KB_bag_word_to_concept_encoder_migration_plan_2026-07-02.md` sect. Step 3.
- Step 1 cell: `experiments/exp_encoder_migration_step1_train_concept_encoder_970K_KB_v1_core.py`.
- Step 1 pre-reg: `preregs/2026-07-04_encoder_migration_step1_train_concept_encoder_970K_KB_v1.md`.
- Step 2 cell: `experiments/exp_encoder_migration_step2_sparse_encode_970K_KB_v1_core.py`.
- Step 2 pre-reg: `preregs/2026-07-04_encoder_migration_step2_sparse_encode_970K_KB_v1.md`.
- Step 1 SMOKE output: `data/substrate_concept_encoder_v1_smoke/encoder.npz`.
- Step 2 SMOKE output: `data/substrate_concept_encoder_v1_smoke/E_concept.pt`.
- Bag-word baseline E.pt: `data/substrate_director_kb_v1/E.pt` (7.9 GB, char_trigram_v1 n_dim=2048).
- USER strategic direction 2026-07-04 (this session): pre-author Step 3 in parallel with Step 1 FULL + Step 2 SMOKE; do NOT dispatch FULL until Step 1 + Step 2 FULL both land.
- Concept encoder mechanism source: Spoke1 v3-D CG commit 596a8de03, cat/kitten cos_mean=0.492.
- H2 test case cited baseline 0.5381: USER session 2026-07-02 note (bag-word retrieval on storage-strategy query).

ASCII-only. No emojis. No em dashes.
