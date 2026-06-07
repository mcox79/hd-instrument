# exp_dev hand-off -- research: Qwen-7B promotion risks 2x drill

Filed-by: research sub-agent
Date: 2026-06-07
Trigger: notes/research_drill_qwen7b_promotion_risks_2x_2026-06-07.md
Urgency: HIGH -- v1 demo baseline decision; PT1 must run before committing v1 engineering

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be
authored by exp_dev from the research note + cap_map context. Do NOT treat the
descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: qwen7b_hotpotqa_3baseline_v1 (PT1 -- mandatory gate)

Anchor pointer: Research note Section "Top 3 Cheap Pre-Tests" PT1
Substrate-product reading: Runs bare / RAG / substrate-augmented on same 200 HotpotQA
  distractor questions as existing 1.5B run. Directly measures substrate value-add at 7B
  and answers the context utilization question (arxiv 2603.11513 risk). If substrate+7B F1
  < RAG+7B F1, the v1 demo cannot claim "substrate improves retrieval quality" and the
  pitch must be revised to audit-only before customer conversations.
Tier hint: Local GPU (RTX4060 8GB), Qwen-7B Q4_K_M ~5 GB VRAM. ~30-60 min wall time. $0.
Why-now: This is the mandatory gate for any v1 benchmark claim at 7B. All other 7B work
  is blocked on this result. Must run before LLM-decomp retest or any v1 engineering commit.

Pre-reg bands:
  HARD-PASS: substrate+7B F1 >= RAG+7B F1 + 3 pts AND substrate+7B F1 >= 50.
  MIDDLE-BAND: substrate+7B F1 = RAG+7B F1 +/- 2 pts (parity; audit-only story viable).
  HARD-FAIL: substrate+7B F1 < RAG+7B F1 (utilization failure; route to PT5 prompt ablation
    before any further 7B experiments).

### Anchor 2: qwen7b_triviaqa_3baseline_v1 (PT2)

Anchor pointer: Research note Section "Top 3 Cheap Pre-Tests" PT2
Substrate-product reading: Same TriviaQA-RC subset as 1.5B run; 3-condition comparison.
  Resolves whether the TriviaQA +0.023 EM margin survives at 7B or evaporates when the
  LLM's parametric coverage is richer. This is a published customer claim at risk.
Tier hint: Local GPU (RTX4060 8GB). ~30-60 min. $0. Run concurrently with or after PT1.
Why-now: TriviaQA margin is a concrete customer-facing number. If it changes materially
  at 7B, the product pitch must be updated before external communication.

Pre-reg bands:
  HARD-PASS: substrate+7B EM >= RAG+7B EM + 0.010 (margin grows; encyclopedic advantage holds).
  MIDDLE-BAND: substrate+7B EM = RAG+7B EM +/- 0.009 (parity within noise; claim revised to neutral).
  HARD-FAIL: substrate+7B EM < RAG+7B EM - 0.010 (context distraction hurts; 2603.11513 pattern).

### Anchor 3: qwen7b_llm_decomp_retest_v1 (PT3 -- cycle 158 closure check)

Anchor pointer: Research note Section "Top 3 Cheap Pre-Tests" PT3
Substrate-product reading: Re-run cycle 158 LLM-decomp experiment at Qwen-7B. The Pattern B
  unique compositional path claim is valid only if LLM-decomp also fails at 7B. Compositional
  reasoning literature (arxiv 2407.15720) shows CoT starts to help around 7-10B; LLM-decomp
  may work at 7B even though it failed at 1.5B. If it works, Pattern B must be reframed as
  "audit + provenance uniqueness" rather than "compositional uniqueness."
Tier hint: Local GPU (RTX4060 8GB). ~1 hr. $0. Run after PT1 confirms context utilization works.
Why-now: Pattern B claim is in the product pitch. If 7B invalidates it, the pitch must be
  corrected before v1 demo customer conversations.

Pre-reg bands:
  HARD-PASS (Pattern B claim survives): LLM-decomp at 7B achieves F1 < 40 on bridge questions
    (closure holds; substrate-native Pattern B remains unique path).
  MIDDLE-BAND: F1 = 40-50 (marginal; Pattern B still competitive but not unique).
  HARD-FAIL (Pattern B claim must be revised): LLM-decomp at 7B achieves F1 >= 50 (closure
    reverses; Pattern B unique-path claim requires revision before customer communication).

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_qwen7b_promotion_risks_2x_2026-06-07.md
- Prior bridge-ID drill: d:/AI/hd-instrument/notes/research_drill_bridge_id_accuracy_2x_2026-06-07.md
- Prior reasoning+code drill: d:/AI/hd-instrument/notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- Cycle 158 LLM-decomp failure context: see orchestrator notes, cycle 158 verdict entry
- Context utilization failure study: arxiv 2603.11513 (March 2026)
- Qwen2.5 technical report: arxiv 2412.15115

---

## Contract section

Exp-dev is responsible for:
1. Designing anchor cells for PT1/PT2/PT3 from the research note pointers above.
2. Ensuring Qwen-7B Q4_K_M is pulled/verified on the runner before dispatch.
3. Using same 200-question subsets as existing 1.5B runs for direct comparison.
4. Pre-registering bands per research note PT1/PT2/PT3 sections.
5. Reporting results in same format as 1.5B baseline (EM + F1 per condition).

Exp-dev is NOT responsible for:
- Deciding whether to update the v1 pitch (orchestrator + user decision).
- Rerunning 1.5B experiments (already done; use existing results for PT4 comparison).

---

## Autonomy declaration

Exp-dev has full autonomy to sequence PT1/PT2/PT3 in parallel if GPU permits.
PT1 is the mandatory gate; PT2 and PT3 can run in parallel with PT1 or immediately after.
PT4 (substrate+1.5B vs bare+7B comparison) is free after PT1 completes -- authorize from
  existing data, no additional GPU time required.
PT5 (prompt format ablation) is authorized only if PT1 returns HARD-FAIL on substrate
  value-add; do not run PT5 speculatively.
