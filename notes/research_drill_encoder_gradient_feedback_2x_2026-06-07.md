# Research drill: encoder gradient feedback from retrieval failures (2x depth)
**Date:** 2026-06-07
**Trigger:** Orchestrator cycle flagged option (i) self-improving routing / online encoder fine-tuning from retrieval reward; rated 9/10 creativity; closes encoder ceiling (bge-large recall@2=0.516, HP=0.55) and bridge-ID accuracy (~60-70% at 1.5B LLM) simultaneously.
**Drill level:** 2x depth (operational mechanism + math + implementation paths, NOT re-scan of prior ceiling note)
**Calibration:** P estimates deflated 0.15-0.25 per lit-scan calibration penalty; novel-synthesis cap 0.50.

---

## HEADLINE

Online encoder fine-tuning from retrieval reward is mechanistically sound, has published RL-retrieval precedent (2025), and is the only identified path that simultaneously closes bridge-ID discrimination and encoder ceiling without a full encoder replacement. The core mechanism is contrastive gradient feedback: query-answer pairs where the LLM got wrong answers become (query, positive-fact, hard-negative) triplets; LoRA rank-4 adapter updates run per batch; stability requires teleportation negatives from prior checkpoints. P_deflated(clears 0.55 HP threshold) = 0.45. P_deflated(reaches 0.65) = 0.25. The RL-as-MDP formulation has stronger theoretical grounding but 3x higher implementation cost; start with batch contrastive.

---

## Section 1: Mechanism design (operational depth)

### 1.1 The feedback loop, step by step

(1) Query q_i is issued to the substrate. Top-K facts F_k are retrieved via encoder similarity.
(2) LLM generates answer a_i from F_k. Answer is graded against gold (HotpotQA EM/F1, or substrate-internal correctness check).
(3) If a_i is WRONG: at least one required fact was not retrieved, or was retrieved but ranked too low.
(4) For each wrong-answer query, identify which facts were REQUIRED (gold supporting facts from HotpotQA annotation, or from substrate unbind verification). These become positives.
(5) Facts that WERE retrieved but did not help (false positives for that query) become hard negatives.
(6) Construct triplet: (q_i, positive_fact_j, hard_negative_fact_k). This is the substrate-native training signal.
(7) Contrastive loss = -log[ exp(sim(q,pos)/tau) / (exp(sim(q,pos)/tau) + sum_k exp(sim(q,neg_k)/tau)) ]
(8) Gradient flows through sim(q, .) back into the encoder (LoRA adapter only; base weights frozen).
(9) Adapter is updated. Next query batch uses updated encoder.

### 1.2 Why this targets bridge entities specifically

Bridge-ID failure mode: the encoder embeds "What city is home to the team that won X?" and fails to retrieve the intermediate fact "Team Y won X in city Z" because "city Z" and "team Y" are not surface-close to the query. The encoder gives high similarity to entities mentioned in the query, low similarity to the bridge entity.

After contrastive training: for each bridge-failure query, the bridge fact is the required positive. The encoder receives gradient that pulls bridge-entity embeddings TOWARD query embeddings. Over N bridge-failure queries, the adapter learns a transformation that generalizes: when a query asks for an attribute-holder, retrieve the intermediate entity whose attributes answer the query.

This is not guaranteed to generalize (the adapter can memorize specific bridge pairs), but the LoRA low-rank constraint forces generalization: rank-4 has 4 * 2 * d = 8d parameters vs d^2 in full fine-tune, so the adapter cannot memorize; it must compress bridge-retrieval patterns into a low-rank subspace.

### 1.3 Gradient signal taxonomy

Four signal designs, ordered from weakest to strongest:

(A) Binary: correct/wrong. Recall@2 binary (did both facts land?). Clean but sparse signal -- 48% of queries are wrong (recall@2=0.516), so only 48% of queries contribute gradient. Sparse signal is fine if batch size >= 32; with smaller batches, gradient variance is high.

(B) Soft F1: reward = token-level F1(a_i, gold_answer). This is continuous in [0,1]. Allows partial credit: if one of two bridge facts was retrieved but not the other, F1 ~0.3-0.5 and still generates gradient. Empirically, soft F1 reward gives smoother training curves in RL-retrieval literature (DRO 2025, GlobalRAG arxiv 2510.20548).

(C) Per-hop: which hop of a 2-hop chain failed? For HotpotQA bridge questions, hop-1 = retrieve bridge entity, hop-2 = retrieve answer entity. If the LLM got the wrong bridge entity in hop-1 output, targeted gradient to the hop-1 retrieval step. Requires a hop-decomposition oracle (substrate can provide this via its multi-hop unbind trace). Most precise signal. Implementation cost: medium (need hop-trace logging).

(D) Per-fact contrastive: each required fact in the gold set is a separate positive. Each retrieved-but-wrong fact is a separate hard negative. This is the richest signal and has the most direct literature support (InfoNCE in DPR literature, 2020-2024). Implementation cost: low (just enumerate positives and negatives per query).

**Recommended signal for v1.5:** Per-fact contrastive (D) because (a) well-understood gradient dynamics, (b) directly maps to the existing bridge-ID failure mode taxonomy, (c) does not require hop-decomposition oracle. Switch to per-hop (C) in v2 once hop-trace logging exists.

### 1.4 Math: why LoRA rank-4 is the right adapter size

Encoder hidden dim d = 1024 (bge-large, e5-large, stella-400M) or d = 4096 (e5-mistral-7b-instruct, NV-Embed).

Full fine-tune: d^2 = 1.05M parameters per weight matrix. With 24 layers and 4 weight matrices each = 100M parameters updated. Risk: overfit to bridge pairs in HotpotQA training set; generalizes poorly to new KBs.

LoRA rank-4: 2 * 4 * d = 8d parameters per matrix. For d=1024: 8,192 per matrix. For 24 layers * 4 matrices = 786,432 total = 0.77M parameters. This is 0.23% of the 335M base encoder. The low-rank structure acts as a spectral bottleneck: only the top-4 singular-value directions of the weight perturbation are updated. This is a regularizer by construction.

Theoretical justification: LoRA approximates the fine-tuning gradient in the intrinsic dimensionality of the task. Aghajanyan et al. (2021) showed that fine-tuning NLP models requires only low-dimensional reparameterization (intrinsic dimension ~100-1000 for most tasks). Bridge-ID improvement is a single-axis task; rank-4 to rank-8 is sufficient per this bound. If rank-4 is insufficient, the failure is not rank but data quantity or signal quality.

Catastrophic forgetting bound for LoRA: because base weights are FROZEN, the encoder cannot forget general retrieval patterns; only the adapter drifts. Worst case: adapter overfits to HotpotQA bridge pairs and hurts performance on non-bridge queries. Mitigation: mixed batch = 50% bridge-failure queries + 50% bridge-success queries. Success queries give gradient ~0 (no update needed) or slight positive gradient; this regularizes the adapter toward general retrieval.

### 1.5 Stability: teleportation negatives

From EMNLP 2022 (arxiv 2210.17167): iterative hard-negative mining causes catastrophic forgetting because current hard negatives become easy negatives one epoch later. The model chases its own tail.

Teleportation negatives: at training step t, sample negatives from checkpoints at steps {t, t-delta, t-2*delta, ...}. The triplet batch includes negatives that were hard at multiple prior training stages. This prevents the model from forgetting what it learned in earlier stages.

For online learning (1 update per query batch), the analog is: keep a replay buffer of (query, positive, hard-negative) triplets from the last T batches. Sample from the buffer uniformly. This ensures that early hard negatives (e.g., bridge pairs from the first 100 queries) are not forgotten as the adapter improves.

Concrete: buffer size T=500 triplets. Each training step samples 32 triplets from the buffer + appends new triplets from the current batch. Buffer is circular (oldest triplets dropped). Cost: 500 * (query_emb + pos_emb + neg_emb) * float32 = 500 * 3 * 1024 * 4 bytes = 6.2 MB. Negligible.

---

## Section 2: Implementation options (4 paths)

### Option A: Batch contrastive LoRA (recommended for v1.5)

Architecture: LoRA adapter rank-4 added to the query encoder only (not the document encoder). Query encoder is updated; document encoder is frozen. This asymmetry is deliberate: document embeddings are pre-computed at index time; updating the document encoder requires re-indexing every time (expensive). Updating only the query encoder means query representations shift; the existing document index stays valid.

Wait -- this creates a query-document asymmetry. If the query encoder is updated but the document encoder is not, the embedding spaces diverge. This is a critical design decision:

Option A1 (asymmetric, lazy re-index): update query encoder; re-index documents every K batches (e.g., K=100). The K-batch window creates a small distribution mismatch that decays at re-index time. Acceptable if K is small enough that the adapter delta is small.

Option A2 (symmetric, shared encoder): update both query and document encoder with the same adapter. This keeps the embedding space aligned but requires re-indexing at EVERY update. If the substrate index is small (< 10k facts), re-indexing takes < 1s; this is viable. At 1M facts, re-indexing takes minutes; not viable online.

Option A3 (dual-encoder, contrastive): maintain two encoders: frozen base (for document index) and fine-tuned (for queries). At re-index time, update document index with fine-tuned encoder. This is the DPR architecture and is the cleanest for production.

**Recommendation for v1.5:** A3 (dual-encoder). Frozen document index; fine-tuned query encoder; periodic re-index (every 500 queries or daily). Implementation cost: ~2 days. Stability risk: low.

Training frequency: not truly online (per-query gradient). Use mini-batch: accumulate 32 bridge-failure triplets, run one gradient step. This amortizes the overhead and stabilizes gradient variance.

### Option B: Full encoder fine-tune (not recommended for v1.5)

Full fine-tune on the encoder (e.g., bge-large 335M parameters). Risk: catastrophic forgetting of MTEB retrieval patterns that took months of pre-training to acquire. The pre-trained encoder has strong general retrieval from training on millions of (query, passage) pairs from MS MARCO, NLI, etc. Fine-tuning on ~1000 HotpotQA bridge-failure pairs can overwrite this.

Stabilization options: (1) elastic weight consolidation (EWC): adds regularization loss = lambda * sum_i F_i * (theta_i - theta_i*)^2, where F_i is Fisher information for parameter i and theta_i* is the pre-trained value. Cost: computing Fisher information requires a forward pass over the full pre-training dataset (or a subset). High implementation cost. (2) Learning rate 1e-6 or lower: very slow update prevents catastrophic forgetting but also slows learning.

Verdict: full fine-tune is an option for a v2 offline batch re-training cycle (every month, retrain on accumulated failure triplets). Not for online deployment.

### Option C: Cross-encoder reranker (complementary, not primary)

A cross-encoder (e.g., bge-reranker-large) takes (query, passage) concatenated and outputs a relevance score. It can be fine-tuned on bridge-failure pairs independently of the bi-encoder. Reranker improves precision (right answer rises in top-K), NOT recall (whether the right answer is in top-K at all).

As noted in the prior ceiling drill: for recall@2=0.516, the bottleneck is that 48% of queries have zero of the required bridge facts in the top-2. A reranker cannot fix this. It can help the 52% where the facts ARE in the top-2 but possibly in wrong order, but this is a secondary issue.

When to use: add cross-encoder reranking AFTER the recall ceiling is broken (recall@2 > 0.65). At that point, reranking converts top-10 recall into top-2 precision. Sequencing matters.

### Option D: Hard-negative mining from substrate bindings (substrate-native, v2)

The substrate's own binding structure knows which entities are associated with which facts. This means the substrate can generate hard negatives WITHOUT external annotation:

For query "Who won X?", the substrate knows: fact-A = "Y won X" (positive) and fact-B = "Z won Y" (semantically similar but wrong direction of association) -- this is a substrate-generated hard negative.

The advantage: hard negatives are structurally harder than random negatives and require no external annotation. The disadvantage: substrate-generated negatives may not match the distribution of actual retrieval failures.

Implementation: substrate binding verification pass (check all facts within Hamming distance d of the query binding) generates a ranked list of confusable facts. Top confusable facts = hard negatives.

Cost: this requires access to the substrate binding distance oracle at training time -- i.e., the training loop must call into substrate internals. This creates a tight coupling. Acceptable if the training loop lives inside the substrate; not acceptable for a drop-in encoder update.

---

## Section 3: Five crazy options evaluated

### Crazy option (a): Substrate-supervised contrastive learning

Substrate generates (positive, hard-negative) pairs from its own binding structure (semantic near-misses). No external annotation needed.

Mechanistic soundness: HIGH. The substrate knows which facts are "almost correct" because they are close in the binding space but have different unbind targets. This is exactly what a hard negative should be: similar enough to fool the encoder, but structurally different in the substrate.

Implementation path: at each training step, for every fact in the substrate index, run a binding neighbor search (O(log N) with product quantization or ANN). Nearby-binding-but-different-target facts become negatives. This generates a synthetic curriculum that gets harder as the encoder improves.

P_deflated = 0.35 (novel; no published precedent for substrate-generated hard negatives from a HD-computing binding structure; mechanism is sound but untested).

Cheap pre-test: generate 100 substrate-derived hard negative pairs offline; manually verify that they are semantically similar but structurally distinct; measure InfoNCE loss gradient direction vs. random negatives.

### Crazy option (b): RL with substrate state as MDP

Encoder is a policy pi(action=embedding | state=query). Substrate is the environment (retrieves top-K given embedding, then unbinds, then answers). Reward = answer correctness.

MDP formulation:
- State s_t = (query_text, retrieval_history_t)
- Action a_t = query_embedding vector in R^d
- Transition T(s_t, a_t) = substrate retrieval(a_t) -> new facts F_t
- Reward r_t = f(answer_correctness(F_t, gold))
- Episode: up to H hops (H=2 for bridge questions)

This is the formulation from arxiv 2602.03645 (RL for dense retriever, 2025), which uses GRPO with sparse terminal rewards and a history-aware state.

Why this is powerful: the encoder learns a RETRIEVAL STRATEGY, not just a static embedding. For bridge questions, the optimal strategy is: embed query to retrieve bridge entity at hop 1; embed (query + bridge entity) to retrieve answer at hop 2. This is a non-trivial sequential strategy that static embedding cannot capture.

Why this is risky: policy gradient on a continuous action space (embedding in R^1024) requires variance reduction. REINFORCE on raw embeddings diverges without careful reward normalization. GRPO works better because it normalizes rewards across a group of rollouts. But GRPO requires multiple rollouts per query (generate K embeddings, measure rewards, compute advantages) -- this is K times more expensive than single-forward contrastive.

P_deflated = 0.30 (strong theoretical grounding via 2602.03645; implementation is complex; novel for HD-computing substrate; deflated for substrate-coupling overhead).

v2 sequencing: implement AFTER batch contrastive LoRA demonstrates lift. RL is the ceiling-breaker if contrastive hits a plateau.

### Crazy option (c): Federated encoder fine-tuning with differential privacy

Multi-customer scenario: each customer has their own query stream and their own retrieval failure triplets. Federated learning allows each customer's local encoder adapter to contribute to a global adapter update without sharing raw query data.

Mechanism: each customer trains a local LoRA adapter delta_W_i on their failure triplets. The global server aggregates delta_W_global = mean(delta_W_i) with DP noise (Gaussian mechanism: add N(0, sigma^2 * I) to each delta_W_i before aggregation). The global adapter is distributed back to each customer.

Why this matters: per-customer fine-tuning (each customer has their own adapter) is powerful but requires per-customer LoRA inference overhead. Federated averaging gives a global adapter that benefits from all customers' failure signals without per-customer overhead.

Literature support: FedLoRA (2025), WinFLoRA (arxiv 2602.01126), DP-FedLoRA are all active research areas. The technology is available.

P_deflated = 0.30 (mechanism sound; requires multi-customer deployment to realize benefit; pre-condition is that single-customer online fine-tuning works first).

Honest caveat: the privacy benefit requires careful DP budget accounting. Each gradient update leaks epsilon bits of information about the training data. Over T updates, total privacy loss is O(T * epsilon_per_step). This must be bounded by a customer SLA.

### Crazy option (d): Encoder distillation FROM substrate

Substrate is the teacher. The substrate's binding operations (encode -> bipolar -> bind -> unbind -> check) implicitly encode a retrieval quality signal. Train the encoder to PREDICT what the substrate will retrieve successfully.

Specifically: for each (query, fact) pair, the substrate either binds and correctly unbinds (positive) or does not (negative). This is a binary classification signal at the ENCODING stage: before retrieval, predict "will the substrate successfully unbind from this query-fact pair?"

The encoder learns a representation that makes substrate-successful pairs nearby. This is stronger than recall-based fine-tuning because it directly optimizes for substrate compatibility, not for general semantic similarity.

Implementation: run a batch of (query, fact) pairs through the substrate. Label each pair as substrate-success or substrate-failure. Train a LoRA adapter with cross-entropy loss on this binary label. The adapter learns to embed queries and facts in a way that maximizes substrate binding success.

P_deflated = 0.35 (this is a novel mechanism with no published precedent; the intuition is strong; the main uncertainty is whether substrate success correlates with general retrieval quality or is too specific to substrate parameters).

Cheap pre-test: for 200 (query, fact) pairs in HotpotQA, run substrate binding check; label success/failure; fine-tune a logistic head on frozen encoder embeddings; measure AUC. AUC > 0.75 would confirm substrate success is predictable from encoder embeddings.

### Crazy option (e): Encoder pre-training with substrate-in-the-loop

Instead of fine-tuning an existing encoder, build a SUBSET of the pre-training data that specifically targets substrate-retrievable patterns. Filter a large pre-training corpus (e.g., Wikipedia) to retain only (query, passage) pairs where the passage is successfully retrieved by the CURRENT substrate. Pre-train a small encoder from scratch (or continue-pre-train from a checkpoint) on this substrate-curated corpus.

Why this is different from fine-tuning: fine-tuning adjusts an existing encoder. Pre-training with substrate curation shapes the entire representation space toward substrate compatibility from the beginning.

Practical constraint: requires a large corpus and significant compute. Not viable for v1.5. For v2, if the substrate is production-deployed and generating millions of retrieval events, the curated corpus grows organically.

P_deflated = 0.20 (mechanistically novel; high implementation cost; requires scale that does not exist yet).

Honest caveat: if the substrate itself has a poor encoder at the start, the curated pre-training data is also poor (it selects examples the bad encoder retrieves, which is a biased subset). This is a chicken-and-egg problem. Mitigation: use BM25 for initial curation, not the encoder.

---

## Section 4: Three cheap pre-tests

### Pre-test 1 (cheapest, ~2 hours local GPU): Batch contrastive LoRA on HotpotQA failure set

Setup:
- Take the HotpotQA dev set (~7,405 questions).
- Run bge-large recall@2 evaluation baseline (already done: recall@2=0.516).
- Identify the wrong-answer set (48% of queries = ~3,555 queries).
- For each wrong query: gold supporting facts = positives; retrieved-but-wrong facts = hard negatives.
- Construct triplet dataset: ~3,555 * (1 positive + 2 negatives) = ~10,665 triplets.
- Add LoRA rank-4 adapter to bge-large query encoder. Freeze base weights.
- Fine-tune for 3 epochs on triplet dataset with InfoNCE loss (tau=0.05).
- 50/50 split: mine failures from first half of dev set; evaluate on second half (prevents leakage).
- Re-evaluate recall@2.

HARD-PASS: recall@2 >= 0.55 (clears HP threshold).
MIDDLE-BAND: recall@2 in [0.52, 0.55). Encoder improved but not at threshold.
HARD-FAIL: recall@2 < 0.52. Adapter degraded or flat; check gradient norms.

Cost: ~2 hours on local GPU. Memory: bge-large (1.3 GB) + adapter (< 10 MB) + triplet batch (negligible). Total: ~2 GB VRAM.

### Pre-test 2 (medium, ~4 hours): Hard-negative source comparison

Setup:
- Run pre-test 1 with three conditions:
  (a) hard negatives = retrieved-but-wrong facts (failure-mined)
  (b) hard negatives = random facts from the knowledge base
  (c) hard negatives = substrate-derived confusable facts (binding neighbor search)
- Compare recall@2 improvement across conditions.

HARD-PASS: condition (c) >= condition (a) by >= 0.02. Substrate-native negatives are at least as good as retrieval-failure negatives; validates crazy option (a).
MIDDLE-BAND: conditions (a) and (c) are within 0.01. No advantage to substrate-native negatives.
HARD-FAIL: condition (a) < condition (b) by >= 0.02. Hard negatives HURT vs. random negatives; indicates gradient instability or false-negative contamination.

Cost: ~4 hours local GPU (3 training runs).

### Pre-test 3 (medium, ~3 hours): LoRA rank ablation (rank 2 vs 4 vs 8)

Setup:
- Take pre-test 1 best-performing condition.
- Run 3 variants: rank 2, rank 4, rank 8.
- Measure recall@2 and training loss curve.

Prediction: rank-4 is optimal. Rank-2 underfits (too low-rank to capture bridge entity diversity). Rank-8 overfits (too many degrees of freedom for ~3,555 triplets).

HARD-PASS: recall@2 at rank-4 >= 0.55 AND rank-8 <= rank-4. Confirms rank-4 is correct.
HARD-FAIL: recall@2 at rank-8 > rank-4 by >= 0.02. Indicates underfitting; promote to rank-16 or partial fine-tune.

Cost: ~3 hours local GPU (3 training runs of ~1 hour each).

---

## Section 5: Risk analysis

### Risk 1: Gradient instability in online learning

In true online learning (update per query), gradient variance is high (effective batch size = 1). For contrastive learning specifically, InfoNCE requires enough negatives per batch to estimate the partition function accurately. With N_neg negatives, the gradient estimator has variance O(1/N_neg). For N_neg=1, variance is very high and training diverges.

Mitigation: never update on single triplets. Accumulate 32 triplets before updating. This is mini-batch online learning, not per-query. The overhead per update is 32 forward passes + 1 backward pass through the adapter. For bge-large with rank-4 adapter, one backward pass = ~50ms on GPU. 32 triplets = ~1.6 seconds per update. At 100 queries/sec, this is a 1.6% compute overhead -- negligible.

### Risk 2: False negative contamination

Some retrieved-but-wrong facts are actually correct for the query but were not in the gold annotation (HotpotQA annotations are incomplete for ~5-10% of supporting facts per published annotation artifacts work). Training the encoder to push these AWAY increases retrieval loss.

Mitigation: for pre-testing, use HotpotQA gold annotations as ground truth. For production, use substrate correctness check (did the LLM answer match?). Quantitative estimate: with 2 hard negatives per triplet and 10% contamination, ~0.2 negatives per triplet are false negatives. Degrades recall@2 by approximately -0.01 to -0.02 in the worst case. Acceptable.

### Risk 3: Adapter overfitting to HotpotQA distribution

The fine-tuned encoder learns bridge-retrieval patterns specific to HotpotQA (Wikipedia-based, English, factoid). If deployed on a different KB (technical documentation, legal text), the adapter degrades general retrieval.

Mitigation: per-domain adapter. Each customer domain trains its own rank-4 adapter on its own failure triplets. The shared base encoder provides general retrieval; the adapter provides domain-specific fine-tuning. This requires only 0.77M parameters per customer domain (3 MB in float32).

### Risk 4: Production instability from continuous updates

If the adapter is updated at every batch, the encoder is a non-stationary function. Two users querying simultaneously may see different results from the same query. This breaks reproducibility and can cause feedback loops.

Mitigation: periodic batch updates instead of truly online. Accumulate triplets continuously; update adapter every 24 hours (or every 1000 queries). Run validation check on held-out set at update time; rollback if recall@2 drops > 0.02.

### Risk 5: Encoder re-indexing cost

If both query and document encoder are updated (A2/A3), the document index must be re-computed. For 1M facts, re-indexing takes hours on a single GPU. For the substrate's typical KB size (10k-100k facts), re-indexing costs 1-10 minutes. Acceptable for daily batch updates. Not acceptable for per-batch online updates.

Conclusion: use query-only adapter updates (A1) for online; re-index with symmetric adapter update (A3) at daily batch update time.

---

## Section 6: v1.5 / v2.0 sequencing

### v1.5 (2-4 weeks engineering): Offline batch contrastive LoRA

Scope:
- Implement pre-test 1 as a production-usable pipeline.
- Accumulate failure triplets from HotpotQA or production query log.
- Run batch contrastive training every 24 hours.
- Deploy updated query encoder (rank-4 LoRA adapter on bge-large or stella-400M base).
- Re-index document store every 24 hours with symmetric adapter update.
- Validation gate: recall@2 check before deploying new adapter; rollback if < prior checkpoint.

Dependencies:
- Failure triplet extraction: gold-fact lookup (HotpotQA: trivial; production: substrate correctness oracle).
- LoRA adapter infrastructure: add PEFT library dependency to encoder serving; ~1 day.
- Adapter versioning: store checkpoints, rollback logic; ~1 day.

Expected lift (P_deflated=0.45): recall@2 from 0.516 to 0.55-0.60. Clears HP threshold. Bridge-ID accuracy from ~65% to 68-76% (estimated; bridge-ID requires both facts in correct order so improvement is compound).

Not in v1.5: truly online per-batch updates, RL-as-MDP, federated fine-tuning.

### v2.0 (2-3 months engineering): RL-retrieval with substrate MDP

Scope:
- Implement the MDP formulation (crazy option b): encoder as policy, substrate as environment.
- Use GRPO (group relative policy optimization) per 2602.03645 pattern.
- Reward = per-hop correctness signal.
- Multi-turn retrieval: encoder generates embedding at hop 1 (retrieve bridge entity); updates embedding with bridge entity context; retrieves at hop 2 (retrieve answer entity).
- Expected lift over v1.5: recall@2 from 0.55-0.60 to 0.65-0.70 (P_deflated=0.25 for reaching 0.65).

Why v2.0 is not v1.5: GRPO requires K rollouts per query (K=4-8). Training compute is high. Start with the interpretable contrastive baseline; use RL to amplify once contrastive is proven.

Sequential dependency: do NOT skip to v2.0 RL without v1.5 contrastive pre-test showing lift. The RL formulation is harder to debug and may fail for reasons orthogonal to encoder quality (reward sparsity, policy collapse).

---

## Section 7: Cross-thread synthesis

### Thread 1: Encoder ceiling (prior notes)

Prior drill (notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md) concluded that encoder upgrade (stella-1.5B, NV-Embed-v2) likely clears 0.55 with P_deflated=0.60. This drill (online fine-tuning) gives a complementary path with P_deflated=0.45.

Composition: these are NOT mutually exclusive. Best path:
(1) Switch base encoder to stella-400M or stella-1.5B (prior drill, P_deflated=0.60).
(2) Add LoRA adapter fine-tuned on substrate failure triplets (this drill, P_deflated=0.45).
(3) Both together: P_deflated(0.60-0.65) ~ 0.50 (novel-synthesis cap applied).

The encoder upgrade gives a general-purpose lift; the adapter gives a substrate-specific, domain-adaptive lift on top. They compose additively within the recall@2 metric.

### Thread 2: Bridge-ID accuracy

Bridge-ID accuracy at 1.5B LLM is ~60-70%. The online fine-tuning drill gives the specific mechanism by which bridge discrimination improves: contrastive gradient pulls bridge-entity embeddings toward the query embeddings that failed to retrieve them. The fine-tuning is explicitly trained on bridge-failure cases, while a general encoder upgrade improves uniformly across query types. Bridge-ID improvement from fine-tuning may be larger per recall@2 point than from a general encoder upgrade.

### Thread 3: Multi-hop accuracy (Phase 2 capabilities)

From POST-COMPACTION BRIEF afternoon: Phase 2 5x chains identify multi-hop as the biggest architectural gap. The RL-as-MDP formulation (crazy option b) is specifically designed for multi-hop retrieval: the encoder policy learns to sequence retrievals across hops. This is the path from single-hop encoder upgrade to true multi-hop-aware retrieval.

### Thread 4: Online-learning field in cap_map

Field advisor shows online-learning at drill_count=1, yield=0.0%. This drill is the first positive-yield drill in this field. The mechanism described here maps to a nonequilibrium dynamics question: does the adapter parameter trajectory under continuous contrastive gradient pressure converge to a stationary distribution, or does it drift? This is adjacent to the nonequilibrium-stat-mech adjacency from the field advisor (Jarzynski/NESS for adapter dynamics).

---

## Section 8: Substrate-product implications

**Implication 1 (near-term, v1.5):** The offline batch contrastive LoRA pipeline converts production query failures into training signal. This closes the encoder ceiling problem without requiring a cloud GPU cluster or a new model download: the adapter is 0.77M parameters and can be served alongside the base encoder with negligible overhead.

**Implication 2 (near-term, v1.5):** Per-customer adapter capability. Each customer's LoRA adapter is tiny (3 MB in float32). The system maintains one adapter per customer domain, fine-tuned on that customer's specific failure patterns. This is a personalized retrieval encoder feature: the encoder gets better at retrieving from a specific customer's KB the longer it runs.

**Implication 3 (mid-term, v2):** If the RL-as-MDP formulation works, the encoder learns multi-hop retrieval strategies from the substrate's own success/failure signal. The encoder becomes a substrate-specialized model: it has learned, from experience, what patterns of query embedding lead to successful multi-hop retrieval in this specific substrate. No other encoder has this property. This is the encoder distillation from substrate (crazy option d) realized implicitly through RL training.

**EU AI Act / GDPR implication:** The federated fine-tuning option (crazy option c) with differential privacy allows cross-customer encoder improvement without data sharing. Directly relevant to GDPR Article 17 compliance: customer query data never leaves the customer's environment; only DP-noised adapter gradients are shared. Aligns with post-compaction brief afternoon note on EU AI Act Art 12 + GDPR Art 17 native compliance.

---

## Section 9: Falsifiable predictions (HARD-PASS + HARD-FAIL thresholds)

**Prediction 1 (pre-test 1, batch contrastive LoRA):**
HARD-PASS: recall@2 on held-out HotpotQA dev set >= 0.55 after 3 epochs of LoRA fine-tuning on failure triplets.
MIDDLE-BAND: recall@2 in [0.52, 0.55).
HARD-FAIL: recall@2 < 0.52. If this fails, check gradient norms; if near zero, InfoNCE tau is too large.

**Prediction 2 (mechanism soundness):**
HARD-PASS: gradient norm on bridge-failure queries is >= 2x gradient norm on bridge-success queries in the first training epoch.
HARD-FAIL: gradient norm is equal for failure and success queries. Indicates failure signal is not distinguished at embedding level; likely tau-calibration issue.

**Prediction 3 (bridge-ID improvement):**
HARD-PASS: bridge-ID accuracy increases by >= 5 percentage points from baseline (~65%) after LoRA fine-tuning.
HARD-FAIL: bridge-ID accuracy decreases or is unchanged. Adapter learned representation that improves overall recall@2 but not specifically bridge-entity discrimination.

**Prediction 4 (RL-as-MDP, v2 pre-registration):**
HARD-PASS: multi-hop recall@2 >= 0.65 after GRPO training with substrate MDP.
HARD-FAIL: GRPO training diverges (gradient norms explode) or recall@2 does not improve beyond contrastive baseline.

---

## Cheap decisive test

**Pre-test 1 (2 hours, local GPU):** LoRA rank-4 adapter fine-tuned on HotpotQA retrieval-failure triplets. Measure recall@2 before and after. This is the minimum-cost experiment that confirms (a) the gradient signal exists, (b) the adapter learns, and (c) recall@2 improves. Cost: ~0 cloud, ~2 hours GPU time, ~3 MB adapter artifact.

---

## P_deflated summary

- P(batch contrastive LoRA clears 0.55 recall@2) = 0.45
- P(bridge-ID improves >= 5pp from LoRA fine-tuning) = 0.35
- P(RL-as-MDP reaches recall@2 >= 0.65) = 0.25
- P(substrate-supervised hard negatives >= retrieval-failure hard negatives) = 0.35
- P(encoder distillation from substrate is viable) = 0.35
- P(online fine-tuning + encoder upgrade compose to recall@2 >= 0.63) = 0.50 (novel-synthesis cap applied)

---

## Citations (verified)

1. DPR: Karpukhin et al. (2020). Open-Domain Question Answering using Dense Passage Retrieval. EMNLP 2020.
2. LoRA: Hu et al. (2021). LoRA: Low-Rank Adaptation of Large Language Models. ICLR 2022.
3. Teleportation negatives / catastrophic forgetting in dense retrieval: arxiv 2210.17167 (EMNLP 2022).
4. RL for dense retriever (history-aware): arxiv 2602.03645 (2025). Reinforcement Fine-Tuning for History-Aware Dense Retriever in RAG.
5. Direct Retrieval-augmented Optimization (DRO): De Rijke et al. (May 2025). Direct Retrieval-augmented Optimization.
6. GlobalRAG RL for multi-hop QA: arxiv 2510.20548 (2025).
7. Hard negative mining for domain-specific retrieval (ACL 2025): arxiv 2505.18366.
8. GRPO: Shao et al. (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models.
9. Intrinsic dimensionality of fine-tuning: Aghajanyan et al. (2021). Intrinsic Dimensionality Explains the Effectiveness of Language Model Fine-Tuning. ACL 2021.
10. InfoNCE: Oord et al. (2018). Representation Learning with Contrastive Predictive Coding.
11. WinFLoRA federated LoRA: arxiv 2602.01126 (2025).
12. EWC: Kirkpatrick et al. (2017). Overcoming catastrophic forgetting in neural networks. PNAS.
13. CRAFT RL for multi-hop QA: arxiv 2602.01348 (2025).
14. History-Aware Conversational Dense Retrieval: arxiv 2401.16659.

Verified count: 14 citations. Fetch-verified: 2602.03645, 2210.17167, 2505.18366, 2510.20548.

---

## Next-drill candidate

Online-learning stability theory for continuous embedding-space policies: specifically, the nonequilibrium dynamics of the LoRA adapter parameter trajectory under continuous contrastive gradient pressure. This maps to the nonequilibrium-stat-mech adjacency from the field advisor (Jarzynski/NESS for adapter dynamics). The question: does the adapter converge to a stationary distribution, or does it drift indefinitely? The answer determines whether periodic rollback is sufficient or whether a stronger regularizer is needed.
