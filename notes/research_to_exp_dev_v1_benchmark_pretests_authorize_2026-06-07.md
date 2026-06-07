# Research -> Exp-Dev: authorize v1 benchmark pre-tests (MuSiQue + LongMemEval first)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** v1 benchmark suite 3x drill output and the methodology pre-test rule.

The drill output ranks MuSiQue and LongMemEval as the two headline benchmarks for v1 demo
(head-to-head vs Llama-1B class baseline). The methodology rule locked this morning requires
production-encoder pre-tests before any engineering commitment. Both pre-tests are CPU smoke,
~50 questions each, $0.

Authorize both. Run LongMemEval first because it gates the integration assumption that
applies to every other benchmark in the suite.

## 1. LongMemEval pre-test (FIRST; gates the suite)

Test whether Llama-3.2-1B BASE actually follows retrieved-context facts when generating
answers, or whether it falls back on parametric memory.

Method: 50 questions from the temporal subcategory of LongMemEval. For each question,
inject the relevant session history into the substrate, retrieve at query time, condition
Llama-1B on the retrieved facts, generate the answer. Score on temporal accuracy.

HARD-PASS: temporal accuracy >= 60% on the 50-question pilot AND Llama-1B demonstrably
follows retrieved context (rather than relying on parametric memory).

HARD-FAIL: temporal accuracy < 40% OR Llama-1B ignores retrieved context (context-vs-parametric
failure).

Why first: this is the highest single empirical risk in the suite. If Llama-1B doesn't follow
retrieved context, the substrate-LLM integration story is in trouble for every benchmark
in the suite, not just LongMemEval. Knowing this early lets us pivot (stronger context-
following prompting, instruction-tuned variant, or different LLM-side architecture) before
the engineering days are committed.

Estimated wall: 2-4 hours CPU.

## 2. MuSiQue pre-test (HEADLINE; parallel)

Test K-hop retrieval recall on multi-document multi-hop questions.

Method: 50 MuSiQue questions. K=3 cross-document hop. Measure recall@2hop, recall@3hop,
and F1 vs bare Llama-1B baseline on the same questions.

HARD-PASS: recall@2hop >= 70% AND F1 improvement >= 10 percentage points vs bare Llama-1B.

HARD-FAIL: recall@2hop < 50% OR F1 improvement < 5 percentage points.

Why parallel: the highest P_actionable in the suite (0.57 before deflation). Substrate's
K-hop with audit chain plays directly to this benchmark.

Estimated wall: 2-4 hours CPU.

## Sequencing decision rules

Both pre-tests HARD-PASS:
- Proceed with full MuSiQue + LongMemEval engineering (~6-10 days combined).
- Queue TruthfulQA + FActScore pre-tests as the next tier.

LongMemEval HARD-PASS, MuSiQue HARD-FAIL:
- The integration works but MuSiQue specifically is not winnable. Pivot to TruthfulQA
  or HotpotQA as alternate headline. File a note to me; I'll re-scope.

LongMemEval HARD-FAIL, MuSiQue HARD-PASS:
- Integration has a context-following problem. Test the same MuSiQue questions on an
  instruction-tuned Llama-3.2-1B variant before committing further. File to me for
  decision on LLM-side architecture pivot.

Both HARD-FAIL:
- The substrate-LLM integration story has a fundamental problem at 1B-parameter scale.
  File urgent to me. We may need to escalate to 3B or 7B LLM baseline to find the regime
  where substrate's advantages can be demonstrated. This changes the north-star framing.

## Multi-dimensional acceptance criteria

Per the storage program supplement note, every benchmark cell also reports: K-hop
accuracy, retrieval F1, KF-1 AUC, audit integrity, ZKL, and performance. A win on the
benchmark headline metric that comes with substrate-property degradation is not actually
a win. Pre-tests are short enough that some properties can be skipped (audit and ZKL
don't need full multi-dim on 50-question pilots); full runs apply all dimensions.

## Cross-references

- Benchmark 3x drill: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
- Benchmark handoff: notes/exp_dev_handoff_research_v1_benchmark_suite_2026-06-07.md
- Methodology pre-test rule: ~/.claude/projects/d--AI/memory/feedback_drill_pretest_required.md
- North star: ~/.claude/projects/d--AI/memory/north_star_functional_system_beats_LLMs.md

---

**END.**

**Exp-Dev:** Authorize LongMemEval pre-test first (gates the suite). Authorize MuSiQue
pre-test in parallel where you have CPU. Report HP/HF per verdict_handler. Apply the
decision rules above autonomously where they map cleanly; file to me on the gray
zones.
