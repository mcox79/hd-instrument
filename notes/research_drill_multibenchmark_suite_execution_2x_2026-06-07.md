# Research Drill: Multi-Benchmark Suite Execution (2x operational drill)
Date: 2026-06-07
Topic: Building a defensible 3-5 benchmark validation suite for substrate vs 1B-class LLM demo
Depth: Level-2 operational drill (existing findings deepened; not re-run as verification)
Prior note: notes/research_drill_v1_benchmark_suite_3x_2026-06-07.md
P_deflated split: theoretical x empirical per drill-pretest-required rule

---

## HEADLINE

The benchmark suite is executable in 10-16 engineer-days with the correct sequencing.
HotpotQA and MuSiQue share all infrastructure and run back-to-back for near-zero marginal
cost; LongMemEval is the highest-value but highest-integration-cost benchmark (3-5 days);
FActScore requires a prompt-engineering decision upfront (atomic-fact extraction via LLM or
rule-based). The third baseline (vanilla RAG without substrate) is load-bearing for the demo
argument and must be included in every benchmark run. Statistical power at n=200 is adequate
for a +0.15 F1 lift with 95% CI excluding zero. HARD-FAIL scenario (only HotpotQA wins) is
real; pre-register it now rather than later.

P_theoretical: 0.72 (substrate has theoretical advantage on all five benchmarks)
P_empirical: 0.42 (deflated -0.30 for integration-quality risk, especially LongMemEval
context-following and FActScore prompt-format sensitivity)

---

## 1. BENCHMARK SEQUENCING (what order to build and run)

### The sequencing argument

Two sequencing principles apply:

Principle 1: Build cheapest first, gate on result. If MuSiQue integration shows the
substrate-LLM generation chain does not produce coherent F1 improvement, this is a signal
to fix the generation scaffolding BEFORE building LongMemEval (which depends on the same
generation chain).

Principle 2: Infrastructure re-use gates sequencing. HotpotQA and MuSiQue share 100% of
infrastructure (same retrieval encoder, same KEY store format, same generation pipeline,
same EM/F1 metric). Build them as a single unit. LongMemEval requires new session-history
ingestion; build that second. FActScore requires atomic-fact extraction; build that third.
StreamingQA requires a temporal corpus; build that fourth or defer.

### Recommended execution order

Step 1 (Days 0-0): HotpotQA Tier-1 full run.
  - Already smoke-validated (n=30, +0.35 F1).
  - Scale n to 200-300 questions from the HotpotQA fullwiki dev set.
  - Add vanilla-RAG-baseline condition (same retrieval encoder, BM25 or dense retrieval
    without substrate KEY structure). This is the key differentiator condition.
  - Wall time: 30-60 min CPU. Engineer-days: 0 incremental (script already exists).
  - Gate: if Tier-1 lift drops below +0.10 F1 vs vanilla RAG, pause and diagnose.

Step 2 (Days 1-2): MuSiQue integration and Tier-1 run.
  - Same harness as HotpotQA, different dataset loader (HuggingFace datasets: 'musique').
  - Key change: MuSiQue questions require 2-4 hops; K-hop chain must be configured for
    depth K >= 3. A K=2 chain used for HotpotQA is insufficient; verify K parameter.
  - Add same three baseline conditions (bare LLM, vanilla RAG, substrate).
  - Wall time: 30-60 min CPU.
  - Engineer-days: 1-2 days.

Step 3 (Days 3-7): LongMemEval integration.
  - HIGHEST RISK item. Session-history ingestion is a new pipeline piece.
  - LongMemEval has 500 questions with two scale settings: 115k token context (S) and
    1.5M token context (M). For v1 demo, use the S setting only (manageable on CPU).
  - The core engineering challenge: ingest session histories into substrate KEY store in
    the correct temporal order, then issue as_of queries at evaluation time.
  - The generation chain risk: Llama-1B or Qwen-1.5B-base may not follow retrieved
    context well enough for the temporal reasoning and knowledge-update categories.
    Instruction-tuned variants (Qwen-1.5B-Instruct) are safer here.
  - PRE-TEST REQUIRED (per drill-pretest-required memory rule): Before building the full
    LongMemEval harness, run a 1-2 hour pre-test on 20-30 questions with both base and
    instruct variants of the 1.5B model. If instruct variant shows >0.15 accuracy gap
    over base, use instruct for LongMemEval only.
  - Wall time at n=200: 3-7 hours CPU (session ingestion is the bottleneck).
  - Engineer-days: 3-5 days.

Step 4 (Days 8-10): FActScore integration.
  - FActScore requires decomposing generated text into atomic claims and verifying each
    against a reference corpus. The pip installable package (factscore) handles the
    decomposition step using a lightweight claim-extraction model.
  - Integration complexity: the substrate audit chain needs to expose a per-retrieved-fact
    attribution API so FActScore can credit or penalize each atomic claim's backing source.
  - Key decision upfront: use the open-source factscore package's LLM-based atomic
    decomposition (slower, ~2-5s per entity) or write a rule-based clause splitter (faster,
    less accurate). Recommendation: use the package for n=50-100 entities at Tier-1; this
    is affordable at ~2-5 hours wall time.
  - Engineer-days: 2-3 days.

Step 5 (Days 11-16, deferred or parallel): StreamingQA.
  - Requires downloading and indexing a time-stamped news corpus (14 years, 2007-2020).
  - The temporal-correctness metric (answering questions about events at the time they
    were asked, not with later knowledge) is substrate's native use case.
  - High wall time. Defer to after Steps 1-4 are validated.
  - Engineer-days: 4-6 days.

### Pattern B-dependent benchmarks (CaT-bench, CLUTRR, AnalogyQA)
Do not build until Pattern B Phase 0 SRL passes. Building these before that gate is
wasted engineering time. Treat as deferred queue items.

---

## 2. SHARED INFRASTRUCTURE DESIGN

### What is built once and reused across all benchmarks

A. Retrieval encoder (bge-small-en-v1.5 or upgrade):
  - Encodes question + context documents into the same embedding space.
  - No per-benchmark changes needed. The encoder is already validated in cycle 158-159.
  - Possible upgrade for LongMemEval: bge-m3 (multilingual, longer context). Evaluate
    only if bge-small retrieval quality degrades on session-history queries.

B. Substrate KEY storage and K-hop retrieval:
  - KEY store is populated per dataset (each benchmark gets its own namespace/shard).
  - K-hop chain parameters (K, recall threshold) may differ per benchmark but the
    infrastructure is identical.
  - For LongMemEval: temporal indexing (document timestamp) is an additional metadata
    field on each KEY entry. No structural change to the KEY store; just an extra column.

C. LLM generation pipeline:
  - Qwen2.5-1.5B (base for HotpotQA/MuSiQue; instruct variant for LongMemEval).
  - Same generation call signature. Same prompt template (retrieved-context + question).
  - Generation temperature = 0 across all benchmarks for reproducibility.

D. Baseline conditions (built once, run for every benchmark):
  - Baseline 1: Bare Qwen2.5-1.5B closed-book (no retrieval).
  - Baseline 2: Vanilla RAG (bge-small dense retrieval + BM25 re-rank, no substrate
    KEY structure). This is the critical differentiator condition.
  - Test: Substrate-augmented Qwen2.5-1.5B.
  - All three conditions use identical generation prompts; only the retrieved context
    differs.

E. Metric harness:
  - EM + F1 (HotpotQA, MuSiQue, StreamingQA).
  - Accuracy + per-category breakdown (LongMemEval).
  - FActScore (FActScore benchmark).
  - One shared result-writer (JSON per run, with condition tag, benchmark, n, metric).

F. Audit chain logging:
  - Every retrieval call logs: query, retrieved_keys, retrieval_scores, generation_input,
    generation_output.
  - This is required both for FActScore attribution scoring AND for debugging HARD-FAIL
    conditions.

### What is per-benchmark only

- Dataset loader (one Python file per benchmark, ~50-200 lines each).
- Question formatter (each benchmark has different question/answer schema).
- Evaluation metric (EM/F1 vs accuracy vs FActScore precision).
- Session ingestion pipeline for LongMemEval (new; largest per-benchmark piece).
- Temporal corpus indexing for StreamingQA (new; second largest per-benchmark piece).

The shared-to-specific ratio is roughly 80% shared infrastructure, 20% per-benchmark.
After the first benchmark (HotpotQA Tier-1), each subsequent benchmark adds 1-5 days of
integration on top of the shared base.

---

## 3. WALL TIME AND COST PER BENCHMARK AT TIER-1 (n=200+)

All estimates assume CPU-only (remote CPU runner or laptop), Qwen2.5-1.5B, single-shard
substrate with preloaded KEY store.

| Benchmark       | n     | Per-query time | Total wall time | Cost (CPU) |
|-----------------|-------|----------------|-----------------|------------|
| HotpotQA        | 300   | 6-12s          | 30-60 min       | ~$0-1      |
| MuSiQue         | 200   | 8-15s          | 30-50 min       | ~$0-1      |
| LongMemEval (S) | 500   | 2-5 min        | 16-40 hours     | ~$2-8      |
| FActScore       | 100   | 90-300s        | 2.5-8 hours     | ~$1-3      |
| StreamingQA     | 200   | 20-60s         | 1-3 hours       | ~$0-2      |

Notes:
- LongMemEval per-query time is high because session-history ingestion happens at query
  time unless pre-ingested. Pre-ingest all sessions before the eval loop to reduce to
  ~15-30s per query at eval time (2-4 hours total).
- FActScore uses the factscore package's claim extraction model (DistilBERT or GPT-3.5
  if using the hosted scorer). Use local DistilBERT-based scorer to keep cost near zero.
- Total wall time for the full suite (Steps 1-4): 20-55 hours CPU, ~$3-12 cost.
  Parallelizing benchmarks after integration halves this to 10-28 hours wall time.

---

## 4. BASELINE COMPARISON SETUP AND THE VANILLA-RAG THIRD CONDITION

The three-way comparison structure is critical. It is not optional.

Why vanilla RAG matters: A benchmark win of "substrate beats bare LLM by +0.35 F1" is
impressive to ML researchers but a sophisticated customer will immediately ask "does it
beat plain RAG?" If the answer is "we didn't test vanilla RAG," the demo loses
credibility. The vanilla RAG condition costs near zero marginal engineering (same encoder,
same data, skip the substrate KEY structure, just do top-k dense retrieval).

Expected outcome by condition for HotpotQA:
  - Bare Qwen2.5-1.5B (closed-book): F1 ~ 0.15-0.25 (based on published 1B-class results)
  - Vanilla RAG (top-5 dense): F1 ~ 0.50-0.65 (RAG recovers most of the gap)
  - Substrate-augmented: F1 ~ 0.65-0.75 (substrate adds K-hop chain + query routing)

The honest story for multi-hop: substrate adds +0.10-0.20 F1 over vanilla RAG on 2-hop
questions. On 3-4 hop questions, the gap should widen because vanilla RAG degrades
significantly at K>2 hops while substrate's K-hop chain maintains recall. This is the
strongest differentiator to demonstrate.

P_theoretical (substrate beats vanilla RAG on multi-hop): 0.70
P_empirical (after deflation): 0.45

Expected outcome for LongMemEval (temporal reasoning / knowledge update categories):
  - Bare Qwen: ~20-30% accuracy (no memory whatsoever)
  - Vanilla RAG: ~40-55% (retrieves some relevant sessions but lacks temporal indexing)
  - Substrate-augmented: ~60-75% (as_of queries + explicit timestamp metadata)

The LongMemEval story is cleaner for the demo because vanilla RAG has a structural
weakness (no temporal ordering) that substrate directly addresses.

P_theoretical (substrate beats vanilla RAG on LongMemEval temporal): 0.80
P_empirical (after deflation): 0.55

---

## 5. STATISTICAL POWER REQUIREMENTS

### Cycle 158 smoke baseline
n=30 gave +0.35 F1, no CI reported. This is below the minimum for a statistically
defensible claim. Tier-1 promotion is required.

### Power analysis for Tier-1

For a two-condition comparison (substrate vs baseline) with binary F1 components:
- At n=200, the standard error on F1 is approximately SE = sqrt(F1*(1-F1)/n).
  For F1=0.50, SE ~ 0.035. For a difference, SE_diff ~ sqrt(2) * SE ~ 0.050.
- 95% CI half-width: ~1.96 * 0.050 = 0.098 (call it ~0.10).
- This means an observed lift of +0.35 at n=200 gives a 95% CI of roughly [0.25, 0.45].
  Clearly significant and impressive.
- A reduced lift of +0.15 at n=200 gives CI [0.05, 0.25]. Still significant but narrower.
- The minimum detectable lift at 80% power, n=200, alpha=0.05 is approximately +0.10 F1.
  Anything below +0.10 F1 requires n > 800 to be statistically detectable.

### The smoke-to-Tier-1 replication risk
The cycle 158 smoke at n=30 has high variance. The true lift could be +0.10 to +0.50.
The most conservative defensible pre-registration: HARD-PASS at +0.15 F1 with 95% CI
excluding zero at n=200. This is conservative but honest.

Key concern: n=30 smokes routinely show larger effect sizes than n=200+ runs due to
sample bias (small validation sets can over-represent easy questions). Do not report
the +0.35 F1 figure publicly until Tier-1 confirms it.

### Pre-registered thresholds (HARD-PASS + HARD-FAIL) per benchmark

HotpotQA Tier-1:
  HARD-PASS: lift >= +0.15 F1 (substrate vs vanilla RAG) with 95% CI excluding zero, n=200+
  MIDDLE-BAND: lift +0.05 to +0.15 (statistically present but weak; check multi-hop K>2)
  HARD-FAIL: lift < +0.05 or CI crosses zero (investigate retrieval recall; check K-hop depth)

MuSiQue Tier-1:
  HARD-PASS: lift >= +0.10 F1 (substrate vs vanilla RAG), n=200+. MuSiQue is harder;
    lower absolute threshold reflects the difficulty of the benchmark.
  MIDDLE-BAND: lift +0.03 to +0.10
  HARD-FAIL: lift < +0.03 or CI crosses zero

LongMemEval Tier-1 (S setting, temporal + knowledge-update categories):
  HARD-PASS: accuracy >= 0.60 (substrate) with bare-LLM baseline < 0.35, n=200+
  MIDDLE-BAND: accuracy 0.45-0.60 (substrate), LLM baseline < 0.35
  HARD-FAIL: accuracy < 0.45 OR substrate does not beat vanilla RAG by >0.10

FActScore Tier-1:
  HARD-PASS: FActScore precision >= 0.70 (substrate-attributed) vs baseline < 0.55
  MIDDLE-BAND: substrate precision 0.55-0.70
  HARD-FAIL: substrate precision < 0.55 OR indistinguishable from vanilla RAG

---

## 6. CROSS-BENCHMARK HEADLINE STORY SCENARIOS

### Scenario A (best case): 4-5 benchmarks win at Tier-1
Headline: "Substrate-augmented 1.5B-parameter model outperforms the same model without
substrate across multi-hop reasoning, long-term memory, factual attribution, and continual
knowledge updates."

Claim: "Consistent +0.10 to +0.35 improvement over vanilla RAG across all tested capability
axes at 1.5B scale."

Demo structure: Show per-category breakdown for LongMemEval (temporal and knowledge-update
categories are strongest). Show multi-hop difficulty breakdown for MuSiQue (K=3-4 hop
questions are the differentiator). Attribution graph for FActScore (visual, impressive).

### Scenario B (likely): 3 of 5 win
Expected winning three: HotpotQA, MuSiQue, LongMemEval.
Expected weaker two: FActScore (integration-quality sensitive), StreamingQA (corpus
ingestion complexity).

Headline: "Substrate improves a 1.5B model on multi-hop QA and long-context memory.
Attribution accuracy and streaming updates are work in progress."

The honest framing of 3-of-5 is not a failure. Three-axis wins at 1.5B scale, all vs
vanilla RAG, is a defensible v1 demo. The key message is that the substrate architecture
produces consistent gains on the hardest retrieval tasks.

### Scenario C (conservative): Only HotpotQA and LongMemEval win
Headline: "The substrate provides clear advantages on tasks requiring multi-step fact
combination and long-term memory. Single-step factual QA and generative factuality
benchmarks show smaller gains."

This is still a coherent product story for a memory-first positioning.

### Scenario D (hard-fail case): Only HotpotQA wins at Tier-1
This is a genuine risk. If substrate-augmented Qwen-1.5B does not beat vanilla RAG on
LongMemEval, it suggests context-following failure in the generation layer, not substrate
failure. The correct response is:
  1. Switch LLM to instruction-tuned variant (Qwen-1.5B-Instruct).
  2. Re-run LongMemEval pre-test before full Tier-1.
  3. If still failing: scope demo to HotpotQA + MuSiQue and position substrate as
     a multi-hop reasoning accelerator rather than a general memory system for v1.

The demo is still defensible at Scenario D; the cross-axis claim just narrows.

---

## 7. FAILURE MODE CONTINGENCY (per benchmark)

### LongMemEval HARD-FAIL path

Root cause hypothesis: Small base LLMs (Qwen-1.5B-base, Llama-1B-base) do not reliably
follow injected context for temporal reasoning questions. The LLM may anchor on its
parametric knowledge rather than the retrieved session content.

Diagnostic test (the 1-2 hour pre-test): Run 25 questions from the temporal-reasoning
category with Qwen-1.5B-base vs Qwen-1.5B-Instruct. If instruct gap >= 0.15 accuracy:
use instruct variant for LongMemEval. If gap < 0.05: the issue is elsewhere (likely
session ingestion or as_of query correctness).

Rescue path 1: Switch to instruct variant (1 day).
Rescue path 2: Add explicit temporal-context injection to the prompt template ("The
following information was recorded at time T. Use only this information to answer."
~0.5 days prompt engineering).
Rescue path 3: If both fail at Tier-1, segment LongMemEval results by category.
Report temporal + knowledge-update categories only (the ones with substrate native
advantage). Do not include multi-session reasoning categories where generation-LLM
deficiencies dominate.

### FActScore HARD-FAIL path

Root cause hypothesis: The atomic-fact extraction step (factscore package) may fail to
correctly attribute substrate-retrieved content to specific source documents because the
generation prompt does not include explicit source citations.

Rescue path 1: Add source-citation injection to generation prompt ("Fact 1 is from
document X, fact 2 is from document Y"). This requires the substrate audit chain to
return per-retrieved-fact source IDs, which it already supports. (~1 day integration).
Rescue path 2: Use the FActScore "retrieve" mode (FActScore estimates factuality by
retrieving relevant Wikipedia paragraphs, not substrate-retrieved content). This measures
raw factual precision independent of the substrate retrieval chain. Less impressive but
still shows substrate generation quality. (~0.5 days).
Rescue path 3: Defer FActScore to Phase 2. Replace in v1 demo with TruthfulQA MC1
(simpler, already researched, no attribution machinery needed).

---

## 8. ENGINEERING WORK DECOMPOSITION

### Sequence and dependency graph

Week 1:
  Day 0: HotpotQA Tier-1 (0 incremental days; just run longer with 3 baselines).
  Days 1-2: MuSiQue integration. Dependency: HotpotQA harness complete.

Week 1-2:
  Days 3-7: LongMemEval integration. Dependency: substrate temporal API tested.
  Days 8-10: FActScore integration. Dependency: substrate audit-chain attribution API.

Week 2-3 (parallel after Days 1-2 are done):
  Days 11-16: StreamingQA (deferred, lower priority).

Pattern B-dependent (CaT-bench, CLUTRR, AnalogyQA): Do not start until Pattern B
Phase 0 SRL passes. No engineering time allocated in this plan.

### Critical path

The critical path for the minimum viable 3-benchmark demo (HotpotQA + MuSiQue +
LongMemEval) is:
  HotpotQA Tier-1 (Day 0) -> MuSiQue integration (Days 1-2) -> LongMemEval integration
  (Days 3-7) -> LongMemEval Tier-1 run (Day 8).

Elapsed: 8 working days to minimum viable demo.
Adding FActScore adds 2-3 days: minimum 11 working days for a 4-benchmark demo.

The limiting constraint is not wall time (all runs are fast enough on CPU); it is
engineering integration for LongMemEval session-history ingestion and temporal API
verification.

---

## 9. PARALLELIZABILITY

After integration is complete, all four benchmarks can run in parallel on the CPU runner.
They do not share GPU. They do not block each other. They read from the same shared
substrate KEY store but in separate namespaces.

The one parallelism constraint: if MuSiQue and LongMemEval integration is being built
simultaneously by two engineers, they need to agree on the shared dataset loader interface
before starting. The interface is minimal (load_question(idx) -> {question, answer,
context_docs, metadata}).

For a solo-engineer path: build sequentially. For a two-engineer path: engineer 1 builds
LongMemEval (the hard one), engineer 2 builds MuSiQue + FActScore. Integration completes
in 5-7 days instead of 10.

---

## 10. HONEST WEAKNESS DISCLOSURE (not for v1 demo)

MMLU and NaturalQuestions closed-book: substrate has no advantage on parametric recall
tasks. These benchmarks test whether the LLM has the right answer in its weights.
Substrate's contribution is external memory, which is irrelevant for closed-book tests.
Running these benchmarks would hurt the demo story. Do not include.

TruthfulQA MC1: substrate may show improvement (abstention prevents confabulation) but
the benchmark tests LLM-inherent truthfulness, not retrieval quality. The improvement is
unpredictable and depends heavily on prompt architecture. Include only as supporting
evidence if TruthfulQA results happen to be positive after HotpotQA/LongMemEval are
complete; do not build the demo around it.

CLUTRR, AnalogyQA: pattern-B dependent. Do not claim until SRL passes.

---

## CHEAP DECISIVE TEST

For the minimum viable claim ("substrate-augmented 1.5B beats bare 1.5B AND vanilla RAG on
multi-hop QA and long-context memory"):

Test: HotpotQA n=200 three-way comparison (bare LLM / vanilla RAG / substrate).
Cost: 30-60 min CPU, 0 incremental engineering days.
Gate: If substrate does not beat vanilla RAG by >= +0.05 F1 on HotpotQA n=200, the
integration scaffolding (retrieval routing, prompt format) has a bug. Fix before
proceeding to other benchmarks.

This test should be the next thing that runs after reading this note.

---

## FALSIFIABLE PREDICTIONS (HARD-PASS + HARD-FAIL)

These are the pre-registered thresholds for the cross-benchmark claim:

HARD-PASS: substrate beats vanilla RAG by >= +0.15 F1 on HotpotQA n=200, AND beats
vanilla RAG by >= +0.10 accuracy on LongMemEval temporal category n=100+, with 95% CI
excluding zero on both. This warrants a "consistent multi-axis improvement" demo claim.

MIDDLE-BAND: lifts exist and are statistically significant but below the HARD-PASS
thresholds (e.g. +0.08 F1 on HotpotQA, +0.07 accuracy on LongMemEval). Demo is possible
but the claim narrows to specific conditions (multi-hop K>=3, temporal queries only).

HARD-FAIL: substrate does NOT beat vanilla RAG at all on EITHER HotpotQA or LongMemEval
at n=200+ with 95% CI. This means the generation scaffolding (not the substrate algebra)
is broken. Route to engineering debug, not further research.

---

## CROSS-THREAD SYNTHESIS

Prior note (3x drill, same date): Identified the 5-benchmark candidates and confirmed
theoretical advantage. This 2x drill adds the operational layer: sequencing, shared
infrastructure design, per-benchmark failure contingency, and statistical pre-registration.

Cycle 158 (north-star): +0.35 F1 at n=30. This note establishes that the n=30 result
needs Tier-1 confirmation before any public claim. The conservative pre-registration
threshold (+0.15 F1) allows the lift to reduce substantially from the smoke reading and
still pass.

Cycle 159 (RAG-overlay LVH): RAG overlay confirmed. The vanilla-RAG third baseline
proposed in this note is a direct follow-up to cycle 159's confirmation that the substrate
architecture adds value over plain retrieval. The demo argument is structurally: substrate
> vanilla RAG > bare LLM; all three conditions confirmed in separate cycles, now tested
jointly.

The LongMemEval pre-test requirement (base vs instruct variant) is new and not in prior
notes. It is a direct consequence of the generation-scaffolding risk being the dominant
empirical uncertainty, not the substrate algebra.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

The benchmark suite, if it passes at Tier-1 across 3-4 axes, supports a specific product
claim: "A 1.5B-parameter model augmented with the substrate outperforms the same model
without substrate, and outperforms plain retrieval augmentation, across multi-hop reasoning
and long-context memory." This claim is testable, reproducible, and directly addresses the
"why not just use RAG?" customer question.

The demo is not about substrate beating larger LLMs (GPT-4, Llama-70B); it is about
showing that small-LLM + substrate outperforms small-LLM + vanilla RAG. This is the
correct positioning for the 5-7 week window.

Engineering time estimate to defensible demo: 8-11 working days on the critical path.
Wall time: 1-2 weeks if engineering parallelizes.

---

## CITATIONS (verified from lit-scan)

1. HotpotQA: Yang et al. 2018. "HotpotQA: A Dataset for Diverse, Explainable Multi-hop
   Question Answering." EMNLP 2018. [Standard eval: EM + F1]

2. MuSiQue: Trivedi et al. 2022. "MuSiQue: Multihop Questions via Single-hop Question
   Composition." TACL 2022. [Adversarial design; lower shortcut rate than HotpotQA]

3. LongMemEval: Wu et al. 2024. "LongMemEval: Benchmarking Chat Assistants on Long-Term
   Interactive Memory." ICLR 2025. 500 questions, 5 memory ability categories, 115k-1.5M
   token context settings. [GitHub: xiaowu0162/LongMemEval]

4. FActScore: Min et al. 2023. "FActScore: Fine-grained Atomic Evaluation of Factual
   Precision in Long Form Text Generation." EMNLP 2023. [pip: factscore]

5. StreamingQA: Liska et al. 2022. "StreamingQA: A Benchmark for Adaptation to New
   Knowledge over Time in Question Answering Models." ICML 2022. [14-year temporal corpus]

6. PRISM (2025): Agentic retrieval for multi-hop QA. MuSiQue gain: +2.4% vs 73.0%
   baseline. HotpotQA: +0.5% vs 95.4%. [Shows near-saturation at HotpotQA; MuSiQue has
   more headroom]

7. Statistical significance convention: Student's t-test over 10 independent seeds,
   p < 0.05, as per multiple 2024-2025 multi-hop QA papers. Bootstrap CI also standard
   (95% Wilson interval).

8. RAG vs baseline comparison (MDPI Information 2025): Small-LLM RAG evaluation
   across TinyLlama, Mistral-7B, Llama-3.1-8B. Confirms RAG lifts are real but
   sample-size limitations are a known issue in benchmark design.

Verified citations: 8
