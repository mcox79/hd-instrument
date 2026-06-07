# exp_dev hand-off -- research: final implementation performance bottlenecks

**Filed-by:** research sub-agent (Sonnet), 2026-06-07
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_final_implementation_perf_bottlenecks_2x_2026-06-07.md
**Pause state:** Check data/orchestrator_paused.flag before dispatching any GPU anchors.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the anchor implementation, pre-reg bands, and dispatch details. This file provides context pointers and anchor candidates only. No inline experiment design.

---

## Why this hand-off exists

The research drill identified three measurable pre-tests that are worth running before committing v1.1 engineering budget to the identified bottlenecks. These pre-tests convert theoretical bottleneck estimates into empirical data and either confirm or refute the priority ordering. Two of the three are cheap (local CPU/GPU, < 3 hours). One requires a GPU.

The key architectural risk that should be pre-tested urgently: the VRAM budget for RTX4060 8 GB edge deployment is exceeded by the current stack (Llama-8B + Llama-1B L15 + bge-small + KV cache = ~8.3 GB). The distilled encoder option resolves this, but requires quality validation before committing. The VRAM budget measurement confirms whether RTX4060 is a viable edge target at all.

---

## Anchor candidates (rank-ordered by decision value)

### Anchor A: Full pipeline wall-clock decomposition (LOCAL GPU, ~2 hours)
**Why-now:** This is the single most decision-relevant measurement in the system right now. If LLM generation >= 50% of wall-clock (HARD-PASS), all v1.1 optimization budget is confirmed to go to LLM path. If substrate retrieval >= 20% (HARD-FAIL), the current bottleneck ranking is wrong and strategy changes. This cannot be resolved by theory alone -- it requires a single instrumented run.
**Anchor pointer:** Instrument the full query pipeline (bge-small encode -> Llama-1B L15 encode -> substrate retrieval -> Llama-8B generation) with time.perf_counter() at each boundary. 50 queries. Report mean and p95 per stage and as fraction of total.
**Substrate-product reading:** Confirms or refutes the "LLM dominates" finding. If confirmed, the customer pitch framing and engineering priority list are locked. If refuted, strategy requires revision.
**Tier hint:** LOCAL GPU (RTX or equivalent). Not cloud. Cheap.
**HARD-PASS:** LLM generation >= 50% of total wall-clock at p50.
**HARD-FAIL:** Substrate retrieval >= 20% of total wall-clock at N=4096.

### Anchor B: VRAM budget measurement on RTX4060-class GPU (LOCAL GPU, ~1 hour)
**Why-now:** The edge deployment claim ("viable on RTX4060") is under empirical risk. The research drill calculates the stack at ~8.3 GB, which exceeds the 8 GB RTX4060. If this is confirmed empirically, the product must either (a) raise minimum edge spec to RTX4060 Ti 16 GB / M2 Pro, or (b) commit to distilled encoder path. This is a binary decision that affects product positioning.
**Anchor pointer:** Load Llama-8B Q4_K_M + Llama-1B (INT8 or FP16) + bge-small sequentially, measuring nvidia-smi VRAM after each load. Determine if all three fit simultaneously with 0.5 GB KV cache headroom.
**Substrate-product reading:** Binary verdict on RTX4060 8 GB edge viability. If FAIL, minimum spec = RTX4060 Ti 16 GB or M2 Pro. If PASS (e.g., actual VRAM usage is lower than calculated), edge deployment claim is confirmed.
**Tier hint:** LOCAL GPU. Not cloud.
**HARD-PASS:** All three models + 0.5 GB KV cache headroom fit in 8 GB VRAM.
**HARD-FAIL:** Peak VRAM >= 8.2 GB (out of memory or within 2.5% of limit = not viable without CPU offload).

### Anchor C: Encoder batching throughput and latency at batch sizes 1/4/16/64 (LOCAL GPU, ~3 hours)
**Why-now:** The async encoder prefetch optimization (Priority 2 in engineering priorities) is only beneficial if encoders are slow enough at batch=1 to justify the pipelining overhead. If encoders are already fast at batch=1 (< 50 ms total), async prefetch may not be worth the engineering week. This measurement also determines whether encoder quantization (INT8) is needed for v1.1 or can wait for v2.
**Anchor pointer:** Benchmark bge-small and Llama-1B L15 forward pass separately at batch sizes 1, 4, 16, 64 on local GPU. Record mean latency per batch size and throughput (queries/sec). Measure at INT8 vs FP32 for both models.
**Substrate-product reading:** If bge-small batch=1 < 20 ms AND Llama-1B L15 batch=1 < 100 ms: encoder is NOT a bottleneck at current throughput, async prefetch deferred to v2. If either exceeds these thresholds: async prefetch is v1.1 Priority 2 confirmed.
**Tier hint:** LOCAL GPU.
**HARD-PASS:** Llama-1B L15 batch=1 latency < 100 ms (encoder acceptable without optimization).
**HARD-FAIL:** Llama-1B L15 batch=1 latency >= 250 ms (encoder is co-dominant bottleneck, not secondary; must prioritize distilled encoder for v1.1 not v2).

---

## Context pointers

- Research note (full analysis): d:/AI/hd-instrument/notes/research_drill_final_implementation_perf_bottlenecks_2x_2026-06-07.md
- Prior encoder drill: d:/AI/hd-instrument/notes/research_drill_encoder_bottleneck_phase4a_infrastructure_2x_2026-06-05.md
- Production architecture lock: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- HIPAA Option B: see research note Section "Customer Pitch Invalidation Risk Assessment"
- Pattern B 16 bytes/fact confirmation: see POST-COMPACTION BRIEF 2026-06-07 AFTERNOON in MEMORY.md
- Tier 4 speed/energy drill: referenced in research note cross-thread synthesis

---

## Contract

exp_dev designs anchors A, B, C with pre-reg per envelope-fail-bands protocol. This file does not specify implementation, script names, or numerical parameters beyond what is necessary to identify the measurement. exp_dev owns all design decisions.

Dispatch via queue_add.sh to appropriate queue (LOCAL GPU runner for all three; no cloud needed). Post-ship REMOTE VERIFY per role contract. Self-test per formula-selftests.

All three anchors can run on the same local GPU runner in sequence. Total estimated wall time: 6 hours. Total estimated cost: $0 (local hardware).

## Autonomy declaration

exp_dev decides: script implementation, pre-reg band thresholds (using the HARD-PASS/HARD-FAIL values above as minimum guidance), which anchor to run first if queue is constrained, whether to combine anchors A and C into one instrumented run, and whether INT8 vs FP32 encoder comparison in anchor C warrants a separate anchor or is a secondary metric within the same run.
