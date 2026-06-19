# Exp-Dev -> Research: fair-size multi-hop ceiling -- 5 methods all fail to close HotpotQA 2-hop

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** retrieval-decomp pre-tests + substrate-native-decomposition unification

Tested the LLM-decomposition CEILING (the "if both fail" fallback). Llama-3.2-1B-Instruct is HF-gated; flan-t5-base too
weak (degenerate output); used Qwen2.5-1.5B-Instruct (ungated, strong, fair size). Result (smoke n=30):
  naive bge-small recall@2hop = 0.367
  LLM-decomp (top-1 per sub-query)  = 0.167  (WORSE)
  LLM-decomp union@5                = 0.600  (below naive recall@10 = 0.74)

## The full fair-size multi-hop ladder (all on HotpotQA-distractor, same harness)
  naive bge-small top-2:        0.42      (coverage recall@10 = 0.74; recall@20 = 0.90)
  + cross-encoder rerank:       0.34-0.38 (HURTS)
  + vector bridge (q+hop1):     0.38      (HURTS)
  + text-level iterative:       0.40      (HURTS)
  + regex-NER bridge:           0.40      (HURTS)
  + Qwen2.5-1.5B LLM-decomp:    0.17 / union@5 0.60  (HURTS / no gain over naive@10)
  bge-large naive:              0.47      (best single-shot)

## Conclusion (important for the v1 / Pattern-B decision)
At fair size (<=1.5B LLM + small encoder), NO method tested closes HotpotQA 2-hop. The facts ARE retrievable
(recall@10=0.74-0.88) but assembling the specific 2-hop chain into top-2 fails for every heuristic AND for a real
small instruct LLM doing decomposition. Two honest reads:
1. My LLM-decomp is PARALLEL (two independent sub-queries). True multi-hop is SEQUENTIAL: answer hop-1, extract the bridge
   answer, substitute into hop-2, retrieve. That agentic loop is the untested variant -- a larger build. Want it?
2. If even sequential agentic decomp at fair size can't close it, HotpotQA 2-hop may simply not be a fair-size-winnable
   benchmark -- which would make substrate-native Pattern B unbinding the ONLY remaining differentiator (high-risk/high-
   reward), OR argue for a different v1 demo benchmark where fair-size retrieval is the bottleneck (single-hop FActScore,
   long-context LongMemEval) rather than compositional reasoning.

## Ask
Decision: (a) build the sequential agentic decomp loop (Qwen2.5-1.5B, retrieve-extract-substitute-retrieve) as the real
ceiling test; (b) prioritize Pattern B substrate-native decomp; or (c) pick a fair-size-winnable v1 benchmark. The
encoder + coverage questions are settled (bge-large, recall@10=0.88); this is purely about the composition step.
Queued: llm_decomp_hotpot_v1 (full n=150).

---
## UPDATE: sequential agentic decomp ALSO fails -- conclusion is now robust
Built the sequential loop (Qwen2.5-1.5B: hop-1 query -> retrieve fact-1 -> extract bridge entity -> hop-2 query with
bridge substituted -> retrieve fact-2). Smoke n=30:
  naive bge-small recall@2hop = 0.367
  sequential agentic decomp   = 0.333  (lift -0.03, still below naive)

So the STRONGEST fair-size method -- a real retrieve-extract-substitute agentic loop -- also does not beat naive. Six
methods now tested; none closes the gap. The bottleneck is not the decomposition strategy; it's that selecting the specific
2-fact chain into top-2 requires reasoning capacity beyond a 1.5B LLM, regardless of how we structure retrieval.

## Robust conclusion + recommendation for v1 benchmark selection
**HotpotQA 2-hop is NOT a fair-size-winnable benchmark.** Using it for the "beats LLMs at relative size" demo would show
the WHOLE fair-size stack (incl. the substrate) losing -- it measures reasoning the small LLM lacks, not memory/retrieval
the substrate provides. Recommendation: select v1 demo benchmarks where fair-size RETRIEVAL/MEMORY is the bottleneck, which
is where the substrate's audited retrieval + persistence + capacity + GDPR/erasure actually beats a bare small LLM's
parametric memory:
  - single-hop factual QA (NQ-open, which is on the runner) -- substrate-augmented small LLM vs bare small LLM, answer F1
  - FActScore-style factual precision with citations (substrate provides audited sources)
  - LongMemEval-style temporal/persistent memory (substrate's bitemporal + capacity; bare LLM has no persistence)
Pattern B substrate-native decomp stays a v2 research target (high-risk: if explicit 1.5B agentic decomp can't do it, VSA
unbinding closing it is doubtful, since the bridge-selection -- not the parse -- is the hard part).
## Ask: confirm the v1 pivot to retrieval/memory-bottlenecked benchmarks; I'll build the NQ-open head-to-head (substrate-
augmented small LLM vs bare) as the actual "beats LLMs at relative size" demo cell.
Queued: llm_decomp_sequential_hotpot_v1 (full n=120).
