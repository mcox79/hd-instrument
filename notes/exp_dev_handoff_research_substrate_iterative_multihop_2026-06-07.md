# exp_dev hand-off -- research: substrate-augmented iterative multi-hop retrieval via Pattern B

Filed-by: research sub-agent
Date: 2026-06-07 (evening, post-cycle-166)
Trigger: user mandate -- multi-hop ceiling rejected; research identifies Pattern B compositional retriever
as the revival path. See trigger file: notes/testbed_to_research_user_multihop_revive_mandate_2026-06-07.md
Research note: d:/AI/hd-instrument/notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
Pause state: respect data/orchestrator_paused.flag; do not dispatch if paused

Per [[feedback-no-experiment-design-in-prompts]]: this file names candidates, thresholds, and
sequencing only. Exp-dev designs all experiment scripts independently.

---

## Situational update: what changed since the prior handoff

The prior handoff (exp_dev_handoff_research_multihop_precision_ceiling_2026-06-07.md) recommended:
- Primary v1 action: pivot to NQ-open single-hop; do NOT invest in multi-hop for v1
- Three pre-tests listed (BM25 hybrid, NER decomp check, ColBERT bare) as v1.1 candidates

The user has explicitly refused this recommendation. User mandate (verbatim):
  "i want to make sure we revive multihop I think it's extremely important"

Research has identified a MECHANISTICALLY DISTINCT revival path not present in the prior handoff:
substrate Pattern B algebraic unbind as the HOP-2 QUERY GENERATOR, replacing the LLM bridge
extraction step that was the documented failure bottleneck at 1.5B. The prior three HARD-FAILs
(ranker, filter, ColBERT) all tested substrate in passive roles; this tests substrate in the
active compositional role that Pattern B was designed for.

THIS HANDOFF SUPERSEDES the multi-hop section of the prior handoff. The NQ-open recommendation
remains valid but is not in conflict: both can proceed in parallel.

---

## Anchor candidates (rank-ordered; pre-test first, full integration only after gate clears)

### ANCHOR 1 (DECISIVE PRE-TEST -- queue this first)

Anchor pointer: substrate_iterative_multihop_pretest_v1

Substrate-product reading:
The pre-test measures two new quantities that all prior multi-hop work could not measure:
(1) Bridge indexing rate -- fraction of HotpotQA bridge questions where the bridge entity was stored
    in the substrate's bridge index at NER-based indexing time.
(2) Pattern B unbind accuracy on REAL bge-small encoder vectors at N=4096 with L2 norm patch.
Together these determine whether the algebraic multi-hop architecture is viable. The prior three
HARD-FAILs bypassed both of these. If bridge indexing rate >= 0.65 and unbind accuracy >= 0.80,
the recall@2 estimate is 0.58-0.65 -- a genuine improvement over vanilla bge-small (0.42) and
competitive with IRCoT at 0.7B (estimated ~0.52 recall@2).

Architecture to test (exp-dev designs the script; this is the logical spec):
- Step 1: Load 50 HotpotQA distractor bridge questions + provided passage pool (~500 passages total)
- Step 2: Build bridge index: run spaCy NER on all passages, extract entity pairs, store bind(E_A, E_B)
  per co-occurring pair using substrate Pattern B at N=4096 with L2 norm patch
- Step 3: For each question: extract primary entity E_query using Qwen2.5-1.5B from question text
- Step 4: Hop-1 retrieval: standard bge-small cosine on all passages, retrieve top-3
- Step 5: Substrate unbind: for each hop-1 passage, compute unbind(stored_binding, E_query)
  to recover bridge entity vector; superpose across top-3 passages
- Step 6: Hop-2 retrieval: use unbind output as query; retrieve top-2 from bridge index
- Step 7: Measure separately: bridge indexing rate, unbind accuracy, recall@2, answer F1 vs baseline

Tier hint: GPU runner (for bge-small encoder); ~3-4 hours wall time
Requires: spaCy en_core_web_sm, bge-small-en-v1.5, Qwen2.5-1.5B, substrate Pattern B N=4096 with L2 patch
Dataset: HotpotQA distractor dev set (first 50 bridge questions in standard ordering)

Pre-registered thresholds:

HARD-PASS: recall@2 >= 0.60 AND bridge indexing rate >= 0.65
  - Proceed to ANCHOR 2 (full integration, 1-2 weeks)
  - Customer pitch unlock: "substrate Pattern B algebraically composes multi-hop queries;
    recall@2 0.60 approaches IRCoT-class iterative retrieval at <15ms retrieval loop"
  - Compliance claim: each hop is Merkle-chained and tamper-verifiable per cycle 164 HP

MIDDLE-BAND: recall@2 in [0.50, 0.60) OR bridge_indexing_rate in [0.50, 0.65)
  - File a verdict to Research identifying which component is the bottleneck
  - If bridge_indexing_rate < 0.65: try spaCy en_core_web_lg (30 min CPU extension to same run)
  - If unbind_accuracy < 0.80: test N=8192 or FHRR encoding in a follow-up mini-test
  - Do NOT proceed to full integration until bottleneck resolved
  - Expected timeline: 1-2 additional pre-test cycles (days, not weeks)

HARD-FAIL: recall@2 < 0.50 OR bridge_indexing_rate < 0.40
  - Substrate-augmented iterative path blocked at current architecture
  - Fall to ANCHOR 3 (ColBERT bare pre-test -- still not run after CELL-COLBERT harness failure)
  - Do NOT close the multi-hop revival path; route back to research for the Fallback A1/A2 analysis

Important: this pre-test differs from cycle 157 entity_bridge_decomp HF. That used REGEX NER on query
text + bge-small cosine. This uses LLM+spaCy NER on RETRIEVED PASSAGES + substrate algebraic unbind.
Mechanistically distinct; the cycle 157 HF is not predictive for this test.

Why now: this is the lowest-cost test that provides the most decisive information. The bridge indexing rate
measurement does not exist anywhere else in the portfolio. 3-4 GPU hours clears a 1-2 week engineering
decision.

---

### ANCHOR 2 (full integration -- only dispatch if ANCHOR 1 passes hard-pass threshold)

Anchor pointer: substrate_iterative_multihop_integration_v1

Substrate-product reading:
If ANCHOR 1 passes, this is the 1-2 week engineering integration of the substrate-augmented iterative
multi-hop pipeline into the production harness. Full HotpotQA dev evaluation (10K questions).
The key claim to validate at this scale: does bridge indexing rate stay >= 0.65 at 10K questions
(vs 50 in the pre-test)?

Tier hint: GPU runner + CPU for bridge index build (~1-2 days GPU for full eval at 10K)
Gate: ANCHOR 1 must return HARD-PASS before this is queued

Pre-registered thresholds at full-dev scale:
HARD-PASS: recall@2 >= 0.58 at 10K questions (slightly lower bar than 50-question pre-test due to
  harder questions in the full set; still above bge-large 0.47)
HARD-FAIL: recall@2 < 0.50 OR bridge indexing rate < 0.55 at full scale

---

### ANCHOR 3 (fallback -- only if ANCHOR 1 hard-fails)

Anchor pointer: colbert_v2_bare_hotpot_pretest_v2

Substrate-product reading:
If substrate iterative path hard-fails, ColBERT-v2 bare is the next-best option per the prior 3x note.
CELL-COLBERT (cycle 166 context) hard-failed on harness integration issues, not ColBERT retrieval
quality. The bare ColBERT retrieval path has published recall@2 ~0.59 and is the strongest zero-shot
option at fair size in the literature. This pre-test isolates bare retrieval quality from harness issues.

Tier hint: GPU runner; 2-3 hours (index build dominates); ragatouille library
Gate: only dispatch if ANCHOR 1 returns HARD-FAIL

Pre-registered thresholds:
HARD-PASS: recall@2 >= 0.55 (proceed to full ColBERT integration, 2-3 weeks)
HARD-FAIL: recall@2 < 0.50 (accept ceiling; pivot to single-hop + attribution pitch)
Middle: 0.50-0.55 (check recall@10 to see coverage ceiling; proceed with caution)

---

### ANCHOR 4 (parallel, no gate, CPU-only -- queue with ANCHOR 1 if runner capacity allows)

Anchor pointer: bm25_bge_hybrid_hotpot_pretest_v2

Substrate-product reading:
BM25 + bge-small RRF hybrid is the cheapest possible lift on recall@2. No GPU required. Expected
improvement: +0.05-0.10 over bge-small alone. Even if ANCHOR 1 hard-fails, BM25 hybrid improves
the retrieval baseline that Pattern B pair verification operates over. It also provides a better
top-10 candidate pool for any downstream re-ranking.

Tier hint: CPU runner; 2-3 hours; rank-bm25 library; no model download needed
Gate: none; can run in parallel with ANCHOR 1 immediately

Pre-registered thresholds:
HARD-PASS: recall@2 >= 0.50 (include BM25 in production retrieval stack)
HARD-FAIL: recall@2 < 0.47 (no improvement over bge-large; exclude from stack)

---

## Sequencing (exp-dev decides final order, but Research preference is)

Immediate:
- Queue ANCHOR 1 (substrate iterative pre-test) on GPU runner: this is the primary revival test
- Queue ANCHOR 4 (BM25 hybrid) on CPU runner simultaneously: cheap, no conflict, improves baseline

After ANCHOR 1 verdict:
- If HARD-PASS: queue ANCHOR 2 (full integration)
- If HARD-FAIL: queue ANCHOR 3 (ColBERT bare pre-test)
- If MIDDLE: queue follow-up component tests (NER quality, N=8192) per Research guidance

Do NOT queue ANCHOR 2 without ANCHOR 1 passing. Do NOT queue ANCHOR 3 unless ANCHOR 1 hard-fails.
This is a strict dependency gate, not a parallel dispatch.

---

## Context pointers

- Research note (this drill): d:/AI/hd-instrument/notes/research_drill_substrate_iterative_multihop_3x_2026-06-07.md
- Prior 3x note (ceiling analysis + 6 HF stack): d:/AI/hd-instrument/notes/research_drill_multihop_precision_ceiling_3x_2026-06-07.md
- User mandate trigger: d:/AI/hd-instrument/notes/testbed_to_research_user_multihop_revive_mandate_2026-06-07.md
- Prior handoff (superseded for multi-hop section): d:/AI/hd-instrument/notes/exp_dev_handoff_research_multihop_precision_ceiling_2026-06-07.md
- Cycle 166 context (L2 norm patch HP, Pattern B v1.1): d:/AI/hd-instrument/notes/orchestrator_to_research_results_summary_2026-06-07_cycle166.md
- K-hop audit replay HP reference: capability_scorecard.md L44 (khop_audit_replay HP, det=1.000)
- Pattern B primitives HP reference: capability_scorecard.md L375 (cycle 158 acc=1.0 k=2-8)
- ColBERT HARD-FAIL (harness issue, not retrieval quality): notes/testbed_note_colbert_v2_hotpot_distractor_v1_2026-06-07.md

---

## Contract

Exp-dev reads this file and decides whether to dispatch based on:
1. Current queue depth (do not over-fill)
2. Pause flag (data/orchestrator_paused.flag)
3. Gate dependencies above (ANCHOR 2 requires ANCHOR 1 HARD-PASS; ANCHOR 3 requires ANCHOR 1 HARD-FAIL)
4. Per [[feedback-no-experiment-design-in-prompts]]: exp-dev writes all scripts; research only specifies
   the logical architecture and thresholds above

## Autonomy declaration

Exp-dev has full autonomy over:
- Exact script design for each anchor
- Whether to queue ANCHOR 4 in parallel with ANCHOR 1 (Research preference: yes, if runner capacity allows)
- Whether to test spaCy en_core_web_lg vs en_core_web_sm in the same ANCHOR 1 run
- Routing ColBERT result to strategy if it passes (that is a strategy decision, not exp-dev)
- Which runner gets which anchor (ANCHOR 1 needs GPU; ANCHOR 4 is CPU)

Exp-dev does NOT have autonomy over:
- Bypassing the ANCHOR 1 pre-test gate before queuing ANCHOR 2
- Interpreting MIDDLE-BAND result as HARD-PASS for the purpose of queuing ANCHOR 2
- Closing the multi-hop revival path without routing back to research first
- Pre-framing ANCHOR 1 as HARD-PASS expected (per [[feedback-no-preframe-batch-all-pass]])

---

END. Filing this note to trigger exp-dev auto-discovery on next emergency-refill cycle.
