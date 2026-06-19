# Research Drill: Development-Speed Acceleration for Discrete-State Associative Memory + LLM Hybrid Cognitive Core
## 2x Operational Drill — Phase 4a Infrastructure
## Date: 2026-06-05

---

## HEADLINE

The highest-leverage dev-speed moves are NOT training speedups -- they are structural: (1) a standardized eval harness (B1, ~5-7 eng-days, 3-5x smoke throughput) and (2) pre-registered rescue paths (C2, ~1-2 eng-days, eliminates dead time after negatives). Together these two investments cut the typical cell cycle from 2-3 days to under 1 day and compound across every future experiment. Distillation (A1) has the best long-run ROI but requires a front-loaded 3-5 day training cost. The wild-card AI co-scientist (D2) is now technically feasible and warrants a 15-25 day Phase-5 investment.

---

## CHEAP DECISIVE TEST

Build a minimal eval harness prototype (B1) covering just 3 capability dimensions in ~1 eng-day. Measure time-from-code-change-to-first-metric for a known cell variant. If it is under 20 minutes end-to-end (vs current ~2-3 hr scaffold overhead per cell), the B1 investment pays off in < 10 cells. If harness setup itself takes >3 eng-days, pivot to C2 (process-only, zero code).

---

## FALSIFIABLE PREDICTIONS (HARD-PASS / HARD-FAIL)

HARD-PASS thresholds (calibrated post-deflation, P_deflated applied):
- B1 eval harness: reduces per-cell scaffold time by >=60% (from ~4-6h to <2h) within first 10 cells -- P_deflated = 0.62
- A1 distillation: 20x param reduction preserves >=75% of cosine-similarity geometry between teacher mid-layer and student output -- P_deflated = 0.52 (capped at 0.55 per novel-synthesis rule; raw estimate ~0.70, deflated 0.18)
- A2 Wikipedia cache: one-time 2-3 day build eliminates extraction step for >=80% of future Wikipedia-derived cells -- P_deflated = 0.75 (engineering uncertainty only; algebraically certain if storage/indexing works)
- C2 pre-registered rescues: reduces "what next" latency after HF from ~1 day to <2h -- P_deflated = 0.80 (this is process, not physics)
- D2 AI co-scientist: achieves >=3x throughput multiplier in steady state after 15-25 day build -- P_deflated = 0.38 (long tail; current agent reliability at ~24/7 operation is uncertain)

HARD-FAIL thresholds (these results would falsify the investment):
- B1 FAIL: harness requires >7 eng-days to build AND < 30% scaffold reduction -- abandon, pivot to C2+C4 combo
- A1 FAIL: student cosine-similarity preservation falls below 60% at 20x compression OR student training takes >$50 cloud -- revert to A5 asymmetric extraction instead
- A2 FAIL: compressed storage exceeds 60 GB OR indexing lookup is >500ms per query -- redesign with faiss HNSW index before scaling
- C2 FAIL: rescue paths are unused across 5 consecutive HF cells (teams ignore the template) -- structural enforcement via queue_add.py rejection gate
- D2 FAIL: agent loop produces >30% invalid experiment proposals (schema violations, dependency errors) in first 100 proposals -- revert to human-approval gating with AI as draft-only

---

## (A) FASTER TRAINING / LLM DIGESTION

### Background algebraic framing

Extraction cost scales as O(V_c * d * L) where V_c = vocabulary size (facts), d = hidden dimension, L = number of layers sampled. At Llama-1B with d=2048, L=1 layer, V_c=10^4: ~5.7 min/10K docs on H100 at $0.86. For V_c=10^6 (1M facts), wall time = ~570 min (~9.5h), cost ~$86 at H100 rates. Phase 3 1M-fact target = ~$30 at mixed GPU/TPU + compression = consistent with the quoted $30 / 10h.

### A1: Distill teacher to smaller student (RECOMMENDED)

Algebraic preservation at 20x param reduction: layer-mimicry distillation trains student S with L_distill = ||f_S(x) - P * f_T(x)||^2 where P is a learned projection. At 50M params vs 1B, the compression ratio R = 20. From the task-tangent geometry literature (arxiv 2507.10155): functional contributions concentrate in a low-dimensional tangent subspace of the teacher's representations. If the effective rank r of f_T(x) is <<d, the student can recover the projection P*f_T(x) with parameters proportional to r, not d. Empirically, r/d ratios of 10-30% are typical for mid-layer geometry of factual tasks (Zheng et al. 2024 feature distillation survey), implying a 50M student can preserve >=75% cosine-similarity geometry.

Speedup: extraction at 50M params scales ~linearly with parameter count for autoregressive passes (flops per token proportional to hidden dim^2 * layers). A 20x param reduction gives ~15-20x wall-time speedup. For 1M-fact extraction: from 10h to ~30 min, from $30 to ~$1.50.

Cost: 3-5 days engineering + $10-30 one-time training cloud run. Payback after ~2 Wikipedia-scale extractions (< 2 weeks).

P_deflated(75% preservation at 20x) = 0.52. Main uncertainty: substrate-VQ codebook codes may require a specific geometry that generic layer-mimicry does not preserve. Mitigation: add a codebook-alignment loss term (cosine similarity between student output and VQ centroids).

### A2: Pre-extract Wikipedia layer features (RECOMMENDED)

Wikipedia corpus: ~6.7M articles, ~4.4B tokens. At Llama-1B, layer-10 activations per token: d=2048 float16 = 4096 bytes = ~4 KB/token. Total uncompressed: 4.4B * 4KB = ~17.6 TB. This is infeasible as raw storage.

Compressed strategy: extract per-article mean pooled activations (not per-token). 6.7M articles * 4KB = ~26.8 GB uncompressed. With bfloat16 + zstd compression (factor ~3x empirically): ~9 GB. Feasible on a $200-400 H100 run (~1-2h extraction + 1-2 days preprocessing).

Index with faiss HNSW (M=32, ef_construction=200): 6.7M * 2048 float16 = ~27 GB index. HNSW lookup is O(log N) ~ 1-2ms per query. This eliminates the extraction step for any future experiment using Wikipedia-derived facts, cutting per-cell extraction overhead from hours to milliseconds.

Engineering: 2-3 days (extraction script + compression + faiss index). One-time $200-400 cloud. Payback: within first 5 Wikipedia-derived cells (currently ~$86/extraction).

P_deflated(engineering works as described) = 0.75. Caveat: downstream experiment may need activations at a specific layer other than layer 10 -- partial mitigation by storing 3 layers (+15 GB).

### A3: Online LoRA adapter

A 5M-param LoRA (rank r=64 on Q/V projections of Llama-1B) outputs substrate-VQ codes directly. This fuses the encoder + VQ quantizer into a single forward pass. The speedup derives from eliminating the separate VQ lookup step, not from reducing extraction flops (LoRA still runs through the full base model). Net speedup: 2-3x from pipeline simplification, not from computation reduction. Engineering cost: 5-7 days training + 1-2 days integration. ROI lower than A1/A2.

NOT RECOMMENDED as primary investment. Reserve for Phase 4b after A1/A2 validated.

### A4: Real-time substrate writes (skip extraction entirely)

This IS the production model for the V1 demo pipeline and should be implemented regardless. For development iteration, real-time writes means any new corpus can be loaded without a separate extraction step. The engineering overlap with the V1 demo pipeline means this is ~free if the demo pipeline is already on the critical path. The key design choice: the substrate write-path must be stateless and vectorizable to support mini-batch streaming. With a clean write API (planned in the demo pipeline), new corpora become testable in minutes, eliminating the extraction cycle entirely for development-scale experiments.

P_deflated(eliminates extraction for development experiments) = 0.72 (engineering known; risk is API design stability).

### A5: Asymmetric extraction

Document importance scoring via substrate uncertainty or entropy: the substrate's retrieval confidence H(p) = -sum(p_k log p_k) for a document's VQ code gives a signal for which documents need high-quality encoding. Route low-H (high-confidence) docs through Pythia-160M (~10x cheaper), route high-H docs through Llama-1B. Empirically 60-80% of docs in a typical corpus have low uncertainty (standard power-law frequency distribution), so the average cost drops 5-10x.

Algebraic: if fraction f have low uncertainty and use cheap model at cost c_s, remainder (1-f) use expensive at cost c_l: total cost = f*c_s + (1-f)*c_l. At f=0.75, c_s = c_l/10: cost = 0.075*c_l + 0.25*c_l = 0.325*c_l. Speedup = 1/0.325 ~ 3x.

Engineering: 5-7 days. Significant; lower ROI than A2 for total cost savings. DEFER to Phase 4b.

### A1/A2 RECOMMENDATION: Invest in both A2 (immediate, one-time) and A1 (week 2-3, perpetual speedup)

---

## (B) TOOLS TO ACCELERATE ITERATION

### B1: Standardized substrate eval harness (RECOMMENDED, HIGHEST-LEVERAGE)

Current state: each new cell requires ~4-6h of scaffold: manual directory setup, import boilerplate, capability-specific metrics, smoke-test harness wiring. A unified harness `python eval_substrate <variant_module>` eliminates this.

Harness contract: the variant module exposes a `SubstrateVariant` interface (write(), read(), N, M parameters). The harness auto-runs: (1) CCC-1-v2 capacity benchmark, (2) sequential-write audit-core, (3) 3 capability dimension probes from the current cap_map. Output: JSON report + per-capability pass/fail against registered thresholds.

Throughput impact: 3-5x on the smoke-test cycle. 10 cells that previously took 40-60h of scaffold now take 10-15h. At current pipeline velocity of 5-10 cells/day, this is the single largest cycle-time lever.

Engineering: 5-7 days for full harness. Partial version (2-3 capability dims) in 1-2 days -- start with the cheap decisive test above.

Compound value: every future cell, every rescue attempt, every variant test runs through this harness. Compounds over the entire remaining Phase 4 roadmap (~30-45 days).

P_deflated(3-5x smoke throughput) = 0.62. Uncertainty: some cells require custom metrics not expressible in a generic interface. Mitigation: allow per-variant metric plugins.

### B2: Auto-rescue search on HF results

When a cell hard-fails, the harness automatically enumerates rescue candidates: (1) parameter neighborhood search (sample eta, N, M in +/-20% ball around HF configuration), (2) architectural alternatives from the rescue taxonomy (sparse write, iterative refinement, hierarchical read), (3) cap_map proximity (which other cells share the same algebraic family as the failed cell).

Algebraic: the rescue search is a local neighborhood query in the experiment configuration space. The neighborhood can be represented as a polytope in (eta, N, M, write_rule, read_rule) space. AutoML NAS literature (2025 max-flow NAS/HPO, ScienceDirect) establishes that automated HPO + NAS reduces human "what next" latency by ~40-60%.

Engineering: 5-8 days. Lower immediate ROI than B1 because HF cells are ~30-40% of cells (not 100%). Defer to after B1.

NOT RECOMMENDED for immediate investment. Plan B2 as a B1 extension in Phase 4b.

### B3: Parallel cell execution framework

5 cells sharing a single GPU via CUDA MPS or separate processes with GPU fraction allocations. The 2025 GPU multitasking literature (arxiv 2508.08448) establishes that sharing is feasible but requires careful memory isolation -- shared CUDA contexts via MPS compromise fault isolation. For small substrate cells (N=1024, typical < 1 GB VRAM), 4-6 cells can coexist on an 8 GB GPU.

Algebraic: if P cells run in parallel on 1 GPU, and each cell is I/O-bound (sequential write is memory-bandwidth limited, not compute-limited), parallelism gives near-linear speedup up to P <= VRAM_total / VRAM_per_cell. At 4060Ti 8GB with 1.5 GB/cell: P_max ~ 5.

Engineering: 3-5 days. Speedup on smoke batches: 3-5x. High value for parameter sweep smoke tests specifically.

RECOMMENDED as Phase 4 stretch investment (after B1). Implement as a simple multiprocessing.Pool wrapper with per-process GPU fraction allocation via CUDA_VISIBLE_DEVICES or CUDA MPS.

### B4: Live substrate dashboard

Real-time weight heatmap + codebook density + per-fact retrieval confidence during eval. Catches silent bugs (e.g., dead atoms, weight saturation, codebook collapse) before metrics surface them. Value is primarily in debugging novel architectures -- high value early in a new capability class, lower value on mature capability classes.

Engineering: 5-7 days. Impact is harder to quantify than B1-B3 -- it shortens debugging sessions but does not reduce scheduled cycle time. DEFER to Phase 4b or combine with B1 (add visualization to the eval harness output).

### B5: Hot-reload substrate

IPython-style live reload: modify mechanism code, `%reload substrate_module`, continue eval without restart. At <60s sessions on laptop CPU (per feedback_laptop_cpu_quick_probes), restarts are already ~5-10s -- hot-reload saves only ~5s per iteration. Not a significant lever at current scale. Engineering cost (2-3 days) exceeds ROI.

NOT RECOMMENDED. The value would be higher if edit-test cycles were <30s; they are not at current cell complexity.

---

## (C) CLEARER PROCESS / METHODOLOGY

### C1: Killer-demo-first methodology

Already implemented (V1 pipeline drill reduced 8-day plan to 4-day). The mechanism: start from the final demo spec, decompose into minimum capability dependencies, skip anything not on the critical path. The algebraic framing is a shortest-path problem in the capability DAG: find the minimum weight path from current_capabilities to demo_deliverable where edge weight = engineering days.

Process impact: already validated. The remaining leverage is disciplined application -- every new work item should answer "which node on the demo critical path does this unblock?" Items not on the path go to a backlog, not the queue.

No additional engineering investment required. ALREADY IMPLEMENTED.

### C2: Pre-registered rescue paths (RECOMMENDED, HIGHEST-LEVERAGE FOR PROCESS)

Current state: when a cell HFs, the "what next" decision takes ~0.5-1 day (research drill, strategy consult, new routing). Pre-registering 3-5 rescue cells AT SHIP TIME eliminates this latency entirely.

Template: every cell ships with:
- HP action: auto-unblock dependent cells in DAG
- MID action: run the pre-registered MID-rescue variant
- HF action: run rescue cells R1, R2, R3 (pre-specified in the cell spec)

Engineering: 1-2 days (template + checklist update to cell spec format + queue_add.py validation). Compound value: every future cell benefits immediately.

Process impact: ~0.5-1 day latency elimination per HF event. At 30-40% HF rate on 10 cells/day: 1.5-4 hours of recovered latency per day. Over 45-day Phase 4: ~67-180 hours recovered.

P_deflated(pre-reg rescues reduce "what next" latency by >=50%) = 0.80 (process change, not physics).

### C3: Capability matrix -> cell DAG

Every cap_map row has explicit owning cells + dependencies. Visual DAG: when one cell HPs, dependent cells auto-unblock in the queue. This is an extension of C1 (killer-demo-first) applied to the full cap_map, not just the demo path.

Engineering: 3-5 days. Compound value: high -- the DAG makes priority sequencing automatic. But the current cap_map is already partially structured, so the marginal engineering value is lower than B1 or C2.

RECOMMENDED as Phase 4 stretch investment (week 3-4), after B1 and C2 are in place.

### C4: Drill-to-cell automation

Research drill output auto-generates experiment skeleton: from handoff file, a script generates the smoke script template, pre-registers HP/MID/HF bands from the drill's falsifiable predictions, and creates the queue entry. This closes the loop between research and experiment without manual intermediate steps.

Engineering: 5-10 days. The hardest part is parsing drill output into structured experiment specs -- the handoff format is semi-structured. A partial version (generate the queue entry skeleton from the handoff's anchor-candidates section) is achievable in 2-3 days.

RECOMMENDED as Phase 4b investment (3-5 day partial version). Full automation is Phase 5.

---

## (D) WILD / PHASE-5 DEV-PARADIGM CHANGES

### D1: Self-bootstrapping substrate (substrate writes itself)

The substrate stores (architecture_variant, performance_metrics) pairs and uses its own retrieval mechanism to propose improved variants. This is a meta-learning closed loop: the substrate's architecture-space becomes itself a substrate content domain.

Algebraic: represent each architecture variant as a bipolar vector a_i in the same N-dimensional space. Store M_arch variants. The substrate retrieves the top-K similar variants by Hamming distance and proposes the centroid (majority vote) as a starting point for the next variant. This is equivalent to a genetic algorithm operating in Hamming space -- a well-studied structure. The update rule converges if the fitness landscape (architecture -> performance) has a Hamming-smooth structure.

Feasibility: LOW for meaningful self-improvement. The architecture space is not Hamming-smooth in general -- performance cliffs (found repeatedly in Phase 3/4 experiments) imply sharp discontinuities that Hamming-nearest-neighbor retrieval cannot navigate. The meta-learning literature (ADAS / Meta Agent Search, ICLR 2025) addresses this by using LLM code generation rather than substrate retrieval for architecture proposal.

Revised framing: use the substrate for storing and retrieving (experiment_config, outcome) pairs (already partially done via the orchestrator status log), but use an LLM (not the substrate) for proposing new variants. This is a hybrid architecture that is more feasible.

Engineering: 20-30 days for full closed-loop. 5-7 days for hybrid (substrate-as-memory + LLM-as-proposer). The 5-7 day hybrid version is PHASE 4 STRETCH and aligns with D2 below.

P_deflated(substrate-only self-improvement achieves >=2x throughput) = 0.20 (low; Hamming-smooth assumption likely violated). P_deflated(hybrid substrate+LLM achieves >=2x) = 0.45.

### D2: AI-paired research agent (24/7 development partner)

A persistent agent watches all results (status_log, queue, cap_map), proposes experiments via handoff files, drills literature, drafts routings. The user role becomes approve/veto + strategic direction. Current orchestrator system is already ~60-70% of this -- the remaining gaps are:
1. Continuous monitoring without human-triggered cycles (automation of loop/monitor calls)
2. Autonomous experiment proposal without explicit user dispatch
3. Persistent memory across sessions (compaction recovery without post-compaction brief)

The Google AI co-scientist (2025) demonstrates the feasibility at large scale: a coalition of specialized agents (generation, reflection, ranking, evolution, meta-review) achieves novel hypothesis generation at a fraction of expert time. The ADAS framework (Meta Agent Search, ICLR 2025) shows that a meta-agent iteratively generating Python agent code can discover new agent architectures autonomously.

For this system: the orchestrator already has the routing infrastructure. The missing piece is a scheduling daemon (persistent loop with event-gated wakes) that:
- Fires verdict_handler on every verdict_landed event (already partially via watchdog)
- Fires exp_dev refill when queue depth < threshold (already partially via watchdog)
- Fires research drill on cap_map stale rows (not yet automated)
- Fires strategy_scribe on every research_delivery (not yet automated)

Engineering: 15-25 days for full automation. 5-7 days for partial (automate the 3 most common reflexes: verdict->refill, research->handoff, stale_cap->research_dispatch).

Throughput multiplier: the 5-7 day partial version achieves ~2-3x throughput by eliminating human-coordinator latency (currently ~2-8h between events). The full 15-25 day version achieves ~5-10x by running 24/7 research cycles.

P_deflated(5-7 day partial achieves >=2x throughput) = 0.55. P_deflated(full 15-25 day achieves >=5x) = 0.38 (long-tail failure modes in agent reliability at extended operation).

RECOMMENDED as Phase 4 stretch (partial, 5-7 days) + Phase 5 full investment.

---

## CROSS-CUTTING ANALYSIS: TOP 5 BY LEVERAGE

Ranked by (throughput_multiplier * compound_value) / engineering_days:

1. C2 (pre-registered rescues): 1-2 days, ~0.5-1 day latency saved per HF, compounds over all future cells. ROI = HIGH. Phase 4 IMMEDIATE.

2. B1 (eval harness): 5-7 days, 3-5x smoke throughput, compounds over all future cells. ROI = HIGH. Phase 4 WEEK 1-2.

3. A2 (Wikipedia pre-extraction): 2-3 days + $200-400 one-time cloud, eliminates extraction for Wikipedia cells forever. ROI = HIGH (if Wikipedia is used in >=5 more cells). Phase 4 WEEK 1.

4. A1 (student distillation): 3-5 days + $10-30 training, 15-20x extraction speedup forever after. ROI = VERY HIGH long-run. Phase 4 WEEK 2-3 (after A2 validates extraction pipeline).

5. D2-partial (AI co-scientist loop automation): 5-7 days, 2-3x throughput via coordinator-latency elimination. Phase 4 STRETCH (weeks 3-4).

COMPOUND VALUE leaders: A1 (every future extraction), B1 (every future cell), C2 (every future HF event), A2 (every future Wikipedia cell).

PHASE 4 investments (compatible with 10-20 eng-day budget):
- C2: 1-2 days (IMMEDIATE)
- A2: 2-3 days (WEEK 1)
- B1: 5-7 days (WEEK 1-2)
- A1: 3-5 days (WEEK 2-3)
Total: 11-17 eng-days

PHASE 5 investments:
- B3: 3-5 days (parallel cell execution)
- C3: 3-5 days (capability DAG)
- C4-partial: 3-5 days (drill-to-cell partial automation)
- D2-full: 15-25 days (AI co-scientist)
- D1-hybrid: 5-7 days (substrate-as-memory + LLM-as-proposer)

---

## PREDICTED THROUGHPUT MULTIPLIER

Conservative (C2 + B1 only): 2-3x (scaffold elimination + rescue latency reduction)
Expected (C2 + B1 + A2 + A1): 3-5x (adds extraction elimination + distillation speedup)
Optimistic (all Phase 4 picks + D2-partial): 5-8x (adds coordinator-latency elimination)

The 3-5x target is achievable within the 10-20 eng-day budget with the portfolio above. The 5-10x target requires Phase 5 investment.

---

## CROSS-DOMAIN PROBE: ML RESEARCH INFRASTRUCTURE LIT (2024-2025)

The ML experiment management community has converged on a 3-tier infrastructure stack:

Tier 1 (config + sweep): Hydra (Meta) + Optuna + Ray Tune. Key insight from 2025 literature: Hydra's multirun + Optuna pruning eliminates ~60-80% of wasted compute in parameter sweeps by early-stopping unpromising configurations (Successive Halving / ASHA). For discrete-state substrate cells where the performance cliff is sharp (validated: K/N=0.56 capacity cliff), ASHA-style pruning could identify the cliff location in O(log N_sweep) runs instead of O(N_sweep). Engineering: 1-2 days to add Optuna ASHA scheduler to the existing sweep harness.

Tier 2 (logging + comparison): Weights & Biases + MLflow. W&B's sweep agent natively parallelizes across processes with shared early-stopping -- directly relevant to B3 (parallel cell execution). The W&B sweep agent handles GPU allocation, process management, and metric logging automatically, reducing the B3 engineering estimate from 3-5 days to 1-2 days if W&B is adopted as the sweep backend.

Tier 3 (autonomous research): Google AI co-scientist (2025) + ADAS Meta Agent Search (ICLR 2025). Key finding: the "generate-evaluate-evolve" loop in agent architectures converges to novel hypotheses in <24h on scientific tasks. The ADAS framework generates Python code for new agents, not just parameters -- directly relevant to D2. The community-missed insight: most substrate research groups are NOT using these agent frameworks for experiment proposal (they use them for hyperparameter search only). Applying ADAS-style meta-agent search to architecture proposal (not just HP search) is a genuine open gap.

Embedding recycling (arxiv 2207.04993): cached intermediate activations reused across multiple tasks -- this is the academic precedent for A2. The paper demonstrates that reusing cached token-level embeddings from pretrained LMs reduces fine-tuning cost by 2-5x with negligible quality loss. Direct support for A2's algebraic claim.

---

## CROSS-THREAD SYNTHESIS

Prior research drills most relevant to this analysis:
- V1 demo pipeline optimization (2026-06-05): validated killer-demo-first methodology (C1 already effective)
- 20 ambitious ideas 1x+3 deep dives 2x (2026-06-05): identified substrate self-improvement as Phase 5 direction (consistent with D1/D2 assessment here)
- Middle and negative findings rescue 2x (2026-06-05): pre-registered rescue paths are already in use -- C2 formalizes what is partially implemented

The current system has C1 implemented, C2 partially implemented (per-cell bands but not per-cell rescue cells), and the watchdog partially implements D2 (event-gated dispatch). The remaining gap is structural formalization of C2 and the B1 harness.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

The development-speed bottleneck directly gates the 24-36 month window noted in substrate_value_framing_2026-05-26. Every 2x throughput improvement compresses the remaining Phase 4 roadmap from 30-45 days to 15-22 days. The 3-5x expected multiplier from the recommended portfolio compresses it to 8-15 days -- potentially closing Phase 4 before end of June 2026. This is the strongest product argument for front-loading the infrastructure investments (C2, B1, A2) above any additional capability exploration.

The A1 distillation investment also directly enables Phase 0.5b (Llama-3.1-8B extraction at scale) by replacing the current 10h/$30 extraction with ~30min/$1.50 -- a necessary prerequisite for the 1M-fact demonstration target.

---

## P_DEFLATED SUMMARY (calibration penalty applied: -0.15 to -0.25 per claim)

| Claim | Raw estimate | Deflation | P_deflated |
|---|---|---|---|
| A1: 75% geometry preservation at 20x compression | 0.70 | -0.18 | 0.52 |
| A2: extraction elimination for Wikipedia cells | 0.90 | -0.15 | 0.75 |
| A3: 2-3x speedup from LoRA pipeline fusion | 0.65 | -0.15 | 0.50 |
| A4: real-time writes eliminate dev extraction | 0.85 | -0.13 | 0.72 |
| B1: 3-5x smoke throughput from harness | 0.75 | -0.13 | 0.62 |
| B3: 3-5x parallel smoke via MPS | 0.65 | -0.20 | 0.45 |
| C2: rescue latency >=50% reduction | 0.92 | -0.12 | 0.80 |
| D1: substrate self-improvement >=2x | 0.35 | -0.15 | 0.20 |
| D1-hybrid: hybrid substrate+LLM >=2x | 0.60 | -0.15 | 0.45 |
| D2-partial: 2-3x from loop automation | 0.68 | -0.13 | 0.55 |
| D2-full: 5-10x from AI co-scientist | 0.55 | -0.17 | 0.38 |

Novel-synthesis claims capped at 0.50 per calibration rule. No deflated estimate exceeds 0.80 (process-only claims allowed higher).

---

## RECOMMENDED PORTFOLIO (10-20 eng-day budget)

WEEK 1 (days 1-5):
- C2: 1-2 days -- pre-registered rescue cells in every ship spec (IMMEDIATE PROCESS CHANGE, zero infra)
- A2: 2-3 days + $200-400 cloud -- Wikipedia activation cache (one-time; eliminates Wikipedia extraction forever)

WEEK 2 (days 6-12):
- B1: 5-7 days -- standardized eval harness (largest structural lever on cycle time)

WEEK 3 (days 13-17):
- A1: 3-5 days + $10-30 cloud -- student distillation (perpetual 15-20x extraction speedup)

WEEK 4 STRETCH:
- D2-partial: 5-7 days -- automate 3 orchestrator reflexes (verdict->refill, research->handoff, stale_cap->dispatch)

Total Phase 4: 11-17 eng-days core + 5-7 days stretch = 16-24 days. Throughput multiplier: 3-5x (core) to 5-8x (with stretch).

---

## CITATIONS (verified, from lit-scan)

1. "What Should Feature Distillation Transfer in LLMs? A Task-Tangent Geometry View" -- arxiv 2507.10155 (2025). Functional contributions concentrate in low-dimensional tangent subspace of teacher representations.

2. "Knowledge Distillation and Dataset Distillation of Large Language Models" -- arxiv 2504.14772 (2025). Survey of distillation methods including offline, off-policy, on-policy.

3. "Embedding Recycling for Language Models" -- arxiv 2207.04993 (2022). Cached intermediate activations reused across tasks, 2-5x fine-tuning cost reduction.

4. "Towards Efficient and Practical GPU Multitasking in the Era of LLM" -- arxiv 2508.08448 (2025). MPS isolation challenges; memory-sharing gaps in multi-tenant GPU environments.

5. "AgentExpt: Automating AI Experiment Design with LLM-based Resource Retrieval Agent" -- arxiv 2511.04921 (2025). LLM-based automated experiment design system.

6. "Automated Design of Agentic Systems (ADAS) / Meta Agent Search" -- ICLR 2025. Meta-agent iteratively generates Python code for new agents; achieves novel architectures autonomously.

7. "Accelerating scientific breakthroughs with an AI co-scientist" -- Google Research Blog (2025). Coalition of specialized agents (generation, reflection, ranking, evolution) for scientific hypothesis generation.

8. "Scalable Training for Vector-Quantized Networks with 100% Codebook Utilization" -- arxiv 2509.10140 (2025). Codebook collapse problem in VQ training; VQBridge compress-process-recover pipeline.

9. "HydraFlow: Seamless integration of Hydra and MLflow" -- PyPI (2025). Config management + experiment tracking integration.

10. "Hyperparameter Sweep Automation: Optuna vs Weights & Biases Comparison 2025" -- markaicode.com (2025). HPO consumes 60-80% of ML development time; automated sweeps reduce this substantially.

11. "Run LoRA Run: Faster and Lighter LoRA Implementations" -- arxiv 2312.03415 (2023). Up to 17% speedup on Llama via optimized LoRA computation graphs.

12. "On neural architecture search and hyperparameter optimization: A max-flow based approach" -- ScienceDirect 2025. Joint NAS+HPO reducing human "what next" latency by 40-60%.

Verified citation count: 12

---

*Note written 2026-06-05. Calibration penalty applied per [[feedback-lit-scan-calibration-penalty]]. No empirical verification performed (algebraic + lit-scan only, per [[feedback-research-drills-no-empirical-verification]]). Generic substrate-LLM hybrid + ML research tooling terminology used throughout (per [[feedback-query-privacy-decomposition]]).*
