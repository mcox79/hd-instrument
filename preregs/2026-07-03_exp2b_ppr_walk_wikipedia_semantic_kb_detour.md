# Pre-registration: `substrate_stage1_apply_exp2b_ppr_walk_wikipedia_semantic_kb_smoke_2026_07_03`

## Milestone / arc position
Experiment 2B — semantic-KB detour endorsed by cell-author + Skunkworks after Exp 2 landed `MB_STRUCTURAL_LIMIT` with `recovery_rate=0.170` on the synthetic random-UUID KG. POS_CTL=1.000 in Exp 2 proved the PPR mechanism is numerically correct; the 0.170 rate was a **lower-bound floor** attributable to Exp 2's synthetic KG having no semantic edge signal (every entity had 5 random edges — high mass leakage). HippoRAG's precedent (+11-20pp on 2WikiMultihopQA) was on **semantic** KGs where edges have real meaning.

This detour is the **decision-point experiment** for the retrieval-architecture arc:
- HARD_PASS → graph-walk viable at real-KB scale; chain Exp 3 with high confidence.
- HARD_FAIL → graph-walk approach is dead even with semantic signal; revive encoder-swap path as primary.
- MIDDLE → partial signal; call USER for direction.

**Scale-caveat note:** HotpotQA distractor context is a REAL Wikipedia-derived semantic KG (10 titles per query with real title-mention edges). Result here IS representative for the target regime — unlike Exp 2's synthetic random-UUID corpus. This is the honest scale-test.

Author: `hdi_exp_dev` 2026-07-03. HYPOTHESIZED_P_DEFLATED@drill_2026-07-03:0.55 (Architecture C, HippoRAG semantic-KB regime — precedent gain is real on this exact class of data; deflated slightly for scale-difference vs HippoRAG's larger cross-article graph).

## Chain-grade parents (composition provenance — META_RULE_AT)
- **Exp 2 landing** (2026-07-03) — `substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03`: PPR mechanism numerically correct (POS_CTL=1.000, mass conservation OK) on synthetic random-UUID KG; recovery_rate=0.170 = structural floor. REUSE the PPR primitives (`build_undirected_adjacency`, `ppr_iterate`, `rank_chunks_by_ppr`, `seed_from_entities`) VIA IMPORT — no new sparse-linear-algebra abstraction.
- **Exp 1 HARD_PASS** (2026-07-03): char-trigram-fuzzy-entity-extraction from hop-1 dense chunks recovers bridge entity at 0.982. REUSE `build_entity_codebook`, `extract_matched_entities` VIA IMPORT.
- `hdlab/char_trigram_encoder.CharTrigramEncoder` — chain-grade primitive.
- FHRR bind/unbind primitives (Plate 1995; foundational; not directly bound here — PPR ranks in fact-index space).
- Personalized PageRank — Haveliwala 2003; standard sparse linear-algebra iteration.

## Adjacent literature (all previously surveyed in the optimal-arch drill; re-cited here)
- **HippoRAG** (arXiv:2405.14831): PPR seeded from query-linked entity nodes; +11-20pp R@2/R@5 on 2WikiMultihopQA. **Direct precedent — this experiment attempts to reproduce that class of lift on HotpotQA (2WikiMultihopQA's sibling; both are Wikipedia-derived multi-hop QA).**
- **BridgeRAG** (arXiv:2604.03384): +2.55pp F1 on parallel-chain queries; ~0 on already-dense-solvable. Selective-effect precedent (some queries benefit, others don't).
- Documented negative case: HotpotQA graph-coverage lift did NOT convert to F1 in weighted-hypergraph work — so success is not guaranteed even here.

## Substrate-KB pre-work query
Query: `personalized pagerank walk semantic knowledge base Wikipedia bridge entity recovery HippoRAG`.
Top hits (cosine): `3.3 Personalized PageRank for entity ranking` (0.2988, research note), `Wikipedia entity coverage` (0.2793, research note), `Cold-start bridge coverage WITH pre-trained Wikipedia substrate` (0.2695, research note).
Verdict: **genuinely novel at cell level** — no prior cell operationalizes PPR on a real Wikipedia-derived semantic KG (all prior hits are lit-drill notes). Exp 2 is the immediate parent (synthetic-KG mechanism proof); this cell extends it to real semantic signal.

## Prior-work check
Prior-work check: [top hits at cosine <0.30 — all research notes, NO PRIOR CELL. Genuinely novel; Exp 2 is the immediate parent.]

## Functional Requirements (META_RULE §15.E)
1. **HotpotQA loader must construct a proper 10-title mini-KG per bridge query** — nodes = distinct article titles from `context.title`; edges = title-A-mentions-title-B via case-insensitive substring match with word-boundary. Sanity: mean_edges_per_node ≥ 1.0 across sampled queries.
2. **Fixed-iteration PPR must produce valid probability distribution (sum=1.0 ± 0.005, all ≥ 0) after each iteration** — inherited from Exp 2; already proven.
3. **PPR seeded from the TRUE bridge title must recover ≥1 supporting-facts sentence at recall@5 ≥ 0.95** — POS_CTL; proves the PPR + chunk-scoring mechanism works on the semantic KG when given correct seed.
4. **PPR seeded from a random unrelated title in the distractor pool must recover supporting-facts sentence at recall@5 ≤ 0.10** — NEG_CTL; proves lift is not artifact of PPR mass uniformly leaking to all sentences.
5. **PPR seeded from Exp-1-style char-trigram-matched title entities extracted from hop-1 dense-retrieved top-K sentences must recover ≥1 supporting-facts sentence at recall@5 meaningfully higher than hop-1-dense-alone on the missed-by-hop-1 subset** — the mechanism claim.

## Substrate config

| Field | Value | Rationale |
|---|---|---|
| DATASET | `data/datasets/hotpot_qa_distractor_dev_1k.jsonl` | Real Wikipedia-derived bridge-QA data (807 bridge queries / 1000 total; sibling of 2WikiMultihopQA that HippoRAG used). CITED@Yang_2018_HotpotQA |
| N_QUERIES (smoke) | 20 per seed × 3 seeds = 60 total | Fits within 180s smoke gate on CPU. Sampled deterministically per seed from the filtered `type=="bridge"` subset. |
| SEEDS | [11, 17, 23] | Matches Exp 1 / Exp 2 seed convention. |
| TITLES_PER_QUERY | 10 (fixed by HotpotQA distractor) | Constructs a 10-node mini-KG per query. |
| BGE_MODEL | `BAAI/bge-small-en-v1.5` | Reused from RAG-composition SMOKE (fast, CPU-eligible). |
| N_DIM_TRIGRAM | 1024 | Matches Exp 1 char-trigram encoder. |
| COSINE_THRESH | 0.5 | Matches Exp 1 char-trigram matching threshold. |
| PPR_ALPHA | 0.15 | Matches Exp 2. CITED@Haveliwala_2003. |
| PPR_ITERS | 5 | Matches Exp 2 (task spec: 3-5). |
| PPR_TOP_K | 5 | Matches Exp 1/Exp 2 TOP_K for apples-to-apples recall@5. |
| MASS_CONSERVATION_TOL | 0.005 | Matches Exp 2. |
| MENTION_MATCH | case-insensitive substring with word-boundary (regex `\b<title>\b`) | HippoRAG-style OpenIE-lite; deterministic; no LLM. |
| Backend | numpy CPU + bge-small CPU | Small matmul; CPU-eligible. |

## KG construction (real semantic edges — the load-bearing design decision)

Per query, extract the 10 distinct article titles from `context.title`. For each ordered pair `(title_A, title_B)` with `A != B`, count how many sentences from `context.sentences[i]` (where `title[i] == title_A`) contain `title_B` as a case-insensitive **word-boundary** substring (`\btitle_B\b`). This count is `C[A,B]` (directed mentions from A to B). Symmetrize: `C_sym[A,B] = C[A,B] + C[B,A]`. Column-normalize to make PPR mass-preserving: `A[i,j] = C_sym[i,j] / sum_k C_sym[k,j]` (column-stochastic where non-zero).

**Isolated titles** (no mentions in either direction) keep zero column; PPR restart handles those.

**Discriminator-fires sanity**: mean edges per node across sampled queries must be ≥ 1.0. If < 1.0 across ≥50% of sampled queries, EMIT `HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH` and abort — this is a data-availability failure (HotpotQA titles don't reference each other), not a mechanism failure. Distinguishes graph-walk viability from KG-signal-availability.

## Bridge target definition

For each bridge query, the **target set** is the set of `(title, sent_id)` pairs listed in `supporting_facts`. Sentence-index resolution: flatten `context.sentences` into a global list; `TARGET_IDX` = set of flat indices of the supporting sentences.

- **Baseline hit** = `|TOP_K_hop1 ∩ TARGET_IDX| ≥ 1` (binary; matches HippoRAG's recall pattern).
- **PPR hit** = `|TOP_K_ppr ∩ TARGET_IDX| ≥ 1` (binary).
- **Missed-by-hop-1 subset** = queries where baseline hit = 0.
- **Recovery rate** = fraction of missed-by-hop-1 queries where PPR hit = 1.

Chunk scoring inherits Exp 2's subject-only rule: `sentence_score(s) = ppr[article_title_of(s)]`. Ranking = argsort descending. Ties broken by original hop-1 dense score (stable-sort secondary).

## Arms (4)

- **ARM_HOP1_DENSE_ALONE_BASELINE** — recall@5 (binary hit) of TARGET on top-K bge-small hop-1 retrieved sentences over all `context.sentences`. Confounded baseline that (per HippoRAG evidence) misses hop-2/bridge sentences.
- **ARM_MAIN_PPR_RECOVERED** — MAIN. Seed PPR from title-entities extracted (via Exp 1 char-trigram fuzzy match, threshold=0.5) from concatenated text of hop-1 top-K sentences. Fixed 5-iter PPR alpha=0.15. Rank sentences by `ppr[title(sentence)]`. Recall@5.
- **ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE** — seed PPR from the FIRST supporting-facts title directly (bridge/linking article). Must recover TARGET at recall@5 ≥ 0.95.
- **ARM_NEG_CTL_PPR_FROM_RANDOM** — seed PPR from a random title in `context.title` that is NOT in `supporting_facts.title` (deterministic via seed-derived rng). Must recover TARGET at recall@5 ≤ 0.10.

## Discriminator: HP / MB / HF gates

### HARD_PASS
- POS_CTL recall@5 ≥ 0.95 (control gate)
- NEG_CTL recall@5 ≤ 0.10 (control gate)
- PPR mass sum in [0.995, 1.005] per iteration (numerical correctness)
- **PPR_recovery_rate ≥ 0.50** on missed-by-hop-1 subset (main claim; matches HippoRAG precedent)
- CARDINALITY_OK: 4 arms × 3 seeds = 12 units observed
- ARMS-DIFFER: MAIN / POS_CTL / NEG_CTL per-query hit-vector hashes distinct (BASELINE may collide with MAIN when both miss all targets — legitimate exemption; documented).
- Discriminator-fires (KG signal): mean_edges_per_node ≥ 1.0 across ≥ 50% of sampled queries.

### HARD_FAIL (mechanism)
- **PPR_recovery_rate < 0.15** on missed-by-hop-1 subset — graph-walk approach is dead even with real semantic signal; strategic decision-point for the arc (revive encoder-swap).
- OR POS_CTL < 0.95 (mechanism broken by construction; do not trust MAIN).
- OR NEG_CTL > 0.10 (PPR mass leaking uniformly; matched-entity seed doesn't concentrate; do not trust MAIN).

### HARD_FAIL (methodology)
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H (observed units < 12).
- HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF (MAIN identical to POS or NEG — bug).
- HARD_FAIL_PPR_MASS_NONCONSERVATIVE.
- HARD_FAIL_VACUOUS_SUBSET (missed-by-hop-1 subset < 10 queries across all seeds — insufficient discriminator).
- HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH (mean edges per node < 1.0 across ≥ 50% of queries — data problem, not mechanism problem; distinguishes from HARD_FAIL).

### MIDDLE_BAND
- PPR_recovery_rate in [0.15, 0.50) — partial signal; USER decision on whether to chain Exp 3 or pivot.

## CARDINALITY_OK pre-reg field
EXPECTED_N_UNITS = 4 arms × 3 seeds = **12**.
`cardinality_ok: bool`.

## Bias controls
- **POS_CTL_BRIDGE_SEED**: seed from FIRST supporting_facts title; must recover ≥ 0.95.
- **NEG_CTL_RANDOM_SEED**: seed from random `context.title` not in supporting-facts titles.
- **Mass-conservation invariant**: sum PPR distribution 1.0 ± 0.005 per iter.
- **Filtered subset**: `type == "bridge"` (comparison queries are structurally different and don't need bridge recovery).
- **Missed-by-hop-1 restriction**: recovery rate specifically on queries hop-1 missed.
- **Query sampling determinism**: `random.Random(seed).sample(bridge_queries, N_QUERIES)` — reproducible.
- **Do NOT reuse RAG-composition SMOKE failed queries** — those are for the synthetic KG. This cell constructs NEW queries from HotpotQA.
- **Data-availability halt**: if HotpotQA titles don't cross-reference (mean_edges_per_node < 1.0), HALT and report as data problem — NOT mechanism failure.

## Compute architecture
- **Class**: (b) sequential-CPU with justification.
- **Justification**: per-query PPR is a small (10×10) sparse matmul with 5 iters; PPR compute is negligible. Dominant cost is bge-small encoding of ~40 sentences per query × 20 queries × 3 seeds ≈ 2400 encodings on CPU. bge-small on CPU at batch 32 → ~30-40s per seed. Total ~90-120s across 3 seeds. GPU batching would speed the bge phase but the cell is CPU-eligible and SMOKE-only; per Cell 2 precedent, sequential-CPU is honest here. Wall time comfortably < 180s smoke gate.
- **Storage strategy**: no_storage (retrieval-only; no substrate write). Not compositional across queries; no chain-composition concern.

## Compute budget / dispatch
- Local CPU. **SMOKE-only** (USER-locked 2026-07-01).
- Expected wall-clock: ~90-120s across 3 seeds. Smoke gate --timeout 300s (safety headroom).
- STANDARD_HDI_EXP_DEV_SMOKE macro.
- NO GPU. NO remote push required (local_cpu_queue only).

## CRLB / floor
`crlb_n_a` = "PPR recall@5 is a rate, not a shift-noise measurement; no continuous-Gaussian noise floor CRLB applies. Discriminator-reachability instead: NEG_CTL ≤ 0.10 and POS_CTL ≥ 0.95 span the arm-difference band the discriminator must fire in. Adds a KG-signal reachability check via mean_edges_per_node ≥ 1.0."

## Calibration check
`default_ok_for_this_regime`: PPR alpha=0.15 is field-standard (matches Exp 2 which passed POS_CTL=1.000); iters=5; COSINE_THRESH=0.5 matches Exp 1 which passed MATCH_RATE=0.982.

## SCHEMA-VET pre-dispatch fields
- `arms_differ_verified` (smoke sets True)
- `final_metrics_atomicity: tmp_replace`
- `cardinality_ok: bool`
- `discriminator_reachability: true`
- `calibration_check: default_ok_for_this_regime`
- `baseline_in_band: bool` (0.05 < baseline < 0.95 on the failed subset — expected 0.20 < baseline < 0.60 typical HippoRAG regime)
- `sweep_alignment_verdict: N_A` (no sweep axis)
- `discriminating_fraction: N_A` (single-regime cell)
- `composition_edges: SHAPE_MATCH` (char-trigram entity extract → PPR seed → chunk scoring; all substrate-native primitives, no cross-modality adapter)
- `positive_control_arms`: ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE (seed from truth), tolerance 0.05, cited_prior Exp 2 POS_CTL=1.000, test_regime_delta = HotpotQA_bridge (SHAPE_DRIFT from synthetic ENTITIES → real Wikipedia titles).
- `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` (synthetic UUID entities → real Wikipedia titles is a genuine regime shift; POS_CTL is the reproducer at the new regime).
- `progress_logging: print_flush_true` (all print calls use flush=True; sys.stdout.reconfigure line_buffered fallback)
- `cell_chunked: false` (single-seed loop within cell; short overall runtime)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: false` (< 3 min total; excluded per §13 heuristic)
- `defensive_error_checking: passed_all_4_patterns`

## Number-tagging discipline
- 0.170 (Exp 2 recovery_rate on synthetic KG) MEASURED@data/exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03/metrics.json
- 1.000 (Exp 2 POS_CTL) MEASURED@data/exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03/metrics.json
- 0.982 (Exp 1 MAIN) MEASURED@data/exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03/metrics.json
- +11-20pp R@2/R@5 HippoRAG lift CITED@arXiv:2405.14831
- +2.55pp F1 BridgeRAG parallel-chain CITED@arXiv:2604.03384
- alpha=0.15 CITED@Haveliwala_2003
- HARD_PASS ≥ 0.50 HYPOTHESIZED@drill_2026-07-03_and_HippoRAG_precedent
- HARD_FAIL < 0.15 HYPOTHESIZED@matches_Exp2_synthetic_floor_of_0.170 (below this = worse than synthetic = mechanism dead)
- 807 bridge queries in HotpotQA distractor 1k MEASURED@disk_scan_2026-07-03
