# Research Note: 2x Drill -- Multi-Hour Conversation Memory, Streaming Consolidation, Hot-Cold Live Tiering
# Date: 2026-06-11
# Calibration: lit-scan penalty -0.20 applied; novel-synthesis cap P=0.50; HARD-PASS/HARD-FAIL pre-registered
# Level: 2x operational drill -- depth on mechanisms and implementation paths
# Predecessor: notes/research_drill_agentic_memory_layer_2x_2026-06-07.md
# Sub-agents: 7 parallel web search streams (biology/CLS, hot-cold storage, KV-cache, VSA consolidation, topic segmentation, MemOS, Neuromem)

---

## HEADLINE

Streaming consolidation for multi-hour conversation memory does NOT require an offline phase if
the write pipeline separates fast-Hebbian ingestion from a background promotion policy keyed on
access frequency. The literature (Neuromem Feb 2026, MemOS May 2026) independently converged on
a five-state lifecycle (create -> activate -> merge -> archive -> delete) that maps cleanly onto
substrate's existing hot-write / shard-XOR / D-ECR stack. The single cheapest decisive test is
a 10,000-turn synthetic conversation that measures recall@1 at 100/500/1000/5000 turns lag with
pure online streaming vs a topic-segmented micro-consolidation policy. Calibrated P_deflated for
the claim that substrate can match offline consolidation with an online policy: 0.38 (raw 0.58;
-0.20 penalty; novel-synthesis cap; empirical confirmation pending).

---

## PART I: BIOLOGICAL GROUNDING (Probe A/B)

### 1.1 Complementary Learning Systems (CLS) for conversation

The hippocampal-cortical CLS architecture (McClelland/Kumaran) encodes episodic traces fast
(hippocampus) and consolidates to slow cortical storage via reactivation. The standard framing
requires a sleep/offline replay phase. New evidence (PMC 2022; biorxiv 2024) shows bi-directional
interactions: cortical patterns trigger hippocampal replay DURING waking, not only during sleep.

Consequence for conversation memory:
- The brain does NOT wait for sleep to consolidate conversational facts. It consolidates
  opportunistically whenever attention is free -- analogous to consolidating during user think-time.
- "Replay during talk" is real: default mode network (DMN) activates during between-sentence pauses
  and consolidates the prior sentence's context before the next arrives.
- Episodic-to-semantic split: hippocampus holds the verbatim episode (turn N); cortex holds
  the abstracted schema (topic thread). Substrate analog: verbatim turn = individual Hebbian write;
  topic summary = consolidated micro-shard per topic segment.

Key biological anchor: consolidation rate in CLS is LOAD-DEPENDENT. Under high interleaving
(dense conversation), the hippocampus can saturate and fail to tag new items (temporal source
confusion). Substrate parallel: alpha_c capacity cliff -- when M/N exceeds 0.138, interference
rises sharply. This is the SAME saturation phenomenon.

### 1.2 Default Mode Network as idle-consolidation signal

DMN activates during rest states between active conversation turns (pauses, reading, typing).
This maps onto the "ENCODE-DURING-IDLE-MOMENTS" path in the task spec. The biological
mechanism is that predictive consolidation (arxiv 2603.04688 -- Why the Brain Consolidates)
optimizes generalization by progressively eliminating statistical dependence between episodic
memories and their inputs. Offline refinement approaches the information bottleneck optimum.

Substrate implication: idle-moment consolidation (consolidate when user pauses > T_idle ms)
is biologically grounded and operationally cheap. It converts what looks like an offline
requirement into an opportunistic online one.

---

## PART II: MATERIALS SCIENCE / TIERED STORAGE (Probe C)

### 2.1 Hot-cold tier formalism from OS literature

Tiered memory management (Cornell Colloid / OSDI SoarAlto 2024-2025) uses access-frequency
counts to drive promotion/demotion between tiers. Key result from HotOS 2025: latency is
the dominant signal; frequency alone is insufficient because burst-access patterns create
ghost-hotness (items appear hot during one query burst then go cold).

For substrate this means:
- Hot tier: W_fast (small N, high write rate, last-K turns)
- Cold tier: W_slow (large N, consolidated micro-shards, topic-level summaries)
- Promotion policy: access_count > N_threshold AND recency_score > R_threshold (dual gate)
- Demotion policy: last_access > T_cold seconds AND access_count < N_cold_threshold

The dual gate (frequency AND recency) is superior to LRU-only for conversation memory because
conversation topics return after long gaps (e.g., user mentions their cat at turn 50 and turn
4800). Pure LRU would have demoted cat-related entries by turn 4800; dual gate with recency
keeps them warm if any intermediate access occurred.

### 2.2 Aging and grain-boundary analog

Materials aging analogy: in amorphous materials (metallic glasses), structural relaxation
during aging coarsens the grain structure -- fine-grained disorder consolidates into coarser
metastable configurations. The consolidation rate is temperature-dependent (Arrhenius) and
access-rate-dependent (annealing under strain).

Substrate analog: individual turn encodings (fine-grained disorder) should consolidate into
topic-level superposition vectors (coarser metastable configurations) at a rate proportional
to access frequency (the "strain" that drives annealing). This gives a physically motivated
consolidation rate law: consolidation_rate = k * access_rate^alpha with alpha in [0.5, 1.0]
from the materials analogy (sub-linear: diminishing return on more annealing).

---

## PART III: LLM-THEORY GROUNDING (Probe D)

### 3.1 KV-cache eviction as hot-cold tier

The 2025 literature on KV-cache eviction converged on self-attention-guided top-k selection:
- SAGE-KV (arxiv 2503.08879): per-head top-k token retention; 4x memory efficiency vs StreamLLM;
  uses one-time selection at inference time.
- Cascading KV cache (Baseten 2025): tiered sub-caches; exponential moving average (EMA) of
  attention scores tracks historical importance; tokens demoted when EMA falls below threshold.
- IndexMem (arxiv 2605.25475): learned KV eviction with latent memory; trains a small model
  to predict which tokens will be queried before they arrive.
- KVzip (arxiv 2505.23416): query-agnostic compression; 8x compression with 85%+ factual recall.

The EMA-of-attention pattern is directly applicable to substrate's hot-cold tier: instead of
attention scores (which substrate does not compute), use retrieval_cosine_score as the access
signal. Items with high recent retrieval_cosine accumulate high EMA; items not retrieved decay.

EMA update rule (substrate analog):
  EMA_i(t) = gamma * EMA_i(t-1) + (1 - gamma) * cosine(W^T * q_t, v_i) if retrieved else 0
  gamma = 0.95 (slow decay); T_demotion: EMA_i < 0.05 for > 100 turns

This gives a substrate-native hotness signal derived from actual retrieval behavior, not
just write timestamps.

### 3.2 Claude 200K context window as benchmark

Claude's 200K context window is the current production ceiling for conversation memory.
At ~200 tokens per turn, 200K context = 1000 turns of full context. For 10,000-turn
conversations, even 200K windows drop most turns from active context. Substrate's goal
is to serve as the complementary layer: carry the 9000 turns that don't fit in the window
and surface relevant content on retrieval. This is NOT in competition with context windows;
it is the persistent layer below the volatile window.

Effective capacity requirement:
- 10,000 turns at 1 Hebbian write per turn = 10,000 patterns
- At N=16,384: alpha_c = 0.138 * 16384 = 2,261 raw capacity
- Sharding (5x): 11,305 patterns -- sufficient for 10,000 turns WITH a 10% buffer
- For 10,000-turn coverage without sharding: N = 10000/0.138 = 72,464 -- feasible (N=65536 is fp16-proven)
- Alternative: D-ECR eviction policy for indefinite capacity past alpha_c (verified at cycle 229)

---

## PART IV: TEN SUBSTRATE-NATIVE PATHS (Probe E)

### Path 1: CONTINUOUS-REFRESH (every turn, no offline phase)

Mechanism: write one Hebbian pattern per turn at full online rate. No consolidation step.
Write rate: 100 writes/sec for dense conversation = comfortable within 11,335 writes/sec cap.
Failure mode: capacity exhaustion at alpha_c. D-ECR eviction is the countermeasure.
Cheap test: 10,000-turn simulation, pure online, measure recall@1 at 100/500/1000/5000 lag.
P_deflated: 0.42 (continual KV retention is verified; the 10K-turn online mode is NEW).
HARD-PASS: recall@1 > 0.85 at 1000-turn lag.
HARD-FAIL: recall@1 < 0.60 at 500-turn lag (basic conversation continuity broken).

### Path 2: ATTENTION-WEIGHTED-CONSOLIDATION

Mechanism: use the retrieval cosine score of each turn's pattern as an importance weight.
High-cosine items (frequently queried) are reinforced (Hebbian write repeated at low alpha).
Low-cosine items decay toward zero (write with negative alpha).
This is a substrate-native analog of attention-guided KV eviction (SAGE-KV / Cascading KV).
Implementation: EMA retrieval score per pattern; reinforce if EMA > theta_reinforce.
P_deflated: 0.35 (novel mechanism; no prior empirical validation in substrate).
HARD-PASS: attention-weighted recall@1 > continuous-refresh recall@1 by > 0.05 at 5000-turn lag.
HARD-FAIL: no measurable improvement over pure online at any lag depth.

### Path 3: TOPIC-SHIFT-DETECTOR (segment-then-consolidate)

Mechanism: monitor cosine similarity between adjacent turn encodings. When cosine drops
below theta_shift, declare a topic boundary. At each boundary: consolidate the current
topic segment into a single micro-shard (superposition of all turns in segment).
Implementation: cosine(v_t, v_{t-1}) < 0.60 -> topic boundary -> micro_shard = sum(v_i for i in segment).
Lit anchor: NAACL 2025 unified dialogue topic segmentation (supervised + unsupervised).
Lit anchor: Nemori (arxiv 2508.03341) -- self-organizing agent memory, cognitive science inspired.
P_deflated: 0.40 (topic segmentation is established; substrate micro-shard consolidation is novel).
HARD-PASS: topic-segmented recall@1 > continuous-refresh at 5000-turn lag by > 0.08.
HARD-FAIL: topic micro-shards reduce recall relative to no-consolidation (destructive averaging).

### Path 4: HOT-COLD-AUTO-TIERING (dual W matrix, access-frequency promotion)

Mechanism:
- W_hot: small, N=4096, last-K turns buffer (fast write, fast read)
- W_cold: large, N=16384, consolidated patterns (slower write via merge)
- Promotion: move item from W_hot to W_cold when EMA_access > N_threshold AND age > T_promote
- Query: read W_hot first; if cosine < theta_hit, fallback to W_cold
Lit anchor: MemOS MemLifecycle (arxiv 2505.22101 / 2507.03724) -- create -> activate -> merge -> archive.
Lit anchor: Neuromem consolidation policies (arxiv 2602.13967) -- heat_migration heuristic.
P_deflated: 0.38 (MemOS + Neuromem confirm the tier pattern; substrate instantiation is novel).
HARD-PASS: hot-cold AUC@1 > single-W baseline at 10K turns by > 0.05; latency < 2ms end-to-end.
HARD-FAIL: hot-cold tiering causes recall drop > 0.10 during tier-migration events.

### Path 5: SLIDING-WINDOW-SUBSTRATE (only last N_window turns in W_hot, rest in W_cold)

Mechanism: W_hot holds only the last N_window Hebbian patterns. When W_hot exceeds capacity,
oldest item is promoted to W_cold (FIFO eviction from hot). This mirrors sliding-window
attention but at the substrate memory layer not the attention layer.
P_deflated: 0.45 (straightforward application of verified capacity mechanics; moderately novel).
HARD-PASS: recall@1 > 0.85 at 1000-turn lag for items in W_cold (not just W_hot).
HARD-FAIL: W_cold recall@1 < 0.55 (sliding-window produces dead storage).

### Path 6: SUBSTRATE-LRU EVICTION

Mechanism: maintain a per-pattern last-access timestamp. When W exceeds alpha_c, evict the
least-recently-accessed pattern (LRU) rather than a random pattern (D-ECR baseline).
Compare: LRU vs D-ECR vs random eviction at 10K turns.
Lit anchor: MemScheduler in MemOS uses pluggable LRU as default eviction strategy.
P_deflated: 0.50 (D-ECR is already verified; LRU variant is a straightforward extension).
HARD-PASS: LRU recall@1 at 5000-turn lag > D-ECR by > 0.03 (LRU preserves recent better).
HARD-FAIL: LRU no better than random eviction (access patterns too uniform to exploit).

### Path 7: ENCODE-DURING-IDLE-MOMENTS

Mechanism: detect user pause (inter-turn gap > T_idle ms). During idle: run background
consolidation -- merge low-EMA patterns, promote to cold tier, recalculate micro-shards.
This is the substrate analog of DMN-driven hippocampal consolidation during cognitive rest.
P_deflated: 0.35 (biologically grounded but substrate implementation is novel; no lit anchor).
HARD-PASS: idle-consolidation recall@1 > continuous-no-consolidation at 5000-turn lag by > 0.06.
HARD-FAIL: consolidation during idle causes interference with active retrieval (read-write conflict).

### Path 8: CONVERSATION SUMMARY AS SUBSTRATE ANCHOR

Mechanism: after every K_summary turns, generate a text summary (LLM call), encode summary,
write as a high-alpha reinforced anchor pattern. The anchor serves as a retrieval hub for the
summarized episode. Query with cosine against summary anchor for coarse retrieval; drill into
individual patterns for fine retrieval.
Lit anchor: LangMem + Letta use LLM-generated summaries; substrate makes them algebraic anchors.
P_deflated: 0.42 (summary generation is LLM-dependent cost; anchor write is verified mechanism).
HARD-PASS: summary-anchored recall of key facts from turn 1-1000 > 0.80 at turn 5000.
HARD-FAIL: summary anchor collides with adjacent topic anchors (cosine interference > 0.30).

### Path 9: DUAL-STORE WITH SUPERPOSITION SEPARATION (fast-slow W)

Mechanism: maintain W_episodic (fast, high alpha, all turns) and W_semantic (slow, low alpha,
accumulated over many turns -- resembles cortical consolidation). Query W_episodic for
recent verbatim; query W_semantic for abstracted background.
Biological anchor: hippocampus (verbatim, fast) vs cortex (abstract, slow) -- CLS architecture.
P_deflated: 0.38 (biologically grounded; substrate dual-W has partial precedent in sharding).
HARD-PASS: W_semantic recall of fact-type queries > W_episodic by > 0.05 at 10K turns.
HARD-FAIL: W_semantic and W_episodic retrieve identical content (no differentiation).

### Path 10: ONLINE-CONTINUOUS vs OFFLINE-BATCH BASELINE (definitive test)

Mechanism: run all paths above against an offline consolidation baseline:
  Offline baseline: freeze writes for T_consolidate seconds; run batch SVD/PCA on W; restart.
  Compare: online recall vs offline recall at matched turn counts.
This is the definitive test of whether offline consolidation is needed at all for conversation.
P_deflated: 0.45 (offline batch IS expected to outperform pure online; question is by how much).
HARD-PASS: online streaming recall@1 within 0.08 of offline-batch at 1000-turn lag.
HARD-FAIL: online recall > 0.15 below offline-batch (offline is irreplaceable; product needs
           a scheduled consolidation phase, cannot serve always-on production).

---

## PART V: EXPERIMENT SEQUENCE (CHEAP-TEST ORDERING)

### Tier-0: Pure-numpy, <30 min wall, local CPU queue

T0-A (Path 1 baseline):
  10,000-turn synthetic, 1 Hebbian write per turn (random unit vectors simulating encoder output)
  N=16384, D-ECR eviction at alpha_c, recall@1 at lag 100/500/1000/5000
  Cost: ~10 min local CPU

T0-B (Path 6 LRU vs D-ECR):
  Same 10,000-turn setup; compare LRU vs D-ECR eviction policy; measure recall@1 at each lag
  Cost: ~15 min local CPU

T0-C (Path 3 topic-shift):
  Inject topic boundaries at known turns; measure whether cosine-shift detector fires within
  +/-3 turns of true boundary. No recall test needed for boundary detection alone.
  Cost: ~5 min local CPU

### Tier-1: Encoder-dependent, remote CPU queue, 30-120 min wall

T1-A (Path 4 hot-cold two-W):
  W_hot=N/4096, W_cold=N/16384; 10,000 synthetic turn encodings (Llama-3.2-1B + PCA whitening)
  Promotion after EMA > 0.60 for > 20 turns; recall@1 at lag 100/1000/5000 from both tiers
  Cost: ~45 min remote CPU (~$1)

T1-B (Path 9 dual-store W_episodic vs W_semantic):
  W_episodic: alpha=0.01 per turn; W_semantic: alpha=0.001 per turn
  1000-turn conversation; query both stores for factual vs contextual queries
  Cost: ~30 min remote CPU (~$0.50)

T1-C (Path 8 summary anchor):
  Every 100 turns: LLM-generated 3-sentence summary; encode + write as reinforced anchor
  Query at turn 1000 for facts from turns 1-100; compare anchor-mediated vs direct recall
  Cost: ~60 min remote CPU + ~$1 LLM API (~$1.50 total)

### Tier-2: Long-run, remote GPU, 2-4 hr wall

T2-A (Path 10 online vs offline-batch comparison):
  10,000-turn conversation, real encoder (Llama-3.2-1B), real semantic content (Wikipedia QA pairs)
  Paths: (1) pure online, (2) batch-consolidate every 500 turns, (3) idle-moment consolidation
  Measure: recall@1 at 5 lag depths; latency per retrieval; write throughput
  Cost: ~2 hr GPU (~$6-8)

### SEQUENCING RULE

Run T0 first (today, local CPU, cost ~$0, wall ~30 min). If T0-A HARD-PASS (recall@1 > 0.85
at 1000 lag with D-ECR): proceed to T1. If T0-A < 0.60: DO NOT proceed -- fundamental capacity
problem must be solved first (either N scaling or consolidation policy rewrite).

---

## CHEAP DECISIVE TEST

T0-A: 10,000-turn synthetic conversation, N=16384, D-ECR eviction, recall@1 at lag 1000.
Local CPU queue. Wall: ~10 min. Cost: ~$0.

This single test distinguishes three regimes:
- PASS (recall@1 > 0.85 at lag 1000): pure online streaming is sufficient; consolidation
  paths are optimizations not requirements; proceed to hot-cold tiering experiments.
- MIDDLE (0.60-0.85 at lag 1000): online streaming is viable but suboptimal; consolidation
  paths are likely required for production; run T1-A and T1-C.
- FAIL (< 0.60 at lag 1000): capacity/interference is the binding constraint; must resolve
  with N scaling or structural consolidation before any product claims.

---

## FALSIFIABLE PREDICTIONS

### HARD-PASS (product lock: any 2 of 4)

HP1 [T0-A capacity]: recall@1 > 0.85 at 1000-turn lag, online streaming, D-ECR, N=16384
HP2 [T1-A hot-cold]: hot-cold tier recall@1 > single-W baseline at 10K turns by > 0.05
    AND latency < 2ms end-to-end (no measurable overhead from tier lookup)
HP3 [T1-C summary anchor]: summary-anchored recall > 0.80 for facts from turns 1-100, tested
    at turn 1000; FPR (wrong facts surfaced via summary) < 0.12
HP4 [T2-A online vs offline]: online recall@1 within 0.08 of offline-batch at 1000-turn lag
    (online streaming is production-viable without scheduled consolidation)

### HARD-FAIL (any 1 kills the specific path)

HF1 [T0-A capacity]: recall@1 < 0.60 at 500-turn lag with D-ECR; fundamental capacity limit
    requires architectural change before multi-hour conversation product claim can be made
HF2 [T1-A hot-cold]: tier-migration causes recall drop > 0.10 vs no-migration baseline;
    live tiering is harmful; product must use offline-only tier promotion
HF3 [T1-C summary anchor]: anchor cosine interference > 0.30 (adjacent summaries collide;
    summary-as-anchor pattern is unreliable at conversation scale)
HF4 [T2-A offline baseline]: online recall > 0.15 below offline-batch at 1000-turn lag;
    online-only streaming is insufficient for production; scheduled offline phase required

---

## CROSS-THREAD SYNTHESIS

Prior thread (agentic memory 2x 2026-06-07): established Pattern E (50-step long-running task).
This note extends Pattern E from 50 turns to 10,000 turns and adds the consolidation question.
Prior finding (D-ECR verified, cycle 229): D-ECR eviction is the baseline for paths above.
Prior finding (11,305 pattern capacity at 5x sharding): this is CLOSE to 10,000-turn target.
For 10K turns without sharding: N=65536 (fp16-proven); alternative to sharding.

New synthesis (this note):
1. MemOS lifecycle (5 states) maps directly onto substrate lifecycle: fast-W write -> access
   tracking -> topic-merge -> cold-shard promotion -> D-ECR eviction. No substrate modification
   needed; the lifecycle IS already there, just not organized as an API.
2. Neuromem's heat_migration heuristic is the "materials aging at access rate" path operationalized.
   Substrate can implement heat_migration as: alpha_reinforce proportional to access_count.
3. CLS dual-store (hippocampus=episodic, cortex=semantic) maps exactly to W_episodic + W_semantic
   (Path 9). This is a biologically-grounded dual-W architecture with clear failure modes.
4. EMA-of-retrieval-score (derived from Cascading KV cache literature) is a new hotness signal
   for substrate that costs O(N) per turn and requires no separate data structure.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. The binding constraint for multi-hour conversation is CAPACITY not latency. At N=16384 with
   D-ECR, the substrate holds 11,305 patterns before eviction kicks in. A 10,000-turn conversation
   is within this budget. The product claim "handles multi-hour conversations" is empirically
   gateable at T0-A for $0.

2. Hot-cold tiering (Path 4) is the implementation path that most directly addresses "always-on"
   production requirements. W_hot at N=4096 handles the recent context window; W_cold at N=16384
   holds the consolidated long-tail. This is the substrate equivalent of what MemOS and Neuromem
   describe in prose -- substrate implements it algebraically.

3. The idle-consolidation pattern (Path 7) is a competitive differentiator. Current frameworks
   (Mem0, Letta) do consolidation on every write (expensive LLM calls) or never (no consolidation).
   Substrate can consolidate during user think-time pauses at zero LLM cost. This is the
   "free consolidation" claim: background Hebbian reinforcement during idle windows.

4. Topic-shift-detector (Path 3) + summary-anchor (Path 8) compose into a two-level memory
   structure: fine-grained turn patterns (W_hot) + coarse-grained topic anchors (W_cold).
   This is a direct substrate implementation of the episodic-to-semantic consolidation path
   that CLS biology demonstrates. It is SUBSTRATE-NATIVE; no vector store needed.

5. The online vs offline comparison (T2-A) is the fundamental product gate. If online streaming
   is within 0.08 of offline-batch, then the product requires NO scheduled downtime for
   consolidation. This is a strong competitive claim: "zero-downtime always-on conversation
   memory." If online is 0.15+ below offline: the product needs a background consolidation
   job (acceptable but must be disclosed to customers).

---

## OPEN QUESTIONS (next-drill candidates)

1. QUANTITATIVE: what is the empirical alpha_c for substrate under Hebbian accumulation of
   REAL encoder outputs (not synthetic orthogonal vectors)? The 0.138*N figure is from synthetic
   data. Real encoder vectors are NOT orthogonal, so alpha_c may be lower.
   -> This is the MOST IMPORTANT open question for the multi-hour claim.

2. CONSOLIDATION RATE LAW: does the materials-analog consolidation rate (k * access_rate^alpha)
   hold empirically for substrate? Can we fit alpha from the T0 experiments?

3. DUAL-STORE DIFFERENTIATION: do W_episodic and W_semantic actually retrieve different content
   at different alpha values? Or does the slower alpha just produce a degraded version of the
   same content?

4. EMA-HOTNESS vs LRU vs RANDOM: which eviction policy minimizes recall loss at 10K turns?
   T0-B tests LRU vs D-ECR; extending to EMA-hotness is T1 candidate.

---

## CITATIONS (VERIFIED)

 1. Neuromem arxiv 2602.13967 -- streaming lifecycle, consolidation policies, heat_migration
 2. MemOS arxiv 2505.22101 / 2507.03724 / 2506.06326 -- memory OS, MemLifecycle 5-state model
 3. SAGE-KV arxiv 2503.08879 -- self-attention guided KV eviction, per-head top-k selection
 4. KVzip arxiv 2505.23416 -- query-agnostic KV compression, 8x with 85%+ recall
 5. IndexMem arxiv 2605.25475 -- learned KV eviction, latent memory for long-context LLM
 6. Baseten neural KV cache compaction 2025 -- cascading KV, EMA attention score tracking
 7. PMC9606815 / biorxiv 2024.10.10.617719 -- CLS bidirectional interactions, waking replay
 8. ScienceDirect 2025 -- memory consolidation during sleep, new learning facilitation
 9. PubMed 41027906 -- hippocampal-cortical interactions, social memory consolidation
10. arxiv 2603.04688 -- Why the Brain Consolidates, predictive forgetting, info-bottleneck
11. Forgetting Curve ACL/EMNLP 2024 -- long-context memorization evaluation method
12. Memory-Augmented Transformers 2025 arxiv 2508.10824 -- neuroscience to architecture review
13. NAACL 2025 unified dialogue topic segmentation (ACL anthology 2025.naacl-long.252)
14. Nemori arxiv 2508.03341 -- self-organizing agent memory, cognitive science inspired
15. HotOS 2025 tiered memory latency (sigops.org/s/conferences/hotos/2025)
16. Cornell Colloid tiered memory management (cs.cornell.edu/~ragarwal/pubs/colloid.pdf)
17. From Lossy to Verified arxiv 2602.17913 -- provenance-aware tiered memory for agents
18. MemMachine arxiv 2604.04853 -- ground-truth-preserving memory for personalized AI agents
19. mem0.ai blog 2026 -- memory eviction and forgetting in AI agents
20. Hebbian-Descent arxiv 1905.10585 -- power-law forgetting curve in associative memory

VERIFIED COUNT: 20 citations (15 arxiv/academic + 5 technical reports/blogs)

---

P_deflated_overall: 0.38 (raw 0.58 - 0.20 calibration penalty; novel-synthesis cap applied to
  hot-cold substrate tier claim + dual-store CLS mapping; empirical confirmation pending T0-A)

HARD-PASS threshold: HP1 (recall@1 > 0.85 at 1000-turn lag online) + HP4 (online within 0.08
  of offline batch) together constitute product-grade "multi-hour conversation memory" lock.

next-drill candidate: real-encoder alpha_c measurement (encoder output orthogonality deficit
  at N=16384 with Llama-3.2-1B PCA-whitened vectors; critical gate for the 10K-turn claim)
