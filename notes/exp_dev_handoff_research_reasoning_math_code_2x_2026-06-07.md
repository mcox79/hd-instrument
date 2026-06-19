# exp_dev hand-off -- research: reasoning_math_code_2x

Filed-by: research sub-agent
Trigger: d:/AI/hd-instrument/notes/research_drill_reasoning_math_code_2x_2026-06-07.md
Date: 2026-06-07

Per [[feedback-no-experiment-design-in-prompts]]

---

## Pause state

Check data/orchestrator_paused.flag before dispatching. If paused, hold all queue-adding
steps and return.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY)
Name: HumanEval stdlib-class split (RAG-code provenance)
Pointer: research note Section 4C, Pre-test 2
Substrate-product reading: Qwen-1.5B + substrate KB of Python stdlib documentation vs
bare Qwen-1.5B on HumanEval. Split problems into Class A (stdlib-dependent) vs Class B
(algorithm design). This directly tests the code-provenance value claim.
Tier hint: Tier 2 (local runner, 2h, no cloud)
Why now: CodeRAG literature (+35 pass@1) is strong; this is the production-encoder
pre-test gating the broader code-generation claim. Cheapest falsifiable test.
HARD PASS: Class A pass@1 improvement > 15 points.
HARD FAIL: < 5 points or regression.

### Anchor 2
Name: K-hop audit replay determinism (5-question HotpotQA sample)
Pointer: research note Section 7, Pre-test 3
Substrate-product reading: Given 5 HotpotQA multi-hop questions, verify K-hop relay
output can be replayed deterministically via stored chain. This establishes the
auditable-chain claim as a proven capability for regulated-industry positioning.
Tier hint: Tier 1 (local, < 30 min)
Why now: acc=1.0 K-hop compose is already empirically confirmed. This is a
demonstration/proof smoke test, not a novel experiment. Very low cost.
HARD PASS: 5/5 replay identical.
HARD FAIL: any non-determinism.

### Anchor 3
Name: GSM8K formula-class split
Pointer: research note Section 7, Pre-test 1
Substrate-product reading: Qwen-1.5B + KB of formula patterns on GSM8K pattern-A
(formula substitution) problems vs bare Qwen-1.5B. Tests whether knowledge retrieval
closes the math gap on the tractable sub-class.
Tier hint: Tier 2 (local runner, 2-3h)
Why now: Prerequisite before GSM8K full-set comparisons to frontier. Pre-test gates
the math claim.
HARD PASS: Pattern-A accuracy improvement > 20 points.
HARD FAIL: < 5 points.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- RETRO paper (key analogy): arxiv:2112.04426
- CodeRAG (code generation evidence): arxiv:2504.10046
- RAT (retrieval+CoT): arxiv:2403.05313
- Legal AI trustworthiness gap: arxiv:2511.21033
- Production architecture locked: d:/AI/hd-instrument/notes/production_architecture_locked_2026-06-07.md

---

## Contract

exp_dev reads this file and dispatches anchors in rank order subject to:
- Pause gate check (data/orchestrator_paused.flag)
- Production-encoder pre-test requirement (feedback_drill_pretest_required.md) -- each
  anchor above IS the pre-test; no additional pre-test needed before these
- Small-scale-first: all three anchors are local runner / no cloud required
- ASCII-only in scripts, last-token pool for causal LMs, write_metrics() required

## Autonomy declaration

exp_dev owns: pre-reg bands, script writing, queue dispatch, post-ship verify.
exp_dev does NOT own: verdict interpretation, cap_map updates, strategy decisions.
