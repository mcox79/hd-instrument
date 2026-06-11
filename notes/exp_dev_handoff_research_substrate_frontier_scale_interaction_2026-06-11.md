# exp_dev hand-off -- research: substrate frontier-LLM-scale interaction (2x DEEP)

Filed-by: research sub-agent (Opus)
Date: 2026-06-11
Trigger: 2x DEEP research drill on substrate behavior at frontier-LLM-scale interaction conditions.
Source research note: d:/AI/hd-instrument/notes/research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md

Per [[feedback-no-experiment-design-in-prompts]] -- this is a hand-off to exp_dev, not an inline experiment design. exp_dev decides specific cells, seeds, harness implementation, queue lane. Pre-registration of HP/HF thresholds is included so verdict_handler can adjudicate cleanly.

## Pause state

Check data/orchestrator_paused.flag before ship. If paused: file as anchor candidate for refill; do not queue immediately.

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST LEVERAGE) -- Dense-Hopfield codebook regime at frontier scale

- Anchor pointer: research note PART I.1, II.2, VII.1; HP-1, HP-2, HF-1, HF-2.
- Substrate-product reading: validates substrate-product surface for million-fact deterministic Q&A. Differentiator vs LLM long-context: sub-100ms p99 latency + 0 hallucination + calibrated abstention.
- Tier hint: TIER A if HP-1 PASS at M=3M with recall@1 >= 0.85 + p99 latency <= 100ms.
- Why-now: only outstanding question on the frontier-scale substrate-product surface; all theoretical pieces (spherical-code separability, capacity-precision tradeoff) are settled in 2025 lit. Single 4-6 hour GPU test decides product-surface viability.
- HP-1: recall@1 at M=3M >= 0.85 with N=4096, dense-Hopfield codebook regime, single namespace.
- HP-2: p99 retrieval latency at M=3M <= 100 ms on single GPU.
- HF-1: recall@1 at M=3M < 0.50. Linear-superposition contamination of codebook layer; regime hypothesis refuted.
- HF-2: p99 latency > 500 ms. Differentiation claim refuted.
- Cost: 4-6 hours single GPU.

### Anchor 2 -- 3-tier conversational memory at 10000-turn lag

- Anchor pointer: research note PART II.1, II.2, III; HP-3, HF-3.
- Substrate-product reading: validates substrate-product surface for long-running agent memory + multi-hour dialog. Differentiator vs RAG: no chunking artifacts, constant retrieval latency irrespective of total store size.
- Tier hint: TIER B if HP-3 PASS; TIER A if HP-3 + HP-4 both PASS (calibration + lag both held).
- Why-now: 4 independent 2025-2026 systems (MMAG, CAIM, CogMem, Multi-Layer Memory Framework) converge on the 3-tier + gating pattern; substrate already has the structural pieces.
- HP-3: recall@1 at 5000-turn lag >= 0.70 with topic-segmented episodic tier; abstention precision >= 0.90.
- HF-3: recall at 5000-turn lag < 0.30 OR abstention precision < 0.50.
- Cost: 2-4 hours single GPU (synthetic 10000-turn corpus + topic-segmented write/read harness).

### Anchor 3 (HIGHEST PROBABILITY) -- Calibrated-abstention ECE vs LLM verbalized confidence

- Anchor pointer: research note PART VI (substrate wins), PART VII; HP-4, HF-4.
- Substrate-product reading: substrate-as-calibration-engine. Differentiator: native similarity-score abstention is mathematically deterministic, not post-hoc calibrated.
- Tier hint: TIER B if HP-4 PASS substrate-only; TIER A if also held composed with LLM frontend (substrate calibrates LLM outputs).
- Why-now: lowest-risk claim in the drill (P_deflated 0.55). 2025 LLM-calibration lit (I-CALM, behaviorally-calibrated RL) gives clean baseline numbers (ECE 0.10-0.25) to compare against.
- HP-4: substrate abstention ECE <= 0.05 on frontier-scale eval set.
- HF-4: substrate abstention ECE > 0.15.
- Cost: 1-2 hours CPU/GPU (calibration-curve sweep on existing substrate stack + benchmark eval set).

### Anchor 4 (CHEAP / FAST) -- Capacity-precision tradeoff (low-precision wide substrate)

- Anchor pointer: research note PART VII.2.
- Substrate-product reading: 4x memory savings at frontier scale with no separability loss (fp8 wide vs fp32 narrow).
- Tier hint: TIER C (engineering optimization, not product-surface gating).
- Why-now: 1-hour CPU test; if positive, becomes default config for all frontier-scale substrate deployments.
- Cost: 1 hour CPU.

## Context pointers (file paths, not summaries)

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md
- Predecessor (streaming consolidation): d:/AI/hd-instrument/notes/research_drill_conversation_memory_streaming_2x_2026-06-11.md
- Predecessor (1M-scale pinv/SMW): d:/AI/hd-instrument/notes/research_drill_substrate_1M_scale_risks_2x_2026-06-07.md
- Predecessor (extreme-scale emergent): d:/AI/hd-instrument/notes/research_drill_substrate_emergent_extreme_scale_5x_2026-06-08.md
- Substrate-LLM boundary memory: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_LLM_boundary_decomposition_2026-06-10.md
- Substrate v3.2 engineered wrapper: C:/Users/marsh/.claude/projects/d--AI/memory/substrate_v32_engineered_wrapper_2026-06-11.md
- Drill-pattern memory: C:/Users/marsh/.claude/projects/d--AI/memory/drill_pattern_temporal_contextual_not_structural_2026-06-11.md

## Contract

- Pre-reg per envelope-fail-bands (HP/HF thresholds in each anchor above).
- Smoke gate before full ship.
- Ship via queue_add.sh.
- Post-ship REMOTE VERIFY.
- Self-test per formula-selftests.
- Verdict_handler will adjudicate against HP/HF thresholds.

## Autonomy declaration

exp_dev autonomous on: which anchor(s) to ship first, queue lane (GPU vs CPU local), cell harness implementation, seed strategy, smoke-test composition, integration with existing substrate stack.

Research-deferred decisions (escalate back if blocked): if Anchor 1 HF-1 hits (recall collapse at M=3M), DO NOT retry larger N as fix -- this would refute the codebook regime hypothesis and require 3x drill on substrate-as-codebook architectural assumption.

Recommended priority order: Anchor 4 (1 hr cheap) -> Anchor 3 (highest P, 1-2 hr) -> Anchor 1 (highest leverage, 4-6 hr) -> Anchor 2 (depends on Anchor 1 result).
