# exp_dev hand-off -- research: substrate Wikidata ingest optimization

**Filed:** 2026-06-09 by research sub-agent.

**Trigger:** Research drill `notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md` found 5 concrete actionable encoding anchors for Wikidata ingest into FHRR substrate. Anchors are grounded in VSA/HDC literature (Plate 1995, HolE 2016, GHRR 2024, PathHD 2025). Each anchor has a cheap decisive test, HARD-PASS and HARD-FAIL bands.

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching; these are local CPU anchors (WD-1 through WD-3) and light GPU (WD-4, WD-5); all pass the small-scale-first methodology (rung-1 scale, <30 min wall each).

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### WD-1: Q-code atomic symbol ingest with per-predicate sharding

**Anchor pointer:** Research note Section 2 (encoding architecture) + Section 7 (Anchor WD-1).

**Substrate-product reading:** This is the foundational ingest architecture decision. If per-predicate sharding with Q-code atomic symbols gives precision@1 > 0.80 on a 1M-triple P31 slice, the full Wikidata ingest path is structurally validated. Failure (< 0.50) means the per-predicate bundles are over-filled and sub-sharding by entity type is required before full ingest.

**Tier hint:** Local CPU / Remote CPU. No GPU required. Ingest 1M triples from P31 slice of truthy dump, generate FHRR vectors from Q-code hash seeds, build per-predicate bundle, evaluate 1K held-out queries. Wall time estimated <30 min.

**Why now:** This is the gate for all other WD anchors. Without validating the encoding architecture at small scale, full ingest is premature per [[feedback-small-scale-first-methodology]].

---

### WD-2: 1-bit bundle compression validation

**Anchor pointer:** Research note Section 5 OPT-3 + Section 7 Anchor WD-2. PP-200 1-bit quantization applied to per-predicate bundles from WD-1 output.

**Substrate-product reading:** PP-200 is already validated for substrate's core storage layer. This anchor validates that the same 1-bit mechanism preserves retrieval fidelity for KG triple bundles, which have different distributional properties than the memory-storage use case. Success opens the path to 16x memory reduction on the full Wikidata bundle store (640 MB float32 -> 40 MB 1-bit).

**Tier hint:** Local CPU. Requires WD-1 bundle output. Binarize bundles, re-run query eval, compute relative precision. Wall time <5 min after WD-1.

**Why now:** Immediately follows WD-1 in the pipeline; cheap validation of a high-value storage optimization.

---

### WD-3: Lazy label resolution warmup benchmark

**Anchor pointer:** Research note Section 4 + Section 7 Anchor WD-3.

**Substrate-product reading:** The label resolution strategy determines whether Wikidata becomes a live query-answering layer or a batch-lookup system. If warm-cache resolution is <1ms, substrate can answer natural-language entity queries (resolved at query time) without pre-loading 6 GB of label data. If cold-cache resolution exceeds 10ms, pre-warmup of top-1M entities becomes mandatory.

**Tier hint:** Local. No GPU. Load English labels for top-1M Wikidata entities by Wikipedia link count (available from wikistats or precomputed frequency tables). Benchmark cache hit rate and latency on 10K synthetic queries sampled from the Zipf distribution.

**Why now:** Design decision for the query layer that affects v1 demo architecture. Needs to be resolved before full ingest to avoid retrofitting.

---

### WD-4: 2-hop GHRR path index validation

**Anchor pointer:** Research note Section 2 (Step 4) + Section 5 OPT-2 + Section 7 Anchor WD-4. Uses GHRR binding (arXiv:2405.09689) with b=32 blocks.

**Substrate-product reading:** Multi-hop retrieval is the key capability differentiator for the substrate vs. flat vector indexes. PathHD achieved 86.2% Hits@1 on WebQSP using GHRR path encoding at N=8192. If substrate achieves >0.65 precision@1 on 2-hop Wikidata queries, this directly supports the multi-hop revive priority (memory: PROJECT: MULTI-HOP REVIVE PRIORITY) and provides a new retrieval primitive that LLMs of relative size cannot match without search.

**Tier hint:** Remote CPU or local GPU. Requires GHRR implementation (Yeung 2024; block-diagonal complex multiplication). Pre-encode 500 common 2-hop relation chains from WD-1 output. Build path index. Evaluate 1K 2-hop queries. Wall time <2 hours if GHRR binding is not already implemented; <15 min if it is.

**Why now:** This is the highest-differentiation anchor. PathHD is the strongest empirical precedent for multi-hop revival; substrate at N=8192 should match or exceed it with native FHRR alignment. Empirical confirmation here would be a strong capability signal.

---

### WD-5: Bitemporal qualifier encoding

**Anchor pointer:** Research note Section 5 OPT-5 + Section 7 Anchor WD-5. Permutation-based temporal encoding of P580/P582 qualified triples.

**Substrate-product reading:** Temporal versioning of facts is a differentiating feature (PP-154 alignment). Most KG embeddings and LLM-based systems treat facts as timeless; substrate can natively encode the valid-time dimension via permutation operators. Success here enables "what was true in year T" queries as algebraic operations.

**Tier hint:** Local CPU. Requires a 500-triple held-out test set of temporally-versioned Wikidata facts (e.g., head of government changes over time). Implement permutation encoding, compare temporally-keyed retrieval precision vs. unkeyed baseline.

**Why now:** Lower priority than WD-1 through WD-4; schedule after those anchors are resolved. But included here because bitemporal encoding is architecturally orthogonal and can be validated independently on a small synthetic test.

---

## Context pointers

- Research note: `d:/AI/hd-instrument/notes/research_drill_substrate_wikidata_ingest_optimization_2x_2026-06-09.md`
- GHRR paper: arXiv:2405.09689 (Yeung et al. 2024)
- PathHD paper: arXiv:2512.09369 (Sun et al. 2025)
- Plate 1995 HRR: https://redwood.berkeley.edu/wp-content/uploads/2020/08/Plate-HRR-IEEE-TransNN.pdf
- Wikidata truthy dump: https://www.wikidata.org/wiki/Wikidata:Database_download
- Multi-hop revive: memory file `project_multihop_revive_priority.md`
- PP-200 1-bit quantization: existing substrate implementation (no external ref needed)
- Per-strength sharding: PP-127/131/132/147 existing substrate implementation

---

## Contract

exp_dev picks which of WD-1 through WD-5 to dispatch based on queue state, current authorized experiments, and pause flag. All anchors are structured to pass the pre-dispatch speed+harden+progress discipline (memory: feedback_pre_dispatch_speed_harden_progress_discipline.md). WD-1 is the gate anchor; WD-2 and WD-3 depend on WD-1 output; WD-4 is independent; WD-5 is independent.

## Autonomy declaration

exp_dev has full autonomy on: anchor naming, N choice (must be >=4096 for 1-bit to hold per literature), block size b for GHRR, seed count, queue assignment, threshold band calibration, smoke vs. full profile decision, and implementation approach for GHRR binding. Orchestrator does not pre-specify any numerical parameter.
