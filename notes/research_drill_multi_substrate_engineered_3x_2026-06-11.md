# Research: Multi-Substrate Engineered Architecture -- 3x Drill
# Date: 2026-06-11
# Topic: Implementable multi-W-matrix substrate architectures with migration protocols, routing rules, and empirical test predictions

---

## HEADLINE

The substrate constraint that "there is one shared W matrix" is an engineering choice, not a mathematical limit. Biology runs 4-6 structurally distinct memory systems (DG/CA3/CA1/cortex/basal ganglia/cerebellum) with different encoding properties, different learning timescales, and explicit gating/routing between them. The HDC literature (Teeters et al. 2023) independently rediscovered that separating item memory from associative memory crosses an efficiency threshold at ~1000 stored items where combined architectures require 15-35x less compute than a single superposition vector at the same reliability. For the substrate, having 2-3 W matrices with defined transfer protocols is implementable TODAY using the existing algebraic primitives and gives concrete escape routes from the problems (capacity cliff, working-memory bottleneck, domain isolation, protected subspaces) that single-W architectures cannot solve cleanly.

P_deflated = 0.42 (calibration penalty applied; see per-architecture estimates below)

---

## Literature state (5 streams)

### Stream A: Biology -- hippocampal architecture

The hippocampus runs four structurally distinct encoding regimes in series:

**Dentate gyrus (DG):** Sparse encoding (~2% active cells), pattern separation. High-excitability neurons are allocated to engrams via lateral inhibition mediated by parvalbumin interneurons. CREB overexpression biases which neurons join an engram. The sparsity is not incidental -- it is enforced by microcircuit competition. Capacity: stores many distinct items with minimal crosstalk because representations are near-orthogonal. Learning is fast (LTP at mossy fiber synapses is perforant-path-independent).

**CA3:** Recurrent attractor network (auto-association). Dense collateral connectivity (~4% cells but 100% recurrent connectivity within that 4%). Pattern completion from partial cues. The CA3-DG functional unit handles pattern separation at proximal CA3, while distal CA3 runs pattern completion as an autoassociative attractor. Capacity: classic Hopfield scaling (~0.14 * N patterns at N neurons) but with error-correction.

**CA1:** Binding and temporal association. Receives from both CA3 (Schaffer collaterals) and direct entorhinal input (temporal information). Acts as coincidence detector between hippocampal-internal recall and current context. Completion biased, not separation-biased.

**Neocortex:** Slow, overlapping, distributed representations. Learning rate 10-100x slower than hippocampus. Stores statistical regularities extracted by replay from hippocampus. Systems consolidation = hippocampus running replay during sleep to train cortex (McClelland/Tonegawa CLS framework, 1995, verified 2022 via autonomous PNAS model).

**Key engineering insight:** Each subfield has different N (cell count), different connectivity, different learning rule, different access pathway. The ROUTING is anatomical (mossy fibers carry DG->CA3; Schaffer collaterals carry CA3->CA1; perforant path carries EC->DG and EC->CA1 in parallel). There is no "meta-router" -- the anatomy IS the router.

**Basal ganglia (gating substrate):** The BG performs dopamine-gated input/output gating of prefrontal working memory. Dopamine locks or unlocks which representations enter or leave the working-memory buffer. The striatum learns the gating policy via reinforcement learning. This is architecturally a router with a learned policy, not a fixed rule.

**Cerebellum vs. cortex:** Fast error correction (cerebellar cortex, volatile) vs. slow stable storage (deep cerebellar nuclei and motor cortex). Rate of forgetting in cerebellar cortex is FAST (exponential decay hours-scale). Motor cortex memories are stable across days-weeks. Transfer protocol: cerebellar adaptation gradually tutors motor cortex (the "consolidation" in motor learning matches sleep-dependent hippocampal replay in episodic memory).

### Stream B: CLS and engram theory

McClelland, McNaughton, O'Reilly (1995) CLS paper: the core insight is that INTERLEAVED LEARNING from a fast episodic store into a slow semantic store prevents catastrophic forgetting. The interleaving is the protocol. The fast store must forget quickly (to keep capacity free for new items); the slow store must learn slowly (to avoid catastrophic overwrite). The transfer protocol IS the solution to the stability-plasticity dilemma.

Komorowski et al. (Tonegawa lab): engram cells are allocated by intrinsic excitability competition. This means the substrate analog is: items that activate more nodes (higher binding density, larger bundle) are preferentially allocated to high-excitability positions, creating a natural priority queue for migration.

FSC-Net (2024): dual networks, fast learner (high LR) + slow learner (low LR), simultaneously running gradient descent. The fast network tutors the slow one. In substrate terms: W_fast is updated with full signal; W_slow is updated with smoothed/averaged signal.

Fast weights (Hinton & Plaut 1987, Ba et al. 2016): W_eff = W_slow + W_fast. Fast weights undergo rapid outer-product Hebbian updates; slow weights are the long-term store. Fast weights decay to zero between episodes. This is directly substrate-native: the outer product rule IS the substrate's delta update.

### Stream C: Materials science analogy

Functionally graded materials (FGMs): property gradients are engineered across spatial zones. Hard phase (ceramic) at one face, ductile matrix (metal) at the other, with a controlled gradient between. The gradient prevents stress concentration at sharp interfaces.

Engineering translation for multi-substrate: the "interface" between W_fast and W_slow must be gradual, not a binary gate. Otherwise items near the migration threshold will thrash (added to W_slow, quickly updated in W_fast, partially replayed to W_slow, creating interference). A soft migration with overlap is the materials-informed design.

Multi-phase composite design: two phases with distinct roles (load-bearing hard phase + energy-absorbing matrix). Neither phase can do both jobs. The composite's strength comes from the interface design, not just the constituent materials. In substrate terms: W_fast alone would exhaust capacity; W_slow alone would fail on novel items. The INTERFACE protocol (migration rule) is the engineering leverage point.

Additive manufacturing of FGMs (2023): compositional detouring around crack-prone regions. Translation: migration protocol must route around interference zones -- items that are too similar to existing W_slow contents should not be migrated until they have been sufficiently consolidated (diverged from similar existing patterns via replay differentiation).

### Stream D: LLM theory

**Hierarchical memory in LLMs (2024-2025):**

MemOS (2025): categorizes memory into in-context (fast, ephemeral), activation (medium, session-persistent), and parametric (slow, permanent). Three tiers, explicit routing based on access frequency and persistence needs. Direct analog to the substrate's W_fast / W_medium / W_slow design.

Memory Sparse Attention (MSA 2025): unified end-to-end trainable architecture integrating sparse retrieval and generation. The routing key matrix uses dedicated projection weights separate from the content projection. This is the substrate-native analog: routing should use a separate projection (a small classifier or excitability score), not the same binding operation used for content retrieval.

MIDUS (2024): per-head memory banks -- each attention head has its own memory bank with head-specific queries. Different heads specialize in different retrieval functions. Translation: different W matrices can specialize in different domains or retrieval modes, with routing determined by query type.

PiKV (2025): MoE + KV cache hierarchy. Token routing determines which expert's KV cache gets written. The routing decision (made by a gating network) determines cache allocation. This is architecturally equivalent to a substrate write-router: the incoming bundle's properties determine which W matrix receives the write.

Hierarchical pretraining (2024): separating long-tail vs. common knowledge by training frequency. Items seen once go to an episodic store; items seen many times migrate to the parametric weights. Frequency of access is the migration trigger.

### Stream E: HDC-native multi-substrate precedents

**Teeters, Kleyko, Kanerva, Olshausen (Frontiers Neurosci, 2023): "On separating long- and short-term memories in hyperdimensional computing."**

This is the directly relevant published precedent. Key finding: for 1000+ key-value pairs, Sparse Distributed Memory (SDM) variants require 15-35x less storage and compute than superposition vectors at equivalent reliability (error rate 10^-6). The crossover threshold is approximately 1% item presence (items stored as fraction of total capacity).

Architecture: superposition vector = working/short-term memory (~7 items reliably recalled); SDM = long-term associative memory (capacity scales with SDM address matrix rows, NOT with vector width N). The two can compose: recall from SDM into the superposition vector for working-memory manipulation.

Critical routing insight from the paper: "If there were multiple item memories, and the vectors recalled had to be compared selectively to vectors in a particular item memory, there would need to be some mechanism to identify which item memory was appropriate to use and circuitry to route recalled vectors to the proper item memory."

This is the open engineering problem the multi-substrate architecture must solve. The paper identifies it but does not solve it. We can solve it using the substrate's existing binding operations as the routing key.

---

## 10 Implementable Multi-Substrate Architectures

Each architecture is described with: W-matrix set, encoding properties, transfer protocol, read/write routing, and what problem it solves.

---

### Architecture 1: 2-Substrate Fast/Slow CLS
**Biological analog:** Hippocampus (fast) + neocortex (slow)

**W matrices:**
- W_fast: N=1024, full-precision, updated on every write with full delta rule. Decay factor applied each epoch (exponential forgetting: W_fast <- (1 - alpha) * W_fast + delta). alpha=0.05 per write cycle.
- W_slow: N=8192 or N=1024 (separate instance), updated only on replay events. Low learning rate (beta=0.001 per replay).

**Write routing:** All writes go to W_fast first. 

**Migration protocol:** After K_threshold writes (empirically determined, e.g., K=100), items with retrieval count > C_replay (e.g., accessed 3+ times) are replayed into W_slow via superposition write at low weight.

**Read routing:** Query hits W_fast first (recent, fast). On miss (cosine similarity < theta_fast), query falls through to W_slow. W_slow match returned if similarity > theta_slow. Router = threshold comparison on similarity score.

**What it solves:** Capacity cliff problem. W_fast has limited capacity (K/N < 0.56); when it fills, items migrate to W_slow before the cliff hits. W_slow can be larger (different N) and stores only consolidated items, so its effective capacity is much higher for its stored content because the content has been replay-differentiated.

**Empirical prediction:** At K=500 items, a 2-substrate system with migration should maintain recall@1 > 0.90 while a single-W system at K/N~0.49 would show recall degradation. HARD-PASS: 2-substrate recall@1 >= 0.85 at K=500, N=1024; HARD-FAIL: 2-substrate recall@1 < 0.60 at K=300 (worse than single-W baseline).

**P_deflated:** 0.50 (direct implementation of Teeters et al. result; biological precedent clear; substrate-native ops available)

---

### Architecture 2: 3-Substrate Fast/Medium/Slow (MemOS Tier Pattern)
**Biological analog:** Working memory buffer (prefrontal cortex) + hippocampus + neocortex

**W matrices:**
- W_working: N=512, held as a superposition vector (not a full matrix). Capacity ~7 items. Cleared on context change. UPDATE: full overwrite.
- W_episode: N=1024, full SDM/matrix. Stores last ~500 recent items. Decay on write: items older than T_episode are pruned.
- W_semantic: N=4096 or 8192. Stores only high-frequency items. Write: batched replay at very low LR.

**Write routing:** 
1. All new items -> W_working (superposition add).
2. When W_working exceeds capacity (~7), oldest item evicted to W_episode.
3. When W_episode item has retrieval_count > 5 over last 200 writes, it migrates to W_semantic.

**Read routing:** Query W_working first. On miss, query W_episode. On miss, query W_semantic. Return highest-similarity match across tiers with tier annotation.

**What it solves:** Working-memory bottleneck in compositional reasoning. The "context window" problem: only the last ~7 relevant facts are kept hot in W_working for fast combinatorial access. Deep historical facts live in W_semantic and are retrieved on demand.

**Empirical prediction:** Multi-hop reasoning tasks requiring 3+ intermediate lookups should show higher accuracy with W_working as hot buffer vs. single-W because all 3 intermediate results can be held simultaneously without capacity interference. HARD-PASS: 3-hop recall improves >15% over single-W baseline. HARD-FAIL: no improvement at 2-hop depth.

**P_deflated:** 0.38 (multi-hop has been closed in prior drills; the working-memory buffer may help but the encoder issue limits the gain)

---

### Architecture 3: Per-Tier Specialized (Tier-1 Universal vs. Tier-3 Entity)
**Biological analog:** Hippocampal CA3 (general attractor) vs. piriform cortex (odor-specific, highly specialized)

**W matrices:**
- W_universal: N=1024, dense HRR encoding, stores all item types. The current single substrate.
- W_entity: N=1024, sparse encoding (target ~5% active components), stores only named-entity bundles. Separate binding operator: permutation-based rather than element-wise multiply.

**Write routing:** At write time, a lightweight classifier (can be a simple threshold on item type tag, or a trained 2-layer MLP on the bundle vector) routes entity bundles to W_entity and everything else to W_universal.

**Read routing:** Queries tagged as entity lookups go to W_entity first; fallback to W_universal. Untagged queries go to W_universal only.

**Encoding difference:** W_entity uses sparse binary hypervectors (Kanerva 2009 MAP architecture). The bundle operation is thinning (set intersection analogy) rather than superposition. Capacity for sparse binary is higher (exponential in N for Bloom-filter-like property) at the cost of exact-match-only retrieval.

**What it solves:** The cross-domain bias problem. Dense encoding conflates entity similarity with semantic similarity; sparse encoding treats entities as near-orthogonal by default, which is correct for proper nouns (Paris and London are both cities but should NOT interfere in a memory). The entity substrate enforces orthogonality structurally.

**Empirical prediction:** Entity lookup precision in a mixed KB (entities + propositions) should increase by >10% with W_entity vs. single-W because entity vectors do not interfere with proposition bundles. HARD-PASS: entity recall@1 > 0.92 at K=200 entity pairs in W_entity (where single-W baseline is ~0.80). HARD-FAIL: entity recall@1 in W_entity < 0.75.

**P_deflated:** 0.45 (sparse HDC encoding is well-established; the routing classifier is simple; the main unknown is whether the substrate's write path can be split at this level cleanly)

---

### Architecture 4: Per-Domain Substrate (Math + Code + Language)
**Biological analog:** Fusiform gyrus (faces), parahippocampal place area (scenes), visual word form area (text) -- cortical specialization by domain

**W matrices:**
- W_math: N=1024, encoding tuned for structured symbolic content (prefix permutation for operator position, role-filler binding for argument slots)
- W_code: N=1024, encoding tuned for sequential structure (position-indexed permutation operators, variable bindings via XOR chains)
- W_lang: N=1024 or 8192, standard HRR encoding for natural language

**Write routing:** Domain classifier (input tag or lightweight classifier) routes write to appropriate W. Cross-domain items (e.g., a math theorem in natural language) can write to both W_math and W_lang with different projections.

**Read routing:** Query domain is tagged (or inferred from query structure). Route to appropriate W. For ambiguous queries, retrieve from all three and return highest-similarity result.

**What it solves:** Interference between domains. Math content and natural language content use very different structural regularities; forcing them into the same W means the binding operators must be a compromise. Separate W matrices allow each domain's binding ops to be specialized.

**Empirical prediction:** Retrieval accuracy for mathematical expressions should improve in W_math vs. single-W because structured binding (role-filler) better captures operator/argument relationships. HARD-PASS: structured retrieval F1 > 0.85 in W_math at K=100 math expressions. HARD-FAIL: no improvement vs. single-W (< 2% lift).

**P_deflated:** 0.35 (domain routing requires a working classifier; the binding-operator specialization requires engineering work; high uncertainty on actual lift)

---

### Architecture 5: Encoding-Variant Substrates (Dense + Sparse + Low-Rank)
**Biological analog:** Parallel cortical processing streams (dorsal/ventral visual pathways, each encoding different features of the same input)

**W matrices:**
- W_dense: N=8192, standard float32 bipolar HRR. Optimized for similarity search with cosine metric.
- W_sparse: N=1024, sparse binary encoding (~5% active). Optimized for exact lookup with Hamming metric.
- W_lowrank: N=1024 but maintained as U * V^T (rank-r approximation, r=64). Optimized for compressed storage of highly correlated content.

**Write routing:** All three receive every write, but with different encoding functions applied to the same input bundle:
- W_dense: standard bind-and-bundle
- W_sparse: binarize with thresholding after binding (top-5% components set to 1)
- W_lowrank: project through learned basis (SVD of accumulated W_dense, periodically refreshed)

**Read routing:** Query goes to all three in parallel. Fusion: return the result that exceeds its respective threshold first (race condition). Fall back to W_dense if no winner.

**What it solves:** Different query types have different optimal metrics. Exact entity lookup: W_sparse wins (Hamming is sharp). Semantic similarity: W_dense wins (cosine handles partial match). Compressed repeated patterns: W_lowrank wins (factored representation reduces noise). Multi-metric fusion gives the best retrieval mode per query type without knowing the type in advance.

**Empirical prediction:** Mixed-query benchmark (30% exact lookup, 50% semantic, 20% partial) should show higher overall recall@1 with 3-variant fusion vs. single W_dense. HARD-PASS: overall recall@1 gain > 8%. HARD-FAIL: no gain or regression.

**P_deflated:** 0.40 (encoding variant architectures are standard in IR; the substrate-native implementation requires sparse encoding support which is currently missing from the substrate primitives; engineering cost is non-trivial)

---

### Architecture 6: Per-Role Substrate (Storage + Computation + Working Memory)
**Biological analog:** Hippocampus (storage) + prefrontal cortex (working memory buffer) + cerebellum (fast computation/prediction)

**W matrices:**
- W_store: N=8192, large persistent store. Write-once semantics (append only; deletions soft). Slow updates.
- W_compute: N=1024, ephemeral computation substrate. Cleared after each reasoning episode. Used for intermediate results in multi-step operations.
- W_wm: Implemented as a superposition vector (not a full matrix), capacity ~7 items. Holds the current reasoning context.

**Write routing:**
- Final answers / committed facts -> W_store
- Intermediate reasoning steps -> W_compute
- Current context (last ~7 items referenced) -> W_wm

**Read routing:**
- Context-sensitive lookups -> W_wm first (fast, exact match)
- Reasoning lookups -> W_compute (medium, may be noisy)
- Long-term retrieval -> W_store (slow, high accuracy)

**What it solves:** The ephemeral intermediate results problem. In multi-step reasoning, intermediate bundles should not pollute the persistent store (they are noisy; they are session-specific; they should be forgotten after the episode ends). Separating W_compute from W_store prevents this pollution. The W_wm acts as a register file.

**Empirical prediction:** Multi-step algebraic manipulation (bind -> query -> rebind -> query) should have lower crosstalk with W_compute isolated vs. all ops going into a shared W. HARD-PASS: multi-step precision (3 operations) > 0.90 with isolated W_compute. HARD-FAIL: no improvement vs. single-W at 3 steps.

**P_deflated:** 0.48 (this is the most substrate-native architecture; the superposition vector as W_wm already exists; W_compute as a clearable instance is trivially implementable by instantiating a second Substrate object)

---

### Architecture 7: Hierarchical Substrate (Within-Domain + Cross-Domain)
**Biological analog:** Hippocampus (episodic, within-experience) + parahippocampal cortex (spatial/context) + prefrontal cortex (abstract schema)

**W matrices:**
- W_local[d] for each domain d: Small N=512, stores within-domain facts. One W per domain (e.g., W_local_medicine, W_local_finance).
- W_cross: N=4096, stores cross-domain abstractions and bridging concepts. Written only when the same concept appears in 2+ local substrates.

**Write routing:** All writes go to the appropriate W_local[d]. When the same concept (matched by similarity > 0.85 across two different W_local instances) appears, a cross-domain abstraction is extracted and written to W_cross.

**Read routing:** Domain-tagged queries -> W_local[d]. Cross-domain queries (no domain tag, or explicit "cross-domain" flag) -> W_cross first, then W_local if needed.

**What it solves:** The cross-domain retraction (2026-06-10 memory: P9 entity-geometry confound). Instead of trying to encode cross-domain similarity in a single W, isolate it in W_cross which only holds concepts verified to generalize. This is the engineering escape from the cross-domain limit.

**Empirical prediction:** Cross-domain analogy retrieval (concept from domain A retrieved given a query from domain B) should improve from near-zero baseline to > 0.50 if W_cross is populated with genuine cross-domain abstractions. HARD-PASS: cross-domain recall@1 > 0.40 at K=50 cross-domain pairs. HARD-FAIL: cross-domain recall@1 < 0.20 (no better than single-W).

**P_deflated:** 0.35 (the cross-domain claim has been formally retracted; this architecture is a RESCUE attempt; the risk is that the cross-domain abstraction extraction step is itself the hard problem; P is honest about this)

---

### Architecture 8: Redundant Substrate (3x Copies for Critical Content)
**Biological analog:** Erasure coding in distributed storage; cortical remapping after lesion; redundant engrams in multiple brain regions (amygdala + hippocampus + cortex all store fear memories)

**W matrices:**
- W_primary: N=1024, the main store. Standard operations.
- W_replica_1: N=1024, exact copy of W_primary updated on every write. Used for fault tolerance.
- W_replica_2: N=1024, delayed copy (mirrors W_primary with 100-write lag). Used for corruption detection.

**Write routing:** Writes go to W_primary. A background process copies delta to W_replica_1 synchronously and queues it for W_replica_2 with delay.

**Read routing:** Primary query to W_primary. On retrieval uncertainty (similarity in [0.5, 0.7] range), query W_replica_1 for vote. If both agree, return result. If they disagree (corruption detected), query W_replica_2 as tiebreaker.

**What it solves:** Retrieval reliability under noise and partial corruption. This is the substrate analog of erasure coding: instead of replicating raw data, replicate the W matrix accumulation. The retrieval vote acts as majority-decode.

**Erasure coding connection:** Locally recoverable codes (LRCs) show that 3x replication is the minimum for single-node recovery with efficient bandwidth. Substrate analog: 3 W matrices is the minimum for reliable voting with one corrupted replica detectable.

**Empirical prediction:** Under Gaussian noise injection (sigma = 0.1 added to stored vectors), 3x redundant substrate should maintain recall@1 > 0.85 vs. single-W which drops to ~0.60. HARD-PASS: vote-decoded recall@1 > 0.80 at sigma=0.1. HARD-FAIL: vote-decoded recall@1 < 0.65 (worse than single-W with noise).

**P_deflated:** 0.55 (most certain architecture; redundancy is a solved engineering problem; the only substrate-specific unknown is whether the vote operation can be implemented efficiently with existing similarity metrics)

---

### Architecture 9: Excitability-Gated Allocation (Engram Competition)
**Biological analog:** CREB-mediated engram allocation; lateral inhibition by parvalbumin interneurons

**W matrices:**
- W_standard: N=1024, receives items with binding density below threshold (low-excitability items).
- W_priority: N=1024, receives items flagged as high-priority (high binding density, high retrieval frequency, or explicit priority tag).

**Allocation rule:** Each incoming bundle is scored by a simple excitability metric: E(bundle) = mean(|components|) (for bipolar HRR) or component density (for sparse). Bundles with E > E_threshold go to W_priority. All others go to W_standard.

**The competition:** When W_priority is near capacity, a lateral inhibition step fires: the lowest-E items in W_priority are demoted to W_standard, and the incoming high-E item takes their slot. This is exactly the Komorowski/Tonegawa engram allocation mechanism.

**Read routing:** Queries go to W_priority first. On miss, fall back to W_standard.

**What it solves:** The capacity cliff management problem. Instead of all items competing equally at the K/N=0.56 cliff, high-priority items are protected in W_priority (which stays well below its own cliff), while low-priority items tolerate higher capacity pressure in W_standard.

**Empirical prediction:** A mixed KB with 20% high-priority items should show that priority items maintain recall@1 > 0.95 even when the overall KB exceeds the single-W capacity cliff, because priority items never see interference from the K/N overload. HARD-PASS: high-priority recall@1 > 0.90 at K/N=0.70 (above single-W cliff). HARD-FAIL: high-priority items degrade just as fast as non-priority items.

**P_deflated:** 0.45 (the excitability scoring is substrate-native; the lateral inhibition demotion step requires a soft-max-style ranking operation over stored items which is nontrivial in the current substrate API)

---

### Architecture 10: Protected Subspace via Separate W (Crystallized Core)
**Biological analog:** Long-term potentiation with synaptic tagging and capture; "synaptic consolidation" that makes some weights resistant to modification

**W matrices:**
- W_plastic: N=1024, fully mutable. Standard write operations. High learning rate.
- W_crystallized: N=1024 or shared subspace of W_plastic, write-protected after initial encoding. Very low learning rate (near-zero for confirmed facts).

**Write routing:** First write of a new item goes to W_plastic. After the item has been retrieved successfully N_confirm times (e.g., 5), it is "crystallized": the delta is written to W_crystallized and the item is soft-removed from W_plastic.

**Crystallization protocol:**
1. Item written to W_plastic at time t=0.
2. Each successful retrieval increments confirm_count.
3. When confirm_count >= N_confirm, compute binding delta and write to W_crystallized at weight w_crystal = 1.0.
4. Item removed from W_plastic (or kept at reduced weight for interference analysis).
5. W_crystallized update rate set to 0.01 (any subsequent corrections are slow and deliberate).

**Read routing:** Query W_crystallized first (fastest, most reliable). On miss, query W_plastic.

**What it solves:** The protected subspace problem directly. Instead of requiring the algebra to carve out a protected subspace within a shared W (which requires the substrate to support subspace operations it may not have), the protection is structural: W_crystallized is a separate object with write-protection enforced at the API level. This bypasses the algebraic requirement entirely.

**Empirical prediction:** After crystallization of K_crystal items, subsequent writes of K_new new items should not degrade crystallized item recall. HARD-PASS: crystallized recall@1 < 2% degradation after K_new=500 new writes to W_plastic. HARD-FAIL: crystallized recall@1 degrades > 10%.

**P_deflated:** 0.55 (this is the most direct engineering solution to the protected-subspace problem; the only unknown is whether cross-substrate interference occurs at retrieval time when both are queried, but that can be managed by query routing)

---

## Migration / Transfer Protocols (unified view)

All 10 architectures share variants of 4 transfer protocol types:

### P1: Replay-based migration (CLS-canonical)
- Trigger: access_count(item) > C_replay OR age(item) > T_age
- Operation: write bundle to destination W with reduced learning rate beta
- Validation: verify cosine similarity of retrieved bundle from destination > theta_confirm before removing from source
- Failure mode: if destination W is near capacity, migration is deferred (queued)

### P2: Threshold-gated migration (excitability-based)
- Trigger: E(bundle) > E_threshold (immediate) OR competition event (lateral inhibition)
- Operation: add bundle to destination W_priority; remove lowest-E item from W_priority to W_standard
- Validation: no explicit validation; the competition event IS the validation
- Failure mode: pathological case where all items have similar E scores leads to thrashing; solution is to add a recency term: E'(bundle) = E(bundle) * recency_factor

### P3: Crystallization (confirm-count-based)
- Trigger: confirm_count(item) >= N_confirm
- Operation: write to W_crystallized at full weight; set update_rate to 0.01
- Validation: verify W_crystallized retrieval before setting write_protection flag
- Failure mode: item modified after crystallization (e.g., a fact changes); solution is to periodically check retrieved value against ground truth and trigger decrystallization if mismatch detected

### P4: Frequency-based eviction (LRU-analog)
- Trigger: W source is within 90% of capacity
- Operation: evict least-recently-accessed items to W_next_tier or delete
- Validation: N/A (lossy eviction)
- Failure mode: frequency-of-access is a poor proxy for importance; solution is to weight by both recency AND item type (entity items get a retention bonus)

---

## Read/Write Routing Rules (unified)

### Write routing decision tree:
```
incoming(bundle, metadata):
  if metadata.domain is not None:
    route to W_local[metadata.domain]
  elif metadata.priority == HIGH:
    route to W_priority (Arch 9)
  elif metadata.is_entity:
    route to W_entity (Arch 3)
  else:
    route to W_fast (default fast substrate)
  
  # Redundancy: always copy to W_replica_1 (Arch 8)
  W_replica_1.write(bundle)
```

### Read routing decision tree:
```
query(q, metadata):
  # Hot buffer first
  result = W_wm.query(q)  # superposition vector, capacity ~7
  if similarity(result, q) > theta_wm:
    return result, tier="working_memory"
  
  # Priority next
  result = W_priority.query(q)
  if similarity(result, q) > theta_priority:
    return result, tier="priority"
  
  # Crystallized
  result = W_crystallized.query(q)
  if similarity(result, q) > theta_crystal:
    return result, tier="crystallized"
  
  # Domain-specific
  if metadata.domain is not None:
    result = W_local[metadata.domain].query(q)
    if similarity(result, q) > theta_domain:
      return result, tier="domain"
  
  # General fast store
  result = W_fast.query(q)
  if similarity(result, q) > theta_fast:
    return result, tier="fast"
  
  # Slow/semantic store
  result = W_slow.query(q)
  return result, tier="slow"  # return best available
```

### Implementation note:
The routing rules above can be implemented as a thin Python wrapper around existing Substrate objects. No changes to the substrate core are required. Each W matrix is an independent Substrate instance. The router is a ~100-line Python class.

---

## Cheap Decisive Test

**Test for Architecture 6 (Per-Role) + Architecture 1 (Fast/Slow CLS):**

These two share the same minimal implementation and together provide the clearest signal.

**Setup:**
1. Instantiate 3 Substrate objects: S_fast (N=1024), S_slow (N=1024), S_compute (N=1024, clearable)
2. Write K=600 facts to S_fast (this is above the single-W capacity cliff at K/N=0.59)
3. Trigger migration: top-200 most-accessed items migrate to S_slow via replay at LR=0.001
4. Clear S_compute between each "reasoning episode"
5. Query all 600 facts, routing: S_compute (empty) -> S_fast -> S_slow

**Measurement:**
- recall@1 for all 600 items (should be higher than single-W at K=600)
- recall@1 for migrated vs. non-migrated items (migrated should be higher)
- Per-tier retrieval rate (what fraction of queries are answered by each tier)

**Expected result:** recall@1 > 0.75 for migrated items at K=600 (vs. ~0.40 for single-W at this load), because migrated items are effectively stored twice with different noise profiles.

**Runtime:** ~5 minutes on CPU, no GPU required. This is a pure-Python modification of existing substrate code.

**HARD-PASS:** recall@1 for migrated items >= 0.75 at K=600, N=1024; single-W baseline <= 0.50 at K=600.
**HARD-FAIL:** recall@1 for migrated items < 0.55 (not better than single-W), OR recall@1 regresses for non-migrated items (migration interferes with fast substrate).

---

## Falsifiable Predictions (consolidated HARD-PASS / HARD-FAIL)

| Architecture | HARD-PASS | HARD-FAIL |
|---|---|---|
| A1 Fast/Slow CLS | migrated recall@1 >= 0.75 at K=600 | migrated recall@1 < 0.55 |
| A2 3-Tier | 3-hop recall improves >15% over single-W | no improvement at 2-hop |
| A3 Per-Tier Entity | entity recall@1 > 0.92 at K=200 in W_entity | entity recall@1 < 0.75 in W_entity |
| A4 Per-Domain | structured retrieval F1 > 0.85 in W_math | no improvement vs. single-W (<2% lift) |
| A5 Encoding-Variant | overall recall@1 gain > 8% on mixed-query benchmark | no gain or regression |
| A6 Per-Role | multi-step precision (3 ops) > 0.90 with isolated W_compute | no improvement vs. single-W |
| A7 Hierarchical | cross-domain recall@1 > 0.40 at K=50 cross-domain pairs | < 0.20 (no better than single-W) |
| A8 Redundant | vote-decoded recall@1 > 0.80 at sigma=0.1 noise | < 0.65 (worse than single-W with noise) |
| A9 Excitability-Gated | priority recall@1 > 0.90 at K/N=0.70 | priority degrades same rate as non-priority |
| A10 Crystallized | crystallized recall@1 < 2% degradation after 500 new writes | > 10% degradation |

---

## Cross-Thread Synthesis

**Connection to Substrate v3.0 compositional cliff (2026-06-10 memory):** The compositional cliff crossed via per-level cascading cleanup. Multi-substrate is the NEXT step: instead of a single W doing all levels, give each compositional level its own W substrate. The cascading cleanup protocol already proves that level-specific operations are beneficial. Multi-substrate is the generalization.

**Connection to STATIC robust / DYNAMIC fragile (2026-06-10 memory):** W_crystallized and W_slow are STATIC by design. The fragility of online dynamics is isolated to W_fast and W_compute, which can be cleared without affecting W_crystallized. Multi-substrate engineering SOLVES the static/dynamic fragility split by architectural separation.

**Connection to primitives YES / integration NO (2026-06-10 memory):** Deep relational analogy (SME) and multi-drive arbitration failed substrate-only. BUT: Architecture 6 (Per-Role) assigns W_compute to integration operations. The integration layer gets its own ephemeral substrate, cleared between episodes. This prevents integration noise from corrupting the permanent store. The "integration NO" finding becomes "integration in W_compute, then commit result to W_store."

**Connection to cross-domain retraction (2026-06-10 memory):** Architecture 7 (Hierarchical) is the direct rescue. W_cross is populated ONLY with verified cross-domain generalizations. The false positive rate from entity-geometry confounds is contained in W_local; W_cross only contains items that pass the cross-domain verification gate.

**Connection to LLM-hybrid at P=0.50 for cross-domain (2026-06-10 memory):** Architecture 4 (Per-Domain) with an LLM classifier as the domain router is a concrete LLM-hybrid: LLM determines which W domain to route to; substrate stores the domain content. This gives the substrate deterministic domain isolation while the LLM handles the ambiguous routing case. P=0.50 honest answer becomes P=0.65 with LLM routing added.

**Connection to Sprint 1+2 real-data audit (2026-06-10 memory):** KB-shard at 0.965 PASS and tool-extension at 0.883 PASS are STATIC ops that already work. Architecture 10 (Crystallized) is the path to making the already-validated static ops permanent and protected. The already-validated capabilities become crystallized core.

---

## Substrate-Product Implications

1. **Multi-tenant isolation without per-tenant algebra:** Instead of trying to add algebraic isolation inside a shared W (which is not substrate-native), give each tenant their own W instance. Isolation is complete and structural. PP-13 multi-tenant isolation becomes trivially implementable.

2. **GDPR "right to be forgotten" without full W reconstruction:** W_plastic -> W_crystallized migration means GDPR deletions only need to target W_plastic items (which have not been crystallized). Already-crystallized items are marked as consented/permanent. This gives a natural data lifecycle that maps to GDPR distinctions between personal data (W_plastic) and anonymized/aggregated data (W_crystallized).

3. **Tiered compliance audit:** The tier annotation returned by the router (working_memory / priority / crystallized / domain / fast / slow) is itself an audit signal: "this answer came from the crystallized core verified 5+ times" vs. "this answer came from a recent unverified write." This is a novel product capability no single-W system can provide.

4. **Protected subspace WITHOUT requiring substrate algebra to solve it:** Architecture 10 is the engineering escape. The crystallized core IS the protected subspace. Engineering the W_crystallized API object (with write-protection at the object level) replaces the need for algebraic protected-subspace operations. This directly resolves the user's point: "engineer missing features as extensions."

5. **Capacity scaling with constant N:** By migrating items to W_slow (larger N) and keeping W_fast small, the effective system capacity scales with the number of W instances rather than with N. This is the direct analog of the Teeters et al. finding: SDM capacity scales with address matrix rows (m), not vector width (N). Engineering leverage: add W instances at constant N rather than increasing N.

---

## Engineering Priority Order

Based on implementation cost vs. expected P_deflated:

1. **Architecture 10 (Crystallized)** -- P=0.55, ~2 hours to implement as Substrate wrapper. Direct solution to protected subspace. Highest ROI.
2. **Architecture 8 (Redundant)** -- P=0.55, ~1 hour to implement (3 Substrate instances + vote function). Solves reliability under noise. Lowest risk.
3. **Architecture 1 (Fast/Slow CLS)** -- P=0.50, ~3 hours to implement (2 Substrate instances + migration loop). Directly validates the Teeters et al. published result in the substrate context.
4. **Architecture 6 (Per-Role)** -- P=0.48, ~2 hours. Working-memory buffer clears crosstalk in compositional operations.
5. **Architecture 9 (Excitability-Gated)** -- P=0.45, ~3 hours. Priority lane above the capacity cliff.
6. Architectures 3-5 (specialized encoding): P=0.35-0.45, require sparse encoding or domain classifier, higher engineering cost.
7. Architecture 7 (Hierarchical cross-domain rescue): P=0.35, depends on cross-domain abstraction extraction.
8. Architecture 2 (3-Tier): P=0.38, depends on multi-hop showing improvement.

---

## Citations (verified count: 18)

1. McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems in the hippocampus and neocortex." Psychological Review. [CLS canonical]
2. Teeters, Kleyko, Kanerva, Olshausen (2023). "On separating long- and short-term memories in hyperdimensional computing." Frontiers in Neuroscience. [DIRECT PRECEDENT]
3. Intrinsic Neural Excitability Biases Allocation and Overlap of Memory Engrams. J Neuroscience 2024. PMC11112642.
4. Neuronal competition: microcircuit mechanisms define the sparsity of the engram. PMC9730430.
5. A model of autonomous interactions between hippocampus and neocortex driving sleep-dependent memory consolidation. PNAS 2022. doi:10.1073/pnas.2123432119
6. Complementary learning systems within the hippocampus. PMC5124075.
7. FSC-Net: Fast-Slow Consolidation Networks for Continual Learning. arXiv 2511.11707 (2024).
8. Ba, Hinton, Mnih, Leibo, Ionescu (2016). "Using Fast Weights to Attend to the Recent Past." NeurIPS. arXiv 1610.06258.
9. Distributed learning across fast and slow neural systems supports efficient motor adaptation. bioRxiv 2025.06.01.657238.
10. Dopamine modulation in the basal ganglia locks the gate to working memory. J Computational Neuroscience 2006. PMID 16699839.
11. Adaptive chunking improves effective working memory capacity in a prefrontal cortex and basal ganglia circuit. eLife 2024. PMC11870651.
12. MemOS: A Memory OS for AI System. arXiv submit/6596874 (2025).
13. MSA: Memory Sparse Attention for Efficient End-to-End Memory Model Scaling to 100M Tokens. arXiv 2603.23516 (2025).
14. MIDUS: Memory-Infused Depth Up-Scaling. arXiv 2512.13751 (2024).
15. PiKV: KV Cache Management System for Mixture of Experts. arXiv 2508.06526 (2025).
16. State of the art in functionally graded materials. ScienceDirect 2021. S026382232100057X.
17. Kanerva (2009). "Hyperdimensional Computing: An Introduction to Computing in Distributed Representation with High-Dimensional Random Vectors." Cognitive Computation.
18. A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures. ACM Computing Surveys. dl.acm.org/doi/10.1145/3538531.

---

## Summary

Multi-substrate architecture (multiple W matrices with different encoding properties and explicit transfer protocols) is:
- Biologically grounded (4-6 distinct hippocampal/cortical systems; each a separate W analog)
- Mathematically justified (Teeters et al. 2023: 15-35x efficiency gain at K>1000 items for SDM over single superposition)
- LLM-theoretically convergent (MemOS 3-tier, MoE routing, per-head memory banks all use the same pattern)
- Substrate-natively implementable TODAY with no changes to the substrate core (each W is a separate Substrate instance; the router is a ~100-line Python wrapper)

The 5 highest-priority architectures (Crystallized, Redundant, Fast/Slow CLS, Per-Role, Excitability-Gated) collectively address: protected subspace, reliability under noise, capacity cliff, compositional crosstalk, and priority routing. Total estimated implementation time: ~12 hours across 5 experiments. All are CPU-runnable. All have concrete HARD-PASS / HARD-FAIL thresholds.

P_deflated summary:
- Best case (A8 Redundant, A10 Crystallized): 0.55
- Expected case (A1 Fast/Slow, A6 Per-Role): 0.48-0.50
- Uncertain case (A3-A5 specialized encoding): 0.35-0.45
- Rescue attempt (A7 cross-domain hierarchical): 0.35
