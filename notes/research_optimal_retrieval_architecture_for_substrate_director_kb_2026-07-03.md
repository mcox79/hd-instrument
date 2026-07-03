# research: optimal production retrieval architecture for the substrate Director-KB (bridge-chunk surfacing)

**Date:** 2026-07-03
**Trigger:** direct research drill; follows composite ruling (commit f2eba7d69: "rerank architecture NOT validated; substrate composition WORKS when fed correctly (ORACLE 0.783); bottleneck is retrieval not composition; iterative retrieval or query decomposition is production path forward")
**Method:** 4 parallel Sonnet lit-scan sub-agents (generic CS/IR terms only, no substrate-novel names off-platform) + direct code-read of `hdlab/director_kb.py` and `backend/kb/wikipedia_ingest.py` + prior-arc grep of substrate KB.
**Field-advisor note:** `research_field_advisor.py` covers the 22-field physics/math taxonomy; consulted, found non-applicable (this is IR/retrieval-architecture engineering literature, same non-applicability noted in the 2026-07-03 selector-vs-reranker drill). Ranking below is from the 4 dedicated lit-scan axes.

---

## HEADLINE

**The substrate's Director-KB is already a knowledge graph** (`hdlab/director_kb.py` composes `KGStore` + `CharTrigramEncoder`, not dense embeddings) — this is the single most load-bearing fact this drill surfaces, and it changes the framing from "should we add KG-walk infrastructure" to "we already have the graph; we are missing the iterative-hop *trigger* mechanism that walks it." Literature strongly and specifically corroborates that **graph-walk retrieval, seeded by an initial dense/lexical hit, reliably surfaces bridge facts that dense-only single-shot retrieval structurally cannot reach** (HippoRAG +11-20pp R@2/R@5 on 2WikiMultihopQA; BridgeRAG's ablation shows the effect concentrates almost entirely, +2.55pp p<0.001, on exactly the "parallel-chain" query subtype where hop-1 and hop-2 share no lexical/semantic overlap — precisely the failure mode the RAG-composition SMOKE HARD_FAIL exhibited). Equally important: this lift is **narrow, not universal** — one documented case shows higher graph-coverage on HotpotQA failing to convert into answer-F1 gains at all, and dense-only retrieval already closes much of the multi-hop gap as top-k grows on easier splits. The recommended production architecture is **not** a pure pick from {A, B, C} — it is the natural composition of all three that the substrate's existing architecture already half-implements: **(B) graph-walk query decomposition natively on the existing KGStore, triggered by (A) MDR/Baleen-style dense-feedback iteration (no LLM), seeded by (C) the existing bge/stella dense frontend's hop-1 hits.** None of the four lit-scan axes found a single LLM call anywhere in the strongest-precedent versions of any of the three architectures — full USER-locked substrate-native compliance is achievable.

---

## Part 1 — Three candidate architectures, compared

### (A) Iterative retrieval — query bridge after hop-1 reveals intermediate entity

**Mechanism:** re-query using information surfaced in hop 1 (entity extraction, dense re-encoding of query+passage, or a small trained scorer), no generative LLM in the loop.

**LLM-free-capable precedents (verified this pass):**
- **MDR** (Xiong et al., ICLR 2021, arXiv:2009.12756): concatenate question + hop-1 passage text, re-encode with bi-encoder, ANN lookup for hop 2. Pure dense-similarity feedback, zero LLM. SOTA dense retrieval on HotpotQA fullwiki (62.3 EM / 75.3 F1 downstream). Known to degrade beyond 2 hops and OOD.
- **Beam Retrieval** (arXiv:2308.08973, NAACL 2024): jointly-trained encoder + classifier scores partial passage-chain hypotheses via beam search — no generative call to trigger the next hop. ~50% relative improvement over baselines on MuSiQue-Ans; SOTA HotpotQA; 99.9% precision on 2WikiMultihopQA. Strongest current numbers of any LLM-free candidate.
- **GoldEn Retriever** (Qi et al., EMNLP-IJCNLP 2019, arXiv:1910.07000): small trained span/query-generation module (pre-LLM era) + classical IR. Explicitly ablated to prove the mechanism works with **no pretrained LM at all**: Answer F1 +11.6pp (49.79 vs 38.19), Supporting-fact F1 +9.76pp, gold-doc recall nearly doubles to 61.0%. Strongest "proof of concept that this needs no LLM" precedent.
- **Baleen** (Khattab et al., NeurIPS 2021, arXiv:2101.00436): late-interaction retriever (FLIPR/ColBERT-style) + small trained condenser extracts salient facts to drive next-hop query. SOTA multi-hop retrieval, no LLM.

**Contrast — architectures that LOOK iterative but require an LLM as the actual mechanism** (IRCoT, IterDRAG, Self-RAG, DecomP, and the 2026 "training-free" BridgeRAG, which despite the name uses an LLM judge for chain selection): all disqualified for USER-locked substrate-native compliance — removing the LLM removes the core mechanism in every one of these, not an optimization.

**P_deflated = 0.55** (strong empirical precedent for LLM-free iteration; deflated for substrate-transfer uncertainty — none of these have been tested on the substrate's own KGStore/char-trigram stack).
**Substrate-implementability:** high. Hop-2 trigger = re-encode(query ⊕ hop-1-passage) via the existing dense frontend, or extract entity names via char-trigram fuzzy match against KGStore node names. Both already exist as primitives.

### (B) Query decomposition — rewrite multi-hop into sequential single-hops via templates / graph-walk

**Mechanism:** decompose the NL question into sub-queries or directly traverse a KG's relation structure, without a generative model.

**Strongest LLM-free precedents (verified this pass):**
- **STAGG** (Yih et al., ACL 2015): fully symbolic staged search — entity linking → beam-search graph-walk growing the "core inferential chain" → constraint augmentation. A log-linear/CNN scorer ranks partial query graphs; construction itself is classical. F1 52.5% on WebQuestions (then-SOTA).
- **GraftNet** (Sun et al., EMNLP 2018, arXiv:1809.00782): heuristic (non-learned) subgraph retrieval + GNN reasoning over the retrieved subgraph. Hits@1 66.4 WebQuestionsSP; 97.0/94.8/77.7 on MetaQA 1/2/3-hop — the MetaQA numbers are the single clearest quantitative demonstration in this whole drill of graph-native multi-hop working well when the KG is complete.
- **PullNet** (Sun et al., EMNLP 2019, arXiv:1904.09537): replaces GraftNet's heuristic with a *trained* iterative graph-expansion policy (small LSTM+GCN scorer deciding which nodes to "pull" each iteration) — still no LLM. Consistently beats GraftNet under incomplete-KB settings, which is the more realistic regime for a 170K-atom store that is not a complete Freebase-scale KG.
- **QDMR/Break-trained decomposer + DecompRC** (Wolfson et al. 2020 TACL, arXiv:2001.11770; Min et al. 2019 ACL): small trained (non-LLM) seq2seq/span-copy decomposers that split NL questions into ordered atomic sub-questions; DecompRC was HotpotQA-leaderboard-topping in its era without any LLM.

**P_deflated = 0.55** (STAGG/GraftNet/PullNet numbers are on Freebase-scale, densely-populated KGs — deflated because the substrate's atom-store graph is sparser and less complete; PullNet's incomplete-KB robustness is the most relevant precedent specifically because of this gap).
**Substrate-implementability: highest of the three.** This is the most direct match to what already exists — `KGStore` (CERT 584/585) IS the graph GraftNet/PullNet traverse; the substrate needs only an iterative expansion *policy* on top (start simple: PPR-style fixed-iteration walk: cheap linear algebra, no training needed at all, matching HippoRAG's approach below — upgrade to a PullNet-style trained scorer only if PPR proves insufficient).

### (C) Hybrid BM25 + dense + KG-walk — entity-linked graph traversal seeded by lexical/dense hits

**Mechanism:** combine lexical/dense retrieval (candidate generation) with graph traversal (bridge-surfacing), fused by rank or score.

**Verified precedents:**
- **RRF** (reciprocal rank fusion): general-purpose fusion, ~7.4% NDCG lift over either method alone on a non-multi-hop benchmark (WANDS e-commerce) — modest, general, not multi-hop-specific.
- **HippoRAG** (arXiv:2405.14831, NeurIPS 2024): offline entity-KG extraction (uses an LLM for this OFFLINE step only) + at query time, Personalized PageRank seeded from query-linked entity nodes, passages ranked by aggregated PPR mass. **+11-20pp R@2/R@5 on 2WikiMultiHopQA** (largest gain on the benchmark with the most structurally disconnected bridge entities), only **~3% on MuSiQue**, non-dominant on HotpotQA. The PPR traversal ITSELF requires no LLM (only the offline graph-build step does, in the published version — and the substrate can construct its KG without an LLM, since `director_kb.py` already does this via schema-driven triple extraction, not LLM OpenIE).
- **BridgeRAG** (arXiv:2604.03384, 2026): explicit ablation is the single most decision-relevant number in this drill: bridge-conditioned re-ranking gains **+2.55pp F1 (p<0.001) on parallel-chain (non-lexically-connected) query subtypes** vs **≈0 lift on single-chain subtypes**. This directly confirms the mechanism is *selective*, not universal — it fixes exactly the RAG-composition SMOKE's observed failure mode (bridge chunks with no lexical/semantic overlap to the query) and does nothing extra where dense retrieval already works.
- **Documented negative case:** a weighted-hypergraph KV-graph retrieval method beat PPR-style KG retrieval by +3.4-3.6 F1 on 2Wiki/MuSiQue, but higher structured-support coverage on HotpotQA did **not** convert into answer-F1 gains at all — graph-walk lift is real but does not uniformly transfer across benchmarks/regimes.

**P_deflated = 0.45** (real, on-point precedent directly matching the observed failure mode — but explicitly narrower/more conditional than architectures A/B alone would suggest; deflated further for the documented negative HotpotQA case).
**Substrate-implementability:** high for the PPR-seeded-by-dense-hits pattern specifically (cheap: PPR is a sparse linear-algebra op, no training); the offline-LLM-graph-extraction step in HippoRAG's published recipe is NOT required for the substrate since its KG is already built from schema-driven triples, not LLM OpenIE — this is a substrate advantage over the published recipe, not a gap to fill.

---

## Part 2 — Recommendation: single production architecture

**Recommended:** Composition of (B) as the backbone + (A) as the hop-trigger + (C) as the seeding mechanism. Concretely — a **dense-seeded PPR graph-walk over the existing KGStore, with MDR-style dense re-query as the fallback/refinement step when PPR under-specifies the walk.**

### Pipeline sketch

1. **Hop 1 (sensory layer, dense frontend):** query embedded with the existing/upgraded bge-class encoder (per prior 2026-07-03 encoder drill: bge-large is fine-for-purpose now; stella_en_1.5B_v5 or arctic-embed-l-v2.0 remain the recommended upgrade path on separate license/context-length grounds, orthogonal to this drill). Retrieve top-K candidates from the flat/dense index (Wikipedia-sentence lane) and/or the KGStore (atom lane).
2. **Bridge-entity extraction (classical, substrate-native):** extract entity mentions from hop-1 candidates via char-trigram fuzzy match against existing `KGStore` node names (no NER model, no LLM — the substrate already has the node vocabulary to match against).
3. **Hop 2 (graph-walk, substrate-native):** seed a fixed-iteration Personalized PageRank walk from the matched entity nodes over `KGStore`'s existing edge structure; surface passages/atoms connected to those nodes with non-trivial PPR mass. This is the step that recovers exactly the BridgeRAG/HippoRAG-validated regime (structurally disconnected bridge chunks that hop-1 dense retrieval could not reach).
4. **Fallback/refinement (MDR-style, only if PPR mass is degenerate/empty):** re-encode query ⊕ hop-1-passage-text with the dense frontend and re-query the flat index directly (this is the cheap fallback for KG-incomplete regions, matching PullNet's rationale for outperforming GraftNet specifically under incomplete-KB conditions — the substrate's 170K-atom KG is far from Freebase-complete).
5. **Composition (substrate reasoning layer, unchanged):** feed the UNION of {hop-1 dense candidates, hop-2 PPR candidates, MDR-fallback candidates} into the existing chain-grade composition primitives. This restores ORACLE-like conditions (0.783 measured) since bridge chunks are now actually present in the candidate set — the composition mechanism itself does not need to change; it was never the bottleneck (per the standing composite ruling).

### Substrate integration point

- Steps 2-3 are new code but compose entirely on EXISTING chain-grade primitives: `hdlab/kg_traversal.py::KGStore` (already the graph) + `hdlab/char_trigram_encoder.py` (already the fuzzy-match substrate). PPR itself is a new ~50-line addition (sparse matrix power iteration), not a new primitive class — it is linear algebra, squarely inside Principle-11 composition discipline.
- Step 1/4's dense frontend is the "sensory input" layer per USER directive — bge/stella stays frozen and external to the substrate; only its OUTPUT (candidate embeddings/passages) crosses into substrate-native code.
- No step in this pipeline requires an external LLM call at query time. The only place any of the four literature precedents used an LLM (HippoRAG's offline OpenIE graph-build) is already replaced in the substrate by the existing schema-driven triple extraction in `director_kb.py` — a substrate-native advantage over the published recipe, not a gap.

### Cortex-layer implications

Per `notes/design_m3_cortex_layer_substrate_operates_off_stage1_findings_2026-07-03.md`: this pipeline is exactly what "Task-class-fit META: cortex routes retrieval-task queries to dense-frontend; VSA-native queries to substrate direct" already anticipates — the cortex layer's job becomes routing between hop 1 (dense-frontend) and hops 2+ (substrate-native graph-walk), and this drill supplies the concrete trigger condition for that routing decision: **route to graph-walk whenever hop-1 candidates fail to jointly cover the query's detected entity set** (a cheap, substrate-computable trigger — no LLM needed to decide when to escalate). This also gives the cortex layer's "closed loop" atomization hook a natural target: every successful PPR-walk resolution is itself atomizable back to the KB as a MEASURED bridge-path fact, directly compounding the KG's completeness over time (mitigating the incomplete-KB weakness flagged in the PullNet precedent).

### Empirical tests needed before committing engineering effort (see Part 3 for full pre-registration)

1. Does bridge-entity fuzzy-match (char-trigram against KGStore node names) actually recover the entities the RAG-composition SMOKE HARD_FAIL missed? (cheapest, code-only check against the existing HARD_FAIL's logged queries)
2. Does a fixed-iteration PPR walk seeded from those matched entities surface the correct bridge chunk at meaningfully higher recall than hop-1-dense-alone, on the substrate's OWN KGStore (not a published benchmark)?
3. Does feeding the PPR-surfaced candidates into the EXISTING composition primitives recover ORACLE-adjacent performance (approaching the measured 0.783), confirming composition was never the bottleneck and this is purely a retrieval-completeness fix?

---

## Part 3 — Cheap decisive experiments (pre-registered)

### Experiment 1: Bridge-entity coverage check (cheapest — code-only, no new infra, ~1-2 hrs)
Re-run the RAG-composition SMOKE's failed queries. For each, extract entity mentions from the hop-1 dense-retrieved candidates via char-trigram fuzzy match against existing `KGStore` node names, and check whether the TRUE bridge entity (known from the query's gold annotation) is among the matched set.
- **HARD-PASS:** ≥ 60% of failed queries have their true bridge entity correctly matched from hop-1 candidates (confirms entity-extraction is not itself the bottleneck; PPR walk can proceed).
- **HARD-FAIL:** < 25% match rate (would mean hop-1 dense retrieval is so far off-target that even entity-level signal is missing, and the fix needs to happen upstream of graph-walk, e.g. a better hop-1 encoder or index).
- **MIDDLE:** 25-60% — partial signal; graph-walk helps some queries but a query-decomposition (Architecture B, template/QDMR-style) pre-processing step may be needed to improve entity-extraction coverage first.
- P_deflated = 0.55 (direct code-read confirms the primitives exist; genuine uncertainty on real hit-rate against the substrate's own sparse KG).

### Experiment 2: PPR-walk bridge-recovery test (moderate — ~1 day impl + CPU smoke)
Implement fixed-iteration PPR (3-5 iterations, standard restart probability 0.15) over `KGStore`, seeded from Experiment 1's matched entities. Measure recall@k of the true bridge chunk among PPR-ranked candidates vs. hop-1-dense-alone, on the same failed-query set.
- **HARD-PASS:** PPR recovers the bridge chunk for ≥ 50% of queries where hop-1-dense-alone missed it entirely (directly reproduces the BridgeRAG/HippoRAG regime-specific lift pattern on the substrate's own KG).
- **HARD-FAIL:** < 15% recovery (would mean the substrate's KG is too sparse/incomplete for PPR to find a path at all — matches the documented HotpotQA negative case where graph coverage didn't help; escalate to Architecture A's MDR-style dense-feedback fallback as the primary mechanism instead).
- **MIDDLE:** 15-50% — real but narrow lift (matches BridgeRAG's own selective-effect finding); worth shipping but expectations should be modest, not transformative.
- P_deflated = 0.45 (matches Part 1's Architecture-C estimate; this is the direct empirical test of that estimate).

### Experiment 3: End-to-end composition recovery test (moderate — reuses existing composition primitives, ~half day)
Feed the UNION of hop-1 + PPR-hop-2 candidates (from Experiment 2) into the EXISTING substrate composition pipeline (the one that scored ORACLE=0.783 when fed correct chunks). Measure whether composition F1 on the previously-failed queries approaches the ORACLE baseline.
- **HARD-PASS:** composition F1 on the PPR-recovered candidate set ≥ 90% of the ORACLE=0.783 reference (confirms retrieval-completeness, not composition, was the sole bottleneck — directly validating the standing composite ruling).
- **HARD-FAIL:** composition F1 < 60% of ORACLE even with PPR-recovered candidates present (would mean composition ALSO degrades when fed noisier/larger candidate sets than the clean ORACLE condition — a genuinely new finding that would require revisiting the composition mechanism itself, not just retrieval).
- **MIDDLE:** 60-90% — composition mostly holds but shows some degradation from noisier real candidate sets vs. the clean ORACLE condition; worth a follow-up on composition robustness to distractor density.
- P_deflated = 0.50 (novel-synthesis cap; this is a prediction about an untested interaction between two previously-separate findings).

**Total cost estimate for all 3 experiments: 1-2 days CPU-only, no GPU, no external LLM, no new benchmark data needed** (reuses the RAG-composition SMOKE's own failed queries and the existing KGStore) — this is the cheapest possible discriminative path before any production engineering commitment.

---

## Part 4 — Answer: swap encoder, fine-tune, or neither?

**Neither swap nor fine-tune alone fixes the RAG-composition HARD_FAIL — this is an architecture problem, not an encoder-quality problem**, and this drill's hybrid-retrieval literature (Part 1.C) directly confirms the general finding from the prior 2026-07-03 encoder-evaluation drill: no single-vector encoder in the current landscape (through Qwen3-Embedding-8B, NV-Embed-v2) crosses the compositional/multi-hop ceiling — the mechanism that fixes bridge-surfacing is structural (graph-walk), not a better embedding.

- **Is bge good enough?** Yes, for its actual job (hop-1 candidate generation / sensory input) — this was already established (r@5=0.992 on Wikipedia single-hop, near-ceiling). No amount of encoder swapping fixes bridge-surfacing because the failure mode is structural (single-vector similarity cannot represent "this chunk complements that chunk"), confirmed independently by this drill's Axis-C literature (dense-only retrieval structurally cannot reach disconnected bridge entities regardless of encoder quality) and the prior drill's Axis on compositional ceilings.
- **Should we still swap to stella_en_1.5B_v5 or arctic-embed-l-v2.0?** That recommendation stands on its OWN merits (license, 512-token truncation risk, Matryoshka flexibility) from the prior 2026-07-03 encoder drill — it is orthogonal to and does not substitute for the architecture fix recommended here. Do both; don't expect the swap to fix bridge-surfacing.
- **Should we fine-tune?** Worth doing LATER, as a second-order lift on top of the architecture fix, not instead of it. Published fine-tuning studies (GPL: up to +9.3 nDCG@10; REFINE: +5.76 to +6.58pp Recall@3 on small-corpus fine-tunes, with the LARGEST gains specifically on structured/tabular content where "vanilla BGE struggled") show a moderate (+3-9pp), not transformative, lift — and REFINE's finding that structured data benefits most maps directly onto the substrate's 170K atom records (analogous to REFINE's tabular subset). Recipe if pursued: no manual labels needed — LLM-generate synthetic queries per record (170K atoms + 100K Wikipedia facts → 300K-800K triplets, matching GPL's demonstrated data volume), mine hard negatives via BM25∩dense-retriever union, full fine-tune with frozen-model interpolation regularization (REFINE's overfitting-avoidance technique for small-corpus regimes). Single-GPU, not multi-day.

---

## Falsifiable predictions (HARD-PASS + HARD-FAIL) — top-level

### Prediction 1: graph-walk over the existing KGStore recovers a meaningful fraction of the RAG-composition SMOKE's missed bridge chunks
- HARD-PASS: Experiment 2 clears ≥ 50% recovery (see above)
- HARD-FAIL: < 15% recovery
- P_deflated = 0.45

### Prediction 2: composition F1 was never the bottleneck — feeding correct candidates (via graph-walk) restores near-ORACLE performance
- HARD-PASS: Experiment 3 clears ≥ 90% of ORACLE=0.783
- HARD-FAIL: < 60% of ORACLE even with correct candidates present
- P_deflated = 0.50 (novel-synthesis cap)

### Prediction 3: the graph-walk lift is regime-selective (large on structurally-disconnected bridge queries, ~zero on already-dense-solvable queries), NOT a uniform multi-hop fix
- HARD-PASS: stratifying Experiment 2's results by query subtype (lexically-connected vs disconnected hops) shows the BridgeRAG pattern replicates — most of the recovery concentrated in the disconnected subtype
- HARD-FAIL: recovery is uniform across subtypes, or (per the documented HotpotQA negative case) shows no correlation with subtype at all
- P_deflated = 0.50 (this is the single most literature-corroborated claim in the drill — two independent papers, BridgeRAG and the weighted-hypergraph/HotpotQA negative case, both point to selectivity — but capped at novel-synthesis ceiling since applying it to the substrate's own query distribution is untested)

---

## Cross-thread synthesis

This drill directly operationalizes the standing composite ruling (commit f2eba7d69, 2026-07-03): "rerank architecture NOT validated; substrate composition WORKS when fed correctly (ORACLE 0.783); bottleneck is retrieval not composition; iterative retrieval or query decomposition is production path forward." It also directly extends the same-day selector-vs-reranker drill (`research_substrate_as_selector_vs_llm_reranker_theoretical_empirical_2026-07-03.md`), whose Axis 4 (COGS/CFQ/MetaQA hop-scaling, Shaw et al. 2021's explicit-structure-wins regime boundary) and the never-executed HRR-binding-chain design (2026-06-11) both anticipated exactly the finding formalized here — that structured/graph methods decisively win specifically at hop-count ≥ 2 with reasonably complete relational coverage. That drill flagged the design as "ready-to-dispatch" but focused on true VSA bind/unbind chains for EXPLICIT template structure; this drill's contribution is narrower and more immediately actionable: the substrate does not need to wait for a full HRR-binding-chain redesign — its EXISTING KGStore (already in production for the Director-KB itself, unrelated to the HotpotQA cell) is directly reusable as the graph PPR/GraftNet/PullNet-class methods traverse, with a much cheaper PPR-only first cut before any trained-scorer (PullNet-style) upgrade is needed.

It also directly extends the prior 2026-07-03 encoder-evaluation drill (`research_best_retrieval_encoder_evaluation_2026-07-03.md`), confirming from an independent literature angle (hybrid/graph retrieval, not compositional-generalization benchmarks) the same structural conclusion: no encoder swap crosses the compositional ceiling; the differentiator is architecture, not encoder quality. Two independent literature axes (compositional-generalization benchmarks in the selector drill; graph/hybrid retrieval benchmarks in this drill) now corroborate the same regime-boundary claim, satisfying 2x-drill discipline.

---

## Substrate-product implications

1. Do not frame this as "add a RAG library feature" — frame it as "extend the KGStore the Director-KB already runs on with an iterative-hop traversal policy." This is genuinely lower-lift than building new graph infrastructure from scratch, and keeps the substrate-native discipline intact (PPR is linear algebra; entity-match is the existing char-trigram encoder).
2. The three cheap experiments (Part 3) are CPU-only, reuse existing failed-query logs and the existing KGStore, and require no new benchmark data or GPU dispatch — this should be the very next exp_dev cycle's anchor rather than a full production build.
3. Expectation-setting: per Prediction 3, do NOT expect this to uniformly fix all multi-hop retrieval — expect it to fix the specific structurally-disconnected-bridge-entity subclass that the RAG-composition SMOKE exhibited, while leaving already-dense-solvable queries unchanged. Report results stratified by query subtype, not as a single aggregate recall number, to avoid the HotpotQA-negative-case failure mode (aggregate coverage improving while F1 doesn't move).
4. The cortex layer's routing decision (dense-frontend vs. substrate-native graph-walk) now has a concrete, cheap, substrate-computable trigger condition (entity-coverage gap in hop-1 candidates) rather than an open design question.

---

## Citations (verified count)

**~30 distinct sources** surfaced across the 4 parallel lit-scans this pass (see each sub-agent's report for full per-claim sourcing); key ones:
1. IRCoT — Trivedi et al., arXiv:2212.10509
2. IterDRAG — Yue et al., arXiv:2410.04343
3. Self-RAG — Asai et al., arXiv:2310.11511
4. DecomP — Khot et al., arXiv:2210.02406
5. BridgeRAG — arXiv:2604.03384 (2026)
6. MDR — Xiong et al., arXiv:2009.12756
7. Beam Retrieval — arXiv:2308.08973
8. GoldEn Retriever — Qi et al., arXiv:1910.07000
9. Baleen — Khattab et al., arXiv:2101.00436
10. SplitQA / ComplexWebQuestions — Talmor & Berant 2018, arXiv:1803.06643
11. STAGG — Yih, Chang, He, Gao 2015, ACL P15-1128
12. QDMR/Break — Wolfson et al. 2020, arXiv:2001.11770
13. DecompRC — Min et al. 2019, ACL (github shmsw25/DecompRC)
14. GraftNet — Sun et al. 2018, arXiv:1809.00782
15. PullNet — Sun et al. 2019, arXiv:1904.09537
16. PRA — Lao et al., arXiv:1404.3301
17. HippoRAG — arXiv:2405.14831 (NeurIPS 2024)
18. GraphRAG — Microsoft, arXiv:2404.16130 (caveat: one comprehensiveness/EM figure circulating for this paper could not be independently confirmed — flagged unverified, not cited as fact above)
19. DyVo — arXiv:2410.07722
20. RRF/hybrid WANDS eval — ceur-ws.org Vol-4173/T3-7
21. Evidence-coverage study (2WikiMultiHopQA dense-vs-lexical@k) — arXiv:2606.06758
22. GPL — Wang et al., arXiv:2112.07577
23. NV-Retriever — arXiv:2407.15831
24. LoRA vs full-FT retrieval — arXiv:2410.21228
25. Domain-matched pretraining (DPR-PAQ-adjacent) — arXiv:2107.13602
26. coCondenser — arXiv:2108.05540
27. REFINE (BGE fine-tune case study) — arXiv:2410.12890

One quantitative claim (GraphRAG "86% vs 57% comprehensiveness / EM 0.392→0.474") is explicitly flagged UNVERIFIED — could not be confirmed against the primary source, possibly conflated with a different comparison paper; excluded from any HARD-PASS/HARD-FAIL threshold above.

---

## P_deflated summary

| Claim | P_deflated | Deflation rationale |
|---|---|---|
| Architecture A (MDR/Beam Retrieval/GoldEn Retriever LLM-free iterative hop-trigger) transfers to substrate | 0.55 | strong external precedent, deflated for substrate-transfer (untested on KGStore) |
| Architecture B (STAGG/GraftNet/PullNet graph-walk decomposition) transfers to substrate's existing KGStore | 0.55 | strong precedent but on denser/more-complete KGs than the substrate's 170K-atom store |
| Architecture C (BridgeRAG/HippoRAG-style graph-walk seeded by dense hits) recovers bridge chunks | 0.45 | on-point precedent but explicitly narrow/selective per BridgeRAG's own ablation + documented HotpotQA negative case |
| Combined architecture (B backbone + A trigger + C seeding) is the correct production recommendation | 0.50 (capped) | synthesis judgment across three literatures, not a single measured fact — capped at novel-synthesis ceiling |
| Composition F1 recovers to near-ORACLE once correct candidates are supplied | 0.50 (capped) | untested interaction between two previously-separate findings (ORACLE result + graph-walk recall) |
| Fine-tuning bge-class encoder on substrate corpus yields +3-9pp lift, largest on structured atom records | 0.50 | consistent published pattern (GPL, REFINE) but not yet locally measured on this specific corpus |

**Novel-synthesis P capped at 0.50 per [[feedback-lit-scan-calibration-penalty]].**
