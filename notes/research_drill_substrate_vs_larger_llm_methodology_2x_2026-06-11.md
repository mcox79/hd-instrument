# Research drill: substrate vs 7B/70B-class LLM head-to-head benchmarking methodology (2x DEEP)

Date: 2026-06-11
Status: 2x DEEP synthesis from 10 parallel lit-scan threads
Caveat: external lit-scan calibration penalty applied (deflate 0.15-0.25); novel-synthesis P capped at 0.50.

## (a) HEADLINE

Cross-scale head-to-head against 7B/70B LLMs is FAIR and MEASURABLE if and only if benchmark methodology adopts a four-axis normalization (iso-cost, iso-latency, iso-energy, iso-memory) PLUS three scale-invariant differentiation axes that no amount of LLM parameter scaling changes (deterministic recall, calibrated abstention with finite-sample coverage, sub-100ms warm retrieval). Substrate does NOT need to beat 70B on NL fluency to win commercially; it needs to dominate on the four normalization axes at small-LLM accuracy parity on a deliberately-chosen subset of benchmarks where 7B/70B both saturate. The published methodology toolkit for this comparison already exists (TokenPowerBench J/token, normalized-per-GPU throughput, URAG conformal RAG benchmark, KGHaluBench breadth/depth split, scaling-saturation literature). The methodology gap that substrate-specific work must close is the substrate-side measurement harness (J/inference on CPU with RAPL/IPMI, p99 wall-clock at batch=1, conformal coverage at alpha=0.10, memory MB resident set).

P_deflated on methodology validity: 0.55. P_deflated on substrate winning at least 3 of the 4 normalization axes vs Llama-3-8B at small-LLM accuracy parity on classification + factual recall: 0.50. P_deflated on substrate winning even 1 axis vs Llama-3-70B at accuracy parity on the same restricted benchmark set: 0.30 (large LLMs have hard accuracy advantage on broader benchmarks).

## (b) Cheap decisive test

A ~24 GPU-hour + ~24 CPU-hour pilot, costing well under one cloud workstation-day, decides the methodology:

1. Pick three benchmarks where 8B and 70B both saturate near a ceiling: (a) IMDB sentiment classification (lit shows 0.5B saturates near 91.7%; 8B/70B at ~94%), (b) SST-2, (c) a closed-domain factual recall benchmark restricted to KB facts substrate explicitly stores (controlled fact-recall on a 25K-fact KB substrate already validates at 0.996, vs LLM parametric recall at ~80-95% depending on fact frequency).
2. Run substrate (CPU, batch=1, fp32) on full test sets. Measure: accuracy, p50/p99 latency (ms), J/inference (RAPL or IPMI), peak RSS MB, conformal coverage at alpha=0.10 with n_cal=500.
3. Run Llama-3-8B (fp16, single GPU H100, batch=1) on same sets via vLLM. Measure: accuracy, TTFT + total time (ms), J/inference via NVML, peak GPU VRAM GB, sampling variance at temperature=0 across 5 seeds.
4. Run Llama-3-70B (fp8, 8xH100 if available; otherwise estimate from published TokenPowerBench numbers as a stand-in) on same sets. Same measurements.
5. Tabulate the four normalization axes side by side. Pre-register HARD-PASS / HARD-FAIL thresholds per axis (below).

If the pilot succeeds methodologically (substrate measurement harness produces stable numbers on each axis), the full commercial demo is a one-week extension across 6-8 benchmarks.

## (c) Falsifiable predictions with HARD-PASS / HARD-FAIL

### Axis 1 - Cost per inference (cost normalization)

Published methodology: NVIDIA blog normalizes throughput to request-per-second per GPU; TokenPowerBench reports cost as J/token x grid-price. For substrate, normalize as: amortized-CPU-core-hour-cost / inferences (US$ ~ 0.01-0.05 per core-hour; cheap CPU on commodity hardware).

- HARD-PASS: substrate cost per inference is at least 10x cheaper than Llama-3-8B at iso-accuracy on IMDB+SST-2+closed-KB-recall.
- HARD-FAIL: substrate cost per inference within 2x of Llama-3-8B (would mean substrate has no cost moat at this scale).

### Axis 2 - Latency at batch=1 (latency normalization)

Published: TTFT for 7B is hundreds of ms even on H100; 70B is 2-3x that of 13B at iso-hardware. Substrate has no autoregressive decode; retrieval is one matmul + cleanup.

- HARD-PASS: substrate p99 latency at batch=1 less than 100ms while Llama-3-8B TTFT exceeds 200ms on the same task.
- HARD-FAIL: substrate p99 latency exceeds 500ms on any task in the suite (would mean substrate has no latency moat).

### Axis 3 - Energy per inference (energy normalization)

Published: Llama-3-70B at fp8 on 8xH100 with vLLM reaches ~0.39 J/token; 1B-to-70B scaling is super-linear (7.3x energy for 70x parameters). For a typical 50-token response, that is ~20 J for Llama-3-70B; ~3 J for Llama-3-8B at best-practice deployment. Substrate is one matmul on CPU: roughly 0.01-0.1 J per inference.

- HARD-PASS: substrate J/inference at least 30x lower than Llama-3-8B and at least 200x lower than Llama-3-70B at iso-accuracy on saturating benchmarks.
- HARD-FAIL: substrate within 5x of Llama-3-8B J/inference (would mean energy moat is illusory).

### Axis 4 - Memory footprint (memory normalization)

Published: Llama-3-8B fp16 = 16 GB VRAM; Llama-3-70B fp8 = 70 GB; fp16 = 140 GB. 125M parameter Transformer can memorize ~1M Wikidata triples at 95% accuracy. Substrate kb25k storage is in low single-digit MB; kb500k extrapolates to ~100 MB.

- HARD-PASS: substrate MB-per-fact at least 10x more efficient than parametric LLM MB-per-fact at iso-recall accuracy on closed-KB benchmark.
- HARD-FAIL: substrate within 3x of parametric LLM MB-per-fact (would mean no memory moat per fact).

### Axis 5 (scale-invariant differentiator) - Calibration / abstention with finite-sample coverage

Published: URAG benchmark reformulates RAG generation as multiple-choice and applies conformal prediction; CONFLARE is direct conformal-prediction-over-LLM-retrieval framework. LLM uncertainty is generally NOT calibrated and requires expensive ensemble or test-time-augmentation for guarantees. Substrate cleanup-margin is a Vovk nonconformity score (per today's conformal drill).

- HARD-PASS: substrate produces conformal sets at coverage in [0.88, 0.92] for alpha=0.10 with average set-size less than 3 on the closed-KB benchmark; LLM achieves coverage only via expensive ensemble (greater than 5x compute) at similar set-size, OR LLM-without-ensemble has uncalibrated coverage outside [0.85, 0.95].
- HARD-FAIL: substrate coverage outside [0.85, 0.95] at any benchmark in the suite.

### Axis 6 (scale-invariant differentiator) - Reproducibility / determinism

Published: 2026 lit shows even greedy decoding LLMs have run-to-run variance from numerical precision; seed variance up to 15% on AIME'24 across 20 seeds. Substrate is bit-exact deterministic.

- HARD-PASS: substrate produces bit-identical outputs across 10 runs; Llama-3-8B at temperature=0 produces non-zero accuracy variance across 5 seeds on the same prompts.
- HARD-FAIL: substrate shows non-determinism above the floating-point-rounding level (would mean implementation bug).

### Axis 7 (LLM-favoring axis to acknowledge) - Per-benchmark accuracy ceiling on open-domain tasks

Published: 70B parameter LLMs have hard accuracy advantages on open-domain QA, multi-hop reasoning, broad knowledge tasks (MMLU 70B ~80%; 8B ~67%; substrate-only NL ~50% on similar benchmarks). Substrate does NOT win these axes and must not claim to.

- HONEST FRAMING: pre-declare which benchmarks substrate is comparing on (saturating classification + closed-KB + math-word-problem-with-VIB) and which benchmarks substrate explicitly defers to a 0.5-3B LLM front-end (open-domain QA, free-text NL).

## (d) Cross-thread synthesis with prior entries

This drill closes a methodology gap that has been latent across several recent entries:

- The frontier-scale drill earlier today (notes/research_drill_substrate_frontier_scale_interaction_2x_2026-06-11.md) established the 3-tier architecture + dense-Hopfield capacity argument. That drill addressed CAN substrate scale to frontier interaction conditions. THIS drill addresses HOW we MEASURE substrate's win vs a frontier-class LLM.
- The conformal-calibration drill (notes/research_drill_substrate_conformal_calibration_2x_2026-06-11.md) delivered the substrate-side conformal-prediction mechanism. THIS drill incorporates that mechanism as Axis 5 of the head-to-head benchmark.
- The substrate-LLM boundary decomposition (memory: substrate_LLM_boundary_decomposition_2026-06-10) decomposed which capabilities substrate owns vs which the LLM-front-end owns. THIS drill restricts the head-to-head to substrate-owned capabilities (classification, closed-KB recall, math, code, structured comm) and explicitly does NOT claim substrate wins on open-domain NL (which the boundary decomposition assigned to the LLM).
- The drill_pattern_temporal_contextual memory predicts that fixed-structural drills FAIL more often than temporal/contextual; this benchmarking methodology IS structural, so apply the calibration penalty harder (deflated to 0.50 not 0.65).
- The north-star (NORTH STAR FUNCTIONAL SYSTEM BEATS LLMS): this drill operationalizes "exceeds LLMs of relative size in clear measurable ways" by making the four normalization axes the measurable terms. Without these axes the head-to-head is anecdotal.

The methodology must also account for the published 2025-2026 finding that 1.5B-3B small models achieve the highest efficiency scores for generation tasks; substrate's Qwen2.5-0.5B comparison sits in the most-favorable-to-substrate regime for energy and latency, while the 70B comparison sits in the most-unfavorable-to-substrate regime for absolute accuracy on open-domain tasks. Both must be present so the commercial claim does not over-reach.

## (e) Substrate-product implications

1. The four normalization axes (cost / latency / energy / memory) plus three scale-invariant axes (calibration / determinism / fact-recall-on-closed-KB) become the public-facing benchmark dashboard.
2. The honest commercial story is NOT "substrate beats 70B LLM"; it is "substrate dominates 70B LLM on four cost-style axes at accuracy-parity on the deliberately-restricted task family where modern LLMs saturate anyway, while ceding open-domain NL to a small LLM front-end that substrate equips with deterministic memory and calibrated abstention."
3. The benchmark suite should be split into three named tiers: (i) substrate-only tasks where substrate beats 70B on all four cost axes (closed-KB recall, structured classification, math-word problems with VIB, code synthesis primitives), (ii) substrate-as-memory tasks where the hybrid beats 70B on cost AND accuracy (long-context fact-recall, multi-session agent memory), (iii) LLM-only tasks where substrate explicitly does not compete (open-domain QA, free-form generation).
4. Each substrate-vs-LLM benchmark result must publish a normalized cost table: J/inference, US$/inference, p99 ms, GB resident. This is non-standard for current LLM benchmarks (which report only accuracy + tokens/sec) and the commercial moat lives in the table that LLM vendors avoid publishing.
5. The MB-per-fact moat is the most defensible regulatory-relevant commercial axis: closed-KB substrate has known provenance per fact (audit trail, deletable, update-able), parametric LLM does not. This connects directly to the EU AI Act Article 12 calendar already in MEMORY.

Engineering items implied by adopting this methodology:

- Substrate measurement harness: RAPL/IPMI energy reader, RSS memory profiler, p50/p99 latency capture, conformal coverage estimator (already drafted in the conformal drill), reproducibility-bit-exactness self-test.
- A small standardized "head-to-head report" template that produces a single 4-axis table per benchmark.
- Inclusion of Llama-3-8B as the formal baseline (relative-size match was Qwen2.5-0.5B; we need a stronger upper-anchor); 70B comparison via published TokenPowerBench numbers if direct GPU access is unavailable.
- A pre-registered "what substrate does NOT win" disclaimer page; this is what makes the claim credible.

## (f) Citations (verified count: 25 distinct URLs surfaced across 10 web searches)

Energy and cost benchmarking:
- TokenPowerBench (arxiv 2512.03024) - phase-aware J/token measurement; Llama3-70B fp8 at ~0.39 J/token best-practice
- NVIDIA Technical Blog - normalized request-per-second-per-GPU for fair LLM cost comparison
- Anyscale - reproducible performance metrics for LLM inference
- Databricks - LLM inference performance engineering best practices
- LLM-Inference-Bench (arxiv 2411.00136) - cross-engine benchmark methodology
- TokenPowerBench AAAI 2026 version (ojs.aaai.org)
- The Price of Prompting (arxiv 2407.16893) - energy profiling
- How Hungry is AI (arxiv 2505.09598) - energy, water, carbon footprint of LLM inference
- Beyond Test-Time Compute Strategies (arxiv 2603.20224) - advocating energy-per-token

Methodology and iso-metric comparison:
- Evaluating Asymmetric Multicore Systems-on-Chip using Iso-Metrics (arxiv 1503.08104)
- Statsig - FLOPS efficiency: computing performance per parameter
- No One-Size-Fits-All (arxiv 2509.22980) - iso-area bit-parallel vs bit-serial

Scaling and ceiling:
- Task-Specific Efficiency Analysis (arxiv 2603.21389) - three scaling regimes; classification saturation near 0.5B
- Does Model Size Matter (arxiv 2510.21443)
- Meta Llama 3 review - 8B outperforms 70B Llama 2 on MMLU
- iternal.ai - 1B vs 8B vs 70B vs 1T comparison

Calibration and conformal:
- URAG (arxiv 2603.19281) - conformal prediction over RAG
- CONFLARE (arxiv 2404.04287) - conformal LLM retrieval
- Conformal Factuality (arxiv 2506.20978) - conditional conformal factuality for RAG
- Trustworthy RAG survey (arxiv 2502.06872)

Reproducibility and determinism:
- Towards Reproducible LLM Evaluation (arxiv 2410.03492) - quantifying uncertainty in benchmark scores
- Numerical Sources of Nondeterminism (arxiv 2506.09501)
- A Sober Look at Progress in Reasoning (arxiv 2504.07086) - 15% Pass@1 variance across seeds

Hallucination and knowledge-base:
- KGHaluBench (arxiv 2602.19643) - breadth and depth of LLM knowledge
- ar5iv 2008.09036 - Language Models as Knowledge Bases; 125M params -> 1M Wikidata triples at 95%
- ExplicitLM (arxiv 2511.01581) - decoupling knowledge from parameters via explicit memory banks
- Memory Layers at Scale (arxiv 2412.09764)
- MEGA-RAG - 40% hallucination reduction with KG augmentation

Latency:
- Databricks - LLM inference performance engineering; TTFT scaling
- DBASolved - TTFT critical latency metric; 7B vs 70B targets

## Substrate-novel-synthesis cap applied

This drill proposes a four-axis normalized benchmark methodology and ranks substrate-vs-LLM differentiation by scale-invariance. The methodology is a SYNTHESIS of published axes (TokenPowerBench J/token, NVIDIA per-GPU normalization, URAG conformal, KGHaluBench fact-recall, iso-metric SoC literature). Each axis has direct lit precedent; the contribution is COMBINATION + commercial-axis ranking. P_deflated capped at 0.55 per novel-synthesis rule.

## Next-drill candidates

- Adversarial open-domain benchmark where substrate intentionally LOSES to 70B but the hybrid (substrate-memory + small-LLM-front-end) catches up; quantify the front-end's required parameter count
- Substrate-front-end-only benchmark on agentic tool use (function calling): substrate as deterministic tool-router vs LLM as stochastic tool-router; cost per successful tool call
- Watermark / provenance / audit-trail axis: substrate has per-fact lineage, LLM does not; what's the regulated-industry buyer willing to pay differential
