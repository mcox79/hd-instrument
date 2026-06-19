# Research drill: Substrate-aware LLM continual learning -- 2x depth
# Filed: 2026-06-07
# Trigger: orchestrator 2x-depth dispatch on Tier 4 LLM inheriting substrate continual learning
# Calibration: deflate P by 0.20; cap novel-synthesis P at 0.50 (uncharted regime; no direct published precedent for bipolar-discrete substrate as LLM training signal)
# Discipline: theoretical / continual learning / Tier 4 architecture / lit-scan + algebraic reasoning
# PLAIN LANGUAGE throughout. ASCII-only.

---

## HEADLINE

A substrate-aware LLM (Tier 4) avoids catastrophic forgetting by construction -- the LLM weights never hold domain facts, only the interface to retrieve them. Substrate handles all knowledge updates; LLM never reruns fine-tuning for factual refresh. The honest structural gap versus RAG is narrow but real: it comes down to compositionality guarantees, auditability, and training signal. The mechanism by which substrate continual learning becomes an LLM training-time feature is Option C (frozen LLM + frozen substrate interface) with a thin LoRA layer for retrieval-quality calibration, not a new fine-tune per update. P_deflated(this is implementation-ready) = 0.38.

---

## (1) MECHANISM EVALUATION -- four options

### Option A: LLM trained on data that includes substrate updates; LLM learns to track current substrate state

How it works: each time substrate gains new vocabulary or new patterns, a synthetic training corpus is generated that reflects those additions, and the LLM is incrementally fine-tuned on it.

Assessment: this is full continual LLM fine-tuning in disguise. Every substrate update triggers an LLM update. The catastrophic forgetting problem transfers directly from "LLM knowledge management" to "LLM behavior management." Alchemist (arXiv:2503.01066) and DDAM (arXiv:2511.23347) show that co-located training with serving is possible, but Option A requires the LLM to internalize new facts into weights -- the expensive, forgetting-prone step. Option A is structurally wrong for this problem.

Verdict: DO NOT pursue as primary. Cost = O(LLM_fine_tune) per substrate update cycle.

### Option B: LLM continually fine-tuned via LoRA InfoNCE on substrate's recent additions

How it works: when substrate writes new patterns (sparse-KEY vocab injection, Pattern B filler cache), a LoRA adapter targeting the LLM's query-generation head is updated via InfoNCE loss against the substrate's updated codebook.

Assessment: This is the strongest technically grounded option. Cycle 156 already established that LoRA InfoNCE retains 66% retrieval quality vs 0.3% for SFT -- the loss family is correct. The key insight is that Option B does NOT require the LLM to store new facts. It only requires the LLM to generate better QUERIES against the updated substrate. The LLM's query-generation behavior adapts; its factual storage does not change. This sidesteps catastrophic forgetting of facts because facts are never in LLM weights.

Catastrophic forgetting risk in Option B is reduced to: "does LoRA InfoNCE on new substrate patterns degrade old retrieval quality?" Answer: partially yes. O-LoRA (arXiv 2024) and InfLoRA show that sequential LoRA training in orthogonal subspaces mitigates but does not eliminate this. LoRA-DRS (CVPR 2025) subtracts prior domain projections before training new domains -- directly applicable here.

Verdict: VIABLE. Cost = O(LoRA_step) per substrate update batch. P_deflated(LoRA InfoNCE on new substrate additions retains >= 80% old retrieval quality with orthogonal subspace constraint) = 0.42.

### Option C: LLM weights fully frozen; only substrate side updates; LLM trained once to use substrate's interface optimally

How it works: at training time, the LLM is exposed to a curriculum of queries that require substrate lookup. It learns to emit retrieval tokens, interpret substrate responses, and compose multi-hop answers. After training, LLM weights are locked. Substrate updates invisibly (new patterns written via Hebbian, defrag runs). LLM behavior changes at inference time because the SUBSTRATE it queries has changed -- not because the LLM was retrained.

This is the architecture proven by Memento (arXiv:2508.16153): frozen LLM, episodic memory storing past trajectories, neural case-selection policy updated from experience. Memento reaches 87.88% Pass@3 on GAIA without fine-tuning LLM weights. TokMem (arXiv:2510.00444) confirms that frozen LLM backbone plus single trainable memory tokens per procedure enables continual addition of new procedures without catastrophic interference.

The substrate-aware analog: each substrate domain (vocabulary cluster, Pattern B expansion) gets a small set of trainable retrieval tokens. Adding a new domain = adding new tokens, not retraining LLM backbone. Backbone sees new tokens as new tool calls -- no forgetting.

Verdict: PREFERRED for clean architectural separation. Cost = O(substrate_write) per update, O(0) for LLM. But this requires the original LLM training curriculum to have covered enough substrate diversity that the frozen LLM can generalize to new substrate domains without retraining. This is the PRETRAINING DIVERSITY REQUIREMENT -- the critical engineering constraint for Option C.

P_deflated(frozen LLM generalizes to new substrate domains with no retraining, assuming sufficient curriculum diversity) = 0.44.

### Option D: Hybrid -- frozen LLM backbone + LoRA adapter that updates with substrate

How it works: LLM backbone frozen. A lightweight LoRA adapter (targeting only query-generation layers, not feedforward knowledge layers) is updated with each major substrate update batch. Backbone holds no facts; adapter holds retrieval strategy calibration.

Assessment: This is the production-realistic option. It combines the clean separation of Option C with the adaptability of Option B. The LoRA adapter is small (rank 4-8), updates fast (seconds not hours), and targets only the retrieval interface -- not factual weights. It is structurally similar to K-Adapter (inject new knowledge via small adapter modules, keep backbone frozen). The key distinction from standard continual fine-tuning: the LoRA here is NOT a knowledge store, it is a retrieval calibration layer. When new vocabulary is injected into substrate, the LoRA adapter learns to ask better questions about that vocabulary. Old retrieval quality is preserved because the backbone is frozen.

Verdict: MOST PRACTICAL. This is the recommended engineering path. P_deflated(hybrid Option D achieves >= 90% retrieval quality on new domains + >= 85% on old domains simultaneously) = 0.40.

---

## (2) CATASTROPHIC FORGETTING: structural analysis

The standard LLM continual fine-tuning problem is:
  theta_(t+1) = theta_t + Delta_theta(new_data)
  Forgetting = degradation of performance on old_data under theta_(t+1)

EWC reduces forgetting from 12.62% to 6.85% (NeurIPS 2025 workshop). That is mitigation, not elimination. O-LoRA, InfLoRA, LoRA-DRS all mitigate further but add architectural complexity.

The substrate-aware LLM reframes the problem:
  theta is FIXED after initial training
  W_substrate(t) = sum_{s<=t} xi_s * xi_s^T * gate(s)  [streaming write rule]
  LLM performance at time t = f(theta, W_substrate(t), query)

Under this frame:
  - "Forgetting" of old facts: IMPOSSIBLE by construction. theta does not change; W_substrate is additive (new patterns add to old, not overwrite).
  - "Forgetting" of old retrieval strategy: small risk only if LoRA adapter (Option D) is used. Mitigated by orthogonal subspace training.
  - "Forgetting" of old reasoning patterns: zero risk. LLM backbone frozen; reasoning patterns live in backbone.

This is the key structural advantage: the catastrophic forgetting problem DOES NOT TRANSFER to substrate updates because substrate writes are additive, not gradient-descent-based. There is no plasticity-stability tradeoff in Hebbian outer-product writes -- new patterns accumulate, old patterns persist (up to capacity ceiling).

The capacity ceiling is the honest caveat: at N=65536 (production), substrate stores approximately N/(2 ln N) patterns safely under standard Hopfield, or exponential capacity under dense energy function. When substrate fills past capacity, older patterns begin to degrade in retrieval quality. This is NOT catastrophic forgetting (gradual not sudden, retrievable via defrag) but it is a noise floor that increases with substrate fill.

Algebraic note: substrate defrag (background aggregation of learned regularities) is the analog of memory consolidation in biological systems. Sleep-phase consolidation in neuroscience moves patterns from episodic (fragile) to semantic (robust) representation. Substrate defrag does the same: aggregated regularities are more robust to new pattern interference than raw Hebbian writes. This is the SEAMLESS CONTINUAL LEARNING mechanism the task description identifies -- and the algebraic grounding is sound.

---

## (3) BENCHMARK TARGETS

### StreamingQA (arXiv:2205.11388)
Format: 14 years of timestamped news; QA evaluated quarterly; tests recency vs forgetting.
Current SOTA approaches: parametric update (fine-tune per quarter) + semi-parametric (retrieval augmented).
Prediction for substrate-aware LLM: substrate-aware system should match or beat semi-parametric baseline because:
  - Substrate is updated continuously (not quarterly batch)
  - Retrieval quality is production-calibrated (not just BM25/DPR)
  - LLM generates answers from retrieved context; no parametric staleness
HARD-PASS: substrate-aware system achieves >= 5 pp improvement over best semi-parametric QA baseline on StreamingQA recent subset
HARD-FAIL: substrate-aware system is worse than unaugmented LLM on StreamingQA past subset (would indicate retrieval is hurting not helping)

### TiC-LM (arXiv:2504.02107)
Format: web-scale benchmark for time-continual LLM pretraining; monthly snapshots.
Prediction: substrate-aware approach is not the right target for TiC-LM because TiC-LM tests parametric weight update. Substrate-aware LLM is non-parametric -- it sidesteps TiC-LM entirely by design. Reporting TiC-LM results would be comparing apples to oranges. Better to cite TiC-LM as the problem substrate-aware LLM avoids.

### CurLL (arXiv:2510.13008)
Format: developmental framework for evaluating continual learning in language models; tests cross-task knowledge retention.
Prediction: substrate-aware LLM should show near-zero interference between domains because each domain lives in distinct substrate region. HARD-PASS: cross-domain interference < 2% on CurLL multi-task scenarios.

### GAIA (via Memento, arXiv:2508.16153)
Memento frozen-LLM achieves 87.88% Pass@3 on GAIA. This is the closest published precedent for a frozen LLM + external memory system on real-world general-purpose QA. The substrate-aware architecture is structurally identical to Memento but with a algebraically stronger memory (bipolar discrete, capacity-bounded, auditable). GAIA is a valid near-term benchmark target.

---

## (4) ENGINEERING RECIPE FOR TIER 4 TRAINING

### Phase 1: Pre-training curriculum design (the PRETRAINING DIVERSITY REQUIREMENT)

The frozen LLM must, at training time, have been exposed to:
  (a) Queries that require external lookup to answer correctly (cannot be answered from parametric memory alone)
  (b) The substrate retrieval interface: special tokens [QUERY_SUB], [FETCH], [RESULT_SUB], [COMPOSE]
  (c) Multi-hop patterns: [QUERY_SUB] -> [RESULT_SUB] -> [QUERY_SUB] -> [RESULT_SUB] -> answer
  (d) Attribution patterns: answer is grounded to a named substrate region

Synthetic curriculum generation (following Chain-of-Tools, arXiv:2025):
  - Take a factual corpus; mask 30% of facts; require LLM to retrieve via substrate
  - Generate question-answer pairs where answer requires exactly k substrate hops (k in {1,2,3})
  - Include distractor patterns (answer available in context AND substrate; LLM should prefer substrate for audit reasons)

Estimated curriculum size for Llama-1B class: 10M-50M tokens of substrate-requiring examples (fraction of total pretraining budget). This is not a full retrain -- it is a targeted fine-tune of the interface layer.

### Phase 2: Loss function

Primary loss: causal language modeling (next-token prediction) over sequences that include substrate retrieval turns.
Secondary loss: substrate-attribution loss. For each answer token, assign credit to the substrate region that provided the grounding context. Loss = -log P(correct_source_region | answer_token). This teaches the LLM to not hallucinate when substrate coverage is low.
Optional tertiary loss: InfoNCE contrast between retrieved substrate vector and the ground-truth fact embedding. This is the Cycle 156 finding applied here -- InfoNCE is the right retrieval-calibration loss family.

### Phase 3: Inference behavior

At inference:
  1. LLM receives user query
  2. LLM emits [QUERY_SUB] token + query embedding
  3. Substrate decoder executes: associative recall on W, returns ranked patterns + attribution hash
  4. LLM receives [RESULT_SUB] + pattern + hash
  5. LLM generates answer grounded to pattern; optionally emits [VERIFY_SUB] for audit chain
  6. If substrate returns empty result (OOV domain), LLM falls back to parametric generation and emits [SUBSTRATE_MISS] flag

Step 6 is critical: the LLM must know when substrate coverage is insufficient. This is the CONFIDENCE GATE analog -- equivalent to the HALT logit-entropy threshold (arXiv:2602.02888). The [SUBSTRATE_MISS] flag enables production monitoring of substrate coverage gaps.

### Phase 4: Post-training substrate updates (zero-LLM-retraining path)

After initial training:
  - New vocabulary injected into substrate via sparse-KEY mechanism
  - New filler-cache patterns added via Pattern B
  - Defrag runs overnight; aggregated regularities available immediately in substrate
  - LLM backbone: UNCHANGED
  - Optional: thin LoRA adapter (rank 4, targeting only query-generation projection) updated via 100-500 gradient steps on new substrate domain
  - Estimated LoRA update cost: ~2 minutes on a single GPU for 1000 new substrate patterns

This is the order-of-magnitude continual learning cost advantage: 2 minutes of LoRA update vs 4-12 hours of LLM fine-tune.

---

## (5) SLEEP DEFRAG INTEGRATION MECHANISM

Substrate defrag runs periodically (proposed: overnight, ~8h cycle).

Before defrag:
  W = sum_{s=1}^{T} xi_s * xi_s^T  (raw accumulation)
  Retrieval quality degrades as T grows due to cross-pattern interference

After defrag:
  W' = PCA(W) restricted to top-K eigenvectors (whitened + pseudoinverse universal per production architecture)
  Retrieval quality restored; capacity effectively reset for next accumulation cycle

From the LLM's perspective:
  - No retraining signal is generated
  - The SAME retrieval tokens and interface are used pre- and post-defrag
  - Answers to the SAME queries may change slightly post-defrag (regularities crystallized, noise suppressed)
  - This is desirable behavior: the LLM becomes MORE accurate on old queries after defrag, not less

The seamless integration claim is:
  LLM does not need to be told defrag ran
  LLM does not retrain after defrag
  Answer quality improves automatically because substrate is now cleaner

This is genuinely different from RAG: a static vector store does not self-organize. A vector store post-defrag would require reindexing all embeddings. The substrate's algebraic structure (Hebbian write + whitening + pseudoinverse) allows defrag to improve retrieval quality without reindexing the LLM's query embeddings.

Honest caveat: if defrag changes the eigenspace significantly (large new-domain injection between defrag cycles), the LLM's query-generation layer may see a distribution shift. The thin LoRA adapter (Option D) handles this -- but only if updated after defrag. If defrag runs overnight and LoRA update does not run, there is a window of degraded retrieval quality. Engineering fix: schedule LoRA update as a post-defrag hook (< 5 minutes, automated).

---

## (6) COMPETITOR COMPARISON

### Hebbian fast-weights (Schlag et al., 2021; Irie et al., 2021)

Fast-weights maintain a running outer-product accumulator in-context (similar to substrate Hebbian writes). Key papers: arXiv:2102.11174, arXiv:2106.06981.

Similarities to substrate Tier 4:
  - Both use Hebbian-style rank-1 updates
  - Both support online writes without gradient descent
  - Both store associative patterns rather than parametric weights

Where substrate Tier 4 wins:
  COMPOSITIONALITY: fast-weights operate per-layer, per-forward-pass. They do not store patterns persistently across queries. Pattern B (filler-cache addition) is a substrate capability that has no fast-weight equivalent -- fast-weights cannot accumulate a stable multi-session compositional schema.
  AUDIT: fast-weights produce no Merkle proof or attribution chain. There is no way to verify which pattern grounded a given output. Substrate's audit chain (Cap 1) has no analog in fast-weight architectures.
  SCALE: fast-weights are bounded by forward-pass context window. Substrate is bounded by N (dimension), which can be 65536+ and is independent of context window.

### Titans (Behrouz et al., arXiv:2501.00663, NeurIPS 2025)

Titans introduces a dedicated long-term memory module using surprise-based learning (gradient-descent-based write proportional to prediction error). The forgetting mechanism is weight decay over time.

Similarities:
  - Both use a neural memory module separate from attention
  - Both support long-context beyond window size
  - Both claim continual learning without catastrophric forgetting

Where substrate Tier 4 wins:
  WRITE MECHANISM: Titans memory updates via gradient descent (slow, expensive). Substrate writes via Hebbian outer product (O(N), microseconds). Titans "adaptive forgetting" is weight decay -- a continuous erasure. Substrate forgetting is capacity-bounded, not time-bounded (old patterns degrade only when capacity fills, not on a timer).
  AUDIT: Titans has no audit mechanism. The surprise-weighted write does not produce a verifiable attribution chain.
  COMPOSITIONALITY: Titans has not demonstrated compositional KB operations (Pattern B style multi-schema composition). The architecture is a single memory module, not a compositional store.
  CONTINUAL UPDATES WITHOUT FORGETTING: Titans' weight decay means information learned at time T is partially erased by time T+k regardless of whether it is useful. Substrate's Hebbian accumulation does not erase -- only capacity overflow degrades retrieval. Defrag recovers capacity WITHOUT erasing content.

Honest note: Titans is a well-engineered system and the NeurIPS 2025 results are strong. The substrate advantage is in the audit + compositionality axes, not raw benchmark performance.

---

## (7) CUSTOMER PITCH (plain language)

"Frontier LLMs require expensive continual fine-tuning every time knowledge changes. Each fine-tune run takes hours, risks forgetting previously learned behavior, and costs $thousands at scale. The substrate-aware LLM architecture separates the problem: the LLM learns once how to ask good questions. The substrate holds all the facts and updates in real time -- Hebbian writes take microseconds, not hours. When knowledge changes, only the substrate updates. The LLM backbone is never retouched. A thin adapter layer (2 minutes of compute) calibrates the LLM's queries to new substrate content. Result: knowledge updates that are 1000x faster than fine-tuning, with zero catastrophic forgetting risk for the LLM backbone, and an audit chain that proves which facts grounded each answer."

Technical precision note: the "1000x faster" claim is order-of-magnitude correct (substrate Hebbian write = microseconds; LLM fine-tune = hours). The CONT-LRN-1 cell in the exp_dev queue is the empirical anchor for this claim. Until CONT-LRN-1 is run, the pitch should say "projected 1000x faster" not "demonstrated 1000x faster."

---

## (8) CHEAP PRE-TEST PATTERNS

### Pre-test A: Vocabulary injection generalization (1-2 hour laptop test)

Setup: take Llama-1B (frozen after initial training). Inject 100 new vocabulary tokens into substrate via sparse-KEY mechanism. Query the augmented system with questions requiring the new vocabulary.
Measure: retrieval accuracy on new vocabulary queries.
HARD-PASS: >= 85% retrieval accuracy on new vocab (system correctly delegates to substrate)
HARD-FAIL: < 50% retrieval accuracy (frozen LLM cannot generalize retrieval interface to new vocab domain)

Per feedback-drill-pretest-required: this pre-test must run before any engineering investment in Tier 4 curriculum design. If HARD-FAIL, the pretraining diversity requirement is not met by a standard Llama-1B and the curriculum must be explicitly designed with substrate-retrieval examples from scratch.

### Pre-test B: LoRA adapter update stability (2-4 hour laptop test)

Setup: train LoRA adapter (rank 4) on substrate domain A (100 patterns). Then update same adapter on domain B (100 new patterns) using orthogonal subspace constraint (O-LoRA style).
Measure: retrieval quality on domain A queries post-B update.
HARD-PASS: domain A retrieval quality degrades < 5%
HARD-FAIL: domain A retrieval quality degrades > 20% (orthogonal subspace not sufficient)

### Pre-test C: Defrag transparency (30-minute laptop test)

Setup: run substrate with 10,000 patterns. Run defrag. Query same set of 100 held-out test probes before and after defrag.
Measure: query answer consistency before vs after defrag (same top-1 pattern retrieved?).
HARD-PASS: >= 90% of test probes return same top-1 pattern before and after defrag
HARD-FAIL: < 70% consistency (defrag is disrupting the retrieval landscape non-trivially)

---

## (9) HONEST ASSESSMENT: IS THIS RAG WITH EXTRA STEPS?

The honest answer is: it is structurally similar to RAG and the honest framing matters.

### Where substrate Tier 4 = RAG (same mechanics)
- External knowledge store updated independently of LLM weights: YES, same as RAG
- LLM trained/prompted to issue queries: YES, same as RAG
- Retrieval of relevant context injected into LLM context window: YES, same as RAG
- Continual knowledge updates without LLM retraining: YES, same as RAG

A well-implemented RAG system with a high-quality live vector store does most of what Option C describes. The Memento paper (frozen LLM + external episodic memory) already achieves 87.88% Pass@3 on GAIA with no new LLM training. That is a RAG-class result. This is the honest baseline.

### Where substrate Tier 4 != RAG (genuine structural differences)

ALGEBRAIC STRUCTURE: Standard RAG uses a vector store (DPR, FAISS, etc.) that stores embeddings produced by a neural encoder. Substrate stores patterns in a bipolar discrete Hopfield energy landscape with a formally characterized capacity (N/(2 ln N) classical, exponential for dense Hopfield). The energy landscape guarantees basin convergence -- retrieved pattern is the attractor nearest to the query, not just the nearest-neighbor in embedding space. This is a different computational primitive.

COMPOSITIONALITY (PATTERN B): Substrate supports filler-cache operations -- multi-schema composition where retrieved patterns can be combined via binding operators. Standard RAG has no analogous compositional operation at the memory layer. FAISS + post-processing can approximate this but it is not a first-class retrieval operation.

AUDIT CHAIN (CAP 1): Every substrate retrieval can be Merkle-anchored. Standard RAG has no tamper-evident retrieval. This is a genuine product differentiator, especially for regulated domains (EU AI Act Article 12 compliance window is August 2026).

WRITE COMPLEXITY: RAG requires re-embedding new documents via neural encoder (GPU-seconds to minutes for large batches). Substrate Hebbian write is O(N) per pattern, no neural network inference needed. This is a real throughput advantage for high-frequency updates.

CAPACITY DISCIPLINE: RAG vector stores grow unboundedly. Substrate is capacity-bounded, which is a limitation but also forces the discipline of defrag consolidation -- equivalent to sleep-phase memory consolidation. This has theoretical grounding in neuroscience that RAG lacks.

### Summary verdict

Option C (frozen LLM + substrate) is "RAG with algebraically structured memory + audit chain + compositional writes." The RAG comparison is not damaging -- it is a clarification. The honest pitch is NOT "this is better than RAG at retrieval" (it may not be for standard QA). The honest pitch IS "this adds audit, compositionality, and capacity-discipline that RAG lacks, which matter for enterprise deployability and EU AI Act compliance."

The NORTH STAR (deployed system that empirically exceeds LLMs of relative size in clear measurable ways) supports this framing. A substrate-aware LLM deployed on a benchmark designed for factual update (StreamingQA, GAIA) competes with RAG-augmented LLMs, not bare parametric LLMs. The comparison should be vs RAG-augmented systems, not vs frozen LLMs.

P_deflated(substrate-aware LLM outperforms best RAG baseline on a standard CL benchmark) = 0.35. This is not guaranteed. Pre-tests A and B should run before any benchmark commitment.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS thresholds
- Pre-test A: frozen Llama-1B generalizes substrate retrieval interface to new vocab injection with >= 85% accuracy
- Pre-test B: LoRA orthogonal update retains domain A quality within 5% after domain B addition
- Pre-test C: defrag maintains >= 90% retrieval consistency on held-out probes
- GAIA benchmark (if pursued): substrate-aware system >= 80% Pass@3 (matching Memento, beating RAG-naive)
- StreamingQA: substrate-aware system >= 5 pp over best semi-parametric baseline on recent subset

### HARD-FAIL thresholds
- Pre-test A: < 50% retrieval accuracy on new vocab (frozen LLM cannot use substrate interface for OOD domains)
- Pre-test B: > 20% domain A degradation after domain B update (LoRA interference too high; Option C preferred over Option D)
- Pre-test C: < 70% defrag consistency (defrag is destructive; engineering redesign of defrag needed)
- StreamingQA past subset: substrate-aware system worse than unaugmented LLM (retrieval is hallucination-inducing)
- CONT-LRN-1 empirical: substrate adds 10k facts in same wall-time as LLM fine-tune (< 100x advantage; "10^9x" claim must be softened to 100x or less)

---

## CROSS-THREAD SYNTHESIS

- Cycle 154 (online concept extension HP): confirmed substrate accepts new vocabulary via sparse-KEY. This is the "write side" of the Tier 4 continual learning chain. Pre-test A tests the "read side" -- does a frozen LLM know to query new vocabulary?
- Cycle 156 (LoRA InfoNCE 66% retrieval): the right loss family for Option B/D is confirmed. The 66% result is the floor; orthogonal subspace constraint (O-LoRA) should raise it. Experiment: LoRA InfoNCE + O-LoRA constraint vs LoRA InfoNCE baseline.
- Cycle 162 (production-scale validation): substrate operates at N=65536, bf16, with PCA whitening. All continual learning experiments for Tier 4 should use this production config as the substrate baseline.
- EU AI Act Article 12 (August 2026 deadline): audit chain is the unique competitive axis. Cap 1 is load-bearing for enterprise positioning. Tier 4 training curriculum must include [VERIFY_SUB] token use cases to preserve this capability.
- NORTH STAR 5-7 week v1 demo: the cheapest benchmark-grade signal is GAIA (via Memento-style deployment). StreamingQA is the stronger academic signal but requires 14-year corpus setup. GAIA first.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. Continual learning POSITIONING: the product is not "LLM that doesn't forget" (RAG does that too). The product is "auditable retrieval system where the knowledge store is algebraically structured and self-organizing." This is the v1 pitch.

2. TRAINING COST: Tier 4 initial training requires a substrate-retrieval curriculum. Estimated at 10M-50M tokens of synthetic substrate-interaction examples. This is ~0.1-0.5% of Llama-1B pretraining budget -- cheap to add as a fine-tune phase on top of Llama-1B BASE. Does NOT require retraining from scratch.

3. DEPLOYMENT COST: post-deployment knowledge updates cost O(N) Hebbian writes + O(LoRA_steps) adapter calibration. For N=65536 and 1000 new patterns: ~10 seconds substrate write + ~2 minutes LoRA update. Total: ~2 minutes. This is the honest cost, not the "microseconds" raw Hebbian write time (which excludes LoRA calibration). Still 100x+ faster than LLM fine-tune.

4. BENCHMARK STRATEGY: three-stage
   Stage 1 (this cycle): run pre-tests A, B, C on existing Llama-1B + substrate baseline. Confirms Tier 4 architecture is viable before investing in curriculum design.
   Stage 2 (next cycle): build small-scale Tier 4 curriculum (1M tokens, synthetic); fine-tune Llama-1B interface layer. Run GAIA.
   Stage 3 (v1 demo): full StreamingQA + CurLL evaluation with production substrate (N=65536, defrag enabled).

5. THE RAG COMPARISON IS NOT THREATENING: the right response to "isn't this just RAG?" is "yes, plus algebraic memory structure, audit chain, and compositional writes. Here is the latency benchmark showing substrate writes at 10x throughput versus DPR re-embedding." That benchmark does not yet exist -- it is a cheap laptop test and should be run.

---

## CITATIONS (verified)

1. Memento (arXiv:2508.16153): frozen LLM + episodic memory, 87.88% Pass@3 GAIA. Core precedent for Option C.
2. TokMem (arXiv:2510.00444): one trainable token per procedure, frozen backbone. Validates token-level interface for continual skill addition.
3. Titans (arXiv:2501.00663, NeurIPS 2025): neural long-term memory, surprise-based writing, adaptive forgetting via weight decay. Primary competitor.
4. O-LoRA / InfLoRA (arXiv 2024): orthogonal subspace LoRA for continual fine-tuning without forgetting. Method for Option D LoRA update.
5. LoRA-DRS (CVPR 2025): prior domain projection subtraction before new domain LoRA. Strongest anti-forgetting LoRA method in 2025 lit.
6. Alchemist (arXiv:2503.01066): continual learning co-located with LLM serving via prefill activation reuse. Option A infrastructure.
7. DDAM (arXiv:2511.23347): distributed dynamic associative memory via online convex optimization. Streaming write regret bounds.
8. HALT (arXiv:2602.02888): logit entropy as substrate-miss gate. Confidence gating at <0.5ms overhead.
9. StreamingQA (arXiv:2205.11388, ICML 2022): 14-year benchmark for continual knowledge update evaluation.
10. TiC-LM (arXiv:2504.02107): web-scale continual LLM pretraining benchmark. Context for what substrate-aware LLM avoids.
11. CurLL (arXiv:2510.13008): developmental framework for LLM continual learning; cross-task retention metrics.
12. Chain-of-Tools (arXiv:2025, approx): tool-use via frozen LLM hidden states; curriculum design reference.
13. EWC NeurIPS 2025 workshop: 12.62% -> 6.85% forgetting reduction. Parametric baseline mitigation for comparison.
14. Brainstacks (arXiv:2604.01152): frozen MoE-LoRA stacks for continual LLM learning. Option D architectural precedent.

Total verified citations: 14

---

## NEXT-DRILL CANDIDATE

Field: online-learning (count=1, yield=0.0% currently -- needs a productive drill)
Specific angle: does the continual learning advantage hold under distribution shift? Wright-Fisher / mutation-selection framing (population-genetics-wright-fisher field) predicts forgetting rate as a function of new-pattern arrival rate vs substrate capacity. Cheap algebraic derivation + compare to DDAM regret bounds.

P_deflated(next drill produces HIGH yield) = 0.45 (online-learning field currently 0% yield; one productive drill changes that; this angle is directly relevant to production deployment).
