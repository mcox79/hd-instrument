# Seven intrinsic-property validation designs (v278, 2026-05-29)

Deliverable per strategic_roadmap_llm_integration_3mo_v278 Item 2: produce concrete, engineer-executable experiment designs for each of the 7 substrate intrinsic properties.

Each design is independent of GPU sweeps -- this is integration-validation engineering, not substrate-physics drilling. The substrate side is treated as a fixed `hdlab` configuration at N=4096, M_frac=4 (per v277 cap_map convergent priorities) unless the property specifically tests a substrate axis. The LLM side varies by property.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]] and the v278 substrate-product framing, P estimates here are the engineering-success probability of validating the property at HARD-PASS thresholds; NOT the strategic-impact probability. Deflations applied 0.15-0.25 where the validation involves "the first time substrate has been measured against an LLM-side metric" (i.e. uncharted measurement regime, not uncharted substrate-physics regime).

---

## Property 1: Native text/byte operation

### A. Property statement

Substrate accepts raw text/bytes via the substrate codebook (Sokolic-Kerdock or equivalent algebraic basis) as the encoder. There is no learned embedder; the codebook deterministically maps tokens to N-dim binary/bipolar vectors, and the binding/superposition operations operate directly on those vectors.

**Mathematical formulation:** For text `s = t_1 t_2 ... t_k` (tokens or bytes), substrate encoding is `phi(s) = bind(phi(t_1), pos_1) + bind(phi(t_2), pos_2) + ...` where `phi(t_i)` is a deterministic codebook lookup of cost O(1) per token (codebook table indexing), and `pos_i` is a fixed positional anchor. The implicit claim being tested: **the encoder cost is structurally zero (just indexing), so substrate retrieval cost = substrate retrieval cost; vs sentence-transformer baselines, the encoder is the dominant cost at small text sizes.**

### B. Test hypothesis

- **HARD-PASS:** Substrate encoding latency `<= 5%` of total retrieval latency (over text sizes 10-1000 tokens), AND substrate encoding latency `<= 10%` of the same metric measured against a sentence-transformer baseline (MiniLM-L6 or BGE-small). Both at single-document granularity.
- **HARD-FAIL:** Substrate encoding latency `>= 30%` of substrate retrieval latency (i.e. encoder is not "free"), OR substrate encoding latency exceeds sentence-transformer latency at >=100 token documents (no encoder advantage).
- **Middle band:** 5-30% of substrate retrieval latency, OR 10-50% of sentence-transformer; this is "encoder is cheap but not negligible" — annotate as partial validation, report numbers, no closure.
- **Sample size:** 5 seeds for codebook initialization (substrate side seeds don't matter for encoding speed but for variance across atom distributions); 1000 queries per document-size bin; 4 document-size bins (10/100/500/1000 tokens). Total: 5*1000*4 = 20K measurements per side.

### C. Baseline architecture

**Same-cost baseline:** Sentence-transformer (MiniLM-L6-v2; 80MB; 22.7M params) doing dense embedding + FAISS HNSW vector retrieval. Use the standard SBERT pipeline:
```
text -> SBERT embed -> 384-dim vector -> FAISS HNSW index lookup -> top-k chunks
```
This is the canonical RAG-replacement baseline. Cost components:
- SBERT embed: ~5-20ms/document on CPU (model load amortized), ~1-5ms on GPU
- FAISS HNSW lookup: ~1-3ms (sub-ms for small indexes)

**Substrate side:**
```
text -> codebook lookup per token -> bind+superpose -> substrate retrieval
```

### D. Experiment design

**Datasets (specific):**
- MS MARCO passage corpus (8.8M passages) — primary retrieval dataset
- BEIR/NFCorpus subset (3.6K queries, 5.6K docs) — small benchmark for variance characterization

**Setup:**
- Substrate: N=4096, M_frac=4 (so M=1024), codebook=Sokolic-Kerdock (16-Hadamard atomic codebook)
- Baseline: MiniLM-L6-v2 + FAISS HNSW (M=32, efConstruction=200, efSearch=64) — standard defaults
- LLM: not used in Property 1 (this is encoder-only test)
- Hardware: single CPU machine, no GPU; this is a CPU-only validation; matches downstream Pattern B target hardware

**Protocol:**
- For each of 4 document-size bins (10/100/500/1000 tokens), randomly sample 1000 docs from MS MARCO
- For each doc, measure:
  - Substrate-side: `t_codebook = time to encode` (deterministic, no model load)
  - Substrate-side: `t_retrieve = time to substrate-retrieve from a 100K-fact substrate`
  - Baseline-side: `t_sbert = time to embed via SBERT` (cold-start amortized over batches of 32)
  - Baseline-side: `t_faiss = time to FAISS-lookup against a 100K-doc HNSW index`
- 5 seeds for codebook initialization on substrate side; SBERT is deterministic so 1 seed suffices for baseline
- Report median, p95, p99 latencies (not just mean — tail matters for downstream Pattern B)

**Code interfaces:**

Substrate API call:
```python
def substrate_encode(text: str, codebook: Codebook, N: int = 4096) -> torch.Tensor:
    """Returns N-dim bipolar vector; deterministic O(len(text)) lookup."""
    
def substrate_retrieve(query: torch.Tensor, store: SubstrateStore, top_k: int = 5) -> list[FactID]:
    """Returns top_k matching fact IDs."""
```

Baseline API call:
```python
def sbert_encode(text: str, model: SentenceTransformer) -> np.ndarray:
    """Returns 384-dim float32 vector."""
    
def faiss_retrieve(query: np.ndarray, index: faiss.Index, top_k: int = 5) -> list[int]:
    """Returns top_k matching doc indices."""
```

### E. Cost estimate

- Engineering: 1.0 senior-engineer-week (codebook integration with text tokenizer; harness; measurement scaffolding)
- CPU: ~50 hours single-core (parallelizable to ~6 hours on 8 cores) for the measurement runs
- GPU: 0 hours (not needed)
- API costs: $0 (no LLM calls)

### F. Independence and parallelization

INDEPENDENT. Property 1 is self-contained; needs only substrate + tokenizer + SBERT baseline. Can run in parallel with all other properties. **Critical-path: NO.**

### G. What this validates vs does not validate

- **VALIDATES:** Encoder cost claim is correct -- substrate codebook lookup is structurally O(1) per token and dominates nothing.
- **DOES NOT VALIDATE:** Token-reduction at LLM-output level (that's Property 2 + Pattern B Item 1). Retrieval quality vs SBERT (that's a separate accuracy test on MS MARCO MRR@10 -- run alongside but report separately). Latency at full Pattern B pipeline level (that's Item 3 of the roadmap).
- **HONEST SCOPE:** This is "encoder is cheap" validation. Real wins come from downstream property compositions. Don't oversell.

### H. Risk register

| Risk | Mitigation |
|---|---|
| Substrate retrieval is slow at 100K-fact store (could dominate vs encoder, making the test trivially PASS on a bad denominator) | Report absolute latencies, not just ratios; if substrate retrieve is >10ms, escalate to Property 5 parallel-retrieval test |
| SBERT batch effects make per-query latency artificially low | Run baseline at batch=1 (matches single-query Pattern B usage) AND at batch=32 (matches indexing) — report both |
| Codebook size effects (small codebook may be artificially fast) | Test at codebook sizes 256, 1024, 16384 atoms; report scaling |
| Token-vs-byte ambiguity (BPE vs raw bytes) | Test both: BPE via GPT-2 tokenizer, raw-byte via UTF-8 encoding; the byte path is the substrate-novel claim |

### I. Integration with Pattern B demo

**FEEDS Pattern B Item 1 directly:** Pattern B needs substrate as text-input/output module. Property 1 validation = Pattern B's encoder-stage benchmark. Run them in coordination: when Pattern B harness is built (Week 1-2), it should expose the encoder measurement points so Property 1 reuses Pattern B's measurement scaffold.

### Engineering-success P (deflated): 0.75
Substrate codebook IS deterministic O(1) lookup by construction. Real risk is only "tail latencies blow up" or "substrate retrieve is so slow the ratio is meaningless on a bad denominator." Both are tractable. HIGH probability of HARD-PASS.

---

## Property 2: Atomic fact granularity

### A. Property statement

Substrate stores facts as bound atoms (`subject ⊛ predicate ⊛ object` or similar role-filler structure), and retrieval returns specific values, not chunks. A query "What is the patient's medication?" returns the exact medication string, not a 500-token paragraph that contains the medication name.

**Mathematical formulation:** A fact `f = (s, p, o)` is stored as `phi(f) = phi(s) ⊛ B_subject + phi(p) ⊛ B_predicate + phi(o) ⊛ B_object` where `B_*` are role anchors. To retrieve `o` given `(s, p)`, compute `phi(o)_query = (phi(s) ⊛ B_subject + phi(p) ⊛ B_predicate) ⊛^(-1) (phi(f))` and cleanup to nearest codebook atom. Implicit claim: **substrate's retrieval-unit is the atom, NOT the document.** This makes it isomorphic to triple-store retrieval but with continuous similarity instead of exact match.

### B. Test hypothesis

- **HARD-PASS:** Substrate returns the correct atomic value (string-exact match) at >=85% accuracy on CounterFact (single-fact closed-world test); chunk-RAG baseline returns the correct value (extracted from its chunk) at <=70%. Margin >=15% absolute.
- **HARD-FAIL:** Substrate accuracy <=70% OR chunk-RAG accuracy >=85%. (Either substrate fails atomic retrieval, or chunk-RAG is so good that the granularity advantage is illusory.)
- **Middle band:** Substrate 70-85% AND/OR chunk-RAG 70-85% — annotated as "atomic granularity is real but not decisive over chunk-RAG with good extraction"
- **Sample size:** 5K CounterFact queries (full standard split); 5 codebook seeds; 1 baseline seed.

### C. Baseline architecture

**Same-cost baseline:** chunk-based RAG with LLM extraction:
```
query -> SBERT embed -> FAISS top-5 chunks -> LLM (GPT-3.5-turbo) prompt:
  "Given these chunks, extract the answer:" -> string output
```
This is the canonical RAG-with-extraction pipeline. Cost: SBERT + FAISS as Property 1 + 1 GPT-3.5 call (~500 tokens input + ~50 tokens output, ~$0.001/query).

**Substrate side:**
```
query -> tokenize -> bind to predicate role -> substrate retrieve -> codebook nearest atom -> string lookup
```

### D. Experiment design

**Datasets:**
- **Primary: CounterFact** (Meng et al. ROME) — 21K (subject, relation, object) triples with both original and counterfactual targets. Use the closed-world setup: substrate stores the (s,r,o) facts; queries are (s,r) and expected answer is o.
- **Secondary: zsRE** (zero-shot RE) — 244K relation extraction examples; tests the same atomic-fact retrieval claim at scale.
- **Tertiary: HotpotQA single-fact subset** — filter to single-hop questions; check whether substrate's atomic retrieval matches the gold answer string-exactly.

**Setup:**
- Substrate: N=4096, M=1024, codebook=Sokolic-Kerdock, fact-encoding=role-filler triple binding (subject⊛B_s + predicate⊛B_p + object⊛B_o)
- Baseline: SBERT + FAISS + GPT-3.5-turbo with structured extraction prompt
- LLM (for baseline only): gpt-3.5-turbo-0125 (cheap, stable; matches what production deployments use)

**Protocol:**
1. **Index phase:** Load 5K CounterFact (s, r, o) triples into substrate (role-filler bind) AND into chunk-RAG store (one chunk per fact, where chunk = "The {r} of {s} is {o}.")
2. **Query phase:** For each of 5K queries (s, r), get substrate's atomic answer and chunk-RAG's extracted answer. String-exact match against gold o.
3. **Variance:** 5 substrate codebook seeds; baseline is deterministic (apart from API non-determinism — use temperature=0).
4. **Variant: ablate granularity** — also test chunk-RAG with chunk-size = full document (10 facts per chunk, simulating "noisy retrieval") to see if substrate's atomic advantage grows when chunks are larger.

**Code interfaces:**

Substrate API:
```python
def substrate_store_fact(s: str, r: str, o: str, store: SubstrateStore, codebook: Codebook) -> FactID:
    """Store role-filler triple. O(1) bind+superpose."""

def substrate_query_atom(s: str, r: str, store: SubstrateStore, codebook: Codebook) -> str:
    """Return atomic value for (s,r). O(M) similarity + O(1) cleanup."""
```

Baseline API:
```python
def chunk_rag_query(question: str, index: faiss.Index, llm_client) -> str:
    """SBERT-FAISS-top5 + LLM extract."""
```

### E. Cost estimate

- Engineering: 1.5 senior-engineer-weeks (role-filler binding wrapper; CounterFact loader; baseline harness; extraction-prompt tuning)
- CPU: ~30 hours
- GPU: 0 hours
- API costs: ~$10 for 5K * 5 seeds CounterFact via GPT-3.5 ($0.001 * 25K queries = $25; deflated by batch effects to ~$10)

### F. Independence and parallelization

INDEPENDENT of Properties 1, 3-7 *except* shares substrate scaffold with Pattern B (Item 1). Can run in parallel; same Pattern B engineer handles both. **Critical-path: NO.**

### G. What this validates vs does not validate

- **VALIDATES:** Substrate retrieves atoms, not chunks. The granularity claim is real and measurable against the natural chunk-RAG baseline.
- **DOES NOT VALIDATE:** Latency (Property 5). Token reduction in production prompts (that's Pattern B end-to-end). Multi-hop atomic composition (Property 3). Verifiability (Property 6).
- **HONEST SCOPE:** This is single-fact closed-world. Real LLM applications need open-world reasoning. CounterFact PASS does not imply HotpotQA PASS at multi-hop.

### H. Risk register

| Risk | Mitigation |
|---|---|
| Substrate codebook may not contain all CounterFact entity strings; codebook lookup degrades to nearest-atom (fuzzy match) | Pre-screen: how many of 5K queries have all 3 atoms in codebook? Report that "codebook coverage" stat alongside accuracy |
| Chunk-RAG baseline with single-fact-per-chunk is artificially good (extraction trivially succeeds) | Add multi-fact chunks (10 facts/chunk) variant; substrate advantage should grow there |
| GPT-3.5 extraction non-determinism | temperature=0; 3 API retries; cache responses |
| HotpotQA single-fact subset is filtered ambiguously | Use the SQuAD-style answer-span as gold; report exact-match AND F1 |

### I. Integration with Pattern B demo

**FEEDS Pattern B Item 1:** Pattern B's primary use case (regulated-industry Q&A) IS atomic-fact retrieval. Property 2 = Pattern B's core retrieval-accuracy benchmark. Run jointly; share CounterFact-style synthetic data scaffold.

### Engineering-success P (deflated): 0.65
Substrate IS atomic by construction. Real risk is codebook-coverage failure on CounterFact entity strings (mitigated by codebook learning). Plausible HARD-PASS path exists; >=85% is achievable based on prior substrate retrieval-accuracy results at N=4096.

---

## Property 3: Compositional binding algebra

### A. Property statement

Substrate composes multi-fact queries internally via binding ops. A query "What is the dose for the medication of the patient with ID 7?" can be decomposed into binding operations on stored facts: `query = (patient_id_7 ⊛ B_med ⊛ B_dose)`, and substrate returns the answer in one retrieval step (not multiple LLM calls + intermediate parsing).

**Mathematical formulation:** Given facts `f_1 = (patient_7, has_medication, drug_X)` and `f_2 = (drug_X, has_dose, 10mg)`, the composed query `Q = (patient_7, has_medication ⋆ has_dose)` should retrieve `10mg` in one substrate operation, where `⋆` is the binding-composition operator (e.g. circular convolution for HRR, element-wise multiplication for FHRR). Implicit claim: **substrate's binding algebra supports composition without intermediate argmax/cleanup steps for k=2-5 hops.**

### B. Test hypothesis

- **HARD-PASS:** Substrate accuracy on 2-hop compositional queries >=70%; 3-hop >=50%; chunk-RAG baseline (with multi-step LLM tool-use) on the same queries: 2-hop <=60%, 3-hop <=40%. **AND** substrate latency for 3-hop query <= 3x LLM-tool-use latency. (Substrate is faster because it doesn't pay LLM-call-per-hop.)
- **HARD-FAIL:** Substrate 2-hop accuracy <=40% OR substrate 3-hop accuracy <=20% (binding decomposition fails). OR LLM-tool-use matches/beats substrate on accuracy AND latency.
- **Middle band:** 40-70% 2-hop OR 20-50% 3-hop — partial validation; substrate composes but with degradation. Annotate as cliff steeper than predicted.
- **Sample size:** 1K queries per hop-depth (2, 3, 4, 5); 5 seeds; 1 baseline seed per query.

### C. Baseline architecture

**Same-cost baseline:** Multi-call LLM tool-use:
```
query "What is the dose of the medication of patient 7?"
LLM call 1: "Decompose into sub-queries" -> ["What medication does patient 7 take?"]
LLM call 2: "What is the dose of {result_of_call_1}?"
... (iterate up to max-depth)
```
Cost per query: O(k) LLM calls where k = hop depth. Each call ~$0.001.

**Substrate side:**
```
parse query -> identify role-chain (B_med, B_dose) -> compose binding -> substrate retrieve -> string lookup
```

### D. Experiment design

**Datasets:**
- **Primary: HotpotQA** — 113K multi-hop questions with explicit supporting-fact annotations; filter to "comparison" and "bridge" question subtypes which are mechanically compositional. 2-hop subset.
- **Secondary: MuSiQue** — 25K multi-hop questions with 2-4 hop chains explicitly labeled; perfect for hop-depth ablation.
- **Tertiary: Synthetic SuperGLUE-style multi-fact** — generate 5K synthetic 2-5 hop chains over a known fact base (substrate-friendly closed-world; validates the algebra in isolation before noisy real-world data)

**Setup:**
- Substrate: N=4096, M=1024, codebook=Sokolic-Kerdock, role-filler binding with 10 distinct role anchors
- Baseline: GPT-3.5-turbo with tool-use loop (LangChain-style ReAct agent over a key-value fact store)
- Hardware: CPU for substrate; API for LLM

**Protocol:**
1. **Pre-step: validate algebra in isolation** on synthetic data. If substrate fails synthetic 3-hop at >=70%, that's an immediate framework problem (HARD-FAIL) -- do not proceed to MuSiQue.
2. **Index phase:** Load HotpotQA's gold supporting-fact pool into substrate (role-filler triples).
3. **Query phase:** For each query, substrate computes composed binding directly; baseline LLM runs tool-use loop.
4. **Metrics:** answer string exact-match (primary), F1 (secondary), latency per query, $-cost per query
5. **Variance:** 5 substrate seeds; baseline is run once per query (cost prohibits multi-seed at $0.005/query * 5 = $0.025 * 1K * 4 hop-depths = $100; affordable but skip for variance)

**Code interfaces:**

Substrate API:
```python
def substrate_compose_query(roles: list[RoleAnchor], values: list[str], store: SubstrateStore) -> str:
    """Compose role-chain binding; retrieve composed atom.
    Example: compose_query([B_med, B_dose], [patient_7], store) -> '10mg'
    """
```

Baseline API:
```python
def llm_tool_use_query(question: str, fact_store: dict, llm_client, max_hops: int = 5) -> str:
    """ReAct-loop over fact_store."""
```

### E. Cost estimate

- Engineering: 2.0 senior-engineer-weeks (role-anchor design; query-parser substrate-side; tool-use loop for baseline; eval harness)
- CPU: ~20 hours for substrate runs
- GPU: 0 hours
- API costs: ~$150-200 for baseline (4K queries * 5 seeds * 3-5 LLM calls each = up to 100K API calls at $0.001-0.002 = $100-200)

### F. Independence and parallelization

INDEPENDENT of Properties 1, 2, 4-7. **DEPENDENT on substrate role-anchor design choices that Pattern B will inherit** -- run BEFORE Pattern B Item 1 final architectural decisions. **Critical-path: YES, gates Pattern B architecture.**

### G. What this validates vs does not validate

- **VALIDATES:** Substrate's binding algebra supports k=2-5 hop composition. The "compositional algebra" claim is operational, not just mathematical.
- **DOES NOT VALIDATE:** Substrate composes BETTER than transformer multi-hop reasoning at depth d>10 (canonical substrate cliff at d=25-50 still applies). Open-ended natural language composition (this is structured-query composition).
- **HONEST SCOPE:** Substrate is GOOD at structured multi-hop within its role-anchor algebra; UNKNOWN beyond. Multi-hop accuracy ceiling is bounded by depth-cliff regardless.

### H. Risk register

| Risk | Mitigation |
|---|---|
| Substrate role-anchor algebra doesn't cleanly express HotpotQA question structure (the questions require open-domain parsing) | Pre-step on synthetic data isolates the algebra; HotpotQA failure becomes a parser problem, not an algebra problem |
| Multi-hop depth cliff (substrate breaks at d>3 per prior cap_map) | Cap test at d=5 max; report cliff explicitly; HARD-PASS thresholds tuned to 2-3 hops where substrate is known-good |
| LLM tool-use is so good that "substrate composes natively" isn't a meaningful advantage | Report COST (substrate doesn't pay per-hop LLM cost) — substrate's value is latency+$cost reduction, not accuracy beat |
| Coherent-multihop QE-2 v278 result lands during this validation and changes the substrate algebra | Coordinate: if QE-2 HARD-PASS, re-run Property 3 with QE-2 architecture; if HARD-FAIL, this validation uses standard binding |

### I. Integration with Pattern B demo

**CRITICAL FEED to Pattern B:** Pattern B's value proposition includes "compose multi-fact queries internally without LLM round-trips." Property 3 is the empirical witness. **Run Property 3 first (Week 1-2)**; the role-anchor design decisions there propagate into Pattern B (Week 3+).

### Engineering-success P (deflated): 0.45
Substrate composes at d=2 (well-established). At d=3-5, depth cliff bites. HARD-PASS thresholds tuned to 2-3 hop sweet spot. Risk: HotpotQA questions may not cleanly decompose to substrate role-anchors (open-domain parsing problem). Calibration penalty applied (-0.20 from naive 0.65 estimate) because this validates the algebra against open-domain LLM benchmarks, not just substrate-internal synthetic.

---

## Property 4: LLM-internal representation compatibility (SPECULATIVE)

### A. Property statement

Substrate could store and retrieve LLM internal representations (residual-stream activations, attention KV-cache, layer-N hidden states) rather than just text strings. This would let substrate serve as a compressed/auditable memory of "what the LLM thought" not just "what the LLM read."

**Mathematical formulation:** Given an LLM hidden state `h ∈ R^d_model` (e.g. d_model=768 for GPT-2-small, 4096 for LLaMA-7B), there exists a projection `P : R^d_model -> {-1,+1}^N` such that substrate-retrieve(P(h_query)) returns indices of stored `h_stored` with high accuracy on retrieval task R (where R could be: top-k nearest-neighbor in cosine space; learned representation similarity; etc.). Implicit claim: **substrate's codebook can serve as a hash function for high-dimensional continuous LLM activations without learning a separate encoder.**

### B. Test hypothesis

- **HARD-PASS:** Substrate-stored LLM residual-stream activations retrieve correct context at >=70% top-5 accuracy on a "needle-in-haystack" task (store 1K LLM hidden states from a corpus; query with a held-out hidden state; correct answer is the original passage); AND projection `P` is random/structural (Johnson-Lindenstrauss-style; no learned weights), preserving substrate's "no learned embedder" claim.
- **HARD-FAIL:** Substrate top-5 accuracy <=30% (basically random over 1K items would be 0.5%; <=30% means substrate can't even use the projection meaningfully) OR projection requires learned weights to work (which breaks the "structural compatibility" claim).
- **Middle band:** 30-70% — substrate can use LLM representations but with degradation; annotate as "compatible at the order-of-magnitude level"
- **Sample size:** 1K LLM hidden-state items; 5 codebook seeds; 100 query items.

### C. Baseline architecture

**Same-cost baseline:** Vector DB (FAISS HNSW) over the raw 768-dim LLM hidden states. This is the strongest baseline because it bypasses the projection entirely.

**Substrate side:**
```
LLM activation h (768-dim float32) -> random projection P -> sign() -> N-dim bipolar -> substrate-store
```

### D. Experiment design

**Datasets:**
- **Primary: Wikipedia passages** — 1K passages from Wikitext-103; for each, get the GPT-2-small final-layer residual-stream activation at last token (768-dim)
- **Secondary: CounterFact** — same setup but with CounterFact's natural-language prompts; tests whether substrate retrieval over LLM-internal reps correlates with the LLM's own factual knowledge

**Setup:**
- Substrate: N=4096, codebook=Sokolic-Kerdock OR random-bipolar (test both — codebook may not be necessary for LLM-rep compatibility)
- Projection P: random sign matrix (768 x N); each entry ±1 with equal prob
- LLM: GPT-2-small (open weights, easy to extract activations; 768-dim is small enough to be cheap and large enough to be representative)
- Hardware: GPU for activation extraction; CPU for substrate ops

**Protocol:**
1. **Cheapest first test:** before doing anything else, sanity check: does random-projection-then-sign of LLM activations preserve top-5 cosine-similarity neighbor structure at all? Run a simple Johnson-Lindenstrauss-style test: pick 100 query hidden states, find their true top-5 cosine neighbors in 768-dim, find their top-5 substrate-retrieve neighbors, compute overlap. If overlap is <=10%, ABORT -- the projection doesn't preserve enough signal. This is a 1-hour CPU test before committing to full design.
2. If sanity passes: full needle-in-haystack with 1K items, 5 seeds.
3. **Variance:** 5 codebook seeds; report median overlap @5.

**Code interfaces:**

```python
def extract_llm_activation(text: str, model: GPT2LMHeadModel, layer: int = -1) -> torch.Tensor:
    """Returns d_model hidden state at last token of `text` at `layer`."""

def project_to_substrate(h: torch.Tensor, P: torch.Tensor) -> torch.Tensor:
    """Random projection sign(P @ h); returns N-dim bipolar."""
```

### E. Cost estimate

- Engineering: 2.0 senior-engineer-weeks (LLM activation extraction; projection design; needle-in-haystack harness)
- CPU: ~10 hours
- GPU: ~5 hours (for activation extraction on Wikipedia subset)
- API costs: $0 (open-weights LLM)

### F. Independence and parallelization

INDEPENDENT of Properties 1-3, 5-7. Highest engineering risk. Recommend: **start with cheapest sanity check (1-hour CPU) before committing 2 weeks of engineering**.

### G. What this validates vs does not validate

- **VALIDATES (if PASS):** Substrate IS compatible with LLM-internal reps via random projection; this opens Pattern C (deep integration into LLM inference loop) as a viable path.
- **DOES NOT VALIDATE:** That this is BETTER than vector-DB-over-raw-activations. The substrate advantage at this layer is auditability (you can read off bound atoms), not retrieval quality.
- **HONEST SCOPE:** This is the SPECULATIVE property per user. PASS opens a research direction; FAIL closes it cleanly (don't pursue Pattern C representation-level integration).

### H. Risk register

| Risk | Mitigation |
|---|---|
| Random projection loses too much signal (substrate has only N=4096 dims to represent a 768-dim continuous space) | Test at N=4096, 16384, 65536; if scaling helps, the property holds at larger N; if not, real failure |
| LLM activations have non-uniform geometry (concentrated mass near low-dim subspace) so random projection inherits the same anisotropy | Pre-analyze: report PCA spectrum of LLM activations; if top-50 components contain >95% variance, use those 50 dims projected, not full 768 |
| Substrate codebook is ill-suited for continuous-valued queries (designed for discrete atoms) | Compare to RANDOM bipolar baseline (no codebook structure); if random-bipolar is better, substrate-specific structure adds nothing here |
| LLM choice matters (GPT-2 is small; LLaMA-7B is the real target) | Test on GPT-2 first; if PASS, replicate on LLaMA-7B at a single point |
| User flagged this as "speculative" — high prior for HARD-FAIL | Cheapest test (1-hour sanity check) gates expensive engineering; FAIL early is GOOD |

### I. Integration with Pattern B demo

**STANDALONE.** Property 4 is the gating test for Pattern C (deep representation-level integration), NOT Pattern B. Pattern B works fine with text-only substrate. Run Property 4 in parallel with Pattern B; the result informs whether Pattern C is in the 12-month roadmap or not.

### Engineering-success P (deflated): 0.30
User flagged as speculative; calibration penalty applied (-0.25 from naive 0.55 estimate; capped at novel-synthesis P=0.50 then deflated). The 1-hour sanity check has P=0.50 (Johnson-Lindenstrauss-style projections preserve neighbor structure with reasonable probability). If sanity passes, full P rises to 0.55-0.65. If sanity fails, the whole property is closed for ~$200 cost.

---

## Property 5: Parallel retrieval during LLM inference

### A. Property statement

Substrate operations are fast enough to run alongside token generation in an LLM inference loop. Specifically: a substrate retrieval can complete in less than 1 token-generation latency budget on the same hardware, enabling "prefetch" patterns where the LLM generates tokens while substrate fetches the next relevant memory.

**Mathematical formulation:** Let `T_token` be the time to generate 1 LLM token on hardware H. Let `T_retrieve` be the time for substrate to complete a single retrieval (encode + match + cleanup) on the same H. Claim: `T_retrieve <= T_token` for production-relevant hardware H. For frontier LLMs on A100/H100, `T_token ≈ 10-50ms`. For substrate at N=4096, M=1024, the claim is `T_retrieve <= 10ms`.

### B. Test hypothesis

- **HARD-PASS:** Substrate retrieval p95 latency <= 10ms on CPU (matching typical LLM-API token latency), with substrate-store of >=100K facts.
- **HARD-FAIL:** Substrate retrieval p95 latency >= 100ms (i.e. 10x slower than token generation; cannot run in parallel)
- **Middle band:** 10-100ms p95 — substrate can run NEAR token-gen latency but with occasional stalls; annotate as "parallel-retrieval feasible with scheduling overhead"
- **Sample size:** 10K retrieval queries; 5 codebook seeds; report median, p95, p99, max.

### C. Baseline architecture

**Same-cost baseline:** FAISS HNSW vector retrieval at the same store size (100K vectors). This is the production-vector-DB-of-record baseline.

**Substrate side:**
```
query -> codebook encode -> M-similarity scores -> top-k cleanup
```

### D. Experiment design

**Datasets:**
- 100K synthetic facts (s, r, o) triples; substrate-friendly closed-world; the LATENCY test is hardware-bound, not data-bound

**Setup:**
- Substrate: N=4096, M=1024, codebook=Sokolic-Kerdock
- Baseline: FAISS HNSW (M=32, efConstruction=200, efSearch=64)
- Hardware: TWO hardware points:
  1. CPU-only (single Intel Xeon or M2 core) — matches production lambda/edge deployment
  2. GPU (single A100 or H100) — matches LLM-inference-server hardware
- LLM reference: we DON'T run an LLM; we measure substrate latency against published token-gen latencies (~10-50ms on CPU LLM-API; ~5-20ms on GPU LLM-server)

**Protocol:**
1. **Latency measurement:** 10K queries, log per-query latency; report median, p95, p99
2. **Store-size scaling:** repeat at 10K, 100K, 1M facts; substrate latency should be ~constant (similarity is O(M)), FAISS HNSW is ~log(N_facts)
3. **Concurrency:** can substrate run M parallel retrievals on same CPU? Report throughput, not just latency
4. **Hardware ablation:** CPU vs GPU substrate; CPU-side substrate is the more relevant target (matches Pattern B serverless deployment)

**Code interfaces:**

```python
def substrate_retrieve_timed(query: torch.Tensor, store: SubstrateStore) -> tuple[FactID, float]:
    """Returns (fact_id, latency_ms)."""

def faiss_retrieve_timed(query: np.ndarray, index: faiss.Index) -> tuple[int, float]:
    """Returns (fact_id, latency_ms)."""
```

**Concurrency benchmark:**

```python
def measure_throughput(store, num_concurrent: int = 64) -> dict:
    """Returns throughput (queries/sec) at concurrency level."""
```

### E. Cost estimate

- Engineering: 1.0 senior-engineer-week (timing harness; concurrency wrapper; store-size scaling)
- CPU: ~20 hours
- GPU: ~5 hours
- API costs: $0

### F. Independence and parallelization

INDEPENDENT of all other properties. **HARDWARE DEPENDENCY:** results depend on chosen hardware; report on canonical target (single Intel Xeon CPU; single A100 GPU) plus 1 alt for sanity.

### G. What this validates vs does not validate

- **VALIDATES:** Substrate retrieval CAN run in parallel with LLM token generation (latency budget compatible).
- **DOES NOT VALIDATE:** Actual production parallel-retrieval works end-to-end (that's Pattern C engineering, not pure latency). Substrate retrieval quality (that's Properties 2+3).
- **HONEST SCOPE:** A latency benchmark proves the timing claim; downstream integration is a separate engineering project.

### H. Risk register

| Risk | Mitigation |
|---|---|
| Substrate similarity computation (M x N float ops) is slow on CPU because not vectorized well in stock numpy/PyTorch | Optimize: use SIMD via Numba or Rust; report both unoptimized and optimized numbers |
| Cold-cache effects dominate latency at low query rates | Warm up before measurement; report both cold-cache and steady-state |
| FAISS baseline is so fast that substrate is uncompetitive on raw latency | Substrate's value over FAISS is at indexing (substrate update is O(1); FAISS HNSW is O(M log N)); report indexing latency alongside retrieval |
| Token-gen latency depends on LLM choice (GPT-4 is ~50ms, Haiku is ~10ms); substrate target moves | Report substrate latency in absolute ms, let downstream choose LLM target |

### I. Integration with Pattern B demo

**STANDALONE for Pattern B**, but **GATES Pattern C**. Pattern B doesn't need parallel-retrieval (it's a tool-use pattern: LLM pauses, substrate retrieves, LLM resumes — sequential). Pattern C (deep integration) requires Property 5 PASS.

### Engineering-success P (deflated): 0.70
Substrate retrieval IS O(M*N) similarity which at N=4096, M=1024 is ~4M float ops — single-digit ms on a modern CPU is plausible. Risk: if implementation is poorly vectorized, p95 blows up. HARD-PASS achievable with engineering attention.

---

## Property 6: Structural output verification

### A. Property statement

Substrate outputs are deterministic and exact, so they can bypass LLM phrasing for facts that require structural certainty (compliance answers, audit responses, regulated-content fields). Given a substrate retrieval result, the same query against the same store always returns the same atom; no sampling, no temperature.

**Mathematical formulation:** Substrate query `q -> retrieve(q, S)` is a deterministic function of `(q, S)`. There is no stochastic decoding. Additionally, retrievals produce a similarity score `sim(q, retrieved_atom)`; this score is calibrated and interpretable, allowing thresholding for "I don't know" responses without LLM hallucination.

**Implicit claim:** **substrate retrievals can be audit-trail-grade verifiable in a way LLM outputs structurally cannot.**

### B. Test hypothesis

- **HARD-PASS:** On a 1K-fact closed-world store, substrate retrieves correct atomic value at >=95% accuracy with sim threshold = 0.7 (atomic exact-match), AND retrieves "I don't know" (sim below threshold) on out-of-distribution queries at >=90% true-negative rate. Substrate output is byte-deterministic across runs (10/10 identical).
- **HARD-FAIL:** Substrate accuracy <95% on closed-world OR true-negative rate <70% on OOD (substrate hallucinates atoms it doesn't have) OR substrate output is non-deterministic across runs.
- **Middle band:** 85-95% accuracy OR 70-90% true-negative — partial validation, calibration is suboptimal
- **Sample size:** 1K in-distribution + 1K out-of-distribution queries; 5 codebook seeds; determinism check via 10 identical runs.

### C. Baseline architecture

**Same-cost baseline:** LLM with structured-extraction prompt + JSON-mode output. This is the production "verifiable LLM" pattern (constrained decoding + structured output validation).

**Substrate side:**
```
query -> retrieve -> similarity score -> if sim < threshold: "I don't know" else: atom_string
```

### D. Experiment design

**Datasets:**
- **Primary: CounterFact in-distribution (1K)** — facts the substrate stored
- **Primary: CounterFact-counterfactual OOD (1K)** — facts present in CounterFact but NOT stored in substrate (test true-negative rate)
- **Secondary: TriviaQA closed-world subset** — same in/OOD split for redundancy

**Setup:**
- Substrate: N=4096, M=1024, codebook=Sokolic-Kerdock, threshold = 0.7 (or grid-searched on small dev set)
- Baseline: GPT-4-turbo with JSON-mode structured output + "answer or say UNKNOWN" prompt
- Hardware: CPU for substrate; API for baseline

**Protocol:**
1. **Store 1K facts in substrate**
2. **Determinism check:** run same 100 queries 10 times; verify byte-identical output every run
3. **In-distribution accuracy:** 1K queries on stored facts; report acc + sim score distribution
4. **OOD true-negative rate:** 1K queries on NOT-stored facts; substrate should return "I don't know" via sim < threshold
5. **Calibration:** plot sim score vs is-correct; ROC analysis; report AUC
6. **Baseline comparison:** same 2K queries through GPT-4 structured output; measure (a) accuracy on in-dist, (b) hallucination rate on OOD ("answered" when should be UNKNOWN), (c) determinism (run 3x, check identical)
7. **Adversarial:** inject mis-phrased / typo'd queries; substrate's atom-cleanup behavior should be characterized

**Code interfaces:**

```python
def substrate_retrieve_with_score(query: str, store: SubstrateStore, threshold: float = 0.7) -> tuple[str | None, float]:
    """Returns (atom_string or None if sim<threshold, sim_score)."""
```

### E. Cost estimate

- Engineering: 1.0 senior-engineer-week (threshold tuning; OOD harness; determinism check; ROC analysis)
- CPU: ~10 hours
- GPU: 0 hours
- API costs: ~$50 for 2K GPT-4-turbo calls * 5 seed reruns = 10K calls * $0.005 = $50

### F. Independence and parallelization

INDEPENDENT of all other properties. **Critical-path: NO.**

### G. What this validates vs does not validate

- **VALIDATES:** Substrate outputs are deterministic + structurally exact + calibration-able for "I don't know". The compliance positioning's verifiability claim has empirical grounding.
- **DOES NOT VALIDATE:** That substrate's verifiability covers ALL aspects required for regulatory audit (legal review still required). That substrate doesn't have OTHER failure modes (e.g. codebook-edge atoms that fuzzy-match plausibly).
- **HONEST SCOPE:** This is "deterministic exact output, calibrated UNKNOWN" — useful product claim, not full compliance certification.

### H. Risk register

| Risk | Mitigation |
|---|---|
| Substrate similarity threshold doesn't cleanly separate in/OOD (continuous sim distribution; no obvious cutoff) | Report ROC curve, not single threshold; let product-side choose operating point |
| OOD queries that fuzzy-match an in-dist atom (close in codebook geometry) return wrong answer with high confidence | Adversarial test for this; report rate of "high-confidence-wrong" responses; this is the substrate-specific failure mode that needs to be characterized for compliance positioning |
| GPT-4 with JSON mode + UNKNOWN-prompt is actually quite good at OOD (Anthropic/OpenAI have trained for this) | Substrate's structural advantage may be smaller than expected; report margin honestly |
| Determinism breaks if substrate has multi-threading races at retrieval | Single-threaded retrieval for the test; document the determinism guarantee as conditional on serial retrieval |

### I. Integration with Pattern B demo

**CRITICAL FEED to Pattern B + COMPLIANCE POSITIONING:** Property 6 IS the empirical witness for the compliance-grade auditable-memory positioning. **Run Property 6 in parallel with Pattern B (Week 1-2)**; results feed both the demo and the compliance documentation track (Item 13 of roadmap).

### Engineering-success P (deflated): 0.65
Substrate IS deterministic by construction. Threshold calibration is straightforward. Real risk is the OOD true-negative rate (substrate codebook geometry may produce high-confidence-wrong on adversarial OOD). HARD-PASS achievable with attention to threshold tuning.

---

## Property 7: CoT state management

### A. Property statement

Substrate could hold intermediate reasoning state across CoT steps, so an LLM doing 100-step reasoning can offload intermediate results to substrate (rather than carrying them in context window) and retrieve them on demand. This bypasses the context-window-token-budget limitation that currently caps CoT depth.

**Mathematical formulation:** Given a CoT trace `t_1 t_2 ... t_k` of intermediate-step outputs, substrate stores each `t_i` as an atomic fact tagged with step index `i`. Subsequent steps query substrate for prior intermediate results: `t_j = substrate_retrieve(query=context_at_step_j, store=CoT_state_store)`. The claim: **substrate's atomic + role-filler structure supports state-management for arbitrary-depth CoT without context-window growth.**

### B. Test hypothesis

- **HARD-PASS:** LLM with substrate-mediated CoT achieves >=80% accuracy on a 50-step reasoning task (e.g. multi-step arithmetic or constraint satisfaction); same LLM without substrate (pure in-context CoT) achieves <=60% at 50 steps OR fails at context-window limit (~16K tokens in 50 steps). Substrate-mediated version maintains accuracy at 100+ steps where in-context fails entirely.
- **HARD-FAIL:** Substrate-mediated CoT accuracy <=60% at 50 steps (substrate retrieval breaks the reasoning chain), OR no advantage over in-context at depth where in-context still fits.
- **Middle band:** 60-80% — partial validation; substrate helps at some depths but with degradation
- **Sample size:** 500 CoT problems at each of (10, 50, 100, 200) steps; 5 substrate seeds; 1 baseline seed.

### C. Baseline architecture

**Same-cost baseline:** Pure in-context CoT — LLM generates the full reasoning trace within its context window. Token-by-token, no external state.

**Substrate side:**
```
LLM step generates intermediate result -> substrate stores (step_idx, intermediate_result)
LLM step needs prior result -> substrate retrieves by (step_idx, role)
LLM step uses retrieved value -> generates next step
```

### D. Experiment design

**Datasets:**
- **Primary: synthetic multi-step arithmetic** — generate problems requiring 10-200 sequential arithmetic operations with intermediate results; standard CoT benchmark from "Show Your Work" line of research
- **Secondary: AQuA-RAT** — 100K multi-step reasoning problems
- **Tertiary: GSM8K subset extended** — synthesize longer chains by composition

**Setup:**
- Substrate: N=4096, M=1024, codebook=Sokolic-Kerdock, with role-anchor for "step_index" and "intermediate_result"
- LLM: GPT-4-turbo (state-of-the-art CoT); ALSO test GPT-3.5-turbo (cheaper, sees substrate benefit more clearly because GPT-3.5 has less native CoT competence)
- Baseline: same LLM, pure in-context CoT; capped at context-window limit
- Hardware: CPU for substrate; API for LLM

**Protocol:**
1. **Define the CoT-substrate protocol:** at each step, LLM emits structured tag `[STORE step_i = value]` or `[RETRIEVE step_j]`; substrate parses these tags and stores/retrieves accordingly
2. **Run on 500 problems at each depth (10/50/100/200)**:
   - Pure in-context CoT (baseline)
   - Substrate-mediated CoT (test)
3. **Metrics:**
   - Final answer accuracy
   - Context-window tokens used (substrate should reduce this drastically at high depth)
   - $-cost per problem ($-savings from context reduction is the product story)
4. **Failure-mode analysis:** when substrate-mediated fails, was it (a) LLM emitting wrong tag, (b) substrate returning wrong value, (c) LLM misinterpreting retrieved value?

**Code interfaces:**

```python
class SubstrateCoTState:
    def store_step(self, step_idx: int, role: str, value: str): ...
    def retrieve_step(self, step_idx: int, role: str) -> str: ...

def run_substrate_cot(problem: str, llm_client, state: SubstrateCoTState, max_steps: int = 200) -> str:
    """LLM-substrate loop with tag-parsing."""
```

### E. Cost estimate

- Engineering: 2.5 senior-engineer-weeks (tag protocol; LLM prompting; substrate-CoT loop; failure-mode analysis)
- CPU: ~10 hours for substrate; minimal compute
- GPU: 0 hours
- API costs: ~$300-500 (GPT-4-turbo at 50-200 step CoT * 500 problems * 5 seeds = a lot of API calls; estimate ~10K-50K calls at $0.01-0.03/call = $300-500)

### F. Independence and parallelization

DEPENDENT on Property 3 (Compositional binding) — uses role-anchor algebra that Property 3 validates. **Critical-path: AFTER Property 3.**

### G. What this validates vs does not validate

- **VALIDATES:** Substrate can hold CoT intermediate state across 50+ steps; substrate-mediated CoT achieves depths that exceed pure in-context.
- **DOES NOT VALIDATE:** Substrate's CoT-state management is BETTER than alternative "external scratchpad" approaches (e.g. recurrent-memory, file-tool, prior tool-use research). The substrate advantage may be auditability + structural (not depth).
- **HONEST SCOPE:** This validates substrate as a CoT scratchpad. Comparison to other scratchpad approaches is a separate ablation.

### H. Risk register

| Risk | Mitigation |
|---|---|
| LLM emits wrong tags ([STORE]/[RETRIEVE]) because it's not trained for them | Few-shot prompt with 5 worked examples; in-context demonstration; OR fine-tune on synthetic tag-correct traces (expensive escape hatch) |
| Substrate retrieval at step k accumulates errors across the chain (cascading failures) | Report per-step accuracy; identify error-cascade pattern |
| GPT-4-turbo's native CoT is so good at 50 steps that substrate doesn't help (saturation) | Test on harder/longer problems; substrate's value is at depths >50 where GPT-4 in-context degrades |
| API costs may exceed estimate if 200-step problems require many API roundtrips | Pre-budget: cap at $1K for full validation; if mid-run cost is on track for $2K+, downsample step depths |
| Substrate codebook may not contain numeric values at sufficient resolution (CoT arithmetic involves arbitrary integers) | Use string-encoded values, not codebook-atomic; substrate stores arbitrary strings via role-filler binding |

### I. Integration with Pattern B demo

**STANDALONE.** Property 7 is NOT in Pattern B's critical path. Pattern B is single-pass Q&A, not multi-step CoT. Property 7 enables a DIFFERENT product narrative (substrate as CoT state manager) that's complementary to compliance positioning. Run Property 7 in parallel; results feed the "substrate as state layer for thousands-step LLM reasoning chains" thread of strategic positioning.

### Engineering-success P (deflated): 0.40
LLM-side reliability (tag emission, retrieval interpretation) is high-variance. Substrate-side mechanics are straightforward. Calibration penalty applied (-0.20 from naive 0.60 estimate) because this validates substrate against an LLM behavioral benchmark, not pure substrate retrieval.

---

# CONCLUSION

## Summary table

| # | Property | P_deflated | Eng-wks | API $ | Critical path | Pattern B feed | Speculative? |
|---|---|---|---|---|---|---|---|
| 1 | Native text/byte op | 0.75 | 1.0 | $0 | NO | YES | NO |
| 2 | Atomic fact granularity | 0.65 | 1.5 | $10 | NO | YES | NO |
| 3 | Compositional binding | 0.45 | 2.0 | $150 | YES (gates Pattern B arch) | YES | NO |
| 4 | LLM-internal rep compat | 0.30 | 2.0 | $0 | NO | NO | YES (user-flagged) |
| 5 | Parallel retrieval | 0.70 | 1.0 | $0 | NO | NO (gates Pattern C) | NO |
| 6 | Structural verification | 0.65 | 1.0 | $50 | NO | YES + compliance | NO |
| 7 | CoT state management | 0.40 | 2.5 | $400 | AFTER Prop 3 | NO | NO |

**Combined cost:** 11 engineer-weeks ≈ 4-6 calendar weeks with 2 engineers parallel + occasional bottlenecks at Property 3-7 chain. Matches user estimate of "4-6 weeks calendar."

**Total API budget:** ~$650 (well under $1K).

## EV ranking — highest-EV to ship FIRST

EV = P_deflated * strategic_impact / engineering_cost. Strategic-impact scoring assumes Pattern B is the highest-leverage strategic goal.

1. **Property 6 (Structural verification) — RANK 1.** Highest EV. P=0.65, low engineering cost (1 wk), directly feeds the compliance-grade-auditable-memory primary positioning, AND Pattern B. Determinism + calibrated UNKNOWN is the substrate's most defensible product claim. Ship Week 1.

2. **Property 1 (Native text/byte) — RANK 2.** P=0.75 (highest probability of HARD-PASS), low cost (1 wk), feeds Pattern B, validates the "no learned embedder" architectural distinction. Should ship Week 1 alongside Property 6.

3. **Property 3 (Compositional binding) — RANK 3.** P=0.45, but CRITICAL PATH — gates Pattern B's architectural decisions. Higher cost (2 wks), higher API cost ($150), but ship Weeks 1-2 because Pattern B (Item 1 in roadmap) cannot start its architecture without this validation result.

4. **Property 2 (Atomic granularity) — RANK 4.** P=0.65, 1.5 wks, feeds Pattern B. Co-runnable with Property 6 (shares CounterFact harness). Ship Week 2.

5. **Property 5 (Parallel retrieval) — RANK 5.** P=0.70, 1 wk, BUT gates Pattern C (deep integration) which is 12-month horizon. Lower urgency. Ship Week 3-4 once Properties 1+6 land.

6. **Property 4 (LLM-internal rep — SPECULATIVE) — RANK 6.** P=0.30, BUT recommend the 1-hour sanity check FIRST. **Action:** ship the 1-hour Johnson-Lindenstrauss-style sanity check in Week 1 (cost: 1 day eng). If sanity FAILS, close Property 4 cleanly (saves 2 weeks). If sanity PASSES, full validation moves to RANK 5-6 priority.

7. **Property 7 (CoT state management) — RANK 7.** P=0.40, highest engineering cost (2.5 wks), highest API cost ($400), DEPENDENT on Property 3 result. Defer to Week 5-6. Open a different product narrative; not Pattern B critical path.

## Recommended ship sequence

**Week 1 (parallel, 2 engineers):**
- Eng A: Property 1 (native text/byte) + Property 6 (structural verification) — shared SBERT/FAISS harness
- Eng B: Property 3 (compositional binding) — synthetic pre-step + HotpotQA setup
- Eng A or B (1 day): Property 4 cheapest sanity check (1-hour CPU test)

**Week 2 (parallel, 2 engineers):**
- Eng A: Property 1 + 6 completion + reports
- Eng B: Property 3 continuation + Property 2 (Atomic granularity) start
- IF Property 4 sanity PASSED: Eng C joins (or Eng A pivots after Week 1 deliverables) for full Property 4

**Week 3 (parallel):**
- Property 2 completion
- Property 5 (parallel retrieval latency benchmark)
- Property 3 completion (with Pattern B arch decision)

**Week 4-5:**
- Property 7 (CoT state management) — AFTER Property 3 lands

**Week 6:**
- Buffer; combined report; Pattern B coordination

## Critical-path summary

```
Property 3 (Compositional binding)  --GATES-->  Pattern B architecture
Property 6 (Structural verification) --FEEDS--> Pattern B + Compliance positioning + Item 13 (regulatory)
Property 1 (Native text/byte)        --FEEDS--> Pattern B
Property 2 (Atomic granularity)      --FEEDS--> Pattern B retrieval-accuracy demo

Property 7 (CoT state)  -- depends on Property 3 --
Property 5 (Parallel retrieval)  --GATES--> Pattern C (12-mo horizon)
Property 4 (LLM-internal rep)  --SPECULATIVE; GATES Pattern C deep--
```

**The critical-path bottleneck is Property 3:** Pattern B architecture cannot finalize until compositional-binding result is in hand. Ship Property 3 with high engineering attention in Weeks 1-2 even though P=0.45 is the lowest of the non-speculative properties.

## Property 4 SPECULATIVE handling (per user)

The cheapest possible test (1-hour CPU sanity check) gates expensive engineering investment:

**Test:** 100 GPT-2-small hidden states (768-dim) extracted from Wikipedia passages; random sign-projection to 4096-dim bipolar; compute top-5 cosine neighbors in original 768-dim space and top-5 substrate-retrieve neighbors; report overlap.

**HARD-FAIL threshold for sanity check:** overlap <= 10% — close Property 4 entirely.
**HARD-PASS threshold for sanity check:** overlap >= 30% — proceed to full Property 4 design.

This 1-day investment either CONFIRMS or REFUTES the property's premise before any expensive validation work.

## Property 5 hardware-dependency benchmark setup

Substrate latency must be benchmarked at TWO hardware points to match downstream integration scenarios:

1. **CPU-only (single Intel Xeon E5 or M2 core)** — matches lambda-style serverless deployment and edge/on-device. This is the PRIMARY target because Pattern B's likely deployment is CPU-based.

2. **GPU (single A100/H100)** — matches LLM-inference-server hardware. RELEVANT for Pattern C parallel-retrieval scenario where substrate co-resides with LLM on same GPU.

Token-gen latency reference points:
- GPT-4-turbo via API: ~30-50ms/token observed
- LLaMA-7B on A100: ~10-20ms/token
- Haiku via API: ~5-15ms/token
- Substrate target: p95 <= 10ms (must be less than slowest production LLM)

The HARD-PASS at 10ms p95 is calibrated to be "always faster than token gen" so substrate retrieval can be prefetched in parallel.

## Coordination with Pattern B (Item 1 of roadmap)

Pattern B has 6-8 week build cost. Properties 1, 2, 3, 6 all feed Pattern B and should be Week-1 priorities. Recommended:

- **Pattern B engineering kickoff:** Week 1
- **Property 1+3+6 results inform Pattern B architecture:** End of Week 2
- **Property 2 result informs Pattern B retrieval-accuracy demo:** End of Week 3
- **Pattern B alpha-pipeline ready:** Week 5-6 (Pattern B's own milestone)
- **Pattern B full demo:** Week 7-8 (Pattern B's own milestone)
- **Properties 4 (full), 5, 7 results:** Weeks 4-6 (parallel)

Pattern B critical path drives the schedule. Property validations are HARNESSES for Pattern B's evaluation, not separate threads.

## Engineering bandwidth recommendation

User said "1-2 weeks each, mostly parallelizable, combined 10-15 weeks but 4-6 calendar with parallelization." Our estimate matches: **11 engineer-weeks, 4-6 calendar weeks with 2 engineers.**

If only 1 engineer is available: 11 calendar weeks (>>3-month roadmap). If 3 engineers: 4 calendar weeks (matches Pattern B's own 6-8 week timeline; properties finish before Pattern B does).

**Recommendation: 2 engineers parallel on properties, 1 engineer dedicated to Pattern B Item 1.** 3 engineers total for the Foundation phase of the 3-month roadmap.

## Honest scope reminder

Per [[feedback-no-smoke]]: validating a property is NOT validating the strategic claim. Property 6 PASS gives us "substrate is deterministic + calibrated UNKNOWN." It does NOT give us "substrate is compliance-grade verifiable for EU AI Act Aug 2026." That requires lawyer review (Item 13). The properties are MECHANICAL witnesses; the strategic claims require additional non-engineering work.

## Risk if NONE of the properties HARD-PASS

Calibrated: probability that ALL 7 HARD-FAIL is roughly the product of (1-P_i) ≈ 0.005 (very low). Probability that 5+ HARD-FAIL is ~5%. The MORE LIKELY adverse scenario: 2-3 HARD-FAIL and 4-5 PASS/middle-band. In that case:

- Compliance positioning survives IF Property 6 PASSes (the load-bearing one)
- Pattern B survives IF Properties 1, 2, 3 jointly land in HARD-PASS or middle-band
- Pattern C path closes IF Property 4 OR Property 5 HARD-FAIL

Worst credible outcome: Property 6 HARD-FAIL would force compliance positioning back to first principles. This is the single highest-risk property to monitor.

## Files referenced

- d:/AI/hd-instrument/notes/strategic_roadmap_llm_integration_3mo_v278_2026-05-29.md (Item 2 source)
- d:/AI/hd-instrument/notes/research_surge_synthesis_v276_2026-05-29.md (v277 surge context)
- d:/AI/hd-instrument/notes/research_quantum_analog_dwave_for_classical_v278_2026-05-29.md (secondary positioning context)
- d:/AI/hd-instrument/notes/research_coherent_multihop_qe2_v278_2026-05-29.md (multi-hop coherent propagation context; relevant to Property 3 cliff)

## Citations (verified count: 0 new external)

This is an engineering-design document, not a literature scan. External citations are not the deliverable form. Internal cross-references to v276-v278 surge notes are documented above.

Calibration: P_deflated values are deflated by 0.15-0.25 per [[feedback-lit-scan-calibration-penalty]] from naive engineering estimates; novel-synthesis cap (P<=0.50) applied to Property 4 only (the speculative one).
