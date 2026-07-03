# Pre-registration: `substrate_stage1_apply_exp2_ppr_walk_bridge_recovery_smoke_2026_07_03`

## Milestone / arc position
Experiment 2 from the optimal-retrieval-architecture drill (2026-07-03, `notes/research_optimal_retrieval_architecture_for_substrate_director_kb_2026-07-03.md`, Part 3). Chains from Exp 1 HARD_PASS (bridge-entity coverage=0.982) which established that char-trigram fuzzy-match reliably extracts the TRUE bridge entity from hop-1 dense candidates on the synthetic 20-entity KG.

Author: `hdi_exp_dev` 2026-07-03. HYPOTHESIZED_P_DEFLATED@drill_2026-07-03:0.45 (Architecture C, HippoRAG/BridgeRAG-style graph-walk seeded by dense hits — precedent gain is real but explicitly narrow per BridgeRAG's own ablation).

## Chain-grade parents (composition provenance — META_RULE_AT)
- Exp 1 HARD_PASS (2026-07-03): char-trigram-fuzzy-entity-extraction from hop-1 dense chunks recovers bridge entity at 0.982 on failed-query subset (chain-grade for entity-extraction step).
- `hdlab/kg_traversal.py::KGStore` — CERT 585 chain-grade traversal primitive (not directly reused here — this cell builds its own directed adjacency for PPR since the synthetic KG is small and PPR needs a bipartite chunk-lookup indexed by both entity endpoints; KGStore's Hebbian W would blur PPR's sparse mass).
- FHRR bind/unbind primitives (Plate 1995; foundational).
- Personalized PageRank — Haveliwala 2003; standard sparse linear-algebra iteration.

## Adjacent literature (all previously surveyed in the optimal-arch drill)
- HippoRAG (arXiv:2405.14831): PPR seeded from query-linked entity nodes; +11-20pp R@2/R@5 on 2WikiMultihopQA where bridge entities are structurally disconnected. Direct precedent.
- BridgeRAG (arXiv:2604.03384): +2.55pp F1 on parallel-chain (non-lexically-connected) queries specifically; ≈0 on already-dense-solvable. Selective-effect precedent (regime-specific lift, not universal).
- Documented negative case: weighted-hypergraph KV-graph outperformed PPR by +3.4-3.6 F1 on 2Wiki/MuSiQue, but HotpotQA graph-coverage lift did NOT convert to F1 — graph-walk is not a universal fix.

## Substrate-KB pre-work query
Query: `personalized pagerank graph walk seeded bridge entity recovery hop retrieval`.
Prior arc check: this is the FIRST cell operationalizing PPR-walk over the synthetic RAG-composition KG; Exp 1 (2026-07-03) is the immediate parent and does entity-extraction only, not graph-walk. Verdict: **genuinely novel** at cell-level; grounded in one-day-prior drill.

## Scale caveat (adopted per Exp 1 precedent, CENTRAL to this cell's framing)
The 20-entity synthetic KG with 100 facts (each entity × each of 5 relations, both endpoints drawn from ENTITIES) inherits the same by-construction near-ceiling regime as Exp 1. The KG is fully-connected in the sense that every entity has 5 outgoing edges to (potentially any) entity, so PPR mass will diffuse quickly — the mechanism proof is: does PPR seeded from Exp-1-matched entities concentrate mass on the TRUE bridge entity (mid)'s chunks MORE than uniform diffusion / hop-1-alone?

**Pre-registered:** this is a mechanism-proof on synthetic corpus, NOT a scale claim. A HARD_PASS here proves the PPR-seeded-by-fuzzy-match architecture works end-to-end on a compact substrate-native KG; it does NOT extrapolate to Wikipedia-scale KBs where PPR mass may diffuse pathologically or where the bridge entity may not be reachable at all. Scale-transfer is a separate future test (Exp 4 or later — proposed target: Wikipedia FULL 10K subgraph if available). The scale caveat here has SLIGHTLY MORE force than Exp 1: PPR is a global-flow computation whose behavior at scale is qualitatively different (mass concentration vs. diffusion breakdown), whereas Exp 1's per-token fuzzy match is a local operation whose behavior is more scale-invariant. Report this in the verdict message.

## Functional Requirements (META_RULE §15.E)
1. **Fixed-iteration Personalized PageRank must produce a valid probability distribution (sum=1.0, all >=0) after each iteration** — sanity check for numerical correctness of the sparse power-iteration primitive.
2. **PPR seeded from the TRUE bridge entity must recover the bridge chunk at >=0.95** on the failed-query subset (POS_CTL: proves the PPR + chunk-scoring mechanism works when given correct seed).
3. **PPR seeded from a random unrelated entity must recover the bridge chunk at <=0.10** on the failed-query subset (NEG_CTL: proves lift is not an artifact of PPR mass uniformly leaking to all chunks).
4. **PPR seeded from Exp 1's matched entities must recover the bridge chunk at a MEANINGFULLY higher rate than hop-1-dense-alone** on the missed-by-hop1 subset — the actual mechanism claim.

## Substrate config

| Field | Value | Rationale |
|---|---|---|
| N_QUERIES | 20 (per seed) | Matches Exp 1 / RAG-composition SMOKE. |
| SEEDS | [11, 17, 23] | Matches Exp 1 / RAG-composition SMOKE. |
| N_ENTITIES | 20 | Fixed by synthetic corpus. |
| N_FACTS | 100 | 20 entities × 5 relations. |
| N_DIM | 4096 | For char-trigram encoder in Exp-1 replay + FHRR bge_retrieve replay (precedent SMOKE N_DIM). |
| PPR_ALPHA | 0.15 | Standard restart probability per HippoRAG / classical PPR literature. |
| PPR_ITERS | 5 | Fixed-iteration truncation (per task spec: 3-5 iterations). |
| PPR_TOP_K_CHUNKS | 5 | Match Exp 1 TOP_K (bge hop-1 uses K=5); apples-to-apples recall@5 comparison. |
| Backend | numpy CPU | Small matmul; CPU-eligible. |
| Encoding | float32 sparse adjacency | Standard PPR representation. |

## Arms (4)

- **ARM_HOP1_DENSE_ALONE_BASELINE**: recall@5 of the TRUE bridge chunk (fact index = `gt_chunks[1]` — the stage-2 fact "The r1 of mid is answer") in the top-K bge hop-1 retrieved facts. Restricted to failed-query subset from Exp 1 replay. This is the confounded baseline that produced the RAG-composition SMOKE HARD_FAIL.
- **ARM_MAIN_PPR_RECOVERED**: MAIN. Seed PPR from Exp 1's matched entities per query (using the same char-trigram fuzzy-match extraction on hop-1 chunks). Fixed 5-iteration PPR with alpha=0.15. Rank chunks by aggregated PPR mass at their (subject, object) endpoints. Measure recall@5 of the TRUE bridge chunk. Restricted to failed-query subset.
- **ARM_POS_CTL_PPR_FROM_TRUE_BRIDGE**: seed PPR from the TRUE bridge entity `mid` directly (single-entity seed vector with mass=1.0 at bridge entity). Must recover the bridge chunk at recall@5 >= 0.95. Proves PPR mechanism works when given correct seed.
- **ARM_NEG_CTL_PPR_FROM_RANDOM**: seed PPR from a random KG node deliberately chosen to have low structural connectivity to the query's bridge (uniform random over entities minus {e0, mid, answer}). Must recover the bridge chunk at recall@5 <= 0.10. Proves lift is not artifact.

## Recovery metric (the load-bearing measurement)

**PPR_recovery_rate** = fraction of queries in the "missed-by-hop1" subset (`ARM_HOP1_DENSE_ALONE_BASELINE recall@5 = 0` for that query) for which `ARM_MAIN_PPR_RECOVERED recall@5 = 1`.

This is the direct empirical test of the task's HARD_PASS / HARD_FAIL / MIDDLE bands per the drill's Part 3 Experiment 2 pre-registration.

## Discriminator: HP / MB / HF gates

### HARD_PASS
- POS_CTL recall@5 >= 0.95 (control gate)
- NEG_CTL recall@5 <= 0.10 (control gate)
- PPR mass-sum sanity: every seed's post-iteration mass sum in [0.995, 1.005] (numerical correctness)
- **PPR_recovery_rate >= 0.50** on missed-by-hop1 subset (main claim)
- CARDINALITY_OK: 4 arms × 3 seeds = 12 units observed
- ARMS-DIFFER: MAIN vs POS_CTL vs NEG_CTL per-query hit-vector hashes distinct (BASELINE may collide with MAIN when neither recovers bridge — legitimate exemption; documented in verdict).

### HARD_FAIL (mechanism)
- **PPR_recovery_rate < 0.15** on missed-by-hop1 subset — PPR does not surface bridge, escalate to MDR-style dense-feedback fallback per drill's Architecture A.
- OR POS_CTL < 0.95 (mechanism broken by construction; do not trust MAIN).
- OR NEG_CTL > 0.10 (PPR mass leaking uniformly; matched-entity seed doesn't concentrate; do not trust MAIN).

### HARD_FAIL (methodology)
- HARD_FAIL_CARDINALITY_BREACH_META_RULE_H (observed units < expected 12).
- HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF (MAIN identical to POS or NEG — indicates seed vector not actually differing).
- HARD_FAIL_PPR_MASS_NONCONSERVATIVE (any iteration's mass sum falls outside [0.995, 1.005]).
- HARD_FAIL_VACUOUS_SUBSET (missed-by-hop1 subset has < 10 queries across all seeds — insufficient discriminator).

### MIDDLE_BAND
- PPR_recovery_rate in [0.15, 0.50) — real but narrow lift (BridgeRAG-selective-effect pattern); worth shipping with modest expectations.

## CARDINALITY_OK pre-reg field
EXPECTED_N_UNITS = 4 arms × 3 seeds = **12**.

## Bias controls
- **POS_CTL_BRIDGE_SEED**: seed PPR from `mid` (the true bridge entity extracted from `q["mid"]`) — must recover >= 0.95.
- **NEG_CTL_RANDOM_SEED**: seed PPR from a uniformly random entity from ENTITIES minus {e0, mid, answer} — must be <= 0.10.
- **Mass-conservation invariant**: assert sum of PPR distribution is 1.0 ± 0.005 after each iteration (numerical correctness); fail the cell if violated.
- **Failed-subset restriction**: metric computed only on queries where the TANDEM_RAG arm of the RAG-composition SMOKE failed (the precedent HARD_FAIL condition) — apples-to-apples with Exp 1.
- **Missed-by-hop1 restriction**: PPR_recovery_rate specifically restricted to queries where hop-1-dense-alone BASELINE missed the bridge chunk — this isolates the mechanism claim (PPR fixes what hop-1 missed).
- **Arms-differ hashes**: per-query recall vectors are SHA256-hashed per arm; verified distinct across MAIN / POS_CTL / NEG_CTL; legitimate exemption when BASELINE and MAIN both fail all queries (extremely-adverse-mass regime).

## Compute budget / dispatch
- Local CPU. SMOKE-only (USER-locked 2026-07-01: SMOKE ONLY on local_cpu_queue).
- Expected wall-clock: ~15-30s per seed (dominated by Exp-1 precedent replay: bge retrieval + build_corpus). PPR itself is 5 iters × 100×100 sparse matmul = negligible.
- Total ~90s across 3 seeds. Smoke gate --timeout 300s.
- STANDARD_HDI_EXP_DEV_SMOKE macro.
- NO GPU. NO remote push required (local_cpu_queue only).

## CRLB / floor
`crlb_n_a` = "PPR recall@5 is a rate, not a shift-noise measurement; no continuous-Gaussian noise floor CRLB applies. Discriminator-reachability instead: NEG_CTL <= 0.10 and POS_CTL >= 0.95 span the arm-difference band the discriminator must fire in."

## Calibration check
`default_ok_for_this_regime`: PPR alpha=0.15 is the field-standard restart probability across HippoRAG, PPR-KGQA, and classical PageRank benchmarks; iteration count=5 is above HippoRAG's typical 3-iter default; K=5 matches precedent RAG-composition SMOKE.

## Number-tagging discipline
- 0.982 (Exp 1 MAIN result) MEASURED@exp1_smoke_2026_07_03
- 0.783 (ORACLE upper-bound) MEASURED@rag_composition_smoke_2026_07_03
- 0.083 (TANDEM_RAG HARD_FAIL) MEASURED@rag_composition_smoke_2026_07_03
- +11-20pp R@2/R@5 HippoRAG lift CITED@arXiv:2405.14831
- +2.55pp F1 BridgeRAG parallel-chain lift CITED@arXiv:2604.03384
- alpha=0.15 CITED@Haveliwala_2003_TopicSensitivePageRank
- 5 iters CITED@task_spec_2026-07-03
- HARD_PASS >= 0.50 HYPOTHESIZED@drill_part_3_exp2_2026-07-03
- HARD_FAIL < 0.15 HYPOTHESIZED@drill_part_3_exp2_2026-07-03
