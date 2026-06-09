# Research drill: structured KB as speculative draft model -- 5x deep probe

**Date:** 2026-06-09
**Author:** research sub-agent
**Trigger:** orchestrator direct dispatch -- speculative decoding 5x deep probe mandate
**Prior art baseline:** Testbed HARD_FAIL on short-answer QA (0.48x, data/cell_specdec_results/metrics.json)

---

## HEADLINE

Speculative decoding's speedup math is real (2-4x empirical on longform generation) and
theoretically lossless. "Structured KB as draft model" is a genuine gap in the literature:
REST/RAPID/ReSpec all retrieve from text corpora or prompt history, not from algebraically
structured KBs with compositional operators and per-token audit chains. The categorical
advantages (sub-ms draft latency, per-token provenance, multi-tenant KB isolation,
confidence-gated drafting, exact erasure) are not addressed by any existing draft architecture.
However: the acceptance rate is the pivotal unknown. If the KB draft distribution diverges
from the LLM's output distribution (likely in open-ended generation), speedup collapses to
near-zero. The technique is genuinely novel and publication-worthy, but the "does it actually
help?" gate requires an empirical acceptance-rate measurement before engineering investment.
P_deflated (novel speedup mechanism) = 0.38.

---

## 1. Speculative decoding fundamentals

### 1.1 Core algorithm (Leviathan 2023; Chen 2023)

Both Leviathan et al. (arXiv 2211.17192) and Chen et al. (arXiv 2302.01318) independently
published lossless speculative decoding in late 2022 / early 2023. The algorithm is:

1. Draft model generates gamma candidate tokens autoregressively (fast, cheap).
2. Target LLM evaluates all gamma+1 positions in ONE parallel forward pass (prefill-mode).
3. A modified rejection sampling scheme accepts the longest prefix consistent with the
   target distribution. Crucially: when a draft token is rejected, a corrected sample is
   drawn from a residual distribution, ensuring the EXACT output distribution of the
   target LLM is preserved.
4. Expected tokens per cycle: E[accepted] = (1 - alpha^(gamma+1)) / (1 - alpha),
   where alpha = E[acceptance rate per token].

The distribution-preservation guarantee is mathematically exact -- not approximate. This
is the core value: zero quality regression is provable, not empirical.

### 1.2 Speedup formula

Theoretical walltime speedup:

  S = (1 - alpha^(gamma+1)) / ((1 - alpha) * (1 + gamma * c))

where c = cost_draft / cost_target (ratio of draft to target model forward-pass time).

At alpha=0.8, gamma=5, c=0.05: S = 3.1x theoretical.
At alpha=0.6, gamma=5, c=0.05: S = 1.9x.
At alpha=0.4, gamma=5, c=0.05: S = 1.1x (barely above 1; overhead nearly eats the gain).

Key insight: the draft must be much cheaper than the target (c << 1) AND the acceptance
rate must be high (alpha >= 0.6) for meaningful speedup. Below alpha=0.5, speculative
decoding is slower than baseline.

The Testbed result (wall_speedup=0.48x on HotpotQA short answers) did NOT contradict this
formula. Short answers (~6 tokens) have no amortization room for setup overhead. The
formula assumes hundreds of tokens per generation. The failure was workload mismatch, not
algorithm failure.

### 1.3 Self-speculative decoding

Several 2024-2025 papers (LayerSkip, SWIFT, CLaSp, KnapSpec) use the target LLM itself
as draft by skipping intermediate layers. No additional model needed, no memory overhead.
CLaSp uses cosine similarity of hidden states from prior verification passes to select
optimal skip configurations dynamically. Reported speedups: 1.5-2.5x depending on task.

---

## 2. Existing draft model architectures -- empirical landscape

| Architecture | Mechanism | Speedup | Acceptance rate | Notes |
|---|---|---|---|---|
| Small LLM (Llama-1B -> Llama-70B) | Independent smaller model | 2-3x | 0.6-0.75 | Vocab must match |
| Medusa (Cai 2023) | Multi-head MLP on last hidden state | 2.2-3.6x | 0.65-0.80 | Needs fine-tuning |
| EAGLE (Li 2024) | Feature-level (2nd-to-last layer) autoregression | 2.7-3.5x | 0.70-0.82 | State of art at launch |
| EAGLE-2 | EAGLE + dynamic draft tree by confidence | Higher than EAGLE-1 | 0.72-0.85 | Best published |
| EAGLE-3 | Training-time test scaling for EAGLE | 70-80% across positions | 0.70-0.80 | Maintains rate at length |
| REST (NAACL 2024) | Trie datastore, longest-suffix match | 1.62-2.36x | Not reported | Code/text; no extra training |
| Lookahead / PLD | N-gram from prompt/context | 1.5-3x on summarization | Context-dependent | ReSpec reports 5.21x on doc summarization |
| SAM-Decoding | Suffix automaton on prompt+context | 2.45x | Context-dependent | Training-free |
| ReSpec | SAM + additional heuristics | 3.05x Vicuna-7B | Context-dependent | 33% over EAGLE-2 on summarization |
| Self-speculative (LayerSkip etc.) | Layer-skipping within target | 1.5-2.5x | N/A (same model) | No extra memory |
| RAPID (2025, ICML) | RAG drafter on shortened context | >2x on longform | Not reported as alpha | LLM drafter, not KB drafter |

Notes on the landscape:
- EAGLE-family (feature-level autoregression) is the current leader on generation tasks.
- Retrieval-based methods (REST, ReSpec, SAM-Decoding) are competitive on tasks where
  output closely mirrors input (summarization, code reuse). They fail on open-ended chat.
- RAPID is the closest analog to the structured-KB idea, but it uses a RAG-fed LLM as
  drafter, not a structured KB with algebraic operators.
- Hydra (2024) adds sequential dependency between Medusa heads -- improves coherence.
- No paper uses an algebraically structured KB (hypervector bundle, Datalog operators,
  confidence scores) as the draft model.

---

## 3. Knowledge-augmented speculative decoding -- where the lit lives

### 3.1 Speculative RAG (Google, 2024, arXiv 2407.08223)

This inverts the RAG/spec-dec relationship: a SMALLER specialist LLM is the drafter, the
LARGER generalist LLM is the verifier. Both operate on retrieved documents. This is about
accelerating the RAG pipeline quality, NOT about the KB being the draft model.

### 3.2 RAPID (ICML 2025, arXiv 2502.20330)

RAG drafter: the draft LLM operates on a shortened context from retrieval (<=16K tokens)
and drafts for the target long-context LLM (32K+). Speedup: >2x for long contexts.
Key difference from the structured-KB proposal: RAPID's drafter is still an LLM -- it just
has shorter context. The KB provides the shortened context, not the draft tokens directly.

### 3.3 REST (NAACL 2024, arXiv 2311.08252)

Uses a text datastore (trie over corpus) to retrieve and propose draft tokens via
longest-suffix matching. Speedup 1.62-2.36x on code/text generation. Closest to
"external structure as draft" but:
- Datastore is a flat text corpus (n-gram trie), not a structured compositional KB.
- No algebraic operators, no confidence scores, no audit chain.
- No per-tenant isolation; the datastore is shared across queries.
- Relies entirely on exact or near-exact string matching.

### 3.4 SAM-Decoding / ReSpec / PLD

These all retrieve from prompt+context history, not an external KB. The "KB" is the input
itself. No structured semantics.

### 3.5 KBLaM (Microsoft / JHU, ICLR 2025, arXiv 2410.10450)

Encodes KB as key-value attention tokens injected into the LLM's attention layers. The KB
is available to the LLM as extended context. This is not speculative decoding at all -- it
is a KB-augmented context mechanism. But it is the closest system in spirit: structured KB
+ LLM integration. The difference is KBLaM modifies how the LLM uses the KB (as attention
context), whereas the structured-KB-as-draft idea uses the KB to generate draft tokens
EXTERNALLY before the LLM.

### 3.6 Verdict on novelty

No paper in the literature proposes an algebraically structured KB (hypervectors,
compositional operators, confidence gates, audit chain) as the DRAFT MODEL in speculative
decoding. The gap is genuine. The closest analogs are REST (text trie datastore) and RAPID
(RAG-shortened context LLM drafter), but neither provides:
- Compositional algebraic structure in draft token generation
- Per-token provenance / audit chain
- Multi-tenant KB isolation at draft time
- Confidence-gated drafting (accept draft only when KB confidence > threshold)
- Sub-ms draft latency (REST/RAPID still invoke LLM components)

---

## 4. Speedup empirics -- what the numbers actually say

### 4.1 Production deployment

vLLM (2024-2025): Llama-3.1-70B + 1B draft --> 2.31x speedup. Llama-3.1-8B on A100 -->
1.8x. Arctic Inference + vLLM --> 4x for agentic long-generation workloads.

TensorRT-LLM on H200: Llama-3.1-405B with speculative decoding + FP8 quantization -->
3.6x throughput improvement.

Standard reported range for well-matched draft models on longform generation:
- Alpha = 0.75-0.85, gamma = 5: approximately 2.5-3.5x speedup.
- Alpha < 0.6: speedup below 2x; potentially not worth deployment overhead.

### 4.2 Hardware sensitivity (important caveat)

An RTX 3090 measured 1.5x speedup; an H100 showed no speedup under the same configuration.
Higher-bandwidth GPUs (H100, GH200) leave less idle compute for speculative decoding to
exploit. The mechanism that enables speedup is that LLM inference is memory-bandwidth-bound
in autoregressive mode, and speculative decoding switches the verification step to
compute-bound (prefill mode). On memory-constrained GPUs, this is a large win. On
bandwidth-saturated GPUs, the win is smaller.

Implication for the structured-KB draft: if the runner is an H100 or GH200, a sub-ms
KB draft may not produce speedup even with a high acceptance rate, because the GPU is
already operating near its memory-bandwidth ceiling. Need to measure on the actual target
hardware.

### 4.3 Draft model latency analysis

Small LLM drafts (OPT-125M): 6.23 ms per draft token.
Small LLM drafts (OPT-6.7B): 18.56 ms per draft token.
Sub-ms retrieval (structured KB at 100M+ scale): ~0.3-1.0 ms per batch.

The structured KB has a 6-20x draft latency advantage over even the smallest LLM drafts.
This means the cost ratio c = cost_draft / cost_target is much smaller, which directly
improves the speedup formula. Even at alpha=0.5 (mediocre acceptance), the sub-ms KB
draft may still produce positive speedup where a 6ms LLM draft would not.

### 4.4 The acceptance rate problem

The fundamental risk for structured-KB-as-draft is acceptance rate. A text-trie datastore
(REST) achieves meaningful alpha because it matches verbatim corpus continuations. An
algebraic KB proposes tokens based on compositional queries and intent classification. This
is a qualitatively different distribution:

- KB is strong where queries ask for structured facts already in the KB (entities,
  relations, numerical values). Alpha could be 0.7-0.9 for these.
- KB is weak where generation is narrative, creative, or requires reasoning over gaps.
  Alpha could be 0.1-0.3 for these.
- KB is completely blind where the LLM generates from its parametric knowledge on topics
  not in the KB. Alpha = 0 (every draft rejected).

The KB draft is not competitive with EAGLE-family methods on open-ended generation.
It is a domain-specific draft, not a general-purpose draft.

---

## 5. Risk profile for KB-based draft

### Risk 1: Low acceptance rate on open-ended generation (HARD-FAIL risk)

If the KB draft distribution diverges from the LLM output distribution (expected for
open-ended chat, creative writing, reasoning), alpha < 0.4 is likely. At alpha=0.4 with
any positive c, speedup is near 1.0x -- no benefit. This is not a safety failure (quality
is preserved by the rejection sampling guarantee), but it is a business failure: no
speedup, added engineering complexity.

Mitigation: scope the KB draft STRICTLY to query types where KB coverage is known
(factual Q&A, structured retrieval, entity/relation lookups). Detect out-of-scope queries
via the intent classifier and disable drafting for those.

### Risk 2: Coverage gaps (SAFE failure mode)

When a query asks about entities or facts not in the KB, the KB cannot generate a
meaningful draft. This degrades to alpha~0 and the system falls back to LLM-only decoding.
Quality is preserved (LLM output unchanged). Speedup drops to 1.0x for those queries.
This is the safest failure mode: graceful degradation to baseline.

### Risk 3: Draft latency exceeds LLM token time on high-bandwidth GPUs

On H100/GH200, LLM token generation time may already approach the latency floor. If the
KB pipeline (intent classify + algebraic query + vector retrieval + token projection)
accumulates to >5ms, and LLM token time is 8-12ms on H100, the speedup headroom is
narrow. The sub-ms raw retrieval may expand to 3-5ms when accounting for:
- Intent classifier inference (~1-2ms)
- Datalog query compilation + execution (~0.5ms)
- Confidence score computation (~0.2ms)
- Token vocabulary projection (~0.5ms)

Total KB draft pipeline: ~2-4ms is a plausible estimate. This keeps c = 0.2-0.4 on a
fast GPU -- still favorable but not the "c -> 0" regime assumed above.

### Risk 4: Vocabulary alignment mismatch

The KB's token projection must map KB outputs to the exact LLM vocabulary distribution.
If the KB produces entity phrases that the tokenizer splits differently from the LLM's
expected single-token prediction, the draft tokens are systematically wrong and alpha
collapses. This requires careful design of the KB-to-token projection layer.

### Risk 5: Systematic bias in KB draft (important but managed)

If the KB always drafts from the same high-frequency entities, the rejection sampling
still produces the correct LLM distribution, but with low efficiency (always rejecting
the same draft pattern). This is detectable via alpha monitoring and can be corrected by
confidence-gating (don't draft when KB confidence is low -- disable early rather than
let through low-quality drafts).

### Risk 6: Multi-tenant security contamination

In a multi-tenant setting, per-tenant KB isolation is one of the claimed advantages. But
if the routing logic leaks one tenant's KB content into another's draft token stream (even
briefly), this is a privacy violation. The audit chain (PP-184) is a mitigation, but the
isolation must be verified as a hard invariant, not just an architectural intent.

### Worst-case behavior

Worst case: alpha < 0.2 on all query types, pipeline overhead 5ms, H100 target GPU. In
this case speculative decoding is actively slower than baseline (0.7-0.9x wall speedup)
with no quality change. The system degrades gracefully (quality preserved) but the
engineering investment is wasted. This is not catastrophic but it is a 2-3 engineer-week
loss if discovered late.

---

## 6. Categorical advantages of structured KB as draft

### 6.1 Sub-ms draft latency (largest practical advantage)

KB retrieval at sub-ms vs LLM draft at 6-20ms is a 6-50x latency ratio improvement in
the draft cost c. This moves the speedup formula from c~0.1 (small LLM) toward c~0.02
(KB at 0.3ms on 15ms LLM token). Even at lower acceptance rates, the KB draft may produce
positive speedup where a small-LLM draft would not.

At c=0.02 and alpha=0.5, gamma=5: S = 1.6x (vs 1.1x for c=0.05).
At c=0.02 and alpha=0.6, gamma=5: S = 2.1x (vs 1.9x for c=0.05).

The sub-ms draft latency is the KB's single largest competitive advantage over
small-LLM drafts.

### 6.2 Per-token audit chain (novel in speculative decoding literature)

No existing speculative decoding paper provides per-token provenance. Standard speculative
decoding is a black box: accepted tokens come from a mix of draft and target model
corrections, with no record of which is which. The structured KB (PP-184 Merkle audit
chain) enables, for every accepted draft token:
- Which KB record it was derived from (source document ID, version, timestamp)
- Which algebraic operation produced the draft
- Confidence score at draft time
- Whether LLM accepted or corrected the draft

This is novel in the spec-dec literature. No paper from the survey implements per-token
provenance for accepted draft tokens. It is also commercially differentiated: regulated
industries (healthcare, finance, legal) care about token-level attribution for audit
compliance.

### 6.3 Multi-tenant KB isolation

Each tenant's KB is an independent FHRR bundle. Per-tenant draft models require zero
additional LLM copies -- only the KB changes per tenant. Small-LLM drafts require either
a fine-tuned per-tenant draft model (expensive) or a shared draft model that loses
per-tenant specificity. The structured KB gives per-tenant drafting at no per-tenant LLM
cost.

This is a meaningful commercial differentiator for multi-tenant SaaS settings.

### 6.4 Exact erasure of draft sources (PP-104)

If a user invokes GDPR right-to-erasure and their data record is deleted from the KB,
future drafts will no longer be sourced from that record. No existing speculative decoding
system supports this. Standard draft models (fine-tuned LLMs) memorize training data and
cannot provide record-level erasure. The structured KB provides exact erasure with
algebraic guarantees (the record's hypervector bundle is removed; related drafts are no
longer generated).

### 6.5 Confidence-gated drafting (PP-107)

The KB algebraic confidence score enables early exit from drafting: if confidence < theta,
don't generate a draft, let the LLM decode freely. This prevents wasting verification
overhead on low-quality drafts. Existing methods (EAGLE, Medusa) also have confidence
mechanisms (via tree pruning), but they are model-internal -- not tied to an external
knowledge structure. The KB confidence is semantically meaningful: high confidence means
the KB has a direct algebraic match to the query intent.

### 6.6 Compositional draft generation

The KB's Datalog^neg operators enable multi-hop compositional drafts: "entity A, relation
R, entity B, attribute P of B" can be composed algebraically. This is qualitatively
different from all existing draft architectures (which are purely distributional, not
compositional). For structured factual queries, the KB can generate longer correct draft
prefixes than an LLM-based drafter, potentially driving gamma higher (more draft tokens
per step) without quality loss.

---

## 7. Novel research opportunity assessment

### 7.1 Literature gap confirmation

Exhaustive search across:
- arXiv speculative decoding survey (2401.07851v3)
- REST (2311.08252, NAACL 2024)
- RAPID (2502.20330, ICML 2025)
- Speculative RAG (2407.08223)
- KBLaM (2410.10450, ICLR 2025)
- EAGLE, EAGLE-2, EAGLE-3
- Medusa, Hydra, Lookahead, PLD, SAM-Decoding
- Full GitHub awesome-speculative-decoding catalog

No paper proposes: (a) an algebraically structured KB (hypervector bundle, compositional
operators) as the draft model, (b) per-token provenance for speculative decoding accepted
tokens, or (c) per-tenant KB isolation for multi-tenant speculative drafting.

The closest is REST, which uses a text datastore (trie) for draft token retrieval. The
difference: REST is a shallow n-gram index; the structured KB has algebraic composition,
confidence scoring, audit chain, and per-tenant isolation.

### 7.2 Novelty axes (ranked)

1. Sub-ms algebraic KB as speculative draft (mechanism novelty): No prior work.
2. Per-token provenance for accepted speculative tokens (audit novelty): No prior work.
3. Multi-tenant KB isolation for draft model (deployment novelty): No prior work.
4. Exact erasure of draft sources (privacy novelty): No prior work.
5. Confidence-gated drafting from algebraic KB confidence (efficiency novelty): Partially
   exists in EAGLE-2 tree pruning but not tied to external KB.

### 7.3 Publication potential

Strong signal for a systems/NLP venue (NAACL, EMNLP, ACL, ICLR workshop) IF the
acceptance rate on structured KB queries is empirically demonstrated to be >= 0.6. The
privacy/audit angle is independently publishable (no quality-speedup contribution needed).
The multi-tenant KB isolation angle could be a deployment systems paper.

Calibration: P(publishable with positive speedup result) = 0.42 (deflated from 0.55 raw).
P(publishable on privacy/audit angle alone, speedup irrelevant) = 0.65.

### 7.4 Commercial value

High if deployment target is regulated industries (healthcare, finance, legal) where
per-token audit compliance is a purchasing decision. Moderate for general enterprise SaaS
(multi-tenant isolation is differentiating but not regulatory-mandated). Low for consumer
or research LLM deployments (speedup alone does not differentiate if EAGLE-3 is available
and acceptable for their use case).

---

## 8. Empirical proof-of-concept plan -- 5 anchors

### Anchor A: acceptance_rate_kb_draft_v1 (CHEAPEST DECISIVE TEST)

Goal: Measure alpha directly on a structured KB draft against Pythia-160M (or Qwen2.5-1.5B)
on a dataset where KB coverage is known (e.g., a set of factual lookups drawn from the
KB's own records).

Design intent (not implementation spec):
- Pre-load KB with K known facts.
- Generate N queries that ask directly about those facts (high expected alpha).
- Generate N' queries that ask about topics NOT in the KB (expected alpha near 0).
- Record token-level acceptance rate per query type.
- Measure actual draft pipeline latency vs LLM token time.

Pre-registration:
  HARD-PASS: alpha >= 0.65 on KB-covered factual queries AND draft pipeline < 3ms.
  MIDDLE-BAND: alpha = 0.45-0.65 OR pipeline 3-8ms (marginal; further optimize before commit).
  HARD-FAIL: alpha < 0.40 on KB-covered queries OR pipeline > 10ms.

Hardware: CPU laptop, no GPU required (Pythia-160M CPU fine for measurement; acceptance
rate measurement is the signal, not throughput). Estimated wall: 1-2 hr.

This is the single cheapest decisive test. If alpha < 0.40, the entire architecture is not
viable for longform generation, and the audit-chain + multi-tenant advantages can be
pursued without the speculative-decoding framing.

### Anchor B: draft_pipeline_latency_breakdown_v1

Goal: Time each stage of the KB draft pipeline independently (intent classifier, algebraic
query, vector retrieval, confidence score, token projection) to identify dominant latency
term.

Pre-registration:
  HARD-PASS: total pipeline < 2ms on runner hardware.
  MIDDLE-BAND: 2-5ms (workable but narrows speedup headroom).
  HARD-FAIL: > 8ms (eliminates speedup on fast GPU targets).

Hardware: CPU/GPU local. Wall: ~30 min.

### Anchor C: wall_speedup_longform_v1

Goal: End-to-end wall speedup comparison on longform generation (target 256+ token
outputs). Requires Anchor A to confirm alpha >= 0.5 first.

Pre-registration:
  HARD-PASS: wall speedup >= 1.5x on longform KB-factual queries.
  MIDDLE-BAND: 1.2-1.5x.
  HARD-FAIL: < 1.1x.

Hardware: GPU (16GB+), local runner preferred. Wall: 2-4 hr.

### Anchor D: quality_preservation_v1

Goal: Confirm LLM output distribution is unchanged by KB drafting (per rejection-sampling
guarantee). Measure perplexity on a held-out set with and without KB draft.

Pre-registration:
  HARD-PASS: perplexity delta < 0.5% AND answer F1 delta < 0.02.
  HARD-FAIL: any statistically significant quality regression.

This anchor is expected to PASS by the theoretical guarantee. If it fails, there is an
implementation bug in the rejection sampling (very high priority to fix).

### Anchor E: multi_tenant_isolation_v1

Goal: Confirm that per-tenant KB isolation prevents cross-tenant draft token leakage.
Design two tenant KBs with non-overlapping entities; verify that tenant A queries never
produce draft tokens from tenant B records.

Pre-registration:
  HARD-PASS: zero cross-tenant draft tokens in N=1000 queries.
  HARD-FAIL: any single cross-tenant draft token.

This is a correctness test, not a performance test. Binary pass/fail.

---

## Falsifiable predictions

### HARD-PASS thresholds (architecture viable)

1. alpha >= 0.65 on KB-covered factual queries (Anchor A).
2. Draft pipeline < 3ms on runner hardware (Anchor B).
3. Wall speedup >= 1.5x on 256+ token generation (Anchor C).
4. Quality delta < 0.5% perplexity (Anchor D -- expected from theory).
5. Zero cross-tenant draft leakage (Anchor E).

### HARD-FAIL thresholds (stop or pivot)

1. alpha < 0.40 on KB-covered queries --> stop speculative-decoding direction; pivot to
   KB-as-context (KBLaM-style) or RAG-integration only.
2. Draft pipeline > 10ms --> eliminate speculative-decoding integration; KB sub-ms
   advantage is lost.
3. Quality regression > 2% perplexity --> implementation bug in rejection sampling;
   block on fix before any further speedup measurement.
4. Any cross-tenant draft token leakage (Anchor E) --> block v1 demo multi-tenant launch;
   architectural redesign required.

---

## 9. Cross-thread synthesis with prior findings

### 9.1 Testbed HARD_FAIL context

The June 7 Testbed result (wall_speedup=0.48x on HotpotQA, ~6.4 tokens/answer) does NOT
falsify the structured-KB-as-draft direction. It falsifies speculative decoding for
short-answer QA workloads regardless of draft model type. The mechanism is clear:
amortization requires long generation (256+ tokens). The Testbed note correctly identified
"workload mismatch" as the cause.

Implication: the structured-KB-as-draft is relevant ONLY for the long-generation path in
the v1 demo (multi-turn chat, long summarization, explanation generation). It is NOT
relevant for the hotpot_3baseline short-answer QA path.

### 9.2 Connection to Tier-5c LM results

The HARD_PASS substrate-attention results (Pythia +20% ppl, Qwen-1.5b +15% ppl) show that
the substrate can provide useful signal to LLM attention. The structured-KB-as-draft is a
different integration point (draft generation vs attention modulation), but the empirical
finding that "substrate can beneficially interact with LLM inference" supports the
plausibility of KB-influenced draft quality.

### 9.3 PP-184 Merkle audit chain as per-token provenance

PP-184 was designed for KB record-level audit. Repurposing it for per-token draft
provenance is an extension of the existing design, not a new capability. The Merkle
structure naturally supports token-level attribution: each draft token maps to a KB record
version hash. This is implementable without new infrastructure.

### 9.4 Multi-hop retrieval revival connection

The multi-hop revival project (HARD_FAIL on ColBERT-v2 but iterative retrieval validated
at +0.04) has structural overlap with speculative decoding: both involve multi-step
compositional inference. The KB's Datalog^neg operators that support multi-hop retrieval
are the same operators that could generate compositional multi-step draft prefixes.
Speculative decoding could be a downstream beneficiary of multi-hop KB improvement.

---

## 10. Substrate-product implications

### For v1 demo

Short-answer QA (hotpot_3baseline): speculative decoding provides no speedup. Closed
by Testbed evidence. The answer step is not the latency bottleneck for 6-token answers.

Long-generation tasks (chat, summarization, explanation): speculative decoding is
applicable. The KB draft is viable IF alpha >= 0.5 on the relevant queries. Must
measure before committing engineering time.

### For v1.1 enterprise differentiators

Per-token audit chain is a genuine enterprise differentiator for regulated industries.
This is achievable regardless of speedup results (can ship audit chain for ALL accepted
tokens, draft or not, as a production feature). Does not require speculative decoding to
be the acceptance rate winner.

Multi-tenant KB isolation for drafting is relevant for SaaS deployments. Architecturally
clean: no additional per-tenant LLM, only per-tenant KB.

### For research positioning

The novelty is real. The question is whether the acceptance rate justifies the speedup
claim or whether the value is purely in the audit/privacy/multi-tenant angles. Both paths
lead to publishable contributions; the speedup path also leads to system performance claims
that are commercially more visible.

---

## 11. Confidence-calibrated recommendation

1. Run Anchor A (acceptance rate measurement) first. This is the pivotal gate. 1-2 hr, CPU,
   no cloud cost. If alpha < 0.40, redirect engineering investment to audit-chain and
   multi-tenant angles without the speculative-decoding framing.

2. If Anchor A PASSES (alpha >= 0.65), run Anchor B (pipeline latency) in parallel with
   Anchor D (quality preservation). Both are cheap and fast.

3. If both pass, Anchor C (wall speedup on longform) is the investment decision gate.
   Only then route to Testbed for GPU validation.

4. Anchor E (multi-tenant isolation) should run in parallel with development as a
   correctness invariant, not as a performance gate.

5. Do NOT assume hardware independence. The H100/GH200 memory-bandwidth saturation effect
   means a GPU-local measurement on the exact target hardware is required before
   production claims.

P_deflated (structured KB as draft viable for speedup): 0.38.
P_deflated (per-token audit chain as standalone product feature): 0.72.
P_deflated (multi-tenant KB isolation as standalone product feature): 0.65.

---

## Citations (verified from search, 23 sources)

1. Leviathan et al. (2023). "Fast Inference from Transformers via Speculative Decoding." arXiv 2211.17192.
2. Chen et al. (2023). "Accelerating Large Language Model Decoding with Speculative Sampling." arXiv 2302.01318.
3. Cai et al. (2023). "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads." Semantic Scholar.
4. Li et al. (2024). "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty." arXiv 2401.15077.
5. Li et al. (2024). "EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees." arXiv 2406.16858.
6. Li et al. (2025). "EAGLE-3: Scaling up Inference Acceleration via Training-Time Test." arXiv 2503.01840.
7. He et al. (2024). "REST: Retrieval-Based Speculative Decoding." arXiv 2311.08252. NAACL 2024.
8. Anonymous et al. (2025). "RAPID: Long-Context Inference with Retrieval-Augmented Speculative Decoding." arXiv 2502.20330. ICML 2025.
9. Zheng et al. (2024). "Speculative RAG: Enhancing Retrieval Augmented Generation through Drafting." arXiv 2407.08223.
10. Fu et al. (2024). "Break the Sequential Dependency of LLM Inference Using Lookahead Decoding." arXiv 2402.02057.
11. (2024). "Prompt Lookup Decoding." GitHub / Aphrodite Engine docs.
12. (2024). "ReSpec: When, What, and How: Rethinking Retrieval-Enhanced Speculative Decoding." arXiv 2511.01282.
13. Yang et al. (2024). "Hydra: Sequentially-Dependent Draft Heads for Medusa Decoding." arXiv 2402.05109.
14. Meta AI (2024). "LayerSkip: Enabling Early Exit Inference and Self-Speculative Decoding." arXiv 2404.16710.
15. Xia et al. (2024). "SWIFT: On-the-Fly Self-Speculative Decoding for LLM Inference Acceleration." arXiv 2410.06916.
16. (2025). "CLaSp: In-Context Layer Skip for Self-Speculative Decoding." arXiv 2505.24196.
17. (2025). "KBLaM: Knowledge Base Augmented Language Model." arXiv 2410.10450. ICLR 2025.
18. Su et al. (2024). "Sequoia: Scalable, Robust, and Hardware-aware Speculative Decoding." arXiv 2402.12374.
19. (2024). "CREST: Effectively Compacting a Datastore For Retrieval-Based Speculative Decoding." arXiv 2408.04678.
20. (2025). "Decoding Speculative Decoding." ACL Anthology, NAACL 2025.
21. (2024). "Online Speculative Decoding." arXiv 2310.07177.
22. Survey: Xia et al. (2024). "Unlocking Efficiency in LLM Inference: A Comprehensive Survey of Speculative Decoding." arXiv 2401.07851.
23. Testbed (2026-06-07). "CELL-SPECDEC Qwen-1.5B speculative decoding pretest HARD_FAIL." d:/AI/hd-instrument/notes/testbed_note_speculative_decoding_qwen_v1_2026-06-07.md.
