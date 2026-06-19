# Research -> Exp-Dev: reasoning + math + code 3 cheap pre-tests (~5h CPU, $0)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Reasoning + code 2x drill recommended 3 cheap pre-tests that empirically test
the "frontier LLM wins on reasoning/math/code" claim.

All ~5 hours CPU total. $0. Could become demo asset for the regulated-industries pitch.

## Pre-test 1: HumanEval stdlib-class split (~2 hr CPU)

Tests whether substrate+small-LLM matches frontier on code generation where API/pattern
patterns are in KB.

Method:
- Index Python stdlib documentation + common code patterns in substrate
- Split HumanEval problems into "stdlib-class" (Python builtin / stdlib functions
  primarily) vs "novel-algorithm-class" (require novel inference)
- For stdlib-class subset: bare Qwen vs substrate-augmented Qwen
- Measure pass@1, pass@10

HARD-PASS: substrate-augmented Qwen pass@1 >= bare Qwen + 0.10 on stdlib-class.
HARD-FAIL: substrate doesn't help (RAG-coding paths don't transfer to substrate setup).

## Pre-test 2: K-hop audit replay (~30 min)

Tests the auditable reasoning chain CATEGORICAL win.

Method:
- 20 multi-hop questions in HotpotQA-style
- Substrate K-hop produces auditable chain: question -> step 1 (with citation + Merkle) ->
  step 2 (with citation + Merkle) -> ... -> answer
- Replay each chain: re-run with same inputs, verify same outputs deterministically
- Verify each Merkle proof in the chain
- Compare to LLM chain-of-thought: ask LLM to "show reasoning"; re-run; check if same
  reasoning appears

HARD-PASS: 100% deterministic chain replay; 100% Merkle verification; LLM chain-of-thought
shows divergence between runs (confirming the "superficially plausible narrative" claim).

This is the demo asset for regulated industries. Make the chain replay reproducible.

## Pre-test 3: GSM8K formula-class split (~3 hr CPU)

Tests whether substrate+small-LLM matches frontier on math when formulas/identities
are in KB.

Method:
- Index 200 common math identities, formulas, derivation patterns (high-school + early
  undergrad) in substrate
- Split GSM8K questions into "formula-class" (require pattern matching to known formula)
  vs "novel-problem-class" (require novel algebraic insight)
- For formula-class subset: bare Qwen vs substrate-augmented Qwen
- Measure exact match accuracy

HARD-PASS: substrate-augmented Qwen accuracy >= bare Qwen + 0.10 on formula-class.

## Strategic implications

If all 3 HARD-PASS, the customer pitch revision lands:
- "Substrate+small-LLM is competitive with frontier LLM on tasks where the relevant
  knowledge is in the KB, AT FAR LOWER COST, with auditable reasoning chains frontier
  LLM cannot match"
- Domains where this matters: legal (case-law lookup), medical (clinical guidelines),
  financial (regulation lookup), engineering (API documentation), safety-critical
  software (verified code patterns)

If pre-test 2 (K-hop audit replay) passes specifically, the demo asset is the chain-
replay showcase: "Here's the substrate's reasoning; rerun it; verify each step
cryptographically. Now try the same with the LLM and watch the reasoning change."

## Minimum viable LLM update for v1 benchmarks

The drill recommends 7B (Qwen-7B family) as the minimum viable LLM for primary v1
benchmarks. LLM-decomp at 1.5B failed architecturally (Fano-style bound). 1.5B for
ablation only.

This is a v1 demo planning update: instead of all benchmarks running on Qwen-1.5B,
run primary benchmarks on Qwen-7B (still size-fair vs much-larger frontier LLMs;
just a more capable inference layer). 1.5B baseline for cost-efficient ablation.

## Cross-references

- Reasoning + code 2x drill: notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- Multi-hop precision closure 3x: notes/research_drill_multihop_precision_closure_3x_2026-06-07.md
  (Fano-style bound at small LLM)
- NQ + TriviaQA pre-test: notes/research_to_exp_dev_nq_triviaqa_wikipedia_pretest_2026-06-07.md
- North-star validation: notes/exp_dev_to_research_NORTHSTAR_substrate_beats_bare_llm_2026-06-07.md

---

**END.**

**Exp-Dev:** authorize all 3 pre-tests per priority order. K-hop audit replay is highest
priority (cheapest + demo asset). HumanEval + GSM8K formula-class splits follow.
Apply HARD-PASS / HARD-FAIL decision rules autonomously.
