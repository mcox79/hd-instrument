# exp_dev hand-off -- research: Tier 4 LLM architecture proposals

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_tier4_llm_architecture_proposals_3x_2026-06-07.md
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev designs the experiment; this file provides anchor candidates and context pointers only.

---

## Anchor candidates (rank-ordered)

### 1. Arch-8 Pythia pre-test (TOP PRIORITY)
Anchor pointer: Tier 4 Arch (8) feasibility smoke -- substrate-derived continual fine-tuning
Substrate-product reading: Does fine-tuning Pythia-160M on 50 substrate-derived examples produce any improvement on a held-out substrate knowledge probe? This is the cheapest decisive test for the entire Tier 4 program.
Tier hint: LOCAL CPU/GPU, short wall (30 min), ~$0.50 if on remote GPU, CPU-only preferred
Why-now: Arch (8) has the highest P_deflated (0.48) of all 8 Tier 4 architectures AND the lowest engineering cost (2-4 weeks). Pre-test is mandatory before authorization per [[feedback-drill-pretest-required]]. All today's empirical HPs (Pattern B production, continual learning concept extension) support that substrate-derived data should be stable as a fine-tuning source.

HARD-PASS: >=1 answer improvement on 10-question substrate probe after 50 fine-tuning steps + <=2% MMLU-5shot degradation
HARD-FAIL: zero improvement on substrate probe after 50 steps

### 2. Arch-5 retrieval head identification pre-test
Anchor pointer: Tier 4 Arch (5) -- identify retrieval-specialized heads in Pythia-160M on substrate-relevant QA
Substrate-product reading: Can retrieval heads be identified (attention entropy differentiation) in Pythia-160M when given 100 substrate-relevant QA examples? This gates the Arch (5) fine-tuning path.
Tier hint: LOCAL CPU, ~45 min wall, no GPU needed
Why-now: Arch (5) has second-highest P_deflated (0.45), fine-tuning-only path (no pretraining), strong lit precedent (DuoAttention, RazorAttention). Head identification is step 0.

HARD-PASS: top-5 heads show >=1.5x higher substrate attention entropy than mean across all heads
HARD-FAIL: no head differentiation (uniform attention on substrate tokens across all heads)

### 3. Arch-1 bipolar backprop feasibility micro-test
Anchor pointer: Tier 4 Arch (1) -- does straight-through estimator produce usable gradient through bipolar W constraint?
Substrate-product reading: Single transformer layer + tiny bipolar W. Confirms whether backprop through bipolar constraint produces training signal at all before any protocol engineering investment.
Tier hint: LOCAL CPU, ~20 min wall, no GPU
Why-now: This gates Arch (1) authorization independently of the compliance protocol work. If gradient is NaN or zero, Arch (1) is closed without needing the protocol engineering. If gradient flows, the protocol work becomes the blocker.

HARD-PASS: loss decreases monotonically over 50 steps with straight-through estimator
HARD-FAIL: gradient is zero or NaN through the bipolar constraint

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_tier4_llm_architecture_proposals_3x_2026-06-07.md
Cap map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Today's supporting HP verdicts: Pattern B production stack (cycle 162), modern Hopfield N=4096-16384, continual learning online concept extension, causal cluster HP

---

## Contract section

exp_dev owns experiment design. This file provides priority ranking and pre-reg thresholds only. exp_dev must: (a) run Pythia sanity check first per [[feedback-pythia-sanity-check-before-cloud]], (b) route CPU-only tests to remote_cpu_queue, (c) pre-register each experiment with explicit HARD-PASS and HARD-FAIL bands before dispatch.

## Autonomy declaration

exp_dev decides: exact script design, dataset construction approach, metric implementation, queue routing, and whether to combine pre-tests into a single batch run.
