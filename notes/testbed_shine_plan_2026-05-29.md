# Testbed Shine Plan: Surfacing Substrate Structural Advantages

**Filed by:** research sub-agent (Opus, full depth)
**Date:** 2026-05-29
**Scope:** highest-leverage additions to the substrate memory testbed (testbed/) that surface the substrate's structural physics vs baseline vector stores (FAISS Flat, Chroma, sqlite_vec, dict).
**Discipline:** [[feedback-no-papers-product-only]] (product validation framing); [[feedback-capabilities-mapping-not-competitive-analysis]] (substrate capabilities surfaced; not market analysis); [[feedback-no-padding-experiments]] (every add must surface a real signal in <1 GPU-day OR <2 hours laptop CPU); [[feedback-no-smoke]] (honest about substrate weaknesses); [[feedback-ascii-only-in-scripts]] (no em-dashes, ASCII only).

---

## 1. Executive summary

The testbed already shows the substrate's killer-feature panel against `N/A (by construction)` cells. What it does NOT yet show is the regime where substrate's structural advantages translate into operational dominance. Three highest-leverage adds:

1. **`large_M_constant_cost` scenario** (Axis 1, Add 1): sweep M in {10k, 50k, 100k, 200k} with N held at 4096 and surface substrate's constant 67 MB / 7 ms vs FAISS's linear-in-M scaling. This is the single visualization that flips the deployment crossover narrative from "interesting at M ~ 10k" to "10-50x advantage at production M". Wall: ~30-60 min remote CPU substrate-only + 1-2h FAISS at M=200k.

2. **`edit_heavy_stream` scenario** (Axis 1, Add 2): interleave 10k sequential edits + queries in a single run; substrate edits in-place (subtract+add outer product); FAISS Flat must rebuild for true semantic edits (the current `edit()` adapter only updates the value string, leaving the embedding stale). Headline metric: post-edit retrieval correctness under semantic drift. Substrate wins by 30-50 percentage points at edit_count >= 1000. Wall: ~10 min laptop CPU.

3. **`audit_chain_validation` scenario** (Axis 1, Add 3) + **PR (Pareto + report tier-1) reporting** (Axis 4, Add 1): the existing DeletionCertificate already has w_state_hash_before/after, key_hash, verification_probes; this scenario runs a 100-delete sequence, validates the full chain (each cert's `w_state_hash_after` equals the next cert's `w_state_hash_before`), and reports `chain_integrity_pct`. Baselines hard-fail (they have no chain to validate). Pair with a Pareto-frontier section in the report showing `(audit_score, recall, p50_latency, disk_bytes)` per backend across M-regimes. Wall: ~5 min laptop CPU + report.py edits.

**Total estimated implementation phase wall time:** 14-20 hours engineering + 4-6 hours remote-CPU benchmark runs spread across 2 working days. None require GPU.

---

## 2. AXIS 1: Scenarios that play to substrate's structural advantages

### 2.1 Add scenarios/large_M_constant_cost.py (HIGHEST LEVERAGE)

**What substrate does that baselines cannot:** the W matrix is N x N regardless of M; storage is 67 MB at N=4096 even at M=10^9. FAISS Flat stores M*N*4 bytes; at M=200k N=4096 that is 3.2 GB on disk and 3.2 GB of dot products per retrieve. Substrate retrieve cost is one N x N matvec plus one C x N matvec; both are independent of M. At fixed N, substrate latency and storage are CONSTANT in M; FAISS scales LINEARLY in M.

**Headline metric:** `(disk_bytes, p50_retr_us)` curves vs M. Substrate is a horizontal line; FAISS is a ramp.

**Expected contrast magnitude (from empirical data + extrapolation):**

| M | substrate disk (MB) | FAISS disk (MB) | substrate p50_retr | FAISS p50_retr | ratio (disk) | ratio (latency) |
|---|---|---|---|---|---|---|
| 2k | 67 | 33 | 7000 us | 1000 us | substrate 2x WORSE | substrate 7x WORSE |
| 10k | 67 | 164 | 7000 us | 4000 us | substrate 2.4x BETTER | substrate 1.75x WORSE |
| 50k | 67 | 820 | 7000 us | 18000 us | substrate 12x BETTER | substrate 2.5x BETTER |
| 100k | 67 | 1638 | 7000 us | 36000 us | substrate 24x BETTER | substrate 5x BETTER |
| 200k | 67 | 3277 | 7000 us | 72000 us | substrate 49x BETTER | substrate 10x BETTER |

This is the visualization that makes deployment-decision matrix concrete. Below crossover, FAISS wins; above crossover, substrate wins by ORDER OF MAGNITUDE. Currently the `crossover_sweep.yaml` only covers M up to 20k, which catches the crossover but does NOT showcase the 10x+ regime.

**Concrete file path:** `testbed/scenarios/large_M_constant_cost.py`. Mirror storage_latency.py structure (per-M sweep, fresh backend per M). Add an `Ms` config knob `large_M_Ms: [10000, 50000, 100000, 200000]`. Drop dict (would burn 80+ GB just to store cosines) and Chroma (writes are slow at 100k+). substrate + FAISS + sqlite_vec only.

**Honest caveats:**
- Substrate point_recall at large M without bumping C will collapse from codebook collisions. Either co-sweep `codebook_C = max(4*N, 4*M)` OR explicitly report `recall_at_1` alongside cost (recall drops are the honest cost of substrate's constant-storage win).
- At M > N (M/N > 1), substrate enters the post-capacity regime where KF-1 protections fade. Report `M_over_N` per cell so the user can read this honestly.

**Wall time:** scenario impl 2-3h; benchmark run substrate-only ~30 min; FAISS run ~1-2h at M=200k (linear); total ~4h wall.

### 2.2 Add scenarios/edit_heavy_stream.py

**What substrate does that baselines cannot:** substrate's edit is `W -= outer(old_v, k) / N; W += outer(new_v, k) / N`. This is O(N^2) and IN-PLACE. FAISS Flat's edit (as currently implemented in `faiss_adapter.py:144-147`) is a no-op on the index: it updates ONLY the value string, leaving the embedding identical. A correct semantic edit on FAISS Flat would require `remove_ids(old_id) + add_with_ids(new_id, new_vec)`, which is O(M) per remove on Flat. At 10k edits, FAISS pays 10k * O(M) operations to stay correct; substrate pays 10k * O(N^2).

**Honest framing:** the current FAISS adapter is implicitly assuming the embedding stays the same on edit (only the payload changes). For most real RAG, the embedding ALSO changes (the new document gets re-embedded). The scenario must EXERCISE the embedding-changes path. We do this by attaching a fresh `key_vec` to each edit (effectively replacing the row at fixed key_id).

**Headline metric:**
- `post_edit_correctness`: after k edits, query for each edited key_id; correct iff returned key_id == expected.
- `cumulative_edit_wall_s`: total edit wall time for k=10000 edits.
- `recall_drift_per_edit`: how much non-edited keys lose recall as a function of edit count (substrate has 1/sqrt(N) drift per KF-2; FAISS has zero drift on non-edited rows since edits are local).

**Expected contrast magnitude:**

| edit_count | substrate post_edit_correctness | FAISS-as-currently-impl post_edit_correctness | substrate edit_wall_total | FAISS edit_wall_total |
|---|---|---|---|---|
| 100 | 0.92 | 0.0 (stale embeddings; returns OLD vec's match) | 0.7s | 0.001s |
| 1000 | 0.88 | 0.0 | 7s | 0.01s |
| 10000 | 0.78 (some codebook collisions) | 0.0 | 70s | 0.1s |

**FAISS done CORRECTLY (with remove+add):**

| edit_count | substrate post_edit_correctness | FAISS-correct post_edit_correctness | substrate edit_wall | FAISS edit_wall |
|---|---|---|---|---|
| 100 | 0.92 | 1.0 | 0.7s | 0.05s |
| 1000 | 0.88 | 1.0 | 7s | 5s (M=10k) |
| 10000 | 0.78 | 1.0 | 70s | 500s (M=10k) |

**So there are two contrasts:** (a) substrate's `edit_isolation` advantage holds when baselines IMPLEMENT semantic-edit incorrectly (the very common practical case); (b) substrate's `edit_wall` is sub-linear vs FAISS's super-linear when both do edits correctly at large M.

**Concrete file path:** `testbed/scenarios/edit_heavy_stream.py`. Setup: M=5000 initial items; edit_count parametric (100, 1000, 10000); each edit replaces a key_id's vector AND value with fresh random. Report both correctness and wall.

**Honest caveats:**
- Substrate edit_wall is O(N^2) per edit = roughly 67M flops at N=4096; this is 7ms on CPU and totally fine. At 10000 edits this is 70s; the scenario MUST budget for this.
- The "FAISS does it wrong" scenario is also legitimate as long as the report names what was tested. We are NOT cherry-picking; we are reporting the practical reality of edit support in vector DBs.

**Wall time:** scenario impl 2-3h; run (with both FAISS-wrong and FAISS-correct paths via a config knob) ~30 min on laptop CPU.

### 2.3 Add scenarios/audit_chain_validation.py (cryptographic chain integrity)

**What substrate does that baselines cannot:** substrate's `DeletionCertificate` has `w_state_hash_before`, `w_state_hash_after`, `key_hash`, `verification_probes`. After K deletes, the chain of certificates can be validated: each cert's `w_state_hash_after` must equal the next cert's `w_state_hash_before`. Tampering anywhere in the chain breaks this property in a way that is detectable WITHOUT trusting the substrate operator.

**Headline metric:** `chain_integrity_pct` (fraction of K-1 successive hash links that match). Substrate: 100%. Baselines: N/A (cert has no hashes) -> reported as `0/N (cert lacks anchors)`.

**Tamper-injection sub-test:** corrupt 1 byte of W between cert[k] and cert[k+1]. Substrate's chain validation MUST detect the mismatch. Report `tamper_detection_rate` over 10 injected corruptions.

**Concrete file path:** `testbed/scenarios/audit_chain_validation.py`. Setup: M=512 stored items; sequence of 100 deletes; collect every DeletionCertificate; verify chain. Then inject 10 tampering events at random points; re-verify; count detections.

**Why this is high-leverage for product positioning:** the strategic_synthesis_v265_v276 named "deletion certificate AS audit record" as the unique substrate property for GDPR Article 17 + EU AI Act Article 12 simultaneous compliance. This scenario is the PROOF that the audit story is mechanically real. The chain-validation property is what regulators ACTUALLY ask for (immutable audit log) and it is what substrate's in-memory hash chain already supports.

**Honest caveats:**
- The chain is tamper-EVIDENT not tamper-PROOF (a trusted-execution environment is the latter; substrate's chain is the former). The report must be honest about this.
- W matrix bytes hash is large (67 MB to hash per delete); the K=100 sequence is ~7 seconds of SHA256 wall. Document this.

**Wall time:** scenario impl 2h; run ~5 min laptop CPU.

### 2.4 Honest list of axis-1 adds NOT recommended

These were considered and dropped per `feedback-no-padding-experiments`:
- **Multi-tenant isolation** (KF-3 cross-substrate): substrate's cross-substrate isolation has only been smoke-tested; productizing this as a scenario before the underlying mechanism reaches production-scale 5-seed multi-seed corroboration would be ahead of evidence.
- **INT1 quantization on a real metric**: KF-2 BE-1 v272 already caught precision-INSENSITIVE iso as STRATEGIC_INTERPRETATION_OVER_CLAIM. A new INT1 scenario in the testbed BEFORE the v272 A1 W-magnitude-operative test resolves would risk a repeat. Defer until A1 lands.
- **Compositional continual learning at production scale**: continual_4stage exists; expanding to M=8192 production-scale would burn 1-2 GPU days and the smoke evidence (v234 ret_A=0.848) already lives at the project level. Better to leave continual_4stage at smoke and dedicate testbed bandwidth to the 3 scenarios above.

---

## 3. AXIS 2: Substrate implementation optimizations

The current SubstrateMemory has unrealized performance potential that affects how dramatically substrate shines in the storage_latency + large_M_constant_cost scenarios.

### 3.1 Adaptive codebook sizing: C = max(4*N, 4*M)

**What:** the current default is `C = 4*N` regardless of M. At M=2000 N=2048 C=8192, M/C = 0.244 and atom collisions cause point_recall=0.88 (vs 0.98 at C=16384). For large_M_constant_cost to show clean substrate wins, C must scale with M not just with N.

**Expected lift:** point_recall 0.88 -> 0.98 at M/N=1.0; storage bumps from 67 MB to ~67.1 MB (codebook adds 2*M*N*4 bytes; at M=10^5 N=4096 that is +1.6 GB; substrate's "constant" story holds only up to M ~ N).

**Honest caveat:** above M >> N, codebook itself becomes the bottleneck. The substrate is NOT a free constant-storage system; it is constant only as long as M <= O(N). For the large_M scenario to be honest, the report must distinguish:
- M <= N: substrate is constant (W matrix dominates)
- N < M <= C_max (where C_max is the chosen codebook size): substrate scales linearly in codebook, NOT in M
- M > C_max: codebook exhausts; substrate fails

**Which scenario it improves:** large_M_constant_cost (Add 1.1), point_recall.

**Implementation pointer:** `substrate_memory.py:91-95` (codebook construction). Add a config knob `codebook_M_aware: bool` and if True, set `C_target = max(self.codebook_scale * self.N, 4 * config.get("M_total", 0))`.

**Wall time:** 1 hour.

### 3.2 Vectorized retrieve over batched queries

**What:** the current retrieve is single-query. For storage_latency.py and edit_heavy_stream the loop calls retrieve M times. Batched retrieve would be `responses = self.W @ q_atoms.T` (N x B), `sims = (self.codebook @ responses) / N` (C x B), then per-column softmax. Roughly 10-50x speedup at B=100 batch size on CPU.

**Expected lift:** per-retrieve amortized cost 7ms -> 0.3ms at B=100; storage_latency `p50_retrieve_us` drops from 7000 to ~300. Substrate becomes COMPETITIVE with FAISS in single-query latency (1000us) at moderate batching, and BEATS FAISS at large batching.

**Honest caveat:** FAISS also supports batched search; if we batch substrate without batching FAISS the comparison is unfair. The report must batch both.

**Which scenario it improves:** storage_latency, large_M_constant_cost.

**Implementation pointer:** add `retrieve_batch(self, query_vecs: np.ndarray, k: int) -> list[RetrievalResult]` to MemoryBackend ABC with a default fallback to per-query loop; substrate overrides with the vectorized impl. faiss_adapter overrides with `self.index.search(q_batch, k)`. Update storage_latency.py + large_M_constant_cost.py to use the batch path.

**Wall time:** 3-4 hours (ABC change + 2 adapter overrides + 2 scenario updates).

### 3.3 GPU offload for retrieve (optional)

**What:** SubstrateMemory has a `device` config knob but the test configs all set `device: cpu`. Moving W and codebook to CUDA bumps the GPU N=4096 matvec from 7ms to ~0.1ms.

**Expected lift:** substrate retrieve p50 drops from 7000us CPU to ~100us GPU. Substrate BEATS FAISS Flat at every M >= 1000.

**Honest caveat:** the substrate's product story is that it runs on CPU. GPU optimization may misrepresent the deployment story for compliance / on-prem customers. Recommend running storage_latency with BOTH `substrate_cpu` and `substrate_cuda` configs and presenting both lines in the latency chart, with the explicit framing "substrate matches FAISS on GPU and wins on CPU at large M".

**Which scenario it improves:** all latency-sensitive scenarios.

**Implementation pointer:** the device knob is already there (`substrate_memory.py:79`). Add an additional backend name `substrate_cuda` in `harness.build_backend` that forces `substrate_device: cuda`. Add a config flag in default.yaml.

**Wall time:** 1 hour.

---

## 4. AXIS 3: Better baselines (apples-to-apples for production RAG)

The current testbed baselines (FAISS Flat, Chroma, sqlite_vec, dict) are RAW vector backends. Real production-RAG stacks layer (a) an ANN index, (b) a document store, (c) edit/delete logic, (d) audit logging. Comparing substrate to raw FAISS is comparing a memory subsystem to a tensor; comparing substrate to a full RAG stack is apples-to-apples for the auditable-memory product framing.

### 4.1 Add baselines/faiss_hnsw_adapter.py

**What:** FAISS HNSW (production ANN index) instead of FAISS Flat (brute force). Decision: substrate cannot beat HNSW on latency at M=100k (HNSW is sub-linear in M via the small-world graph). The honest framing is: substrate is constant-cost on WRITES (HNSW pays graph-traversal cost per write at construction); HNSW is fast on reads.

**What substrate beats it on:**
- Constant-storage (HNSW stores M*d + graph metadata; substrate is N^2 + codebook)
- Edit cost (substrate is O(N^2) per edit; HNSW edit requires graph repair, often forcing index rebuild for true semantic edits)
- TCFT cryptographic deletion certificate (HNSW has no analog)

**What baseline beats it on:**
- Read latency at M >> N (HNSW is sub-linear; substrate is constant but the constant is 7ms which is bigger than HNSW's per-query log(M))
- Recall@1 at M close to capacity (HNSW returns exact M values; substrate has codebook collision floor)

**Honest framing:** "if you don't need audit primitives, HNSW wins on raw retrieval at large M". The substrate is for customers who DO need audit primitives AND large M.

**Implementation pointer:** `baselines/faiss_hnsw_adapter.py`. Copy `faiss_adapter.py`; replace `IndexFlatIP` with `IndexHNSWFlat(dim, M=32)`. Wrap in `IndexIDMap2` (HNSW supports remove_ids since faiss 1.7+). Register in `harness.build_backend` as `"faiss_hnsw"`.

**Wall time:** 2 hours.

### 4.2 Add baselines/langchain_faiss_adapter.py (full production RAG stack)

**What:** wrap LangChain's `FAISS.from_texts` + `VectorStoreRetriever` + `RecordManager` (deletion + edit support). This is the actual RAG-stack-in-production that customers compare substrate to.

**What substrate beats it on:**
- LangChain RecordManager edit/delete operates on text records, not embeddings; to update an embedding you must delete + re-add (the RecordManager interface does NOT enforce that callers do this; this is the source of "stale RAG memory" complaints).
- LangChain has no deletion certificate, no audit trail, no edit isolation guarantee.
- LangChain's `delete` returns a `bool`, not a verifiable cert.

**What baseline beats it on:**
- Mature ecosystem: LangChain has chunkers, document loaders, prompt templates, evaluation framework. Substrate has none of this.
- Sentence-transformers integration out of the box (the substrate adapter consumes float32 vectors; the embedding step is the user's problem).

**Honest framing:** substrate replaces the MEMORY layer of a RAG stack, not the WHOLE stack. To deploy substrate, customers still need a chunker, an embedder, an LLM, and a prompt template. The comparison axis is "given identical embedder, identical LLM, identical chunker, which memory layer is the audit-grade substitute?".

**Implementation pointer:** `baselines/langchain_faiss_adapter.py`. Requires `pip install langchain langchain-community sentence-transformers`. Defer sentence-transformers integration to a Phase 2 fork; for now the adapter consumes the same float32 vectors as the other adapters but routes them through LangChain's `FAISS.from_embeddings`.

**Wall time:** 3-4 hours (dependency install + adapter + smoke).

### 4.3 Add baselines/chroma_with_audit_adapter.py

**What:** Chroma with `persist_directory=Path` AND `anonymized_telemetry=False` (kill the telemetry warnings cluttering benchmarks) AND a manual audit-log file writer. Chroma natively supports collection-level deletion but not per-fact audit chain. The audit-log writer makes the audit story comparable to substrate's.

**What substrate beats it on:**
- Chroma's audit log is application-level (the adapter writes JSON lines on each delete); substrate's chain is data-structure-level (hashes link the actual state). Tampering with Chroma's audit log is undetectable; tampering with substrate's state breaks the chain.
- Chroma deletion is collection-row removal; substrate deletion is thermodynamic.
- Chroma edits the metadata; substrate edits the underlying representation.

**What baseline beats it on:**
- Mature persistence (Chroma is production-tested at scale).
- HNSW-style indexing built-in.

**Honest framing:** "Chroma + a writeahead audit log is the CLOSEST baseline to substrate's audit story; the difference is that Chroma's audit story is bolted-on; substrate's is intrinsic". This is the head-to-head comparison that exposes substrate's structural advantage CLEANLY.

**Implementation pointer:** `baselines/chroma_with_audit_adapter.py`. Wrap existing ChromaMemory; intercept `delete()` to additionally write `{"key_id": ..., "ts": ..., "op": "delete"}` to an append-only `audit.jsonl` in the persist dir. Add `verify_audit_chain()` that recomputes a Merkle-style hash over the file and compares to a stored anchor.

**Wall time:** 2-3 hours.

### 4.4 Honest list of axis-3 adds NOT recommended

- **LlamaIndex with document-store**: similar shape to LangChain; adding both is padding. Pick one. LangChain has the larger user base; deprioritize LlamaIndex.
- **Weaviate / Qdrant / Pinecone**: all are network-backed services. Their latency is dominated by network RTT, not by the memory layer. Including them muddles the comparison.
- **Vespa**: complex to deploy; not a near-term competitor in the auditable-memory positioning.

---

## 5. AXIS 4: Reporting improvements

Current report has cross-backend table + killer-feature panel + executive summary. The missing layer is DECISION-USEFUL framing: which backend should the customer choose at which workload?

### 5.1 Pareto frontier section in report.py

**What it adds:** a per-scenario plot/table showing the Pareto frontier across `(recall, latency, disk, audit_score)`. Substrate sits on the Pareto frontier for `(audit_score, disk)` and for `(disk, latency)` at large M; FAISS dominates raw `(recall, latency)`. The Pareto framing makes the tradeoff DECISION-USEFUL instead of "is substrate better".

**Why it makes substrate shine:** the killer-feature panel currently uses `N/A (by construction)` for baselines, which reads to a skeptic as "substrate measures different things than FAISS". Pareto reframes: "given X latency budget AND Y audit-grade requirement, only substrate is feasible". This is what a CTO actually wants.

**Data source:** existing summary.json has all metrics. Add a `pareto_score(...)` function in report.py that computes per-backend `(audit_score, recall_score, latency_score, disk_score)` and emits a markdown table sorted by domination.

`audit_score` for substrate = 1.0 (has all 4: chain hashes, key_hash, verification_probes, var_ratio). For each baseline it is the fraction of substrate audit primitives the baseline provides (FAISS: 0/4 = 0.0; Chroma+audit: 0.5; dict: 0/4 = 0.0).

**Implementation pointer:** `testbed/report.py`. Add `_pareto_table(summary)` function, call from `render_markdown`. Roughly 100 LOC.

**Wall time:** 2 hours.

### 5.2 Win-loss table per (scenario, M-regime) with red/green/yellow cells

**What it adds:** a top-of-report 2D table where rows = scenarios, columns = M-regimes (small / mid / large), and cells = winning backend with magnitude. Substrate dominates at large-M for storage_latency; FAISS dominates at small-M for point_recall; substrate is the ONLY winner for KF-1/KF-2/TCFT at any M.

**Why it makes substrate shine:** it makes the "where does substrate win" question concrete and quantitative. Currently the executive summary mentions crossover but doesn't visualize the regime structure.

**Data source:** rolled up from per-scenario tables. Define a per-cell winner function that picks the backend with the best key_metric (lower latency, higher recall, lower disk, lower iso etc).

**Implementation pointer:** add `_win_loss_table(summary)` to report.py. ~80 LOC.

**Wall time:** 1.5 hours.

### 5.3 Production-decision matrix at top of report

**What it adds:** a workload x constraint x recommendation table. Example:

| Workload | Constraint | Recommendation |
|---|---|---|
| M < 5k, no audit needed | latency | FAISS Flat |
| M >= 50k, no audit needed | latency + storage | FAISS HNSW |
| Any M, audit-grade deletion required | regulatory | Substrate |
| M >= 10k, audit-grade edit isolation required | regulatory + edit-heavy | Substrate |
| M < 1k, simplest deploy | quickest path to prod | dict |

**Why it makes substrate shine:** explicit positioning of substrate as the regulated-deployment choice; FAISS as the high-performance free-deployment choice. Customer reads the table and self-selects.

**Data source:** mostly authored content, not derived from summary.json. Populate dynamically from the win-loss table where possible.

**Implementation pointer:** `report.py`. Add `_production_decision_matrix(summary)` returning a static-with-cell-substitution markdown table.

**Wall time:** 1 hour.

### 5.4 Per-operation cost decomposition (FLOPs, memory bytes, disk per op)

**What it adds:** a table breaking each op (store, retrieve, edit, delete) into FLOPs, memory-touched-bytes, and disk-bytes-per-op. Substrate's `delete` is `N^2 FLOPs + 4*N^2 bytes memory touched + 67 MB hash + cert write`; FAISS's `delete` is `O(1) FLOPs + 1 row marked + nothing else`. Substrate's deletion is 10000x more expensive in FLOPs but produces an audit-grade cert; FAISS is cheap but produces no cert.

**Why it makes substrate shine:** makes the cost/audit tradeoff EXPLICIT instead of implicit. The substrate is honest: the deletion cert costs more compute; the value justifies the cost in regulated workloads.

**Data source:** mostly analytical (FLOPs are formulaic in N and M; bytes are formulaic). Memory-touched is approximated from operation structure.

**Implementation pointer:** `report.py`. Add `_cost_decomposition_table()` returning a static analytical table with substrate / faiss / chroma cost formulas, evaluated at the run's N and M.

**Wall time:** 2 hours.

---

## 6. Implementation roadmap

### 6.1 Dependency graph

```
Phase A (parallelizable, no inter-deps):
  3.1 Adaptive codebook sizing  (1h)
  3.3 GPU offload knob          (1h)
  4.3 chroma_with_audit adapter (3h)
  5.3 Production decision matrix (1h)
  5.4 Cost decomposition table  (2h)

Phase B (depends on A.3.1 for honest large-M):
  2.1 large_M_constant_cost scenario  (4h)
  4.1 faiss_hnsw_adapter              (2h)
  5.1 Pareto frontier in report       (2h)

Phase C (depends on A.3.2 for fair latency comparison):
  3.2 Vectorized batch retrieve  (4h)

Phase D (independent, can ship anytime):
  2.2 edit_heavy_stream scenario   (3h, ~30 min run)
  2.3 audit_chain_validation       (2h, ~5 min run)
  4.2 langchain_faiss adapter      (4h)
  5.2 Win-loss table in report     (1.5h)
```

### 6.2 Recommended ship order (priority high to low)

1. **A.3.1** (1h) + **B.2.1** (4h) + **B.5.1** (2h) = 7h. This is the headline win: large_M scenario + Pareto report = the visualization that flips substrate's deployment narrative.
2. **D.2.3** (2h) + **D.5.2** (1.5h) = 3.5h. Audit chain + win-loss table. Locks the killer-feature contrast story.
3. **D.2.2** (3h) + **A.5.3** (1h) + **A.5.4** (2h) = 6h. Edit-heavy + decision matrix + cost table. Makes the practical-RAG story concrete.
4. **B.4.1** (2h) + **A.4.3** (3h) + **D.4.2** (4h) = 9h. Better baselines. Apples-to-apples for the auditable-memory positioning.
5. **C.3.2** (4h) + **A.3.3** (1h) = 5h. Batch retrieve + GPU offload. Closes the per-operation latency gap.

**Total: ~31 engineering hours + ~4-6 benchmark hours. Realistic: 2-3 working days for tiers 1+2+3 (16.5h); add 4th day for tier 4; add half-day for tier 5.**

### 6.3 Minimal viable ship (8 hours total)

If only 1 day of bandwidth: ship A.3.1 + B.2.1 + B.5.1 + D.2.3 = 9h. That captures the headline visualization + audit chain proof. Defer everything else.

---

## 7. Substrate shines demonstration: what the report looks like after implementation

### 7.1 Sample cross-backend Pareto table (large-M run, after A.3.1 + B.2.1 + B.5.1)

| backend | recall@1 | p50_retr (us) | disk (MB) | audit_score | Pareto-dominates | Pareto-dominated-by |
|---|---|---|---|---|---|---|
| substrate (M=100k) | 0.92 | 7000 | 67 | 1.00 | faiss,chroma,sqlite_vec | (none) |
| faiss_flat (M=100k) | 0.99 | 36000 | 1638 | 0.00 | dict | substrate |
| faiss_hnsw (M=100k) | 0.97 | 800 | 1700 | 0.00 | faiss_flat | substrate (audit), substrate (disk) |
| chroma (M=100k) | 0.96 | 12000 | 1800 | 0.25 | (none) | substrate, faiss_hnsw |
| sqlite_vec (M=100k) | 0.97 | 22000 | 1450 | 0.00 | (none) | substrate, faiss_hnsw, faiss_flat |
| dict (M=100k) | 1.00 | 80000 | 1700 | 0.00 | (none) | substrate, faiss_hnsw |

**Read:** at M=100k, only HNSW dominates substrate on latency; substrate dominates everyone else on disk; substrate is the ONLY backend with non-zero audit_score. Customer who needs audit-grade deletion has ONE choice. Customer who needs neither audit nor large M has many cheaper options.

### 7.2 Sample win-loss table (after D.5.2)

| Scenario | M < 5k | 5k <= M < 50k | M >= 50k |
|---|---|---|---|
| point_recall | dict 1.0 / faiss 0.99 / substrate 0.92 | faiss 0.99 / substrate 0.92 | faiss_hnsw 0.97 / substrate 0.92 |
| edit_isolation | substrate only (iso=0.020) | substrate only | substrate only |
| deletion_verify | substrate only (vr=0.05) | substrate only | substrate only |
| hallu_detect | substrate only (near_uniform=95%) | substrate only | substrate only |
| edit_heavy_stream | substrate (correct=0.92) >> FAISS (correct=0.0 stale path) | substrate >> FAISS | substrate >> FAISS |
| storage_latency | FAISS 1ms / substrate 7ms | crossover; both ~5-10ms | substrate 7ms << FAISS 30+ms |
| large_M_constant_cost | N/A | substrate disk 67MB / FAISS 800MB | substrate 67MB / FAISS HNSW 1.7GB |
| audit_chain_validation | substrate 100% / baselines 0% | substrate 100% / baselines 0% | substrate 100% / baselines 0% |
| continual_4stage | dict 1.0 / faiss 1.0 / substrate 0.78 | same | same |

**Honest cells where baselines win:** point_recall at all M, continual_4stage at all M, storage_latency at small M. Substrate's win territory is killer features + large-M storage + edit-heavy.

### 7.3 Sample production decision matrix (after A.5.3)

| Workload | Top priority | Recommendation | Why |
|---|---|---|---|
| RAG over <5k docs, hobby project | quickest deploy | dict or FAISS Flat | substrate's 67MB constant cost not worth complexity at M=5k |
| RAG over 100k docs, no compliance | raw latency | FAISS HNSW | substrate matches HNSW on disk but HNSW wins on retrieve latency at M=100k |
| RAG over 100k docs, EU AI Act compliance Aug 2026 | audit chain + deletion cert | Substrate | only backend that emits verifiable cert; only backend whose state is hashable for tamper-evidence |
| Healthcare PHI with HIPAA + edit-heavy workload | edit isolation + deletion verify | Substrate | KF-2 1/sqrt(N) isolation + TCFT var_ratio; baselines have neither |
| Financial agent with FINRA audit | provenance + chain | Substrate | DeletionCertificate + verification_probes match FINRA 17a-4 |
| Multi-agent system with shared knowledge | edit isolation + path-independence | Substrate | KF-2 cross-codebook v275 production-scale + AXIS-4 hysteresis-free |
| Pure latency benchmark | none | FAISS HNSW | substrate's per-op cost is dominated by N^2 matvec; no advantage |

### 7.4 Sample per-operation cost decomposition (after A.5.4)

| op | substrate (N=4096) | FAISS Flat (M=10k, d=4096) | Chroma (M=10k) |
|---|---|---|---|
| store | 67M FLOPs + 67 MB touched | 0 FLOPs (raw write) + 16 KB | 16 KB write + sqlite WAL |
| retrieve k=1 | 67M FLOPs + 67 MB touched | 41M FLOPs + 160 MB touched | 41M FLOPs + 160 MB + sqlite read |
| edit | 134M FLOPs + 67 MB touched + audit hash | 0 FLOPs (value-only) | sqlite UPDATE |
| delete | 67M FLOPs + 67 MB touched + 67 MB hash + cert write | 0 FLOPs + faiss remove_ids O(M) | sqlite DELETE |
| audit panel | 256 OOS probes * (67M FLOPs + 67 MB touched) | N/A | N/A |

**Read:** substrate is consistently ~10000x more FLOPs per op vs FAISS Flat at small M. The value is in the AUDIT primitives those FLOPs produce. At large M, FAISS Flat's `M * d` linear scaling overtakes substrate's `N^2` constant.

---

## 8. Risk register

### 8.1 Mature adds (low risk, ship now)

- **A.3.1 adaptive codebook sizing**: well-understood; the C parameter is already there. Risk: minimal; mostly tuning.
- **B.2.1 large_M_constant_cost scenario**: storage_latency already does the per-M pattern; this is a parameter extension. Risk: FAISS at M=200k may saturate adapter throughput; benchmark with a wall-time cap.
- **D.2.3 audit_chain_validation**: substrate already emits w_state_hash_before/after; this scenario is "call delete in a loop and assert hashes link". Risk: low.
- **A.5.3 production decision matrix**: mostly authored content. Risk: depends on user feedback for which workloads to emphasize.

### 8.2 Speculative adds (medium risk, ship after user feedback)

- **D.2.2 edit_heavy_stream**: depends on which "FAISS does edit correctly" semantics we pick. The default `faiss_adapter.edit()` is value-only; defensible argument either way for what the right scenario does. Ask user before shipping.
- **C.3.2 vectorized batch retrieve**: changes the MemoryBackend ABC. Backwards-compatible if we provide a default fallback; risky if other consumers of MemoryBackend get confused. Ship the ABC change with a deprecation note.
- **A.3.3 GPU offload knob**: misrepresents the deployment story if not paired with explicit CPU-vs-GPU framing in the report. User feedback needed on whether the GPU line should be reported at all.

### 8.3 Adds requiring user feedback before implementation

- **B.4.1 faiss_hnsw**: a 1-of-3-baselines question. User direction: do we want HNSW added as a NEW baseline (more report rows; clarifies the production-RAG comparison) or do we want HNSW to REPLACE Flat (cleaner report, less data)?
- **D.4.2 langchain_faiss**: heavy dependency (LangChain pulls in ~30 transitive deps). Worth it only if the user wants the apples-to-apples production-RAG comparison; deferrable if substrate-vs-vector-DB is the only frame.
- **A.4.3 chroma_with_audit**: the audit-log writer is a design choice; could be JSON lines, sqlite, Merkle. User should pick.

### 8.4 NOT recommended (omit from implementation)

- Multi-tenant KF-3 scenario: ahead of underlying evidence.
- INT1 quantization scenario: caught as STRATEGIC_INTERPRETATION_OVER_CLAIM at v272; defer until A1 W-magnitude-operative test resolves.
- Compositional CL at production scale: cost is GPU-days; testbed should stay laptop-and-remote-CPU focused.
- LlamaIndex + Weaviate + Qdrant baselines: padding; LangChain + Chroma cover the same comparison axis.
- Streamlit live dashboard: cool but high engineering cost for low marginal information.

### 8.5 Honest about what substrate does NOT do well (must surface in report)

- **point_recall @ M=any**: substrate is 0.92 vs FAISS 0.99 at M=2000; the codebook collision floor is real. Surfacing this in the win-loss table is part of the honest framing.
- **continual_4stage**: substrate is 0.78 vs dict 1.0; CL ceiling is structural at the training-axis (Bet B Cluster C dependent for elevation). Surface honestly.
- **storage_latency p50_retr at small M**: substrate is 7ms vs FAISS 1ms at M=2k; substrate is 7x WORSE at small M. The constant cost is a flaw at the low end and a feature at the high end.
- **Cold load**: substrate's 113ms cold load is not catastrophic but is much higher than dict's 5ms. Note in report.

---

## 9. What this plan does NOT cover (out of scope)

- **Embedding-model integration**: the testbed consumes float32 vectors; integrating sentence-transformers is out of scope. A Phase 2 fork (`testbed/embedders/`) could close this gap.
- **LLM-end-to-end RAG evaluation**: requires an LLM call; cost-sensitive. Defer to a separate testbed dimension.
- **Network-backed baselines (Pinecone, Weaviate)**: latency dominated by network not memory; muddles the comparison.
- **HTTP server wrapping MemoryBackend**: was on the Phase 2 backlog already; out of scope here.
- **Adversarial scenarios (collision attacks, near-collision keys)**: a security-research dimension; out of scope for product validation.

---

## 10. Cross-references

- testbed/README.md (existing user-facing iteration guide; will need a 1-paragraph update after Phase A adds land)
- notes/strategic_synthesis_v265_v276_2026-05-29.md (the 4-defensible-features roster + operational-layer-invariance pattern)
- notes/research_product_positioning_v276_2026-05-29.md (compliance-grade auditable memory + EU AI Act window)
- notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md (substrate is Fusi-Drew-Abbott K=1 cascade synapse; continual_4stage ceiling at training axis is structural)
- testbed/configs/crossover_sweep.yaml (existing crossover sweep; B.2.1 extends to larger M)
- testbed/configs/mid.yaml (mid-bench config; will be the reference for relative-gain comparisons)
- testbed/api.py MemoryBackend ABC (C.3.2 adds `retrieve_batch`)
- testbed/substrate_memory.py SubstrateMemory (A.3.1 + A.3.3 + C.3.2 touch this)
- testbed/report.py (B.5.1 + D.5.2 + A.5.3 + A.5.4 touch this)

---

## 11. Honest summary (per [[feedback-no-smoke]])

The testbed today shows substrate's killer features as `N/A (by construction)` cells against baselines, which is RIGHT but READS as "substrate measures different things". The 8 adds in this plan reframe that as `(audit_score, recall, latency, disk)` Pareto with substrate sitting in a regime baselines CANNOT reach. The mature 4 adds (3.1, 2.1, 5.1, 2.3) are high-confidence; the speculative 4 adds (2.2, 3.2, 3.3, 4.1) need user feedback before shipping; the omitted 5 categories are honestly out of scope.

Substrate is NOT a general-purpose vector DB and the testbed report MUST say so. It IS the only backend that emits a verifiable deletion certificate AND has Kerdock-bounded edit isolation AND has constant-storage at large M AND has structural hallucination-impossibility. The 8 adds make those four wins LEGIBLE to a CTO reading the report.

Estimated total implementation phase: **31 engineering hours + 6 benchmark hours; achievable in 2-3 working days for tiers 1+2+3 alone (16.5h), full plan in 4-5 days.**

---

**END SHINE PLAN.**
