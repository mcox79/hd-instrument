# exp_dev hand-off -- research: structured KB as speculative draft model

Filed-by: research sub-agent
Date: 2026-06-09
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_speculative_decoding_5x_2026-06-09.md
Urgency: MEDIUM -- novel architecture direction, no blocking product claim; Anchor A gates all downstream work

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths, tokenizer choices)
are to be authored by exp_dev from the research note + cap_map context. Do NOT treat the
descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: acceptance_rate_kb_draft_v1 (CPU, CHEAPEST DECISIVE TEST)

Anchor pointer: Research note Section 8 "Anchor A" + Section 5 "Risk 1"
Substrate-product reading: Measures token-level acceptance rate (alpha) when the structured
KB draft model proposes tokens against a small target LLM on KB-covered factual queries vs
out-of-KB queries. If alpha >= 0.65 on KB-covered queries, the architecture is viable for
longform generation speedup. If alpha < 0.40, redirect to audit-chain / multi-tenant angles
without speculative-decoding framing.
Tier hint: CPU laptop, no GPU. Pythia-160M or similar tiny model as target. ~1-2 hr.
MUST RUN FIRST -- gates all other anchors in this handoff.
Why-now: The Testbed HARD_FAIL (June 7) was workload mismatch (short answers), not mechanism
failure. The acceptance rate on KB-factual longform generation is the open question. All
downstream engineering (pipeline latency, wall speedup) is irrelevant if alpha is too low.

Pre-reg bands:
  HARD-PASS: alpha >= 0.65 on KB-covered factual queries AND alpha < 0.20 on out-of-KB queries (shows selectivity, not noise)
  MIDDLE-BAND: alpha = 0.45-0.65 (marginal; run Anchor 2 before committing)
  HARD-FAIL: alpha < 0.40 on KB-covered queries OR alpha > 0.35 on out-of-KB queries (no discrimination signal)

### Anchor 2: draft_pipeline_latency_breakdown_v1 (CPU/GPU, fast)

Anchor pointer: Research note Section 8 "Anchor B" + Section 5 "Risk 3"
Substrate-product reading: Times each stage of the KB draft pipeline (intent classify,
algebraic query, vector retrieval, confidence score, token projection) to identify dominant
latency term. Determines whether the sub-ms raw retrieval advantage survives the full pipeline.
Tier hint: CPU or local GPU. ~30 min. Can run in parallel with Anchor 3 once Anchor 1 passes.
Why-now: Literature shows small-LLM drafts at 6-18ms per token. KB must stay <3ms to maintain
speedup formula advantage (c ratio). If pipeline >8ms, speedup headroom is too small on H100/GH200 targets.

Pre-reg bands:
  HARD-PASS: total KB draft pipeline < 2ms on runner hardware
  MIDDLE-BAND: 2-5ms (workable, narrows speedup headroom)
  HARD-FAIL: > 8ms (eliminates speedup advantage; pivot to audit-chain only)

### Anchor 3: quality_preservation_kb_draft_v1 (CPU/GPU)

Anchor pointer: Research note Section 8 "Anchor D" + Section 1.1 "distribution preservation guarantee"
Substrate-product reading: Verifies that the rejection sampling scheme correctly preserves
the target LLM output distribution when KB drafts are applied. Measures perplexity delta
and answer F1 delta on a held-out set. Expected to PASS by theory; failure indicates
implementation bug in rejection sampling.
Tier hint: CPU or local GPU, ~1-2 hr. Run after Anchor 1 confirms alpha >= 0.45.
Why-now: This is a correctness gate, not a performance gate. Must confirm before any
production claim about quality preservation. The Testbed confirmed quality preservation
(F1 delta -0.0006) on the HF assistant_model implementation; this anchor confirms it for
the KB-specific draft implementation.

Pre-reg bands:
  HARD-PASS: perplexity delta < 0.5% AND answer F1 delta < 0.02 (within noise floor)
  HARD-FAIL: perplexity delta > 2% OR answer F1 delta > 0.05 (implementation bug; block all downstream)

### Anchor 4: wall_speedup_longform_kb_v1 (GPU, gated on Anchors 1+2 passing)

Anchor pointer: Research note Section 8 "Anchor C" + Section 4 "speedup empirics"
Substrate-product reading: End-to-end wall speedup on longform generation (256+ token outputs)
using KB draft vs baseline LLM decoding. Determines whether the sub-ms KB draft advantage
translates to measurable wall speedup on actual hardware. NOTE: must run on the exact target
GPU hardware, not a proxy, due to the H100 memory-bandwidth saturation effect documented in
the research note (Section 4.2).
Tier hint: GPU (16GB+), local runner. ~2-4 hr. Only dispatch after Anchors 1 AND 2 pass.
Why-now: Gates the decision on engineering investment for v1 demo long-generation paths.

Pre-reg bands:
  HARD-PASS: wall speedup >= 1.5x on 256+ token KB-factual generation
  MIDDLE-BAND: 1.2-1.5x (marginal; evaluate engineering cost vs benefit)
  HARD-FAIL: < 1.1x (speculative-decoding direction not viable; shift to audit/multi-tenant)

### Anchor 5: multi_tenant_isolation_correctness_v1 (CPU, correctness gate)

Anchor pointer: Research note Section 8 "Anchor E" + Section 5 "Risk 6"
Substrate-product reading: Verifies that per-tenant KB isolation prevents any cross-tenant
draft token leakage. Instantiates two non-overlapping tenant KBs; runs N queries for tenant A
and N queries for tenant B; confirms zero draft tokens from tenant B appear in tenant A's
generation path and vice versa.
Tier hint: CPU, no GPU. ~1 hr. Run in parallel with development as a correctness invariant.
Why-now: A single cross-tenant draft token is a v1 multi-tenant launch blocker. Catching this
early is cheap; catching it at customer demo is expensive.

Pre-reg bands:
  HARD-PASS: zero cross-tenant draft tokens in N=1000 queries (binary)
  HARD-FAIL: any single cross-tenant draft token detected (architectural redesign required before v1 multi-tenant)

---

## Context pointers

- Research note (full lit-scan + analysis): d:/AI/hd-instrument/notes/research_drill_substrate_speculative_decoding_5x_2026-06-09.md
- Prior Testbed HARD_FAIL (workload mismatch context): d:/AI/hd-instrument/notes/testbed_note_speculative_decoding_qwen_v1_2026-06-07.md
- Prior Testbed handoff (spec-dec routing, June 7): d:/AI/hd-instrument/notes/exp_dev_to_testbed_speculative_decoding_handoff_2026-06-07.md
- Testbed per-question latency data (44KB, forensic detail): d:/AI/hd-instrument/data/cell_specdec_results/per_question_latencies.jsonl

---

## Contract

exp_dev is the implementation and dispatch authority for all anchors above.
Research has delivered the lit-scan, novelty assessment, risk profile, and pre-reg bands.
exp_dev authors the experiment scripts, selects model sizes and KB configurations from
the cap_map and substrate state, runs the smoke gates, and dispatches per normal protocol.

No inline experiment design is provided in this file per [[feedback-no-experiment-design-in-prompts]].

---

## Autonomy declaration

exp_dev may reorder anchors 2-5 based on queue state and runner availability.
Anchor 1 is a hard prerequisite for anchors 3 and 4 (but not 5).
If Anchor 1 HARD-FAILs (alpha < 0.40), exp_dev should route the audit-chain and
multi-tenant angles to cap_map annotation rather than experiment dispatch, and inform
Research of the closure.
