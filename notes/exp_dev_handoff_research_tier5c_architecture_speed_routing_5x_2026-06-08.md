# exp_dev hand-off -- research: Tier 5c architecture, speed, routing 5x

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md
Prior Tier 5c drill: notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: t5c_substrate_orchestrator_routing_benchmark_v1

Anchor pointer: Research note Level 3 (orchestration patterns) + Level 4 Section 4.6 (hierarchical routing)
Substrate-product reading: Tests whether the 3-tier hierarchical router (substrate -> tool -> LLM) achieves routing accuracy > 75% and substrate-tier latency < 0.5ms. Builds directly on validated PP-123 cascade router. If substrate-as-orchestrator routes accurately at sub-ms, the LLM can be removed from the routing hot path entirely, achieving 250x latency improvement on substrate-handled queries.
Tier hint: CPU laptop (substrate retrieval is CPU; NumPy math tool is CPU; LLM tier can use quantized small model). CHEAPEST of the five anchors.
Why-now: extends PP-123 without new training; highest signal-to-compute ratio; gates the "substrate as orchestrator" product claim.

Pre-reg bands:
  HARD-PASS: substrate tier latency < 0.5ms; routing accuracy > 75% on three-category test set; math tool returns correct result on 90%+ of test queries
  MIDDLE-BAND: routing accuracy 60-75% (substrate centroids partially coherent; need more examples or centroid refinement)
  HARD-FAIL: routing accuracy < 60% on any category; substrate tier latency > 2ms (O(1) not holding at query batch sizes)

### Anchor 2: t5c_gpu_codebook_retrieval_benchmark_v1

Anchor pointer: Research note Level 2 Section 2.5 (GPU-side substrate) and Level 5 Section 5.1 (memory-mapped access)
Substrate-product reading: Loads substrate codebook to A100 GPU; benchmarks torch cdist retrieval at batch_sizes [12, 128, 1024, 6144]. If single-query GPU latency < 0.1ms (vs current 0.21ms CPU), GPU-resident substrate is the correct default for all Tier 5c architectural patterns. This benchmark gates every GPU-tier Tier 5c experiment.
Tier hint: GPU (A100; infrastructure benchmark; short wall time < 30 min). GATES other anchors.
Why-now: all 8 architectural patterns in the research note depend on substrate retrieval being sub-ms at LLM batch sizes; this confirms or denies that feasibility.

Pre-reg bands:
  HARD-PASS: single-query GPU latency < 0.1ms; batch_size=12 < 0.5ms; batch_size=1024 < 3ms
  MIDDLE-BAND: single-query 0.1-0.5ms (still faster than CPU; acceptable for most Tier 5c patterns but not all-layer per-token retrieval)
  HARD-FAIL: single-query > 0.5ms (complex64 cdist not achieving cuBLAS throughput; would need real-valued approximation or kernel optimization)

### Anchor 3: t5c_lightweight_router_distillation_v1

Anchor pointer: Research note Level 4 Section 4.3 (lightweight distilled router)
Substrate-product reading: Fine-tunes a 100M-param DistilBERT classifier to route queries using Qwen-2.5-3B-Instruct (LLM-ROUTING-T1, 0.833 accuracy) as teacher. If student achieves > 75% accuracy at < 10ms CPU latency, the 50-100ms LLM routing bottleneck is eliminated. This enables high-throughput routing (> 100 queries/second) without LLM in the hot path.
Tier hint: remote_cpu_queue or local GPU for fine-tuning (lightweight; 3 epochs DistilBERT). MEDIUM priority -- gates throughput claim but not immediate Tier 5c architectural feasibility.
Why-now: LLM-ROUTING-T1 result (0.833) is the teacher signal; this anchor uses that result directly; if accuracy holds under distillation, router can be deployed without LLM inference costs.

Pre-reg bands:
  HARD-PASS: student accuracy > 0.75; routing latency < 10ms on CPU
  MIDDLE-BAND: accuracy 0.65-0.75 (some degradation from teacher; acceptable for most routing decisions with substrate as fallback)
  HARD-FAIL: accuracy < 0.65 (query categories not linearly separable at 100M scale; would need larger student or different architecture)

### Anchor 4: t5c_semantic_positional_encoding_probe_v1

Anchor pointer: Research note Level 1 Section 1.1 (substrate as positional encoding)
Substrate-product reading: Adds substrate-retrieved atoms as a semantic-position component to Pythia-160M token embeddings (before attention). If perplexity does not increase (neutral or positive), substrate's codebook provides semantically useful input representations, validating the positional-encoding substitution path. This is architecturally the lowest-cost Tier 5c intervention: additive term at the embedding layer, no training of base model.
Tier hint: GPU (Pythia-160M inference evaluation; single A100; moderate wall time ~2 hr for perplexity eval on WikiText-103)
Why-now: no training required; uses existing Pythia-160M checkpoint + existing substrate codebook; tests whether substrate atoms are semantically coherent enough to enrich LLM input at the encoding stage.

Pre-reg bands:
  HARD-PASS: perplexity change < 2% vs standard RoPE; forward pass overhead < 15%
  MIDDLE-BAND: perplexity change 2-5% (slight degradation; substrate atoms are partially noisy; may improve with codebook quality work)
  HARD-FAIL: perplexity increases > 5% (substrate atoms are adding noise at input stage; encoding substitution not viable without codebook quality improvement)

### Anchor 5: t5c_substrate_conditioned_softmax_probe_v1

Anchor pointer: Research note Level 1 Section 1.7 (substrate-conditioned softmax)
Substrate-product reading: Adds substrate atom-to-vocabulary distributions as a bias on Pythia-160M output logits (gamma=0.1 scaling). Tests whether substrate factual knowledge reduces hallucination on TriviaQA first 200 questions. This is the most direct test of the "substrate-conditioned LLM hallucinates less" product claim.
Tier hint: GPU (Pythia-160M inference + substrate lookup; single A100; moderate wall time)
Why-now: tests the product value claim at minimal engineering cost; result feeds directly into v1 demo narrative and the head-to-head LLM comparison benchmark.

Pre-reg bands:
  HARD-PASS: exact-match accuracy on TriviaQA >= LLM-alone (substrate conditioning at least neutral); hallucination rate (false entity mentions) reduced > 10%
  MIDDLE-BAND: accuracy slightly below LLM-alone (0-5% degradation) but hallucination rate reduced > 10% (there is a quality-fluency tradeoff; can be tuned via gamma)
  HARD-FAIL: accuracy drops > 10% vs LLM-alone (substrate vocabulary distributions are incoherent; conditioning hurts more than it helps)

---

## Sequencing recommendation

GATE ANCHOR: t5c_gpu_codebook_retrieval_benchmark_v1 (Anchor 2) should run first if any of the architectural patterns will use GPU-resident substrate. It is short (< 30 min GPU time) and determines whether GPU-side substrate is viable for all subsequent experiments.

PARALLEL: t5c_substrate_orchestrator_routing_benchmark_v1 (Anchor 1) can run on CPU in parallel with the GPU benchmark. Uses existing PP-123 infrastructure.

SEQUENTIAL: Anchors 3, 4, 5 can run in any order after Anchors 1 and 2 are complete. They are independent of each other.

---

## Context pointers (file paths, not summaries)

- This drill: d:/AI/hd-instrument/notes/research_drill_tier5c_architecture_speed_routing_5x_2026-06-08.md
- Prior Tier 5c drill (attention, differentiability, engineering paths): d:/AI/hd-instrument/notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
- PP-123 cascade router validation: (in cap_map / research notes for cycle PP-123)
- LLM-ROUTING-T1 result (0.833 Qwen-2.5-3B): (in cap_map rows for Tier 5c routing)
- Production architecture lock: C:/Users/marsh/.claude/projects/d--AI/memory/production_architecture_locked_2026-06-07.md
- Evening post-compaction brief (multi-hop context): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- Exp-dev 30-min cadence memory: C:/Users/marsh/.claude/projects/d--AI/memory/feedback_exp_dev_30min_10anchor_cadence.md

---

## Contract section

This handoff proposes 5 anchor candidates ordered by priority. Exp_dev selects from these based on current queue state, runner availability, and pause flag. Exp_dev does NOT need to implement all 5; select the highest-value anchors given current queue depth.

GATE: t5c_gpu_codebook_retrieval_benchmark_v1 is the gate for GPU-tier Tier 5c experiments. If this anchor returns HARD-FAIL (single-query > 0.5ms on GPU), the GPU-resident substrate path needs redesign before other GPU-tier anchors run.

NO GATE: t5c_substrate_orchestrator_routing_benchmark_v1 and t5c_lightweight_router_distillation_v1 are CPU-tier and independent of the GPU benchmark.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchors to dispatch first (subject to sequencing constraint above)
- Choosing cell grid dimensions, seed counts, query set sizes, and hyperparameter values for each anchor
- Routing to local CPU / remote CPU / GPU per feedback_route_gpu_vs_cpu_by_torch_not_N.md and feedback_cloud_only_when_absolutely_necessary.md
- Writing experiment scripts per feedback_metrics_required_fields_write_metrics.md convention
- Choosing whether to run Anchors 4 and 5 locally on GPU or on Lambda based on VRAM availability

Exp_dev is NOT autonomous in:
- Making cap_map decisions from verdicts (orchestrator / verdict_handler owns this)
- Claiming routing or architectural patterns as validated before empirical experiments confirm them
- Making customer-facing claim revisions from these results (orchestrator owns after verdicts are in)
- Reopening the PRODUCTION ARCHITECTURE LOCK (requires explicit user authorization)
