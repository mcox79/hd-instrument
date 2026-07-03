# Pre-registration: `substrate_stage1_apply_exp2c_ppr_walk_synthesized_wikidata_bridges_smoke_2026_07_03`

## Milestone / arc position
Experiment 2C — mechanism-viability revival of Exp 2B (which landed `HARD_FAIL` via `HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH` on HotpotQA distractor 10-title mini-KGs, i.e. INFRASTRUCTURE/SCOPE diagnosis per Skunkworks-verified atom, NOT structural mechanism failure).

Revival criterion from Skunkworks-filed atom: **mean_edges_per_node ≥ 1.5 across ≥ 80% of queries** AND **≥ 30% genuine hop2 in query set**. This experiment satisfies BOTH by construction:
- Wikidata typed relations are dense semantic edges (5,510 typed triples over ~5,371 entities → mean_edges_per_node ≈ 2.05 undirected globally). MEASURED@data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl:disk_scan_2026-07-03.
- Synthesized 2-hop bridge queries are **100% genuine hop2 by construction** (query = "label(A) and label(C)" where A→B→C is a real 2-hop walk in the KG).

**Decision-point experiment:**
- **HARD_PASS** → PPR-walk mechanism is viable on real-semantic-KG scale; report as decision-point closure; USER decides Director-KB scale re-test vs Exp 3 composition-recovery next.
- **HARD_FAIL** → Skunkworks-verify diagnosis (STRUCTURAL vs IMPLEMENTATION/SCOPE) before pivoting. If STRUCTURAL: consider encoder-swap as last-resort pivot.
- **MIDDLE** → present to USER.

Author: `hdi_exp_dev` 2026-07-03. HYPOTHESIZED_P_DEFLATED@drill_2026-07-03:0.60 (this KG is genuinely dense-semantic per HippoRAG precedent; POS/NEG-CTL span is more likely to fire than on HotpotQA distractor).

## Chain-grade parents (composition provenance — META_RULE_AT)
- **Exp 2 landing** (2026-07-03) `substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03` — PPR primitive proven numerically (POS_CTL=1.000, mass conservation OK). REUSE `ppr_iterate`, `seed_from_entities` via import.
- **Exp 2B landing** (2026-07-03) `substrate_stage1_apply_exp2b_ppr_walk_wikipedia_semantic_kb_smoke_2026_07_03` — HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH (infrastructure/scope). REUSE HALT-gate logic + arm structure.
- **Exp 1 HARD_PASS** (2026-07-03) — CharTrigramEncoder + fuzzy match precedent. Adapt (not import) since vocab here = 5,371 Wikidata entities keyed by LABEL, not by Q-id.
- Personalized PageRank (Haveliwala 2003).
- CharTrigramEncoder (chain-grade primitive).

## Adjacent literature
- **HippoRAG** (arXiv:2405.14831): PPR on Wikipedia-derived semantic KGs (+11-20pp R@2/R@5 on 2WikiMultihopQA). This is the closest precedent to a **real-semantic-KG scale test** in the substrate arc.
- BridgeRAG (arXiv:2604.03384): selective-effect precedent.

## Prior-work check
Substrate-KB query: `PPR walk 2-hop bridge Wikidata KG typed relations semantic dense`.
Top hit: `semantic_relation` at cosine=0.317 (WordNet gloss atom; unrelated content). No prior cell operationalizes PPR on the Wikidata-adapted KG. Genuinely novel; Exp 2B is the immediate parent (both parent cells are in-arc). NOT a rediscovery.

## Functional Requirements (META_RULE §15.E)
1. **Wikidata KG loader must construct a global 5,371-node ~5,510-edge undirected KG from the JSONL relations file** with mean_edges_per_node ≥ 1.5 across ≥ 80% of synthesized queries' local subgraph — the Exp 2B revival criterion.
2. **Query synthesizer must produce 2-hop bridge queries where B is provably a genuine 2-hop bridge** (both `A → B` and `B → C` edges exist in the KG) with degree-cap `3 ≤ deg(B) ≤ 50` to prevent super-hub pathologies (Wikidata KG top hub Q65943 has in-degree=1522 which would trivialize NEG_CTL).
3. **Fixed-iteration PPR must produce valid probability distribution (sum=1.0 ± 0.005, all ≥ 0)** — inherited from Exp 2.
4. **PPR seeded from the TRUE bridge Q-id must recover B at recall@5 ≥ 0.95** — POS_CTL; proves PPR mechanism works on the semantic KG when given correct seed. B is BY-CONSTRUCTION the seed → recall@1=1.0 trivially → POS_CTL should saturate to ≥0.95.
5. **PPR seeded from a random unrelated entity must recover B at recall@5 ≤ 0.10** — NEG_CTL; the degree cap on B (max 50) prevents super-hub inflation. Given 5,371 entities and hub-and-spoke topology, a random leaf typically sits in a distant region; PPR mass concentrates near the seed's local neighborhood.
6. **PPR seeded from hop-1 matched entities (CharTrigramEncoder fuzzy match against entity LABELS from query text) must recover B at recall@5 meaningfully higher than hop-1-dense-alone on the missed-by-hop-1 subset** — the mechanism claim.

## Data source
- `data/substrate_state/wikidata_action_api_v2_relabeled_adapted_relations.jsonl` — 5,510 typed triples in format `{"src": "math::T3/wikidata_Q182505", "rel_type": "DEPENDS_ON", "tgt": "math::T3/wikidata_Q65943", ...}`. MEASURED@disk_scan_2026-07-03:wc -l.
- `data/substrate_index/math/atoms.jsonl` — 5,360 Wikidata atoms with `name` labels. MEASURED@disk_scan_2026-07-03: 5,360/5,371 (99.79%) of KG entities are labeled.

## KG construction
Entity keys are normalized from `math::T3/wikidata_Qxxx` to `wikidata_Qxxx` (drop namespace prefix). Nodes = all 5,371 distinct entities appearing as either src or tgt.
For each triple `(src, rel_type, tgt)`, add both `C[src, tgt] += 1` and `C[tgt, src] += 1` (undirected symmetrization). `rel_type` field is IGNORED for PPR (rationale: PPR is a graph-structure global-flow op; typed-edge weighting is a v2 optimization but would complicate POS/NEG interpretation. Vanilla undirected column-stochastic matches Exp 2 + Exp 2B convention).
Column-normalize: `A[i,j] = C[i,j] / sum_k C[k,j]`. Isolated columns stay zero; PPR restart handles them.
Backend: `scipy.sparse.csr_matrix` (sparsity ~0.02% at N=5,371; dense would be 231 MB).

## Query synthesizer
For each seed (11, 17, 23), synthesize N=50 2-hop bridge queries:
1. Precompute adjacency dict `neighbors: Dict[qid, Set[qid]]` (undirected).
2. Filter candidate bridges `B` where `3 ≤ deg(B) ≤ 50` AND B has ≥ 2 distinct neighbors AND B has a label.
3. Deterministic sample via `random.Random(seed)`:
   - Pick `B` from filtered pool.
   - Pick two DIFFERENT neighbors `A`, `C` of B where `A != C` AND `A ∉ neighbors[C]` (ensures B is a genuine bridge, not a triangle-completion).
   - Retry if constraints unsatisfiable (rare).
4. Query text = `label(A) + " " + label(C)` (minimalist template; matches CharTrigramEncoder's token-level fuzzy match design).
5. Ground truth = `B` (Q-id).

## Hop-1 retrieval (dense-alone baseline)
CharTrigramEncoder(n_dim=1024) codebook built from lowercased entity LABELS (parallel-indexed to Q-ids). Query encoded via same encoder; top-K entities by cosine.
Rationale for CharTrigram vs bge-small: bge-small was appropriate for HotpotQA (natural sentences) but this cell's queries are 2-entity concatenations of Wikidata labels (often short, technical, sometimes non-English). Char-trigram matching is entity-lookup-appropriate and matches Exp 1's design for this class of retrieval. MEASURED@Exp1_recall=0.982 shows char-trigram is adequate for label matching.

## Arms (4)
- **ARM_HOP1_TRIGRAM_ALONE_BASELINE** — top-5 entities by char-trigram cosine to query. `hit = 1` iff B ∈ top-5.
- **ARM_MAIN_PPR_RECOVERED** — seed PPR from hop-1 top-5 (uniform mass), 5 iters, alpha=0.15. Rank all 5,371 entities by ppr[i]; hit = 1 iff B ∈ top-5.
- **ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE** — seed PPR from B directly. `hit = 1` iff B ∈ top-5. Expected ≥ 0.95 (B is highest ppr mass by construction; only fails if a neighbor's ppr overtakes B numerically — should not happen with alpha=0.15 restart).
- **ARM_NEG_CTL_PPR_FROM_RANDOM** — seed PPR from a random entity NOT in `{A, B, C, neighbors(B)}`. `hit = 1` iff B ∈ top-5. Expected ≤ 0.10.

## Discriminator: HP / MB / HF gates

### HARD_PASS
- POS_CTL recall@5 ≥ 0.95
- NEG_CTL recall@5 ≤ 0.10
- PPR mass sum in [0.995, 1.005] per iteration
- **PPR_recovery_rate ≥ 0.50** on missed-by-hop-1 subset (mechanism claim; matches HippoRAG precedent)
- CARDINALITY_OK: 4 arms × 3 seeds = 12 units observed
- ARMS-DIFFER: per-query hit-vector hashes distinct (BASELINE/MAIN legitimate collision on all-zero adverse regime documented as exemption per Exp 2B pattern)
- KG-signal-fires (revival criterion): **mean_edges_per_node ≥ 1.5 across ≥ 80% of queries' local subgraph** (measured over B and B's 1-hop neighbors' 1-hop expansion — the region PPR actually visits).

### HARD_FAIL (mechanism)
- PPR_recovery_rate < 0.15 on missed-by-hop-1 subset
- OR POS_CTL < 0.95 (mechanism broken by construction at this KG scale — regime-extension failure from small synthetic KG to 5K-node real KG)
- OR NEG_CTL > 0.10 (PPR mass leaking uniformly — matched-entity seed is not concentrating)

### HARD_FAIL (methodology)
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H
- HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF
- HARD_FAIL_PPR_MASS_NONCONSERVATIVE
- HARD_FAIL_VACUOUS_SUBSET (missed-by-hop-1 subset < 10 total across seeds)
- HALT_KG_DATA_AVAILABILITY_FLOOR_BREACH (mean_edges_per_node < 1.5 across > 20% of queries' local subgraph — data problem)

### MIDDLE_BAND
- PPR_recovery_rate in [0.15, 0.50) — partial signal; USER decision.

## CARDINALITY_OK pre-reg field
EXPECTED_N_UNITS = 4 arms × 3 seeds = **12**. `cardinality_ok: bool`.

## Bias controls
- **POS_CTL** with B-as-seed guards mechanism correctness at scale (5,371 entities is a genuine scale delta from Exp 2's 20-entity synthetic).
- **NEG_CTL** with random-non-neighbor seed guards against mass-diffusion confounds; degree cap on B prevents super-hub NEG_CTL inflation.
- **Mass-conservation invariant** per PPR iter.
- **Missed-by-hop-1 restriction** for recovery rate.
- **Degree cap on B**: `3 ≤ deg(B) ≤ 50`. Rationale: prevents super-hub bridges (Q65943 in-degree=1522, Q24034552 in-degree=1501, Q8366 in-degree=799 — those hubs are Wikidata top-level concepts like "topic of mathematics", not meaningful bridges); AND requires enough structure to be a real bridge.
- **A-C non-adjacency**: `A ∉ neighbors(C)` — B must be a GENUINE 2-hop bridge, not part of a triangle.
- **Query determinism**: `random.Random(seed)` for all sampling.
- **Sub-KG signal check**: for each query, measure mean_edges_per_node in the local subgraph {B} ∪ neighbors(B). If < 1.5 for > 20% of queries → HALT.

## Compute architecture
- **Class**: (b) sequential-CPU with justification.
- **Justification**: 5,371 × 5,371 sparse (5510 nonzeros) PPR matmul is trivial (~0.5 ms/iter via scipy.sparse). Char-trigram codebook build over 5,371 labels at N_DIM=1024 ≈ ~5-15s per seed (one-time). Per-query PPR + ranking ≈ 5-10 ms. Total wall: 30-90s across 3 seeds. GPU batching would speed the codebook build (matmul-eligible) but the SMOKE-only cell's wall is well under 3 min. Sequential-CPU is honest here per Exp 2B precedent.
- **Storage strategy**: `no_storage` (retrieval-only; no substrate write). Not compositional across queries; no chain-composition concern.

## Compute budget / dispatch
- Local CPU. **SMOKE-only** (USER-locked 2026-07-01).
- Expected wall-clock: 30-90s. Smoke gate `--timeout 300s` (safety headroom).
- STANDARD_HDI_EXP_DEV_SMOKE macro. NO GPU. NO remote push required.

## CRLB / floor
`crlb_n_a` = "PPR recall@5 is a rate, not a shift-noise measurement; no continuous-Gaussian noise floor CRLB applies. Discriminator-reachability instead: NEG_CTL ≤ 0.10 and POS_CTL ≥ 0.95 span the arm-difference band the discriminator must fire in. KG-signal reachability via mean_edges_per_node ≥ 1.5 (Exp 2B revival criterion)."

## Calibration check
`default_ok_for_this_regime`: PPR alpha=0.15 is field-standard (Exp 2 POS_CTL=1.000, Exp 2B mechanism ran cleanly — halt was data not mechanism); iters=5; COSINE_THRESH=0.5 matches Exp 1 which passed MATCH_RATE=0.982.

## SCHEMA-VET pre-dispatch fields
- `arms_differ_verified: bool` (smoke sets True)
- `final_metrics_atomicity: tmp_replace`
- `cardinality_ok: bool`
- `discriminator_reachability: true`
- `calibration_check: default_ok_for_this_regime`
- `baseline_in_band: bool` — expected 0.0 ≤ baseline < 0.30 typical (char-trigram matches A and C in query text; B usually not in query text unless it happens to share trigrams with A or C; so baseline recall of B should be ~0-30%). Passes 0.05 < baseline < 0.95 requirement for the discriminating band as long as baseline > 0.05 across ≥50% of query pool. If baseline = 0.0 across ALL queries → discriminator has no missed-subset to test — enter VACUOUS_SUBSET halt.
- `sweep_alignment_verdict: N_A` (no sweep axis)
- `discriminating_fraction: N_A` (single-regime cell)
- `composition_edges: SHAPE_MATCH` (CharTrigramEncoder cosine → PPR seed → PPR argsort ranking; all substrate-native primitives)
- `positive_control_arms`: ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE (seed from truth) — tolerance 0.05 against Exp 2 POS_CTL=1.000 MEASURED. `regime_extension_audit: SHAPE_DRIFT_with_documented_risk` (Exp 2: 20-entity synthetic KG; Exp 2C: 5,371-entity real Wikidata KG — 268x scale delta; degree distribution qualitatively different).
- `progress_logging: print_flush_true`
- `cell_chunked: false` (single-seed loop; short overall runtime)
- `start_marker_written: true`
- `crash_diagnostic_present: true`
- `heartbeat_present: false` (< 3 min total)
- `defensive_error_checking: passed_all_4_patterns`

## Number-tagging discipline
- 0.170 (Exp 2 recovery on synthetic KG) MEASURED@data/exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03/metrics.json
- 1.000 (Exp 2 POS_CTL) MEASURED@data/exp_substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03/metrics.json
- 0.982 (Exp 1 MAIN) MEASURED@data/exp_substrate_stage1_apply_exp1_bridge_entity_coverage_smoke_2026_07_03/metrics.json
- 5,510 triples MEASURED@disk_scan_2026-07-03:wc -l wikidata_action_api_v2_relabeled_adapted_relations.jsonl
- 5,371 distinct entities MEASURED@disk_scan_2026-07-03:python -c "count distinct src+tgt"
- 5,360 labeled atoms (99.79%) MEASURED@disk_scan_2026-07-03:atoms.jsonl scan
- mean_edges_per_node ≈ 2.05 (undirected global) MEASURED@disk_scan_2026-07-03: 2*5510/5371
- Q65943 in-degree=1522 (top hub) MEASURED@disk_scan_2026-07-03
- HARD_PASS ≥ 0.50 HYPOTHESIZED@drill_2026-07-03_and_HippoRAG_precedent
- HARD_FAIL < 0.15 HYPOTHESIZED@matches_Exp2_synthetic_floor_of_0.170
- mean_edges_per_node ≥ 1.5 revival threshold CITED@Skunkworks_Exp2B_diagnosis_atom_2026-07-03
- alpha=0.15 CITED@Haveliwala_2003
