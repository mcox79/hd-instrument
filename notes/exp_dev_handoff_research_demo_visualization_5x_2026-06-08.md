# exp_dev hand-off -- research: demo visualization and UX 5x drill

Filed-by: research sub-agent (2026-06-08)
Trigger: notes/research_drill_demo_visualization_ux_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates,
context pointers, and strategic rationale. exp_dev (and testbed) design actual anchors,
implementation scripts, and queue assignment autonomously. Pre-reg bands below are
research recommendations; exp_dev validates and may refine before dispatch.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or
confirm with orchestrator). Do not ship if paused.

---

## Context summary

Tier 5 sprint is building a live demo URL: Panel A (substrate-KV production) + Panel B
(substrate-attention-layer PoC) on Pythia-1.4B. The demo needs a visual hook that beats
"another text box with answers" and makes substrate's value visceral to a non-technical
investor audience in 30 seconds.

Research drill identified four categorically differentiated demo elements that no API LLM
can replicate: (1) per-token substrate-attention stream (Panel B gate), (2) cryptographic
audit chain with click-to-verify provenance, (3) algebraic operation playground (AND/NOT/
COUNT/do()), (4) 30-question benchmark comparison with cost comparison.

The recommended build order is phased: Phase 1 (static, no live inference) first as a
comprehension gate before investing in live-render infrastructure.

---

## Anchor candidates (rank-ordered by P_actionable x implementation prerequisite)

### 1. DEMO-BENCH-P1 -- Static benchmark comparison page (HIGHEST PRIORITY, no Panel dependency)

Anchor pointer: DEMO-BENCH-P1 (new; not yet queued)
Substrate-product reading: A static HTML page with 3 pre-cached questions comparing
  substrate-augmented Pythia-1.4B vs GPT-4o-mini. Tests whether the visual framing
  communicates the value proposition in under 30 seconds to a non-expert observer.
  This is the comprehension gate for all downstream demo investment.
Tier hint: CPU / local; 2-4 hours wall; no live inference required for Phase 1
Why-now: Cheapest possible gate. If 4/5 observers understand the value proposition in
  30 seconds, the framing works and Phase 2 build is authorized. If not, framing needs
  redesign before any live-render infrastructure investment.

Pre-reg bands (research recommendation):
  HARD-PASS: 4/5 observers answer "I understand what this does" within 30 seconds without
             any explanation text, on the static 3-question page.
  HARD-FAIL: 3 or more observers ask "what is this?" after 60 seconds (framing is broken).
  MID-BAND: 3/5 observers pass within 30 seconds (framing works but needs refinement).

Implementation note: Three pre-selected factual multi-hop questions where substrate-
  augmented Pythia-1.4B answers correctly and GPT-4o-mini answers incorrectly OR correctly
  but with no audit chain. Manual answers are acceptable for this phase. Include inline
  citation markers [1][2] on the substrate answer showing fact sources. Show cost per query.

### 2. DEMO-INGEST-P4 -- "Add your fact" live playground (Panel A, HIGH PRIORITY)

Anchor pointer: DEMO-INGEST-P4 (new; not yet queued)
Substrate-product reading: A single text input that lets the user type any fact, encodes
  it into the substrate KB in real time (~200ms), then immediately runs a query that would
  retrieve the new fact and shows the answer incorporating it. Demonstrates Panel A
  ingestion + retrieval in a single interaction under 60 seconds.
Tier hint: CPU / local or remote GPU if Pythia inference is needed; Panel A already
  implemented; main engineering work is the demo UI wrapper and stable demo-mode harness.
Why-now: Panel A is the current working capability. This playground requires no Panel B.
  It is the fastest path to a live interactive demo element.

Pre-reg bands:
  HARD-PASS: Fact ingestion < 500ms wall; retrieval of new fact on next query succeeds
             with cosine similarity > 0.80; displayed to user within 2 seconds total.
  HARD-FAIL: Ingestion > 2 seconds, OR new fact retrieval fails on first attempt (demo
             reliability is broken; not suitable for live investor demo).
  MID-BAND: Ingestion < 500ms but retrieval requires 2 queries to surface new fact
             (acceptable; add a "search for it" button as UX fallback).

### 3. DEMO-DELETE-P5 -- GDPR delete with visible state change (Panel A, HIGH PRIORITY)

Anchor pointer: DEMO-DELETE-P5 (new; not yet queued)
Substrate-product reading: Input an entity name; system deletes all associated facts and
  shows the KB state change visually (facts fade out of a mini-grid view). Post-delete,
  a query for the deleted entity returns "No facts found." Demonstrates GDPR Article 17
  compliance in a visceral, measurable way: "Deleted 47 facts in 0.4ms."
Tier hint: CPU / local; Panel A delete already implemented per validated production metrics
  (GDPR delete 0.0004ms); main work is demo UI wrapper.
Why-now: Validated substrate capability (0.0004ms delete empirically confirmed). This is
  low-risk high-signal: the physics work; the demo is an implementation task.

Pre-reg bands:
  HARD-PASS: Delete completes and UI confirms within 1 second; post-delete query returns
             "No facts found" correctly; displayed deletion count is accurate.
  HARD-FAIL: Delete succeeds but post-delete query still returns deleted entity (stale
             index bug; blocks the demo entirely).

### 4. DEMO-ATTN-P7 -- Per-token substrate-attention stream (Panel B gate, MEDIUM PRIORITY)

Anchor pointer: DEMO-ATTN-P7 (new; not yet queued)
Substrate-product reading: Two-column live display: left shows Pythia token-by-token
  generation; right shows retrieved substrate facts per token. This is the categorically
  differentiated visualization: no API LLM can expose per-layer KV injection. Requires
  Panel B (substrate-attention layer) to be working at Pythia layer 6.
Tier hint: GPU (Pythia inference); Panel B is the prerequisite gate; do not dispatch
  this anchor until Panel B smoke test passes.
Why-now: This is the highest-differentiation demo element. Blocked on Panel B. Once Panel B
  is working, this should be the first visualization built on top of it.

Pre-reg bands:
  HARD-PASS: Per-token retrieval events visible in UI synchronized within 200ms of token
             generation; 5 consecutive queries work without crash; 60fps on demo hardware.
  HARD-FAIL: Panel B KV injection does not produce distinguishable retrieval events per
             token (substrate layer not firing; fundamental Panel B debugging required).
  MID-BAND: Retrieval events visible but not synchronized per-token (batch mode fallback
             acceptable for demo; label as "batch retrieval mode" in UI).

### 5. DEMO-KHOP-P8 -- K-hop traversal builder with animated graph (MEDIUM PRIORITY)

Anchor pointer: DEMO-KHOP-P8 (new; not yet queued)
Substrate-product reading: Drag-and-drop query builder for K-hop traversal. Animates
  the traversal as a force-directed graph expanding step by step. Each hop shows the
  retrieved fact node and the similarity score on the edge.
Tier hint: CPU / local; requires K-hop retrieval to be stable; iterative retrieval +0.04
  validated per research brief.
Why-now: K-hop is validated empirically. Animated graph is high-comprehension for
  investor demos (the traversal is the intuition-building interaction).

Pre-reg bands:
  HARD-PASS: K=3 traversal completes in < 2 seconds; animated graph renders 60fps at
             K=3 with branching factor 3 (max 27 nodes visible); no crashes in 10 runs.
  HARD-FAIL: K=3 traversal fails to complete or returns empty chains in > 30% of queries
             (K-hop reliability is not demo-ready; needs substrate-physics fix first).

---

## Context pointers

- Research note (full 40+ pattern analysis):
  d:/AI/hd-instrument/notes/research_drill_demo_visualization_ux_5x_2026-06-08.md
- Production architecture locked (latency + recall validated numbers to use in demo):
  d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md
- North Star memory file:
  d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Testbed role scope (Phase A/B + v1 Pythia + cloud H100):
  d:/AI/hd-instrument/memory/role_testbed_not_orchestrator.md
- v1 demo app build brief:
  d:/AI/hd-instrument/notes/testbed_post_compaction_brief_2026-06-08_v1_demo_audit_week.md

---

## Design references for implementation

Priority reference designs (from research drill):
1. Perplexity.ai inline citation pattern (audit chain UX baseline)
2. Transformer Explainer: https://poloclub.github.io/transformer-explainer/ (per-token
   attention animation timing model)
3. 3d-force-graph: https://github.com/vasturiano/3d-force-graph (K-hop traversal graph)
4. BertViz: https://github.com/jessevig/bertviz (attention heatmap pattern for Panel B)
5. Vellum.ai leaderboard: https://www.vellum.ai/llm-leaderboard (benchmark table design)

---

## Contract section

This hand-off is research-to-implementation. The 5 anchor candidates are provided as
pre-reg recommendations. Testbed / exp_dev is responsible for:
- Validating pre-reg bands before dispatch
- Implementing demo harness scripts (static HTML, demo-mode Panel A/B wrappers)
- Assigning to correct queue (DEMO-BENCH-P1 is CPU local; DEMO-ATTN-P7 needs GPU)
- Writing verdict notes for each phase per standard protocol
- Escalating DEMO-BENCH-P1 HARD-FAIL to orchestrator (framing problem blocks all else)

Build phase gate: DEMO-BENCH-P1 is the gate for Phase 2 build authorization. Do not
invest in live-render infrastructure (P4, P5, P7, P8) until P1 HARD-PASS is confirmed.

## Autonomy declaration

Testbed / exp_dev may dispatch DEMO-BENCH-P1, DEMO-INGEST-P4, DEMO-DELETE-P5 independently
without orchestrator approval (all are local/CPU, low cost, Panel A capabilities are
already validated). DEMO-ATTN-P7 requires Panel B smoke test HARD-PASS first.
DEMO-KHOP-P8 requires K-hop reliability confirmation. Any live-demo URL deployment to
external audience requires orchestrator approval before publishing.
